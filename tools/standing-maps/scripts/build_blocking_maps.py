#!/usr/bin/env python3
"""Compile per-group starting blocking-map prompts from scene-state.json.

Every 30-second group gets the starting positions of every registered character
in each of its scene segments, plus characters who enter later in that segment.
A segment reuses the previous map of the same scene instance when its group is
adjacent (or the same) and the starting blocking signature is unchanged.

Usage:
  build_blocking_maps.py --ledger scene-state.json [--storyboard A.md ...]
      [--markdown 站位图提示词.md] [--json blocking-maps.json] [--report check.json]
      [--style realistic|diagram] [--aspect 1:1]
      [--view top-down|scene --camera REGISTERED_CAMERA_ID]
Exit codes: 0 = passed, 1 = content failed, 2 = input/report error.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_scene_state import Ledger, group_key, shot_parts  # noqa: E402
from verify_emphasis_shots import parse_storyboard  # noqa: E402

STYLES = {
    'realistic': ('写实正俯视站位参考图：与该场景资产一致的实景，摄影机在正上方垂直向下拍摄；'
                  '人物按各自服装呈现俯视全身形象，可辨认头顶、肩线和身体朝向；地面不加文字、编号或箭头。'),
    'diagram': ('平面站位示意图：浅灰地面，固定陈设用简洁几何轮廓表示；每个人物用服装主色的圆形标记，'
                '圆上加一个表示身体朝向的箭头，旁边标注中文名字。'),
}
NEGATIVE = ('人物数量多于或少于名单，人物位置互换或左右镜像，透视斜视或侧视角度，人物面部特写，'
            '名单外的路人，固定陈设位置改变，画面乱码文字')
MAP_STATE_FIELDS = ('slot', 'posture', 'facing', 'left_hand', 'right_hand', 'contact')


def segment_sort_key(record, index):
    shot = shot_parts(record['entry_shot'])[1] if record.get('entry_shot') else 0
    return (group_key(record['group']), shot, index)


def later_entries(record):
    rows = []
    for item in record['changes']:
        change = item['change']
        if change.get('field') == 'enter' and isinstance(change.get('to'), dict):
            rows.append((change.get('who'), change['to'].get('slot'), item['shot_no'], change['to']))
    return rows


def signature(record, cast=None):
    def person(name, state):
        return (name, tuple(state.get(field) for field in MAP_STATE_FIELDS),
                json.dumps(cast_entry(name, cast or {}), ensure_ascii=False, sort_keys=True))
    start = tuple(sorted(person(name, state) for name, state in record['entry'].items()))
    later = tuple(sorted((shot, person(name, state)) for name, _, shot, state in later_entries(record)))
    return (record['instance'], start, later)


def cast_entry(name, cast):
    """Exact cast entry, else the longest cast key contained in the name (e.g. 封门保镖甲 -> 保镖)."""
    if name in cast:
        return cast[name] or {}
    keys = [k for k in cast if k and k in name]
    return (cast[max(keys, key=len)] or {}) if keys else {}


def describe(name, state, location, cast, include_plan=True):
    look = cast_entry(name, cast).get('look')
    head = f'{name}（{look}）' if look else name
    label = location['slots'].get(state.get('slot'), state.get('slot'))
    plan = location.get('slot_plans', {}).get(state.get('slot')) if include_plan else None
    where = f'{state.get("posture") or "位于"}{label}' + (f'——{plan}' if plan else '')
    parts = [where]
    if state.get('facing'):
        parts.append(f'身体朝向{state["facing"]}')
    for field, label in (('left_hand', '左手'), ('right_hand', '右手'), ('contact', '')):
        if state.get(field):
            parts.append(label + state[field])
    return head, '；'.join(parts)


def build_prompt(entry, location, cast, style, aspect, view='top-down', camera=None):
    plan = location.get('plan') or {}
    fixed = plan.get('fixed') or []
    if isinstance(fixed, str):
        fixed = [fixed]
    start = list(entry['start'].items())
    later = entry['later']
    if view == 'scene':
        lines = ['写实实际场景站位参考图：保持已确认场景几何、人物身份和身体比例；地面不加文字、编号或箭头。',
                 f'画幅{aspect}，机位：{location["cameras"][camera]["desc"]}；呈现{location.get("name", entry["location_id"])}的本段人物关系。',
                 f'空间方位基准（不代表当前机位画幅左右）：{plan.get("orientation", "")}']
    else:
        lines = [STYLES[style],
                 f'画幅{aspect}，正上方90°垂直俯视，{location.get("name", entry["location_id"])}的活动区域完整入画，不裁掉任何人物。',
                 f'方位：{plan.get("orientation", "")}']
    if fixed:
        lines.append('固定陈设：' + '；'.join(fixed) + '。')
    total = len(start) + len(later)
    lines.append(f'本图共{total}个人物，必须全部画出，且只画这些人：')
    for number, (name, state) in enumerate(start, 1):
        head, where = describe(name, state, location, cast, include_plan=view == 'top-down')
        lines.append(f'{number}. {head}：{where}。')
    for offset, (name, slot, shot_no, state) in enumerate(later, len(start) + 1):
        head, where = describe(name, state, location, cast, include_plan=view == 'top-down')
        lines.append(f'{offset}. {head}（本段第{shot_no}镜才入场，图中画在入场位置并略作淡化）：{where}。')
    negative = NEGATIVE if view == 'top-down' else NEGATIVE.replace('透视斜视或侧视角度，', '')
    lines.append(f'负面：{negative}。')
    return '\n'.join(lines)


def compile_maps(ledger, raw, cast, play_order, style, aspect, view='top-down', camera=None):
    errors, warnings = [], []
    order = sorted(range(len(ledger.segments)), key=lambda i: segment_sort_key(ledger.segments[i], i))
    position = {gid: i for i, gid in enumerate(play_order)}
    maps, group_index, last = {}, {}, {}
    plan_checked = set()
    for idx in order:
        record = ledger.segments[idx]
        location = record['location']
        lid = record['location_id']
        selected_camera = (location.get('cameras') or {}).get(camera)
        if view == 'scene' and (not isinstance(selected_camera, dict)
                                or not isinstance(selected_camera.get('desc'), str)
                                or not selected_camera['desc'].strip()):
            if lid not in plan_checked:
                errors.append({'code': 'scene_camera_missing', 'location': lid,
                               'message': f'Scene view needs a registered camera with desc: {camera!r}.'})
                plan_checked.add(lid)
            continue
        if lid not in plan_checked:
            plan_checked.add(lid)
            if not (location.get('plan') or {}).get('orientation'):
                errors.append({'code': 'plan_orientation_missing', 'location': lid,
                               'message': f'Location {lid} needs plan.orientation (top-down direction statement).'})
        sig = signature(record, cast)
        prev = last.get(record['instance'])
        adjacent = False
        if prev:
            gap = position.get(record['group'], -10) - position.get(prev['group'], -100)
            adjacent = gap in (0, 1)
        if prev and adjacent and prev['signature'] == sig:
            map_id = prev['map']
            maps[map_id]['groups'].append(record['group'])
            reused = True
        else:
            map_id = f"MAP-{record['group']}" + (f"-S{shot_parts(record['entry_shot'])[1]:03d}" if record.get('entry_shot') else '')
            entry = {'id': map_id, 'instance': record['instance'], 'location_id': lid,
                     'location_name': location.get('name', lid), 'first_segment': record['id'],
                     'start': record['entry'], 'later': later_entries(record), 'groups': [record['group']]}
            for name, state in list(record['entry'].items()) + [(n, st) for n, _, _, st in entry['later']]:
                if view == 'top-down' and state.get('slot') not in location.get('slot_plans', {}):
                    warnings.append({'code': 'slot_plan_missing', 'map': map_id, 'character': name,
                                     'message': f'Slot {state.get("slot")} has no plan text; map uses the label only.'})
            entry['prompt'] = build_prompt(entry, location, cast, style, aspect, view, camera)
            maps[map_id] = entry
            reused = False
        last[record['instance']] = {'group': record['group'], 'signature': sig, 'map': map_id}
        voice = (raw.get(record['id']) or {}).get('voice_only') or []
        group_index.setdefault(record['group'], []).append(
            {'segment': record['id'], 'map': map_id, 'reused': reused, 'voice_only': voice,
             'characters': sorted(set(record['entry']) | {n for n, _, _, _ in later_entries(record)})})
    return maps, group_index, errors, warnings


def check_storyboard(groups, group_index, cast):
    errors, warnings = [], []
    for group in groups:
        rows = group_index.get(group['id'])
        if not rows:
            errors.append({'code': 'group_without_map', 'group': group['id'],
                           'message': 'Storyboard group has no scene-state segment, so no blocking map.'})
            continue
        on_map = set().union(*(set(r['characters']) for r in rows))
        voice = set().union(*(set(r['voice_only']) for r in rows))
        subjects = group['fields'].get('主要主体', '')
        for name in cast:
            if re.search(re.escape(name) + r'(?![\u4e00-\u9fff])', subjects) and name not in on_map and name not in voice:
                errors.append({'code': 'cast_missing_from_map', 'group': group['id'], 'character': name,
                               'message': f'{name} is listed in 主要主体 but missing from the group blocking map(s).'})
    return errors, warnings


def render_markdown(maps, group_index, play_order, style, aspect, view='top-down'):
    style_name = '写实实际场景' if view == 'scene' else ('写实正俯视' if style == 'realistic' else '平面示意图')
    out = ['# 起始站位图提示词', '',
           f'风格：{style_name}；画幅 {aspect}。每张图对应一个或多个连续组的起始站位；'
           '相邻组人物、落点、姿态、身体朝向、左右手、接触支撑、持物及已登记形象版本均未变时沿用同一张图。',
           '请按“站位图ID.png”命名回传图片，例如 `MAP-E001-G005.png`。', '', '## 组与站位图对照', '',
           '| 组 | 站位图 | 说明 |', '|---|---|---|']
    ordered = [g for g in play_order if g in group_index] + sorted(g for g in group_index if g not in play_order)
    for gid in ordered:
        for row in group_index[gid]:
            note = '沿用' if row['reused'] else '新建'
            if len(group_index[gid]) > 1:
                note += f'（场景段 {row["segment"]}）'
            out.append(f'| {gid} | {row["map"]} | {note} |')
    for map_id, entry in maps.items():
        out += ['', f'## {map_id}', '', f'- 地点：{entry["location_name"]}（{entry["instance"]}）',
                f'- 用于：{"、".join(entry["groups"])}', '', '```text', entry['prompt'], '```']
    return '\n'.join(out) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--ledger', type=Path, required=True)
    parser.add_argument('--storyboard', nargs='+', action='extend', type=Path, default=[])
    parser.add_argument('--markdown', type=Path)
    parser.add_argument('--json', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--style', choices=sorted(STYLES), default='realistic')
    parser.add_argument('--aspect', default='1:1')
    parser.add_argument('--view', choices=('top-down', 'scene'), default='top-down')
    parser.add_argument('--camera', help='Registered location camera ID; used with --view scene.')
    args = parser.parse_args(argv)
    if args.view == 'scene' and args.style != 'realistic':
        parser.error('--view scene requires --style realistic; diagram is a top-down layout.')
    inputs = [args.ledger, *args.storyboard]
    for out in (args.markdown, args.json, args.report):
        if out and any(out.resolve() == p.resolve() for p in inputs):
            parser.error('Outputs must not overwrite the ledger or a storyboard.')
    artifacts = []
    try:
        raw_bytes = args.ledger.read_bytes()
        artifacts.append({'path': str(args.ledger.resolve()), 'sha256': hashlib.sha256(raw_bytes).hexdigest()})
        data = json.loads(raw_bytes.decode('utf-8-sig'))
        if not isinstance(data, dict):
            raise ValueError('Ledger root must be a JSON object.')
        groups, parse_errors = [], []
        for source in args.storyboard:
            text = source.read_bytes()
            artifacts.append({'path': str(source.resolve()), 'sha256': hashlib.sha256(text).hexdigest()})
            parsed, errs = parse_storyboard(text.decode('utf-8-sig'), source)
            groups.extend(parsed)
            parse_errors.extend(errs)
    except (OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({'schema_version': 1, 'status': 'error',
                          'errors': [{'code': 'input_error', 'message': str(exc)}]}, ensure_ascii=True, indent=2))
        return 2
    ledger = Ledger(data).validate()
    raw = {seg.get('id'): seg for inst in (data.get('instances') or {}).values() if isinstance(inst, dict)
           for seg in inst.get('segments') or [] if isinstance(seg, dict)}
    cast = data.get('cast') or {}
    if groups:
        play_order = [g['id'] for g in groups]
    else:
        play_order = sorted({r['group'] for r in ledger.segments}, key=group_key)
    maps, group_index, map_errors, warnings = compile_maps(ledger, raw, cast, play_order, args.style, args.aspect,
                                                         args.view, args.camera)
    sb_errors, sb_warnings = check_storyboard(groups, group_index, cast) if groups else ([], [])
    errors = ledger.errors + parse_errors + map_errors + sb_errors
    warnings = ledger.warnings + warnings + sb_warnings
    serial = {k: {key: v[key] for key in ('id', 'instance', 'location_id', 'location_name', 'groups', 'prompt')}
              | {'characters': sorted(set(v['start']) | {n for n, _, _, _ in v['later']})} for k, v in maps.items()}
    report = {'schema_version': 1, 'status': 'failed' if errors else 'passed', 'artifacts': artifacts,
              'style': args.style, 'aspect': args.aspect, 'view': args.view, 'camera': args.camera, 'maps': len(maps),
              'groups_indexed': len(group_index), 'reused_links': sum(r['reused'] for rows in group_index.values() for r in rows),
              'group_index': group_index, 'errors': errors, 'warnings': warnings,
              'limitations': ['Map prompts cover registered characters only; unregistered people are invisible to this tool. '
                              'A pass does not prove the generated image matches the prompt.']}
    try:
        if args.markdown:
            args.markdown.parent.mkdir(parents=True, exist_ok=True)
            args.markdown.write_text(render_markdown(maps, group_index, play_order, args.style, args.aspect, args.view), encoding='utf-8')
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(json.dumps({'schema_version': 1, 'maps': serial, 'group_index': group_index},
                                            ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    except OSError as exc:
        report['status'] = 'error'
        report['errors'] = errors + [{'code': 'output_error', 'message': str(exc)}]
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 2
    print(json.dumps({k: report[k] for k in ('status', 'maps', 'groups_indexed', 'reused_links', 'errors', 'warnings')},
                     ensure_ascii=True, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())

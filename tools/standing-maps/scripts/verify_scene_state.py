#!/usr/bin/env python3
"""Compile and verify scene-instance blocking handoffs, including nonadjacent returns.

The scene-state ledger (scene-state.json) stores named standing points (slots),
camera stations and one ordered segment chain per scene_instance_id. A later
segment never states its own entry from memory: its entry is derived from the
latest exit of the same instance plus evidenced off-screen changes.

Modes:
  --ledger L                          validate the ledger chain only
  --ledger L --render E001-G003       print compiled entry sentences (return cards)
  --ledger L --storyboard A.md B.md   also check the rendered Markdown
Exit codes: 0 = passed, 1 = content failed, 2 = input/report error.
"""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_timeline import EPISODE, GROUP_CANDIDATE, episode_number, normalize, scan_lines  # noqa: E402


STATE_FIELDS = ('slot', 'posture', 'facing', 'gaze', 'left_hand', 'right_hand', 'contact')
CHANGE_FIELDS = STATE_FIELDS + ('enter', 'leave')
SIDES = ('左', '右', '中')
GROUP_ID = re.compile(r'E([0-9]{3,})-G([0-9]{3,})')
SHOT_ID = re.compile(r'(E[0-9]{3,}-G[0-9]{3,})-S([0-9]{3,})')
BASIS = re.compile(r'(source|storyboard|reference|design):\S.*')
EVIDENCE_BASIS = ('source', 'storyboard', 'reference')
GROUP_NUMBER = re.compile(r'^##[ \t]+第([0-9]+)组')
SHOT = re.compile(r'^【单镜头([0-9]+)】')
NEGATIVE = re.compile(r'^(?:负面提示词|\*\*负面提示词\*\*)[：:]')
FIELD_LINE = re.compile(r'^-[ \t]+\*\*([^*]+)\*\*[：:]')
SCENE_FIELD = '场景与环境状态'


def group_key(gid):
    match = GROUP_ID.fullmatch(gid or '')
    return (int(match[1]), int(match[2])) if match else None


def shot_parts(sid):
    match = SHOT_ID.fullmatch(sid or '')
    return (match[1], int(match[2])) if match else None


def basis_kind(value):
    match = BASIS.fullmatch(value) if isinstance(value, str) else None
    return match[1] if match else None


def render_state(name, state, location):
    """Canonical natural-language blocking sentence, copied verbatim into prompts."""
    slot = location['slots'][state['slot']]
    parts = [f"{name}{state.get('posture') or '位于'}{slot}"]
    if state.get('facing'):
        parts.append(f"身体朝向{state['facing']}")
    if state.get('gaze'):
        parts.append(f"视线看向{state['gaze']}")
    if state.get('left_hand'):
        parts.append(f"左手{state['left_hand']}")
    if state.get('right_hand'):
        parts.append(f"右手{state['right_hand']}")
    if state.get('contact'):
        parts.append(state['contact'])
    return '，'.join(parts)


def state_diff(expected, actual):
    diffs = []
    for name in sorted(set(expected) | set(actual)):
        if name not in actual:
            diffs.append(f'{name}: missing (expected present)')
        elif name not in expected:
            diffs.append(f'{name}: present but not in derived state')
        elif not isinstance(actual[name], dict):
            diffs.append(f'{name}: written state is not an object')
        else:
            for field in STATE_FIELDS:
                if expected[name].get(field) != actual[name].get(field):
                    diffs.append(f'{name}.{field}: derived {expected[name].get(field)!r}, written {actual[name].get(field)!r}')
    return diffs


class Ledger:
    def __init__(self, data):
        self.data = data
        self.errors, self.warnings, self.segments = [], [], []
        self.by_id = {}

    def issue(self, code, message, warning=False, **where):
        row = {'code': code, 'message': message}
        row.update({k: v for k, v in where.items() if v is not None})
        (self.warnings if warning else self.errors).append(row)

    def check_state(self, name, state, location, where):
        if not isinstance(state, dict):
            self.issue('state_type', f'State of {name} must be an object.', **where)
            return False
        unknown = set(state) - set(STATE_FIELDS)
        if unknown:
            self.issue('state_field', f'{name}: unknown fields {sorted(unknown)}; allowed {list(STATE_FIELDS)}.', **where)
        if state.get('slot') not in location.get('slots', {}):
            self.issue('unknown_slot', f'{name}: slot {state.get("slot")!r} is not defined for this location.', **where)
            return False
        for field in STATE_FIELDS:
            if field in state and (not isinstance(state[field], str) or not state[field].strip()):
                self.issue('state_value', f'{name}.{field} must be a nonempty string; omit unknown fields.', **where)
        return True

    def check_locations(self):
        locations = self.data.get('locations')
        if not isinstance(locations, dict) or not locations:
            self.issue('locations', 'Ledger needs a nonempty "locations" object.')
            return {}
        for lid, loc in locations.items():
            if not isinstance(loc, dict) or not isinstance(loc.get('slots'), dict) or not loc['slots']:
                self.issue('location_slots', f'Location {lid} needs a nonempty "slots" object.', location=lid)
                continue
            # A slot is either a label string or {"label": ..., "plan": top-down position}.
            # Normalize to labels; keep plan text for blocking-map compilation.
            plans = {}
            for sid, value in list(loc['slots'].items()):
                if isinstance(value, dict):
                    label = value.get('label')
                    if isinstance(value.get('plan'), str) and value['plan'].strip():
                        plans[sid] = value['plan']
                    loc['slots'][sid] = label
                if not isinstance(loc['slots'][sid], str) or not loc['slots'][sid].strip():
                    self.issue('slot_label', f'Slot {sid} needs a nonempty label.', location=lid)
                    loc['slots'][sid] = str(sid)
            loc['slot_plans'] = plans
            labels = list(loc['slots'].values())
            if len(set(labels)) != len(labels):
                self.issue('slot_label_duplicate', f'Location {lid} has duplicate slot labels; each must be distinguishable.', location=lid)
            for cid, cam in (loc.get('cameras') or {}).items():
                screen = cam.get('screen', {}) if isinstance(cam, dict) else None
                if not isinstance(screen, dict):
                    self.issue('camera_screen', f'Camera {cid} needs a "screen" object.', location=lid)
                    continue
                for slot, side in screen.items():
                    if slot not in loc['slots']:
                        self.issue('camera_slot', f'Camera {cid} maps unknown slot {slot!r}.', location=lid)
                    if side not in SIDES:
                        self.issue('camera_side', f'Camera {cid} slot {slot!r} side must be one of {SIDES}.', location=lid)
        return locations

    def apply(self, state, change, location, where, offscreen=False):
        who, field = change.get('who'), change.get('field')
        kind = basis_kind(change.get('basis'))
        if not who or field not in CHANGE_FIELDS:
            self.issue('change_shape', f'Change needs "who" and field in {list(CHANGE_FIELDS)}.', **where)
            return
        if kind is None:
            self.issue('change_basis', f'{who}.{field}: basis must be source:/storyboard:/reference:/design: evidence.', **where)
        elif offscreen and kind not in EVIDENCE_BASIS:
            self.issue('offscreen_basis', f'{who}.{field}: off-screen changes need source/storyboard/reference evidence, not design.', **where)
        elif kind == 'design' and field in ('slot', 'enter', 'leave'):
            self.issue('design_blocking_change', f'{who}.{field}: blocking change uses design basis; confirm it adds no plot event.',
                       warning=True, **where)
        if field == 'enter':
            if who in state:
                self.issue('enter_present', f'{who} is already present in this instance.', **where)
            elif self.check_state(who, change.get('to'), location, where):
                state[who] = copy.deepcopy(change['to'])
            return
        if who not in state:
            self.issue('change_absent', f'{who} is not present in this instance at this point.', **where)
            return
        if field == 'leave':
            del state[who]
            return
        current = state[who].get(field)
        if change.get('from') != current:
            self.issue('change_from_mismatch', f'{who}.{field}: change starts from {change.get("from")!r} but current state is {current!r}.', **where)
        target = change.get('to')
        if field == 'slot' and target not in location.get('slots', {}):
            self.issue('unknown_slot', f'{who}: target slot {target!r} is not defined.', **where)
            return
        if target is None:
            state[who].pop(field, None)
        elif not isinstance(target, str) or not target.strip():
            self.issue('state_value', f'{who}.{field}: target must be a nonempty string or null.', **where)
        else:
            state[who][field] = target

    def validate(self):
        locations = self.check_locations()
        if self.data.get('schema_version') != 1:
            self.issue('schema_version', 'Expected schema_version 1.')
        instances = self.data.get('instances')
        if not isinstance(instances, dict) or not instances:
            self.issue('instances', 'Ledger needs a nonempty "instances" object.')
            return self
        for iid, inst in instances.items():
            location = locations.get(inst.get('location')) if isinstance(inst, dict) else None
            if not isinstance(location, dict) or not isinstance(location.get('slots'), dict):
                self.issue('instance_location', f'Instance {iid} references an unknown/invalid location.', instance=iid)
                continue
            previous = None
            for seg in inst.get('segments') or []:
                self.add_segment(iid, inst, location, seg, previous)
                previous = self.segments[-1] if self.segments and self.segments[-1]['instance'] == iid else previous
            if not inst.get('segments'):
                self.issue('instance_segments', f'Instance {iid} has no segments.', instance=iid)
        return self

    def add_segment(self, iid, inst, location, seg, previous):
        sid = seg.get('id') if isinstance(seg, dict) else None
        gid = seg.get('group') if isinstance(seg, dict) else None
        where = {'instance': iid, 'segment': sid, 'group': gid}
        if not sid or sid in self.by_id:
            self.issue('segment_id', 'Each segment needs a unique "id".', **where)
            return
        if group_key(gid) is None:
            self.issue('segment_group', 'Segment "group" must look like E001-G003.', **where)
            return
        if previous and group_key(gid) < group_key(previous['group']):
            self.issue('segment_order', f'Segments must follow playback order; {gid} precedes {previous["group"]}.', **where)
        entry_from = seg.get('entry_from')
        if previous is None:
            if entry_from is not None:
                self.issue('entry_from_first', 'The first segment of an instance has no predecessor; use a new instance only for a new narrative time.', **where)
            if basis_kind(seg.get('entry_basis')) is None:
                self.issue('entry_basis', 'The first segment needs entry_basis (source:/storyboard:/reference:/design:).', **where)
            entry = seg.get('entry')
            if not isinstance(entry, dict):
                self.issue('entry_missing', 'The first segment must write its source-based entry state.', **where)
                entry = {}
            elif not entry:
                self.issue('entry_empty', 'Entry has no characters; valid only for an empty/insert segment.', warning=True, **where)
            entry = {n: copy.deepcopy(s) for n, s in entry.items() if self.check_state(n, s, location, where)}
        else:
            if entry_from != previous['id']:
                self.issue('entry_from_not_latest',
                           f'Entry must consume the latest exit of instance {iid} ({previous["id"]}, group {previous["group"]}), '
                           f'not {entry_from!r}. A nonadjacent return never reads the adjacent group or the original blocking.', **where)
            entry = copy.deepcopy(previous['exit'])
            for change in seg.get('offscreen_changes') or []:
                self.apply(entry, change, location, where, offscreen=True)
            if 'entry' in seg:
                diffs = state_diff(entry, seg['entry'] or {})
                if diffs:
                    self.issue('entry_mismatch', 'Written entry differs from the derived latest exit: ' + '; '.join(diffs), **where)
        entry_shot = seg.get('entry_shot')
        if entry_shot is not None and (shot_parts(entry_shot) or (None,))[0] != gid:
            self.issue('entry_shot', f'entry_shot {entry_shot!r} must be a shot of {gid}.', **where)
        state, changes, last_shot = copy.deepcopy(entry), [], 0
        for change in seg.get('changes') or []:
            parts = shot_parts(change.get('shot'))
            cwhere = dict(where, shot=change.get('shot'))
            if not parts or parts[0] != gid:
                self.issue('change_shot', f'Change carrying shot must be a shot of {gid}.', **cwhere)
                continue
            if parts[1] < last_shot:
                self.issue('change_order', 'Changes must be listed in shot order.', **cwhere)
            last_shot = parts[1]
            self.apply(state, change, location, cwhere)
            changes.append({'change': change, 'shot_no': parts[1]})
        if 'exit' in seg:
            diffs = state_diff(state, seg['exit'] or {})
            if diffs:
                self.issue('exit_mismatch', 'Written exit differs from entry + changes: ' + '; '.join(diffs), **where)
        cameras = location.get('cameras') or {}
        shots = {}
        for shot, spec in (seg.get('shots') or {}).items():
            if (shot_parts(shot) or (None,))[0] != gid:
                self.issue('camera_shot', f'Camera declaration {shot!r} must be a shot of {gid}.', **where)
            elif not isinstance(spec, dict) or spec.get('camera') not in cameras:
                self.issue('camera_unknown', f'{shot}: camera must be defined for location {inst.get("location")}.', **dict(where, shot=shot))
            else:
                shots[shot] = spec['camera']
        record = {'id': sid, 'instance': iid, 'location_id': inst.get('location'), 'location': location,
                  'instance_label': inst.get('label') or inst.get('time') or '', 'group': gid,
                  'prev': previous['id'] if previous else None, 'prev_group': previous['group'] if previous else None,
                  'offscreen_changes': seg.get('offscreen_changes') or [], 'entry': entry, 'changes': changes,
                  'exit': state, 'entry_shot': entry_shot, 'shots': shots}
        self.segments.append(record)
        self.by_id[sid] = record


def classify(record, play_index):
    if record['prev'] is None:
        return 'new_instance'
    if record['prev_group'] == record['group']:
        return 'intra_group_return'
    if play_index and record['group'] in play_index and record['prev_group'] in play_index:
        adjacent = play_index[record['group']] - play_index[record['prev_group']] == 1
    else:
        (pe, pg), (ce, cg) = group_key(record['prev_group']), group_key(record['group'])
        adjacent = (pe == ce and cg == pg + 1) or (ce == pe + 1 and cg == 1)
    return 'direct_continuation' if adjacent else 'nonadjacent_return'


def state_at(record, shot_no):
    """State after all changes carried by earlier shots; characters changing in this shot are 'moving'."""
    state, moving = copy.deepcopy(record['entry']), set()
    for item in record['changes']:
        if item['shot_no'] < shot_no:
            _replay(state, item['change'])
        elif item['shot_no'] == shot_no:
            moving.add(item['change'].get('who'))
    return state, moving


def _replay(state, change):
    who, field = change.get('who'), change.get('field')
    if field == 'enter':
        state[who] = copy.deepcopy(change.get('to'))
    elif who in state:
        if field == 'leave':
            del state[who]
        elif change.get('to') is None:
            state[who].pop(field, None)
        else:
            state[who][field] = change.get('to')


def parse_storyboard(text, source):
    lines, visible, unclosed = scan_lines(normalize(text))
    groups, errors, episode, current = [], [], None, None

    def close():
        if current is None:
            return
        scene, shots, shot_id, in_scene, negative = [], {}, None, False, False
        for number, raw in current.pop('rows'):
            line = raw.strip()
            if NEGATIVE.match(line):
                negative, shot_id, in_scene = True, None, False
                continue
            match = SHOT.match(line)
            if match and not negative:
                shot_id = f"{current['id']}-S{int(match[1]):03d}"
                shots.setdefault(shot_id, {'line': number, 'text': []})
                in_scene = False
                continue
            field = FIELD_LINE.match(line)
            if field and shot_id is None:
                in_scene = field[1].strip() == SCENE_FIELD
                if in_scene:
                    scene.append(line[field.end():])
                continue
            if shot_id:
                shots[shot_id]['text'].append(raw)
            elif in_scene and line:
                scene.append(line)
        current['scene_text'] = '\n'.join(scene)
        current['shots'] = {k: {'line': v['line'], 'text': '\n'.join(v['text'])} for k, v in shots.items()}
        groups.append(current)

    for index, raw in enumerate(lines):
        if not visible[index]:
            continue
        line = raw.lstrip()
        episode_match = EPISODE.match(line)
        if episode_match:
            close()
            current = None
            episode = episode_number(episode_match[1])
        elif GROUP_CANDIDATE.match(line):
            close()
            current = None
            number = GROUP_NUMBER.match(line)
            if not number or episode is None:
                errors.append({'code': 'group_identity', 'file': str(source), 'line': index + 1,
                               'message': 'Group heading needs a preceding 第N集 title and ## 第N组 heading.'})
                continue
            current = {'id': f'E{int(episode):03d}-G{int(number[1]):03d}', 'file': str(source),
                       'line': index + 1, 'rows': []}
        elif current is not None:
            current['rows'].append((index + 1, raw))
    close()
    if unclosed:
        errors.append({'code': 'unclosed_fence', 'file': str(source), 'line': unclosed, 'message': 'Unclosed code fence.'})
    return groups, errors


def screen_claim(text, name):
    escaped = re.escape(name)
    for pattern in (escaped + r'[^，。；;,\n]{0,8}?画面(左|右|中)', r'画面(左|右|中)(?:侧|边|方|部)?的?' + escaped):
        match = re.search(pattern, text)
        if match:
            return match[1]
    return None


def check_storyboard(ledger, groups, require_coverage):
    by_group = {g['id']: g for g in groups}
    play_index = {g['id']: i for i, g in enumerate(groups)}
    issue = ledger.issue
    covered = set()
    per_group = {}
    for record in ledger.segments:
        per_group.setdefault(record['group'], []).append(record)
    for gid, records in per_group.items():
        if len(records) > 1 and sum(1 for r in records if r['entry_shot'] is None) > 1:
            issue('entry_shot_required', 'A group with several scene segments needs entry_shot for each later segment.', group=gid)
    for record in ledger.segments:
        where = {'instance': record['instance'], 'segment': record['id'], 'group': record['group']}
        group = by_group.get(record['group'])
        record['checked_in_storyboard'] = group is not None
        if group is None:
            continue
        covered.add(record['group'])
        if record['prev_group'] in play_index and play_index[record['prev_group']] > play_index[record['group']]:
            issue('segment_play_order', 'Predecessor segment plays after this segment in the supplied files.', **where)
        if record['entry_shot']:
            shot = group['shots'].get(record['entry_shot'])
            target, label = (shot['text'] if shot else None), f'entry shot {record["entry_shot"]}'
        else:
            target, label = group['scene_text'], f'{SCENE_FIELD} field'
        if target is None:
            issue('entry_shot_missing', f'{label} not found in the storyboard.', **where)
        else:
            for name, state in record['entry'].items():
                sentence = render_state(name, state, record['location'])
                if sentence not in target:
                    issue('entry_text_missing', f'{label} must contain the compiled entry sentence verbatim: {sentence}', **where)
        for item in record['changes']:
            change, sid = item['change'], item['change'].get('shot')
            shot = group['shots'].get(sid)
            cwhere = dict(where, shot=sid)
            if shot is None:
                issue('change_shot_missing', f'Carrying shot {sid} not found in the storyboard.', **cwhere)
                continue
            who, field = change.get('who'), change.get('field')
            if field == 'enter' and isinstance(change.get('to'), dict) and change['to'].get('slot') in record['location']['slots']:
                token = record['location']['slots'][change['to']['slot']]
            elif field == 'slot':
                token = record['location']['slots'].get(change.get('to'))
            elif field == 'leave':
                token = None
            else:
                token = change.get('to')
            missing = [t for t in (who, token) if t and t not in shot['text']]
            if missing:
                issue('change_result_missing', f'{sid} must visibly carry {who}.{field} → {token!r}; missing text: {missing}.', **cwhere)
        for sid, camera_id in record['shots'].items():
            shot = group['shots'].get(sid)
            if shot is None:
                issue('camera_shot_missing', f'Camera-declared shot {sid} not found.', **dict(where, shot=sid))
                continue
            screen = record['location']['cameras'][camera_id].get('screen', {})
            state, moving = state_at(record, shot_parts(sid)[1])
            for name, char in state.items():
                if name in moving:
                    continue
                claimed, expected = screen_claim(shot['text'], name), screen.get(char['slot'])
                if claimed and expected is None:
                    issue('screen_side_unmapped', f'{name} is written at 画面{claimed}, but camera {camera_id} does not frame slot {char["slot"]}.',
                          **dict(where, shot=sid))
                elif claimed and claimed != expected:
                    issue('screen_side_mismatch', f'{name} is written at 画面{claimed}; camera {camera_id} puts slot {char["slot"]} at 画面{expected}.',
                          **dict(where, shot=sid))
    if require_coverage:
        for group in groups:
            if group['id'] not in covered:
                issue('group_without_state', 'Storyboard group has no scene-state segment.', group=group['id'])
    return play_index


def render_cards(ledger, gid, play_index):
    records = [r for r in ledger.segments if r['group'] == gid]
    if not records:
        return [f'# {gid}：台账中没有该组的场景段。']
    labels = {'new_instance': '新实例（按原文建立初态）', 'direct_continuation': '直接续接',
              'nonadjacent_return': '隔组回场', 'intra_group_return': '组内回切'}
    out = []
    for record in records:
        loc = record['location']
        kind = classify(record, play_index)
        out.append(f"## 回场卡 {record['id']}（{record['instance']}｜{loc.get('name', record['location_id'])}｜{record['instance_label']}）")
        source = f"承接 {record['prev']}（{record['prev_group']}）的末态" if record['prev'] else '无前序段'
        out.append(f'- 类型：{labels[kind]}；{source}')
        offscreen = '；'.join(f"{c.get('who')}.{c.get('field')}→{c.get('to')}（{c.get('basis')}）" for c in record['offscreen_changes'])
        out.append(f'- 画外变化：{offscreen or "无"}')
        place = f"入场镜 {record['entry_shot']}" if record['entry_shot'] else f'「{SCENE_FIELD}」'
        out.append(f'- 入态站位句（逐字写入{place}）：')
        out.extend(f'  - {render_state(n, s, loc)}' for n, s in record['entry'].items())
        if record['changes']:
            out.append('- 本组变化（承载镜须写出结果）：')
            for item in record['changes']:
                c = item['change']
                to = loc['slots'].get(c.get('to'), c.get('to')) if c.get('field') == 'slot' else c.get('to')
                out.append(f"  - {c.get('shot')} {c.get('who')}.{c.get('field')}：{c.get('from')} → {to}（{c.get('basis')}）")
        for sid, camera_id in sorted(record['shots'].items()):
            cam = loc['cameras'][camera_id]
            state, moving = state_at(record, shot_parts(sid)[1])
            sides = {}
            for name, char in state.items():
                side = '移动中' if name in moving else (f"画面{cam['screen'][char['slot']]}" if char['slot'] in cam.get('screen', {}) else '画外')
                sides.setdefault(side, []).append(name)
            listing = '；'.join(f"{k}：{'、'.join(v)}" for k, v in sides.items())
            out.append(f"- 机位 {sid} = {camera_id}（{cam.get('desc', '')}）：{listing}")
        out.append('- 末态（下一消费者承接）：')
        out.extend(f'  - {render_state(n, s, loc)}' for n, s in record['exit'].items())
    return out


def overwrites(report, inputs):
    for source in inputs:
        if report.resolve() == source.resolve() or (report.exists() and source.exists() and report.samefile(source)):
            return True
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--ledger', type=Path, required=True)
    parser.add_argument('--storyboard', nargs='+', action='extend', type=Path, default=[])
    parser.add_argument('--render', nargs='+', action='extend', metavar='GROUP_ID', default=[])
    parser.add_argument('--require-coverage', action='store_true',
                        help='Fail when a supplied storyboard group has no scene-state segment.')
    parser.add_argument('--report', type=Path, help='Optional JSON report; cannot overwrite inputs.')
    args = parser.parse_args(argv)
    if args.report and overwrites(args.report, [args.ledger, *args.storyboard]):
        parser.error('--report must not overwrite the ledger or a storyboard.')
    for gid in args.render:
        if group_key(gid) is None:
            parser.error(f'--render expects group IDs like E001-G003, got {gid!r}.')
    artifacts, groups, input_errors = [], [], []
    try:
        raw = args.ledger.read_bytes()
        artifacts.append({'path': str(args.ledger.resolve()), 'sha256': hashlib.sha256(raw).hexdigest()})
        data = json.loads(raw.decode('utf-8-sig'))
        if not isinstance(data, dict):
            raise ValueError('Ledger root must be a JSON object.')
    except (OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({'schema_version': 1, 'status': 'error',
                          'errors': [{'code': 'input_error', 'message': str(exc)}]}, ensure_ascii=True, indent=2))
        return 2
    ledger = Ledger(data).validate()
    for source in args.storyboard:
        try:
            raw = source.read_bytes()
            artifacts.append({'path': str(source.resolve()), 'sha256': hashlib.sha256(raw).hexdigest()})
            parsed, errors = parse_storyboard(raw.decode('utf-8-sig'), source)
            groups.extend(parsed)
            ledger.errors.extend(errors)
        except (OSError, UnicodeError) as exc:
            input_errors.append({'code': 'input_error', 'file': str(source), 'message': str(exc)})
    play_index = check_storyboard(ledger, groups, args.require_coverage) if args.storyboard and not input_errors else {}
    errors = input_errors + ledger.errors
    segments = [{'id': r['id'], 'instance': r['instance'], 'group': r['group'], 'consumed_from': r['prev'],
                 'classification': classify(r, play_index), 'checked_in_storyboard': r.get('checked_in_storyboard', False)}
                for r in ledger.segments]
    report = {'schema_version': 1, 'status': 'error' if input_errors else ('failed' if errors else 'passed'),
              'artifacts': artifacts, 'segments_checked': len(segments), 'groups_in_storyboard': len(groups),
              'segments': segments, 'errors': errors, 'warnings': ledger.warnings,
              'limitations': ['Checks the ledger chain, compiled entry sentences, change-result tokens and declared screen sides only. '
                              'It cannot prove the ledger matches the source, that prose elsewhere does not contradict the state, '
                              'reachability, timing, or generated media. A pass is not Audit 2B acceptance.']}
    if args.report:
        try:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        except OSError as exc:
            input_errors.append({'code': 'report_error', 'file': str(args.report), 'message': str(exc)})
            report['status'] = 'error'
    if args.render:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        lines = []
        for gid in args.render:
            lines.extend(render_cards(ledger, gid, play_index))
        if errors:
            lines.append(f'# 台账未通过：{len(errors)} 个错误，先修台账再使用站位句。')
            lines.extend(f"- [{e['code']}] {e.get('segment') or e.get('group') or ''} {e['message']}" for e in errors)
        print('\n'.join(lines))
    else:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    return 2 if input_errors else (1 if errors else 0)


if __name__ == '__main__':
    sys.exit(main())

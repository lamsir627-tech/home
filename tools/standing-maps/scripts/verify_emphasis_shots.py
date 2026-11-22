#!/usr/bin/env python3
"""Verify registered emphasis ("渲染") shots for main-character first appearances and conflict peaks.

Reads emphasis-plan.json (internal record) and the actual storyboard Markdown.
Checks registration completeness, that each registered shot really carries a
rendering technique, minimum/maximum counts, face readability at a first
appearance and per-group slow-motion limits. It does not judge aesthetics,
source support or what a generator executes.
Exit codes: 0 = passed, 1 = content failed, 2 = input/report error.
"""

import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_timeline import EPISODE, GROUP_CANDIDATE, episode_number, normalize, scan_lines  # noqa: E402


RENDER_MARKERS = ('大特写', '特写', '升格', '慢动作', '仰拍', '俯拍', '逆光', '剪影', '轮廓光',
                  '缓推', '推近', '快速推', '环绕', '焦点转移', '移焦')
FACE_MARKERS = ('大特写', '特写', '中近景', '近景')
SLOWMO = re.compile(r'升格|慢动作')
KINDS = {'first_appearance': (1, 2), 'conflict': (1, 3)}
DEFAULT_LIMITS = {'max_per_group': 3, 'max_slowmo_seconds': Decimal('6.0')}
GROUP_ID = re.compile(r'E([0-9]{3,})-G([0-9]{3,})')
SHOT_ID = re.compile(r'(E[0-9]{3,}-G[0-9]{3,})-S([0-9]{3,})')
BASIS = re.compile(r'(source|storyboard|reference|design):\S.*')
GROUP_NUMBER = re.compile(r'^##[ \t]+第([0-9]+)组')
SHOT = re.compile(r'^【单镜头([0-9]+)】[ \t]*([0-9]+(?:\.[0-9]+)?)秒')
NEGATIVE = re.compile(r'^(?:负面提示词|\*\*负面提示词\*\*)[：:]')
GROUP_FIELD = re.compile(r'^-[ \t]+\*\*([^*]+)\*\*[：:](.*)$')
SHOT_FIELD = re.compile(r'^(?:-[ \t]+)?\*\*([^*]+)\*\*[：:](.*)$')
DESC_END = {'角色情绪', '表演动作', '镜头参数', '音效/现场声', '字幕/角色台词/旁白'}
AUDIO_FIELD = '字幕/角色台词/旁白'


def parse_storyboard(text, source):
    lines, visible, unclosed = scan_lines(normalize(text))
    groups, errors, episode, current, shot = [], [], None, None, None
    mode = None
    for index, raw in enumerate(lines):
        if not visible[index]:
            continue
        line = raw.strip()
        episode_match = EPISODE.match(line)
        if episode_match:
            episode, current, shot = episode_number(episode_match[1]), None, None
            continue
        if GROUP_CANDIDATE.match(line):
            number = GROUP_NUMBER.match(line)
            shot = None
            if not number or episode is None:
                errors.append({'code': 'group_identity', 'file': str(source), 'line': index + 1,
                               'message': 'Group heading needs a preceding 第N集 title and ## 第N组 heading.'})
                current = None
                continue
            current = {'id': f'E{int(episode):03d}-G{int(number[1]):03d}', 'file': str(source),
                       'line': index + 1, 'fields': {}, 'shots': {}, 'order': []}
            groups.append(current)
            continue
        if current is None:
            continue
        if NEGATIVE.match(line):
            shot, mode = None, None
            continue
        header = SHOT.match(line)
        if header:
            sid = f"{current['id']}-S{int(header[1]):03d}"
            shot = {'id': sid, 'line': index + 1, 'seconds': Decimal(header[2]), 'desc': [], 'audio': []}
            current['shots'][sid] = shot
            current['order'].append(sid)
            mode = None
            continue
        if shot is None:
            field = GROUP_FIELD.match(line)
            if field:
                current['fields'][field[1].strip()] = field[2].strip()
            continue
        field = SHOT_FIELD.match(line)
        if field:
            name = field[1].strip()
            if name == '镜头描述':
                mode = 'desc'
                if field[2].strip():
                    shot['desc'].append(field[2].strip())
                continue
            if name == AUDIO_FIELD:
                mode = 'audio'
                if field[2].strip():
                    shot['audio'].append(field[2].strip())
                continue
            if name in DESC_END:
                mode = None
                continue
        if mode == 'desc' and line:
            shot['desc'].append(line)
        elif mode == 'audio' and line:
            shot['audio'].append(line)
    if unclosed:
        errors.append({'code': 'unclosed_fence', 'file': str(source), 'line': unclosed, 'message': 'Unclosed code fence.'})
    for group in groups:
        for item in group['shots'].values():
            item['desc'] = '\n'.join(item['desc'])
            item['speech'] = [a for a in item['audio'] if a != '无']
    return groups, errors


class Checker:
    def __init__(self, plan):
        self.plan = plan
        self.errors, self.warnings, self.triggers = [], [], []

    def issue(self, code, message, warning=False, **where):
        row = {'code': code, 'message': message}
        row.update({k: v for k, v in where.items() if v is not None})
        (self.warnings if warning else self.errors).append(row)

    def limits(self):
        limits = dict(DEFAULT_LIMITS)
        raw = self.plan.get('limits') or {}
        if not isinstance(raw, dict):
            self.issue('limits', '"limits" must be an object.')
            return limits
        if 'max_per_group' in raw:
            value = raw['max_per_group']
            if isinstance(value, int) and not isinstance(value, bool) and value >= 1:
                limits['max_per_group'] = value
            else:
                self.issue('limits', 'max_per_group must be a positive integer.')
        if 'max_slowmo_seconds' in raw:
            try:
                value = Decimal(str(raw['max_slowmo_seconds']))
                if not value.is_finite() or value < 0:
                    raise InvalidOperation
                limits['max_slowmo_seconds'] = value
            except (InvalidOperation, ValueError):
                self.issue('limits', 'max_slowmo_seconds must be a nonnegative number.')
        return limits

    def validate_plan(self):
        plan = self.plan
        if plan.get('schema_version') != 1:
            self.issue('schema_version', 'Expected schema_version 1.')
        mains = plan.get('main_characters')
        if not isinstance(mains, list) or not all(isinstance(n, str) and n.strip() for n in mains):
            self.issue('main_characters', '"main_characters" must be a list of names (may be empty only if the job has none).')
            mains = []
        introduced = plan.get('introduced_before_scope') or []
        if not isinstance(introduced, list):
            self.issue('introduced_before_scope', '"introduced_before_scope" must be a list.')
            introduced = []
        unknown = [n for n in introduced if n not in mains]
        if unknown:
            self.issue('introduced_unknown', f'introduced_before_scope lists non-main characters {unknown}.')
        triggers = plan.get('triggers')
        if not isinstance(triggers, list):
            self.issue('triggers', '"triggers" must be a list.')
            triggers = []
        seen, firsts = set(), {}
        for trig in triggers:
            tid = trig.get('id') if isinstance(trig, dict) else None
            where = {'trigger': tid}
            if not tid or tid in seen:
                self.issue('trigger_id', 'Each trigger needs a unique id.', **where)
                continue
            seen.add(tid)
            kind, gid = trig.get('kind'), trig.get('group')
            if kind not in KINDS:
                self.issue('trigger_kind', f'kind must be one of {sorted(KINDS)}.', **where)
                continue
            if not GROUP_ID.fullmatch(gid or ''):
                self.issue('trigger_group', 'group must look like E001-G003.', **where)
                continue
            if not isinstance(trig.get('basis'), str) or not BASIS.fullmatch(trig['basis']):
                self.issue('trigger_basis', 'basis must be source:/storyboard:/reference:/design: evidence.', **where)
            shots = trig.get('shots')
            if not isinstance(shots, list):
                self.issue('trigger_shots', '"shots" must be a list (empty only with a constraint).', **where)
                shots = []
            for sid in shots:
                match = SHOT_ID.fullmatch(sid) if isinstance(sid, str) else None
                if not match or match[1] != gid:
                    self.issue('trigger_shot_id', f'{sid!r} must be a shot ID of {gid}.', **where)
            if len(set(shots)) != len(shots):
                self.issue('trigger_shot_duplicate', 'A shot is listed twice in one trigger.', **where)
            low, high = KINDS[kind]
            if not shots:
                if isinstance(trig.get('constraint'), str) and trig['constraint'].strip():
                    self.issue('trigger_constrained', f'No rendering shot; constraint: {trig["constraint"]}', warning=True, **where)
                else:
                    self.issue('trigger_empty', 'Trigger has no rendering shot and no constraint reason.', **where)
            elif not low <= len(shots) <= high:
                self.issue('trigger_count', f'{kind} needs {low}–{high} rendering shots, found {len(shots)}.', **where)
            if kind == 'first_appearance':
                name = trig.get('character')
                if name not in mains:
                    self.issue('trigger_character', f'first_appearance character {name!r} is not in main_characters.', **where)
                elif name in introduced:
                    self.issue('trigger_introduced', f'{name} is listed as introduced before this scope.', **where)
                elif name in firsts:
                    self.issue('first_appearance_duplicate', f'{name} already has first appearance {firsts[name]}.', **where)
                else:
                    firsts[name] = tid
            self.triggers.append(trig)
        for name in mains:
            if name not in introduced and name not in firsts:
                self.issue('missing_first_appearance', f'Main character {name} has no first_appearance trigger '
                           '(list in introduced_before_scope if already introduced).', character=name)

    def check_storyboard(self, groups, limits):
        by_group = {g['id']: g for g in groups}
        order = [g['id'] for g in groups]
        registered = {}
        status = []
        for trig in self.triggers:
            gid, where = trig['group'], {'trigger': trig['id'], 'group': trig['group']}
            group = by_group.get(gid)
            status.append({'id': trig['id'], 'kind': trig['kind'], 'group': gid, 'checked_in_storyboard': group is not None})
            if group is None:
                continue
            shots = [s for s in trig.get('shots') or [] if isinstance(s, str)]
            for sid in shots:
                registered.setdefault(gid, set()).add(sid)
                shot = group['shots'].get(sid)
                if shot is None:
                    self.issue('shot_missing', f'{sid} not found in the storyboard.', shot=sid, **where)
                elif not any(m in shot['desc'] for m in RENDER_MARKERS):
                    self.issue('no_rendering_technique', f'{sid} 镜头描述 has none of {list(RENDER_MARKERS)}.', shot=sid, **where)
            if trig['kind'] == 'first_appearance' and shots:
                name = trig.get('character') or ''
                if not any(name in group['shots'][s]['desc'] and any(m in group['shots'][s]['desc'] for m in FACE_MARKERS)
                           for s in shots if s in group['shots']):
                    self.issue('first_appearance_face', f'At least one registered shot must name {name} with 特写/大特写/近景.', **where)
                for earlier in order[:order.index(gid)]:
                    if name and name in by_group[earlier]['fields'].get('主要主体', ''):
                        self.issue('possible_earlier_appearance', f'{name} is already listed in 主要主体 of {earlier}; '
                                   'confirm it was voice-only or not visible.', warning=True, **where)
                        break
        for group in groups:
            gid = group['id']
            count = len(registered.get(gid, ()))
            if count > limits['max_per_group']:
                self.issue('group_rendering_cap', f'{count} rendering shots exceed {limits["max_per_group"]}.', group=gid)
            slow = [group['shots'][s] for s in group['order'] if SLOWMO.search(group['shots'][s]['desc'])]
            total = sum((s['seconds'] for s in slow), Decimal('0'))
            if total > limits['max_slowmo_seconds']:
                self.issue('group_slowmo_cap', f'Slow-motion playback {total}s exceeds {limits["max_slowmo_seconds"]}s.', group=gid)
            run = 0
            for sid in group['order']:
                shot = group['shots'][sid]
                if SLOWMO.search(shot['desc']):
                    run += 1
                    if run == 3:
                        self.issue('consecutive_slowmo', 'Three or more consecutive slow-motion shots.', warning=True, group=gid, shot=sid)
                    if sid not in registered.get(gid, ()):
                        self.issue('unregistered_slowmo', 'Slow-motion shot is not registered to a trigger.', warning=True, group=gid, shot=sid)
                    if shot['speech']:
                        self.issue('slowmo_dialogue', 'Slow-motion shot carries dialogue; confirm the speaker is off-screen '
                                   'and nobody lip-syncs in slow motion.', warning=True, group=gid, shot=sid)
                else:
                    run = 0
        return status


def overwrites(report, inputs):
    for source in inputs:
        if report.resolve() == source.resolve() or (report.exists() and source.exists() and report.samefile(source)):
            return True
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--storyboard', nargs='+', action='extend', type=Path, default=[])
    parser.add_argument('--report', type=Path, help='Optional JSON report; cannot overwrite inputs.')
    args = parser.parse_args(argv)
    if args.report and overwrites(args.report, [args.plan, *args.storyboard]):
        parser.error('--report must not overwrite the plan or a storyboard.')
    artifacts, input_errors, groups = [], [], []
    try:
        raw = args.plan.read_bytes()
        artifacts.append({'path': str(args.plan.resolve()), 'sha256': hashlib.sha256(raw).hexdigest()})
        plan = json.loads(raw.decode('utf-8-sig'))
        if not isinstance(plan, dict):
            raise ValueError('Plan root must be a JSON object.')
    except (OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({'schema_version': 1, 'status': 'error',
                          'errors': [{'code': 'input_error', 'message': str(exc)}]}, ensure_ascii=True, indent=2))
        return 2
    checker = Checker(plan)
    limits = checker.limits()
    checker.validate_plan()
    parse_errors = []
    for source in args.storyboard:
        try:
            raw = source.read_bytes()
            artifacts.append({'path': str(source.resolve()), 'sha256': hashlib.sha256(raw).hexdigest()})
            parsed, errors = parse_storyboard(raw.decode('utf-8-sig'), source)
            groups.extend(parsed)
            parse_errors.extend(errors)
        except (OSError, UnicodeError, InvalidOperation) as exc:
            input_errors.append({'code': 'input_error', 'file': str(source), 'message': str(exc)})
    status = checker.check_storyboard(groups, limits) if args.storyboard and not input_errors else []
    errors = input_errors + parse_errors + checker.errors
    report = {'schema_version': 1, 'status': 'error' if input_errors else ('failed' if errors else 'passed'),
              'artifacts': artifacts, 'groups_in_storyboard': len(groups), 'triggers': status,
              'limits': {'max_per_group': limits['max_per_group'], 'max_slowmo_seconds': str(limits['max_slowmo_seconds'])},
              'errors': errors, 'warnings': checker.warnings,
              'limitations': ['Checks registration, rendering keywords, counts, first-appearance face readability and '
                              'slow-motion limits in the text only. It cannot prove a trigger was not missed, that the '
                              'rendering is source-supported or attractive, or what a generator executes.']}
    if args.report:
        try:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        except OSError as exc:
            input_errors.append({'code': 'report_error', 'file': str(args.report), 'message': str(exc)})
            report['status'] = 'error'
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 2 if input_errors else (1 if errors else 0)


if __name__ == '__main__':
    sys.exit(main())

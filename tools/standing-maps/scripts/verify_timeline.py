#!/usr/bin/env python3
"""Validate exact group duration and continuous per-shot local time intervals.

Default: every group, including the final group, is exactly 30 seconds. Use
--group-seconds only for an explicitly authorized different duration. This
read-only structural gate does not measure speech, breaths or action feasibility.
Exit codes: 0 = passed, 1 = content failed, 2 = input/report error.
"""

import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import sys


NUMBER = r'[0-9]+(?:\.[0-9]+)?'
EPISODE = re.compile(r'^第([0-9一二三四五六七八九十百千万零〇两]+)集(?:[｜|]|\s*$)')
GROUP_CANDIDATE = re.compile(r'^#{1,6}[ \t]+第[^\s（(]*组(?=[（(\s]|$)')
GROUP = re.compile(rf'^##[ \t]+第([0-9]+)组[（(]目标[^；;]+[；;]实际({NUMBER})秒[）)][ \t]*$')
SHOT_CANDIDATE = re.compile(r'^【单镜头')
SHOT = re.compile(rf'^【单镜头([0-9]+)】[ \t]*({NUMBER})秒[ \t]*$')
AXIS_CANDIDATE = re.compile(r'^(?:-[ \t]+)?(?:\*\*)?时间轴')
AXIS = re.compile(rf'^\*\*时间轴\*\*[：:][ \t]*({NUMBER})[ \t]*[-–—][ \t]*({NUMBER})秒[ \t]*$')
NEGATIVE = re.compile(r'^(?:负面提示词|\*\*负面提示词\*\*)[：:]')
FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')


def normalize(text):
    return text.removeprefix('\ufeff').replace('\r\n', '\n').replace('\r', '\n')


def episode_number(value):
    if value.isdecimal():
        return str(int(value))
    digits = dict(zip('零〇一二三四五六七八九两', [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 2]))
    if not any(c in value for c in '十百千万'):
        return str(int(''.join(str(digits[c]) for c in value)))
    total = section = current = 0
    for char in value:
        if char in digits:
            current = digits[char]
        elif char == '万':
            total += (section + current) * 10000
            section = current = 0
        else:
            section += (current or 1) * {'十': 10, '百': 100, '千': 1000}[char]
            current = 0
    return str(total + section + current)


def positive_seconds(value):
    try:
        result = Decimal(value)
    except (InvalidOperation, ValueError):
        raise argparse.ArgumentTypeError('Group seconds must be a positive finite decimal.')
    if not result.is_finite() or result <= 0:
        raise argparse.ArgumentTypeError('Group seconds must be a positive finite decimal.')
    return result


def scan_lines(text):
    lines = text.split('\n')
    visible, marker, opening = [], None, None
    for number, raw in enumerate(lines, 1):
        fence = FENCE.match(raw)
        if marker:
            visible.append(False)
            if fence and fence[1][0] == marker[0] and len(fence[1]) >= len(marker) and not fence[2].strip():
                marker = opening = None
        elif fence:
            marker, opening = fence[1], number
            visible.append(False)
        else:
            visible.append(True)
    return lines, visible, opening


def validate_text(text, source='<memory>', group_seconds=Decimal('30'), state=None):
    """Return groups/errors/warnings; share state across files in playback order.

    A selected range may start at group N. Later groups of the same episode must
    increment by one. Episode labels identify original episodes, not file order.
    """
    group_seconds = positive_seconds(str(group_seconds))
    lines, visible, unclosed = scan_lines(normalize(text))
    state = {} if state is None else state
    seen = state.setdefault('seen', set())
    last = state.setdefault('last_group', {})
    groups, errors, warnings = [], [], []
    episode, pending = None, None

    def issue(code, message, line=None, group_id=None, shot_id=None, warning=False):
        (warnings if warning else errors).append({'file': str(source), 'line': line,
            'group': group_id, 'shot': shot_id, 'code': code, 'message': message})

    def finish(end):
        nonlocal pending
        if pending is None:
            return
        start, ep = pending
        pending = None
        heading = GROUP.fullmatch(lines[start].lstrip())
        number = int(heading[1]) if heading else None
        gid = f'E{int(ep):03d}-G{number:03d}' if ep and number is not None else f'{ep or "unknown"}-G{number or "invalid"}'
        error_start = len(errors)
        actual = Decimal(heading[2]) if heading else None
        if not heading:
            issue('group_heading_format', 'Expected ## 第N组（目标MM:SS-MM:SS；实际X.X秒）.', start + 1, gid)
        else:
            key = (ep, number)
            if key in seen:
                issue('duplicate_group', 'Episode/group identity already appeared.', start + 1, gid)
            seen.add(key)
            if number < 1 or (ep in last and number != last[ep] + 1):
                issue('group_numbering', 'Positive group numbers must be consecutive within each episode/range.', start + 1, gid)
            last[ep] = number
            if actual != group_seconds:
                issue('group_duration', f'Actual group duration {actual} must equal {group_seconds}, including the final group.', start + 1, gid)

        positions, negative_seen = [], False
        for i in range(start + 1, end):
            line = lines[i].lstrip()
            if not visible[i]:
                continue
            if NEGATIVE.match(line):
                negative_seen = True
            is_shot, is_axis = SHOT_CANDIDATE.match(line), AXIS_CANDIDATE.match(line)
            if negative_seen and (is_shot or is_axis):
                issue('timing_after_negative', 'Shot/timeline content cannot follow the final negative prompt.', i + 1, gid)
            if is_shot:
                positions.append(i)
            elif is_axis and not positions:
                issue('orphan_timeline', 'Timeline field has no preceding shot in this group.', i + 1, gid)
        if not positions:
            issue('missing_shots', 'Group has no unfenced shot headers.', start + 1, gid)
        elif not 6 <= len(positions) <= 10:
            issue('shot_count_guidance', f'{len(positions)} shots: normally 6–10; review content-driven justification.',
                  start + 1, gid, warning=True)

        cursor, total, shot_rows = Decimal('0'), Decimal('0'), []
        for ordinal, pos in enumerate(positions, 1):
            stop = positions[ordinal] if ordinal < len(positions) else end
            header = SHOT.fullmatch(lines[pos].lstrip())
            sid = f'{gid}-S{ordinal:03d}'
            duration = Decimal(header[2]) if header else None
            if not header:
                issue('shot_heading_format', 'Expected 【单镜头N】X.X秒 with finite decimal duration.', pos + 1, gid, sid)
            else:
                if int(header[1]) != ordinal:
                    issue('shot_numbering', 'Shots must start at 1 and be consecutive within the group.', pos + 1, gid, sid)
                if duration <= 0:
                    issue('nonpositive_duration', 'Shot duration must be positive.', pos + 1, gid, sid)
                total += duration
            axes = [i for i in range(pos + 1, stop)
                    if visible[i] and AXIS_CANDIDATE.match(lines[i].lstrip())]
            begin = finish_time = None
            if len(axes) != 1:
                issue('timeline_count', f'Expected exactly one 时间轴 field, found {len(axes)}.', pos + 1, gid, sid)
            if axes:
                axis_pos = axes[0]
                if axis_pos != pos + 1:
                    issue('timeline_placement', '时间轴 must be the line immediately below the shot header.', axis_pos + 1, gid, sid)
                axis = AXIS.fullmatch(lines[axis_pos].lstrip())
                if not axis:
                    issue('timeline_format', 'Expected **时间轴**：0.0–4.0秒 with finite nonnegative decimals.', axis_pos + 1, gid, sid)
                else:
                    begin, finish_time = Decimal(axis[1]), Decimal(axis[2])
                    if finish_time <= begin:
                        issue('nonpositive_interval', 'Timeline end must exceed its start.', axis_pos + 1, gid, sid)
                    if ordinal == 1 and begin != 0:
                        issue('timeline_start', 'Each group timeline starts at 0.0 seconds.', axis_pos + 1, gid, sid)
                    if begin != cursor:
                        issue('timeline_continuity', f'Expected interval start {cursor}, found {begin}; no gaps or overlaps.', axis_pos + 1, gid, sid)
                    if duration is not None and finish_time - begin != duration:
                        issue('shot_duration', f'Interval length {finish_time - begin} differs from declared {duration}.', axis_pos + 1, gid, sid)
                    if finish_time > group_seconds:
                        issue('timeline_bounds', f'Interval ends past group boundary {group_seconds}.', axis_pos + 1, gid, sid)
                    cursor = finish_time
            shot_rows.append({'id': sid, 'line': pos + 1, 'duration': str(duration) if duration is not None else None,
                              'start': str(begin) if begin is not None else None,
                              'end': str(finish_time) if finish_time is not None else None})
        if total != group_seconds or (actual is not None and total != actual):
            issue('shot_sum', f'Shot sum {total} must equal declared actual {actual} and target {group_seconds}.', start + 1, gid)
        if cursor != group_seconds:
            issue('timeline_end', f'Last interval must end at {group_seconds}, found {cursor}.', start + 1, gid)
        groups.append({'file': str(source), 'episode': ep, 'group': number, 'id': gid,
                       'start_line': start + 1, 'end_line': end, 'target_seconds': str(group_seconds),
                       'actual_seconds': str(actual) if actual is not None else None,
                       'shot_seconds': str(total), 'shots': len(positions), 'shot_intervals': shot_rows,
                       'status': 'failed' if len(errors) != error_start else 'passed'})

    for i, raw in enumerate(lines):
        line = raw.lstrip()
        if not visible[i]:
            if GROUP_CANDIDATE.match(line) or SHOT_CANDIDATE.match(line) or AXIS_CANDIDATE.match(line) or EPISODE.match(line):
                issue('fenced_timing_syntax', 'Fenced headings/time fields cannot serve as a delivery timeline.', i + 1)
            continue
        em = EPISODE.match(line)
        if em:
            finish(i)
            episode = episode_number(em[1])
        elif GROUP_CANDIDATE.match(line):
            finish(i)
            pending = (i, episode)
        elif pending is None and SHOT_CANDIDATE.match(line):
            issue('orphan_shot', 'Shot header appears outside a group.', i + 1)
        elif pending is None and AXIS_CANDIDATE.match(line):
            issue('orphan_timeline', 'Timeline field appears outside a shot/group.', i + 1)
    finish(len(lines))
    if not groups:
        issue('no_groups', 'No unfenced group headings found.')
    if unclosed:
        issue('unclosed_fence', 'Unclosed code fence in input.', unclosed)
    # Fenced syntax failures are detected before group finalization; reflect them
    # in the corresponding group status as well as the report-level verdict.
    for item in groups:
        if any(e['line'] and item['start_line'] <= e['line'] <= item['end_line'] for e in errors):
            item['status'] = 'failed'
    return {'groups': groups, 'errors': errors, 'warnings': warnings}


def report_overwrites_input(report, inputs):
    for source in inputs:
        if report.resolve() == source.resolve():
            return True
        if report.exists() and source.exists() and report.samefile(source):
            return True
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--storyboard', nargs='+', action='extend', type=Path, required=True)
    parser.add_argument('--group-seconds', type=positive_seconds, default=Decimal('30'),
                        help='Exact duration; default 30. Change only for an explicit user instruction.')
    parser.add_argument('--report', type=Path, help='Optional JSON report; cannot overwrite inputs.')
    args = parser.parse_args(argv)
    if args.report:
        try:
            if report_overwrites_input(args.report, args.storyboard):
                parser.error('--report must not overwrite a storyboard.')
        except (OSError, ValueError) as exc:
            parser.error(f'Cannot resolve report/input paths: {exc}')
    errors, warnings, groups, artifacts, state = [], [], [], [], {}
    execution_error = False
    for source in args.storyboard:
        try:
            raw = source.read_bytes()
            text = raw.decode('utf-8-sig')
            artifacts.append({'path': str(source.resolve()), 'sha256': hashlib.sha256(raw).hexdigest()})
            result = validate_text(text, source, args.group_seconds, state)
            groups.extend(result['groups'])
            errors.extend(result['errors'])
            warnings.extend(result['warnings'])
        except (OSError, UnicodeError, ValueError, InvalidOperation) as exc:
            execution_error = True
            errors.append({'file': str(source), 'line': None, 'group': None, 'shot': None,
                           'code': 'input_error', 'message': str(exc)})
    report = {'schema_version': 1, 'status': 'error' if execution_error else ('failed' if errors else 'passed'),
              'group_seconds': str(args.group_seconds), 'artifacts': artifacts,
              'groups_checked': len(groups), 'shots_checked': sum(g['shots'] for g in groups),
              'groups': groups, 'errors': errors, 'warnings': warnings,
              'limitations': ['Structural timing only. Does not measure actual speech, pauses, nonparallel actions, '
                              'semantic continuity, original dialogue coverage, framing, style, camera parameters, '
                              'group character count or generated media. A pass is not full storyboard acceptance.']}
    if args.report:
        try:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        except (OSError, ValueError) as exc:
            execution_error = True
            report['status'] = 'error'
            errors.append({'file': str(args.report), 'line': None, 'group': None, 'shot': None,
                           'code': 'report_error', 'message': str(exc)})
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 2 if execution_error else (1 if errors else 0)


if __name__ == '__main__':
    sys.exit(main())

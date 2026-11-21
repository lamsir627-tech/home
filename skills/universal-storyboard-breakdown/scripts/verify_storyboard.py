#!/usr/bin/env python3
"""Verify lossless source coverage and actual rendered dialogue, using stdlib only.

This checks text/provenance, not the semantic truth of classifications or visuals.
See references/long-text-workflow.md for the source ledger and mapping contract.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


KINDS = {'dialogue', 'vo', 'narration', 'action', 'heading', 'metadata',
         'subtitle', 'translation', 'blank', 'unclassified'}
AUDIO_KINDS = {'dialogue', 'vo', 'narration'}
EPISODE = re.compile(r'^第([0-9一二三四五六七八九十百千万零〇两]+)集\s*[｜|]')
GROUP = re.compile(r'^##\s+第(\d+)组[（(].*?实际([0-9]+(?:\.[0-9]+)?)秒[）)]\s*$')
SHOT = re.compile(r'^【单镜头(\d+)】\s*([0-9]+(?:\.[0-9]+)?)秒\s*$')
AUDIO = re.compile(r'^\*\*字幕/角色台词/旁白\*\*[：:]\s*(.*)$')
ENGLISH_PREFIX = re.compile(r'^英文主声轨[（(]锁定[）)]\s*[—–-]\s*')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


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


def add_error(errors, code, message):
    errors.append({'code': code, 'message': message})


def source_integrity(ledger, ledger_path, errors):
    if not isinstance(ledger, dict) or ledger.get('schema_version') != 1:
        raise ValueError('Ledger must be an object with schema_version=1.')
    source = ledger.get('source')
    units = ledger.get('units')
    if not isinstance(source, dict) or not isinstance(units, list) or not units:
        raise ValueError('Ledger needs source and a nonempty units list.')
    snapshot = Path(source['path'])
    if not snapshot.is_absolute():
        snapshot = ledger_path.parent / snapshot
    data = snapshot.read_bytes()
    text = data.decode('utf-8-sig')
    if digest(data) != source.get('sha256'):
        add_error(errors, 'source_hash', 'Snapshot bytes differ from the recorded source revision.')
    if len(text) != source.get('char_count'):
        add_error(errors, 'source_length', 'Snapshot character count differs from ledger.')
    cursor = 0
    seen = set()
    for order, unit in enumerate(units, 1):
        if not isinstance(unit, dict):
            raise ValueError(f'Unit {order} is not an object.')
        uid = unit.get('id')
        if not isinstance(uid, str) or not uid or uid in seen:
            add_error(errors, 'unit_id', f'Invalid or duplicate unit id at position {order}.')
        seen.add(uid if isinstance(uid, str) else str(order))
        start, end = unit.get('start'), unit.get('end')
        if not integer(start) or not integer(end) or not 0 <= start < end <= len(text):
            add_error(errors, 'unit_span', f'{uid}: invalid source interval.')
            continue
        if start != cursor:
            add_error(errors, 'source_gap_overlap', f'{uid}: expected start {cursor}, got {start}.')
        if unit.get('order') != order:
            add_error(errors, 'unit_order', f'{uid}: unit order differs from source sequence.')
        if unit.get('raw') != text[start:end]:
            add_error(errors, 'raw_mismatch', f'{uid}: raw text differs from snapshot slice.')
        cursor = end
    if cursor != len(text):
        add_error(errors, 'source_gap_overlap', f'Ledger ends at {cursor}; source ends at {len(text)}.')
    return text, snapshot.resolve(), units


def select_units(units, args):
    selected = list(units)
    if args.episodes:
        requested = {episode_number(x) for x in args.episodes}
        known = {u.get('episode') for u in units}
        missing = requested - known
        if missing:
            raise ValueError('Requested episodes absent from ledger: ' + ', '.join(sorted(missing)))
        selected = [u for u in selected if u.get('episode') in requested]
    if bool(args.start_unit) != bool(args.end_unit):
        raise ValueError('--start-unit and --end-unit must be supplied together.')
    if args.start_unit:
        positions = {u['id']: i for i, u in enumerate(units)}
        if args.start_unit not in positions or args.end_unit not in positions:
            raise ValueError('Batch endpoints must be existing source unit ids.')
        first, last = positions[args.start_unit], positions[args.end_unit]
        if first > last:
            raise ValueError('Batch endpoints are reversed.')
        allowed = {u['id'] for u in units[first:last + 1]}
        selected = [u for u in selected if u['id'] in allowed]
    if not selected:
        raise ValueError('Selected source scope is empty.')
    return selected


def classifications(units, selected, text, errors):
    pairs = {}
    for unit in units:
        if unit.get('pair_id'):
            pairs.setdefault(unit['pair_id'], []).append(unit)
    for unit in selected:
        uid, kind = unit['id'], unit.get('kind')
        audible = unit.get('audible')
        episode = unit.get('episode')
        valid_episode = isinstance(episode, str) and re.fullmatch(r'(?:0|[1-9][0-9]*)', episode)
        if (episode is not None and not valid_episode) or (audible is True and not valid_episode):
            add_error(errors, 'episode_id', f'{uid}: audible units need a canonical original episode number.')
        if unit.get('reviewed') is not True:
            add_error(errors, 'unreviewed', f'{uid}: source classification is not reviewed.')
        if kind not in KINDS or kind == 'unclassified' or not isinstance(audible, bool):
            add_error(errors, 'unresolved_classification', f'{uid}: kind/audibility is unresolved.')
            continue
        if (kind in AUDIO_KINDS) != audible:
            add_error(errors, 'kind_audibility', f'{uid}: kind and audibility disagree.')
        if audible:
            start, end = unit.get('spoken_start'), unit.get('spoken_end')
            if not integer(start) or not integer(end) or not unit['start'] <= start < end <= unit['end']:
                add_error(errors, 'spoken_span', f'{uid}: invalid spoken interval.')
            elif unit.get('spoken_text') != text[start:end]:
                add_error(errors, 'spoken_text', f'{uid}: spoken text differs from source slice.')
            if not isinstance(unit.get('speaker'), str) or not unit['speaker'].strip():
                add_error(errors, 'speaker_missing', f'{uid}: audible source needs a speaker/VO label.')
        elif any(unit.get(key) is not None for key in ('spoken_start', 'spoken_end', 'spoken_text')):
            add_error(errors, 'non_audio_text', f'{uid}: non-audible unit retains spoken fields.')
        if kind == 'translation':
            members = pairs.get(unit.get('pair_id'), [])
            counterparts = [u for u in members if u.get('audible') is True]
            if len(members) != 2 or len(counterparts) != 1 or counterparts[0].get('episode') != unit.get('episode'):
                add_error(errors, 'translation_pair', f'{uid}: translation needs one same-episode audible counterpart.')


def parse_storyboards(paths, errors):
    shots, audio_entries, hashes = [], [], []
    ids = set()
    for path in paths:
        data = path.read_bytes()
        hashes.append({'path': str(path.resolve()), 'sha256': digest(data)})
        episode = group = current = None
        collecting = False

        def finish_audio():
            nonlocal collecting
            if not collecting:
                return
            collecting = False
            values = current.pop('_audio_lines', [])
            if values == ['无']:
                return
            if not values:
                add_error(errors, 'empty_audio_field', f'{current["id"]}: empty source-text field.')
            for index, value in enumerate(values, 1):
                value = ENGLISH_PREFIX.sub('', value)
                # One optional ASCII space after the speaker delimiter is
                # presentation syntax. Every additional/trailing source space
                # is significant, including separators at English shot cuts.
                match = re.fullmatch(r'([^：:\n]+)[：:] ?(.+)', value)
                if not match:
                    add_error(errors, 'audio_format', f'{current["id"]}: expected ROLE: exact text on each line.')
                    continue
                audio_entries.append({'shot_id': current['id'], 'audio_index': index,
                                      'episode': episode, 'speaker': match[1].strip(), 'text': match[2],
                                      'play_order': len(audio_entries), 'path': str(path.resolve())})

        for line_number, raw in enumerate(data.decode('utf-8-sig').splitlines(), 1):
            # Remove Markdown indentation only. Stripping the right edge would
            # lose source spaces assigned to the preceding audio fragment.
            line = raw.lstrip()
            em, gm, sm, am = EPISODE.match(line), GROUP.match(line), SHOT.match(line), AUDIO.match(line)
            boundary = em or gm or sm or line.startswith('负面提示词') or (line.startswith('#') and not am)
            if boundary:
                finish_audio()
            if em:
                episode = episode_number(em[1])
                group = current = None
            elif gm:
                if episode is None:
                    add_error(errors, 'missing_episode', f'{path.name}:{line_number}: group lacks episode title.')
                group = {'number': int(gm[1]), 'declared': float(gm[2]), 'shots': []}
                current = None
            elif sm:
                if episode is None or group is None:
                    add_error(errors, 'missing_group', f'{path.name}:{line_number}: shot lacks episode/group.')
                    current = None
                    continue
                sid = f'E{int(episode):03d}-G{group["number"]:03d}-S{int(sm[1]):03d}'
                if sid in ids:
                    add_error(errors, 'duplicate_shot', sid)
                ids.add(sid)
                current = {'id': sid, 'episode': episode, 'duration': float(sm[2]),
                           'audio_fields': 0, 'group': group, 'line': line_number}
                group['shots'].append(current)
                shots.append(current)
            elif am:
                finish_audio()
                if current is None:
                    add_error(errors, 'orphan_audio', f'{path.name}:{line_number}: source field outside a shot.')
                    continue
                current['audio_fields'] += 1
                current['_audio_lines'] = [am[1]] if am[1] else []
                collecting = True
            elif collecting and line:
                current['_audio_lines'].append(line)
        finish_audio()
    seen_groups = set()
    for shot in shots:
        if shot['audio_fields'] != 1:
            add_error(errors, 'audio_field_count', f'{shot["id"]}: expected exactly one source-text field.')
        group = shot['group']
        if id(group) not in seen_groups:
            seen_groups.add(id(group))
            actual = sum(s['duration'] for s in group['shots'])
            if abs(actual - group['declared']) > 0.051:
                add_error(errors, 'group_sum', f'{shot["id"]}: declared {group["declared"]}, summed {actual:.3f}.')
    if not shots:
        add_error(errors, 'no_shots', 'No standard shot blocks found in storyboard files.')
    return shots, audio_entries, hashes


def check_mapping(mapping, ledger, selected, entries, text, errors):
    if not isinstance(mapping, dict) or mapping.get('schema_version') != 1:
        raise ValueError('Mapping must have schema_version=1.')
    if mapping.get('source_sha256') != ledger['source']['sha256']:
        add_error(errors, 'mapping_revision', 'Mapping source revision differs from ledger.')
    fragments = mapping.get('fragments')
    if not isinstance(fragments, list):
        raise ValueError('Mapping fragments must be a list.')
    expected = {u['id']: u for u in selected if u.get('audible') is True}
    rendered = {(e['shot_id'], e['audio_index']): e for e in entries}
    used_targets, covered, valid_fragments = set(), {}, []
    for fragment in fragments:
        if not isinstance(fragment, dict):
            raise ValueError('Every mapping fragment must be an object.')
        uid = fragment.get('unit_id')
        target = (fragment.get('shot_id'), fragment.get('audio_index'))
        if not isinstance(target[0], str) or not integer(target[1]) or target[1] < 1:
            add_error(errors, 'target_id', f'{uid}: invalid rendered target id.')
            continue
        if target in used_targets:
            add_error(errors, 'duplicate_target', str(target))
        used_targets.add(target)
        unit, entry = expected.get(uid), rendered.get(target)
        if unit is None:
            add_error(errors, 'source_out_of_scope', f'{uid}: not an audible unit in selected scope.')
            continue
        if entry is None:
            add_error(errors, 'missing_rendered_fragment', str(target))
            continue
        start, end = fragment.get('start'), fragment.get('end')
        if not integer(start) or not integer(end) or not unit['spoken_start'] <= start < end <= unit['spoken_end']:
            add_error(errors, 'fragment_span', f'{uid}: fragment is outside its spoken interval.')
            continue
        if entry['episode'] != unit.get('episode'):
            add_error(errors, 'wrong_episode', f'{uid}: rendered in episode {entry["episode"]}.')
        if entry['speaker'] != unit.get('speaker'):
            add_error(errors, 'wrong_speaker', f'{uid}: expected {unit.get("speaker")}, got {entry["speaker"]}.')
        if entry['text'] != text[start:end]:
            add_error(errors, 'dialogue_mismatch', f'{uid} -> {target}: rendered text differs from source.')
        covered.setdefault(uid, []).append((entry['play_order'], start, end))
        valid_fragments.append((entry['play_order'], unit['order'], start))
    for target in rendered:
        if target not in used_targets:
            add_error(errors, 'unmapped_rendered_audio', str(target))
    for uid, unit in expected.items():
        cursor = unit['spoken_start']
        for _, start, end in sorted(covered.get(uid, [])):
            if start != cursor:
                add_error(errors, 'speech_gap_overlap_order', f'{uid}: expected fragment at {cursor}, got {start}.')
            cursor = end
        if cursor != unit['spoken_end']:
            add_error(errors, 'missing_source_audio', f'{uid}: coverage ends at {cursor}, expected {unit["spoken_end"]}.')
    ordered_sources = [(order, start) for _, order, start in sorted(valid_fragments)]
    if ordered_sources != sorted(ordered_sources):
        add_error(errors, 'source_order', 'Actual playback order differs from source order.')
    return len(expected)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', required=True, type=Path)
    parser.add_argument('--storyboard', nargs='+', type=Path, help='Actual Markdown files in playback order.')
    parser.add_argument('--mapping', type=Path)
    parser.add_argument('--episodes', nargs='+', help='Original episode numbers; default all source units.')
    parser.add_argument('--start-unit')
    parser.add_argument('--end-unit')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--structure-only', action='store_true', help='Snapshot/offset integrity only, not semantic review.')
    modes.add_argument('--ledger-only', action='store_true', help='Integrity plus reviewed classifications, no storyboard.')
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args(argv)
    report = {'schema_version': 1, 'status': 'fail', 'errors': [],
              'limitations': ['Does not prove classification semantics, action coverage, blocking, or character knowledge.']}
    errors = report['errors']
    protected = [args.ledger, *(args.storyboard or [])]
    if args.mapping:
        protected.append(args.mapping)
    code = 1
    snapshot_identified = False
    try:
        ledger = read_json(args.ledger)
        # Protect the snapshot before integrity validation can raise on a bad unit.
        source_record = ledger.get('source') if isinstance(ledger, dict) else None
        if isinstance(source_record, dict) and isinstance(source_record.get('path'), str):
            early_snapshot = Path(source_record['path'])
            if not early_snapshot.is_absolute():
                early_snapshot = args.ledger.resolve().parent / early_snapshot
            protected.append(early_snapshot.resolve())
            snapshot_identified = True
        if args.report.resolve() in {p.resolve() for p in protected}:
            raise ValueError('Report path cannot overwrite an input file.')
        text, snapshot, units = source_integrity(ledger, args.ledger.resolve(), errors)
        protected.append(snapshot)
        if args.report.resolve() in {p.resolve() for p in protected}:
            raise ValueError('Report path cannot overwrite an input file.')
        selected = select_units(units, args)
        report['source_sha256'] = ledger['source']['sha256']
        report['ledger_sha256'] = digest(args.ledger.read_bytes())
        report['scope'] = {'episodes': list(dict.fromkeys(u.get('episode') for u in selected)),
                           'first_unit': selected[0]['id'], 'last_unit': selected[-1]['id'],
                           'unit_count': len(selected), 'whole_source': len(selected) == len(units)}
        report['mode'] = 'structure' if args.structure_only else 'ledger' if args.ledger_only else 'rendered_audio'
        if not errors and not args.structure_only:
            classifications(units, selected, text, errors)
        if args.structure_only or args.ledger_only:
            if args.storyboard or args.mapping:
                raise ValueError('Ledger-only modes do not accept storyboard/mapping inputs.')
        elif not args.storyboard or args.mapping is None:
            raise ValueError('Rendered verification requires --storyboard and --mapping.')
        elif not errors:
            shots, entries, hashes = parse_storyboards(args.storyboard, errors)
            report['artifacts'] = hashes
            report['shot_count'] = len(shots)
            report['mapping_sha256'] = digest(args.mapping.read_bytes())
            allowed_episodes = {u.get('episode') for u in selected}
            for shot in shots:
                if shot['episode'] not in allowed_episodes:
                    add_error(errors, 'rendered_episode_out_of_scope', shot['id'])
            report['audible_units'] = check_mapping(read_json(args.mapping), ledger, selected, entries, text, errors)
        report['status'] = 'pass' if not errors else 'fail'
        code = 0 if not errors else 1
    except (OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
        add_error(errors, 'input_error', str(exc))
        code = 2
    if args.report.resolve() in {p.resolve() for p in protected}:
        print('ERROR: report path would overwrite an input.', file=sys.stderr)
        return 2
    if not snapshot_identified and args.report.exists():
        print('ERROR: source identity is unresolved; refusing to overwrite an existing report path.', file=sys.stderr)
        return 2
    try:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    except OSError as exc:
        print(f'Cannot write report: {exc}', file=sys.stderr)
        return 2
    print(json.dumps({'status': report['status'], 'mode': report.get('mode'),
                      'errors': len(errors), 'report': str(args.report.resolve())}, ensure_ascii=False))
    for error in errors[:12]:
        print(f'{error["code"]}: {error["message"]}', file=sys.stderr)
    return code


if __name__ == '__main__':
    raise SystemExit(main())

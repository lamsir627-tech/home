#!/usr/bin/env python3
"""Validate an offline LibTV package against rendered storyboards; stdlib only.

Row vocabulary follows official CLI docs 1.1.3/node-types/script.md. This does
not verify prompt semantics, negative-prompt fidelity, or platform acceptance.
"""
import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from verify_storyboard import GROUP, add_error, digest, integer, parse_storyboards

REQUIRED_TEXT = {'plotDescription', 'imageGenerationPrompt', 'videoMotionPrompt', 'shotSize'}
OPTIONAL_TEXT = {'characterAction', 'emotion', 'sceneTags', 'lightingAndAtmosphere', 'audioEffects'}
ROW_REQUIRED = REQUIRED_TEXT | {'durationSeconds', 'characters', 'dialogue'}
ROW_FIELDS = ROW_REQUIRED | OPTIONAL_TEXT | {'videoReference'}
CHARACTER_FIELDS = {'characterName', 'characterDescription', 'characterImageUrl'}
ACTION_ORDERS = {'先做再说', '边做边说', '说完再做', '混合', '无对白', '仅对白'}
TOLERANCE = 1e-6


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def positive(value):
    try:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0
    except OverflowError:
        return False


def check_row(row, where, errors):
    if not isinstance(row, dict):
        add_error(errors, 'row_type', f'{where}: row must be an object.')
        return
    for field in sorted(set(row) - ROW_FIELDS):
        add_error(errors, 'row_field', f'{where}: unsupported row field {field}.')
    for field in sorted(ROW_REQUIRED):
        if field not in row or (field in REQUIRED_TEXT and not nonempty(row[field])):
            add_error(errors, 'row_required', f'{where}: missing/empty required field {field}.')
    for field in sorted(REQUIRED_TEXT | OPTIONAL_TEXT | {'dialogue'}):
        if field in row and not isinstance(row[field], str):
            add_error(errors, 'row_type', f'{where}: {field} must be a string.')
    if 'durationSeconds' in row and not positive(row['durationSeconds']):
        add_error(errors, 'row_type', f'{where}: durationSeconds must be a finite positive number.')
    if 'characters' in row:
        characters = row['characters']
        if not isinstance(characters, list):
            add_error(errors, 'row_type', f'{where}: characters must be an array.')
        else:
            for index, character in enumerate(characters):
                if (not isinstance(character, dict) or set(character) != CHARACTER_FIELDS or
                        not all(isinstance(character.get(k), str) for k in CHARACTER_FIELDS) or
                        not nonempty(character.get('characterName'))):
                    add_error(errors, 'row_type', f'{where}: invalid characters[{index}] object.')
    if 'videoReference' in row:
        reference = row['videoReference']
        if (not isinstance(reference, dict) or set(reference) != {'referenceFrameImage'} or
                not isinstance(reference.get('referenceFrameImage'), str)):
            add_error(errors, 'row_type', f'{where}: videoReference needs only referenceFrameImage:string.')


def compare_order(actual, expected, kind, where, errors):
    if len(actual) != len(expected):
        add_error(errors, f'{kind}_count', f'{where}: expected {len(expected)} {kind}s, got {len(actual)}.')
    for identifier, count in Counter(x for x in actual if isinstance(x, str)).items():
        if count > 1:
            add_error(errors, f'duplicate_{kind}', f'{where}: repeated {identifier}.')
    if actual != expected:
        add_error(errors, f'{kind}_order', f'{where}: {kind} identities/order differ from the complete source sequence.')


def validate(package, shots, entries, errors):
    source_groups, seen = [], set()
    for shot in shots:
        if id(shot['group']) not in seen:
            seen.add(id(shot['group']))
            source_groups.append(dict(id=shot['id'].rsplit('-S', 1)[0], episode=int(shot['episode']), **shot['group']))
    source_ids = [group['id'] for group in source_groups]
    if len(set(source_ids)) != len(source_ids):
        add_error(errors, 'source_duplicate_group', 'Source repeats an episode/group identity.')
    audio = defaultdict(list)
    for entry in entries:
        audio[entry['shot_id']].append(entry['speaker'] + ': ' + entry['text'])
    if not isinstance(package, dict):
        add_error(errors, 'package_schema', 'Package must be an object.')
        return len(source_groups)
    if not integer(package.get('schema_version')) or package['schema_version'] != 1 or package.get('platform') != 'libtv-cli':
        add_error(errors, 'package_schema', 'Expected schema_version=1 and platform=libtv-cli.')
    for field in ('cli_docs_version', 'aspect_ratio', 'style'):
        if not nonempty(package.get(field)):
            add_error(errors, 'package_schema', f'{field} must be a nonempty string.')
    groups = package.get('groups')
    if not isinstance(groups, list) or not groups:
        add_error(errors, 'package_schema', 'groups must be a nonempty array.')
        return len(source_groups)
    compare_order([g.get('group_id') if isinstance(g, dict) else None for g in groups], source_ids, 'group', 'package', errors)
    names = [g.get('node_name') for g in groups if isinstance(g, dict) and isinstance(g.get('node_name'), str)]
    for name, count in Counter(names).items():
        if count > 1:
            add_error(errors, 'duplicate_node_name', f'Package repeats node_name {name}.')
    all_ids = []
    for index, group in enumerate(groups):
        where = f'groups[{index}]'
        if not isinstance(group, dict):
            add_error(errors, 'group_schema', f'{where}: group must be an object.')
            continue
        gid = group.get('group_id')
        ep, number = group.get('episode'), group.get('group_number')
        if (not integer(ep) or not integer(number) or not isinstance(gid, str) or
                not re.fullmatch(r'E\d{3,}-G\d{3,}', gid) or gid != f'E{ep:03d}-G{number:03d}'):
            add_error(errors, 'group_identity', f'{where}: group_id, episode and group_number must agree.')
        if (not nonempty(group.get('node_name')) or group.get('node_type') not in ('storyboard', 'script') or
                not isinstance(group.get('negative_prompt'), str) or not positive(group.get('duration_seconds'))):
            add_error(errors, 'group_schema', f'{where}: invalid node_name/node_type/negative_prompt/duration_seconds.')
        expected = source_groups[index] if index < len(source_groups) else None
        if expected and (ep != expected['episode'] or number != expected['number']):
            add_error(errors, 'group_identity', f'{where}: episode/group differ from source.')
        if expected and positive(group.get('duration_seconds')) and abs(group['duration_seconds'] - expected['declared']) > TOLERANCE:
            add_error(errors, 'group_duration', f'{where}: duration_seconds differs from source group duration.')
        items = group.get('shots')
        if not isinstance(items, list) or not items:
            add_error(errors, 'shot_count', f'{where}: shots must be a nonempty array.')
            continue
        expected_shots = expected['shots'] if expected else []
        ids = [s.get('shot_id') if isinstance(s, dict) else None for s in items]
        all_ids.extend(ids)
        compare_order(ids, [s['id'] for s in expected_shots], 'shot', where, errors)
        for position, item in enumerate(items):
            location = f'{where}.shots[{position}]'
            if not isinstance(item, dict):
                add_error(errors, 'shot_schema', f'{location}: shot must be an object.')
                continue
            sid = item.get('shot_id')
            if not isinstance(sid, str) or not re.fullmatch(r'E\d{3,}-G\d{3,}-S\d{3,}', sid) or sid.rsplit('-S', 1)[0] != gid:
                add_error(errors, 'shot_identity', f'{location}: shot_id must belong to its group.')
            if not isinstance(item.get('action_dialogue_order'), str) or item['action_dialogue_order'] not in ACTION_ORDERS:
                add_error(errors, 'shot_schema', f'{location}: invalid action_dialogue_order.')
            row = item.get('row')
            check_row(row, location, errors)
            if not isinstance(row, dict) or position >= len(expected_shots):
                continue
            source = expected_shots[position]
            if positive(row.get('durationSeconds')) and abs(row['durationSeconds'] - source['duration']) > TOLERANCE:
                add_error(errors, 'shot_duration', f'{location}: durationSeconds differs from source shot duration.')
            if row.get('dialogue') != ('\n'.join(audio[source['id']]) or '无'):
                add_error(errors, 'dialogue_mismatch', f'{location}: dialogue differs from exact source audio entries.')
    for sid, count in Counter(s for s in all_ids if isinstance(s, str)).items():
        if count > 1 and not any(e['code'] == 'duplicate_shot' and sid in e['message'] for e in errors):
            add_error(errors, 'duplicate_shot', f'Package repeats {sid}.')
    return len(source_groups)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--storyboard', type=Path, nargs='+', action='extend', required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.report.resolve() in {p.resolve() for p in [args.package, *args.storyboard]}:
        parser.error('--report must not overwrite a package or source input.')
    errors, sources, shots, entries = [], [], [], []
    source_group_count = 0
    package, package_info = None, {'path': str(args.package.resolve()), 'sha256': None}
    try:
        raw = args.package.read_bytes()
        package_info['sha256'] = digest(raw)
        package = json.loads(raw.decode('utf-8-sig'))
    except (OSError, ValueError) as exc:
        add_error(errors, 'package_read', str(exc))
    for path in args.storyboard:
        try:
            raw = path.read_bytes()
            sources.append({'path': str(path.resolve()), 'sha256': digest(raw)})
            source_group_count += sum(bool(GROUP.match(line.lstrip())) for line in raw.decode('utf-8-sig').splitlines())
        except (OSError, ValueError) as exc:
            add_error(errors, 'source_read', str(exc))
    try:
        shots, entries, _ = parse_storyboards(args.storyboard, errors)
    except (OSError, ValueError) as exc:
        add_error(errors, 'source_parse', str(exc))
    if source_group_count != len({id(shot['group']) for shot in shots}):
        add_error(errors, 'source_empty_group', 'Source group headings include groups without parsed shots.')
    count = validate(package, shots, entries, errors)
    report = dict(schema_version=1, status='fail' if errors else 'pass', mode='offline_structure_mapping',
                  semantic_verified=False, remote_verified=False, negative_prompt_verified=False,
                  row_schema_baseline='1.1.3', package=package_info, sources=sources,
                  group_count=count, shot_count=len(shots), errors=errors)
    try:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    except OSError as exc:
        print(f'Cannot write report: {exc}', file=sys.stderr)
        return 2
    print(json.dumps({'status': report['status'], 'errors': len(errors), 'report': str(args.report)}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())

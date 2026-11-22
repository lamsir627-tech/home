"""Verify a local prewrite evidence package; never call a canvas or generate media.

This checks evidence coverage and immutable inputs, not the truth of image/text
semantics or the identity of a person named as reviewer. See industrial-admission.md.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

CHECKS = [*(f'P{i:02}' for i in range(1, 9)), 'P09Pre', 'P10Pre']
FIELDS = ('global', 'description', 'single', 'composite')
LABELS = {'通过', 'PASS', '全部通过', '站位正确', '动作连贯'}


def factual(value):
    return isinstance(value, str) and bool(value.strip()) and value.strip() not in LABELS


def validate(package_path, candidate_path):
    errors, files = [], []
    base = package_path.resolve().parent

    def load_ref(ref, label, as_json=False):
        path = (base / ref['path']).resolve(strict=True)
        raw = path.read_bytes()
        files.append(str(path))
        digest = hashlib.sha256(raw).hexdigest()
        if digest != ref['sha256']:
            errors.append(f'{label}: content version changed')
        return json.loads(raw) if as_json else digest

    package = json.loads(package_path.read_text(encoding='utf-8-sig'))
    if package.get('schemaVersion') != 1:
        errors.append('Unsupported admission package schema')
    approved = load_ref(package['approved'], 'approved snapshot', True)
    review = load_ref(package['review'], 'independent review', True)
    candidate = json.loads(candidate_path.read_text(encoding='utf-8-sig'))
    if candidate != approved:
        errors.append('Candidate differs from the reviewed snapshot (including order/target/parameters)')
    for key in ('group', 'target', 'prompt', 'references', 'params', 'visiblePeople'):
        if key not in approved:
            errors.append(f'Approved snapshot missing {key}')
    if not factual(approved.get('prompt')):
        errors.append('Approved prompt is empty or a status label')
    if not approved.get('target') or not approved.get('params'):
        errors.append('Target and effective parameters are required')
    if review.get('approvedSHA256') != package['approved']['sha256']:
        errors.append('Review belongs to a different approved snapshot')
    if (not factual(review.get('author')) or not factual(review.get('reviewer'))
            or review.get('author') == review.get('reviewer')):
        errors.append('Distinct author and independent reviewer records are required')

    inputs = package['inputs']
    if not isinstance(inputs, list) or not inputs:
        errors.append('Actual source/input versions are required')
        inputs = []
    ids = [row['id'] for row in inputs]
    if len(ids) != len(set(ids)):
        errors.append('Input IDs must be unique')
    for row in inputs:
        load_ref(row, f'input {row["id"]}')
    dependencies = package['dependencies']
    if not isinstance(dependencies, list):
        errors.append('Dependencies must explicitly list consumed versions')
        dependencies = []
    if review.get('inputVersions') != {'inputs': inputs, 'dependencies': dependencies}:
        errors.append('Input/dependency version inventory differs from the independently reviewed inventory')
    for row in dependencies:
        load_ref(row, f'dependency {row["id"]}')
    references = approved.get('references', [])
    if not isinstance(references, list) or len(references) != len(set(references)):
        errors.append('References must be an ordered list of unique input IDs')
    elif any(ref not in ids for ref in references):
        errors.append('A reference has no actual input version')

    checks = review.get('checks', {})
    for key in CHECKS:
        row = checks.get(key, {})
        if row.get('status') == '不适用':
            if not factual(row.get('reason')) or row.get('confirmedBy') != review.get('reviewer'):
                errors.append(f'{key}: nonapplicability needs a reason and reviewer confirmation')
        elif row.get('status') != '通过' or not factual(row.get('evidence')):
            errors.append(f'{key}: not passed with factual evidence')

    shot_ids = [int(number) for number in re.findall(r'【单镜头\s*(\d+)】', approved.get('prompt', ''))]
    shots = review.get('shots', [])
    actual_ids = [row.get('shot') for row in shots]
    if not shot_ids or len(set(shot_ids)) != len(shot_ids) or sorted(actual_ids) != sorted(shot_ids):
        errors.append('Per-shot evidence does not exactly cover final prompt shots')
    for row in shots:
        if row.get('status') != '通过':
            errors.append(f'Shot {row.get("shot")}: not passed')
        for key in ('initial', 'action', 'final', 'sourceEvidence'):
            if not factual(row.get(key)):
                errors.append(f'Shot {row.get("shot")}: missing {key} facts')
        for key in FIELDS:
            if not factual(row.get('fields', {}).get(key)):
                errors.append(f'Shot {row.get("shot")}: missing {key} field evidence')

    def person_key(row):
        return row['person'], row['map'], row['card']

    expected_people = [person_key(row) for row in approved.get('visiblePeople', [])]
    people = review.get('people', [])
    actual_people = [person_key(row) for row in people]
    if len(set(expected_people)) != len(expected_people) or sorted(actual_people) != sorted(expected_people):
        errors.append('Per-person evidence does not exactly cover the reviewed visible-person inventory')
    for row in people:
        if row.get('status') != '通过' or not factual(row.get('evidence')):
            errors.append(f'Person {row.get("person")}: missing or pending identity/wardrobe evidence')
        if row['map'] not in ids or row['card'] not in ids:
            errors.append(f'Person {row.get("person")}: image/card input version missing')
    if expected_people and checks.get('P04', {}).get('status') != '通过':
        errors.append('Visible people require applicable P04 identity/wardrobe review')

    def requests_generation(value):
        if isinstance(value, dict):
            return any((key in {'run', 'runAll', 'generate', 'generateVideo'} and item is not False)
                       or requests_generation(item) for key, item in value.items())
        return isinstance(value, list) and any(requests_generation(item) for item in value)

    if requests_generation(candidate):
        errors.append('Prewrite admission cannot authorize generation')
    return {
        'eligible': not errors, 'stage': 'prewrite', 'errors': errors,
        'snapshotSHA256': package['approved']['sha256'],
        'candidateSHA256': hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
        'group': approved.get('group'), 'shotsCovered': len(shots), 'peopleCovered': len(people),
        'filesChecked': files, 'globalWriteIsolation': False,
        'automaticallyVerifiedSemantics': False,
        'limits': 'Checks versions and recorded evidence coverage. Independent semantic judgment and live write/readback remain required.',
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True, type=Path)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args(argv)
    protected = {args.package.resolve(), args.candidate.resolve()}
    # Collect all declared inputs before validation, including on malformed review files.
    try:
        package = json.loads(args.package.read_text(encoding='utf-8-sig'))
        refs = [package.get('approved'), package.get('review')]
        refs += package.get('inputs', []) + package.get('dependencies', [])
        for ref in refs:
            if isinstance(ref, dict) and isinstance(ref.get('path'), str):
                protected.add((args.package.resolve().parent / ref['path']).resolve())
    except (OSError, ValueError, TypeError, AttributeError):
        if args.report:
            parser.error('Cannot safely resolve admission inputs for report output')
    if args.report:
        output = args.report.resolve()
        if output in protected or (output.exists() and any(
                path.exists() and output.samefile(path) for path in protected)):
            parser.error('Report must not overwrite admission inputs or evidence')
    try:
        result = validate(args.package, args.candidate)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        result = {'eligible': False, 'stage': 'prewrite', 'errors': [str(error)],
                  'globalWriteIsolation': False, 'automaticallyVerifiedSemantics': False}
    encoded = json.dumps(result, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded + '\n', encoding='utf-8')
    print(encoded)
    return 0 if result['eligible'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

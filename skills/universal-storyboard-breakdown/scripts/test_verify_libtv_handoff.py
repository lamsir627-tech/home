"""Offline handoff regression tests using synthetic, non-project fixtures."""
import contextlib
import copy
import hashlib
import io
import json
import runpy
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name('verify_libtv_handoff.py')
# 20s/0.5s deliberately test mapping without asserting storyboard-contract
# compliance or the remote platform's accepted generation duration range.
MARKDOWN = [
    '第1集｜测试\n## 第1组（目标00:00-00:30；实际5.5秒）\n'
    '【单镜头1】2.5秒\n**字幕/角色台词/旁白**：\n'
    '  A: We need \n  B:  now?!\n'
    '【单镜头2】3.0秒\n**字幕/角色台词/旁白**：无\n负面提示词：\n'
    '## 第2组（目标00:00-00:30；实际20.0秒）\n'
    '【单镜头1】20.0秒\n**字幕/角色台词/旁白**：A：继续。\n负面提示词：\n',
    '第2集｜测试\n## 第1组（目标00:00-00:30；实际0.5秒）\n'
    '【单镜头1】0.5秒\n**字幕/角色台词/旁白**：无\n负面提示词：\n']


def fixture():
    groups = []
    for ep, num, timings, lines in [(1, 1, [2.5, 3.0], ['A: We need \nB:  now?!', '无']),
                                  (1, 2, [20.0], ['A: 继续。']), (2, 1, [0.5], ['无'])]:
        gid = f'E{ep:03d}-G{num:03d}'
        shots = [dict(shot_id=f'{gid}-S{i:03d}', action_dialogue_order='无对白' if line == '无' else '边做边说',
                      row=dict(durationSeconds=duration, plotDescription='人物停在门旁。',
                               imageGenerationPrompt='门旁静态首帧。', videoMotionPrompt='人物抬手。',
                               shotSize='中近景', characters=[], dialogue=line))
                 for i, (duration, line) in enumerate(zip(timings, lines), 1)]
        groups.append(dict(group_id=gid, episode=ep, group_number=num, duration_seconds=sum(timings),
                           node_name=gid, node_type='storyboard', negative_prompt='', shots=shots))
    groups[0]['shots'][0]['row']['characters'] = [dict(characterName='A', characterDescription='', characterImageUrl='')]
    return dict(schema_version=1, platform='libtv-cli', cli_docs_version='1.1.3', aspect_ratio='9:16', style='写实', groups=groups)


class HandoffTests(unittest.TestCase):
    def invoke(self, package=None, markdown=None):
        self.assertTrue(CHECKER.is_file(), 'Offline LibTV handoff verifier has not been implemented')
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            package_path, report_path = work / 'package.json', work / 'report.json'
            raw = json.dumps(fixture() if package is None else package, ensure_ascii=False).encode('utf-8')
            package_path.write_bytes(raw)
            paths = []
            for i, text in enumerate(MARKDOWN if markdown is None else markdown):
                path = work / f'episode-{i}.md'
                path.write_bytes(text.encode('utf-8'))
                paths.append(str(path))
            with contextlib.redirect_stdout(io.StringIO()):
                code = runpy.run_path(str(CHECKER))['main'](
                    ['--package', str(package_path), '--storyboard', *paths, '--report', str(report_path)])
            report = json.loads(report_path.read_text(encoding='utf-8'))
            self.assertEqual(report['package']['sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual([s['sha256'] for s in report['sources']],
                             [hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths])
            self.assertEqual(report['mode'], 'offline_structure_mapping')
            self.assertFalse(report['semantic_verified'])
            self.assertFalse(report['remote_verified'])
            return code, report

    def rejected(self, package, code):
        status, report = self.invoke(package)
        self.assertEqual(status, 1, report)
        self.assertIn(code, [error['code'] for error in report['errors']], report)

    def test_valid_multifile_speech_silence_and_unrestricted_positive_duration(self):
        status, report = self.invoke()
        self.assertEqual(status, 0, report)
        self.assertEqual((report['group_count'], report['shot_count']), (3, 4))
        self.assertEqual(report['errors'], [])

    def test_supported_optional_fields_and_future_document_revision(self):
        package = fixture()
        package['cli_docs_version'] = 'future-reviewed-version'
        package['groups'][0]['node_type'] = 'script'
        row = package['groups'][0]['shots'][0]['row']
        row.update(videoReference={'referenceFrameImage': ''}, characterAction='', emotion='', sceneTags='', lightingAndAtmosphere='', audioEffects='')
        self.assertEqual(self.invoke(package)[0], 0)

    def test_reordering_omitting_and_duplicating_groups_or_shots(self):
        for target in ('groups', 'shots'):
            for mutation, error in [('reverse', f'{target[:-1]}_order'), ('omit', f'{target[:-1]}_count'), ('duplicate', f'duplicate_{target[:-1]}')]:
                with self.subTest(target=target, mutation=mutation):
                    package = fixture()
                    items = package['groups'] if target == 'groups' else package['groups'][0]['shots']
                    if mutation == 'reverse': items.reverse()
                    elif mutation == 'omit': items.pop()
                    else: items.append(copy.deepcopy(items[0]))
                    self.rejected(package, error)

    def test_exact_dialogue_punctuation_and_boundary_spaces(self):
        for value in ['A: We need\nB:  now?!', 'A: We need \nB: now?!', 'A: We need \nB:  now?', 'B:  now?!\nA: We need ', '无']:
            with self.subTest(value=value):
                package = fixture()
                package['groups'][0]['shots'][0]['row']['dialogue'] = value
                self.rejected(package, 'dialogue_mismatch')

    def test_distinct_groups_cannot_reuse_a_node_name(self):
        package = fixture()
        package['groups'][1]['node_name'] = package['groups'][0]['node_name']
        self.rejected(package, 'duplicate_node_name')

    def test_changed_durations(self):
        for group_change in (False, True):
            package = fixture()
            item, field = (package['groups'][0], 'duration_seconds') if group_change else (package['groups'][0]['shots'][0]['row'], 'durationSeconds')
            item[field] += 0.0001
            self.rejected(package, 'group_duration' if group_change else 'shot_duration')

    def test_required_row_fields_and_empty_static_or_motion_prompts(self):
        for field in fixture()['groups'][0]['shots'][0]['row']:
            package = fixture()
            del package['groups'][0]['shots'][0]['row'][field]
            self.rejected(package, 'row_required')
        for field in ('plotDescription', 'imageGenerationPrompt', 'videoMotionPrompt', 'shotSize'):
            package = fixture()
            package['groups'][0]['shots'][0]['row'][field] = ' \t'
            self.rejected(package, 'row_required')

    def test_forbidden_unknown_and_misplaced_row_fields(self):
        for field in ('id', 'hiddenUuid', 'title', 'shotNumber', 'negative_prompt', 'action_dialogue_order', 'model', 'videoPrompt'):
            package = fixture()
            package['groups'][0]['shots'][0]['row'][field] = 'unexpected'
            self.rejected(package, 'row_field')

    def test_row_and_nested_types(self):
        for field, value in [('durationSeconds', True), ('durationSeconds', float('nan')), ('durationSeconds', float('inf')),
                             ('durationSeconds', -1), ('durationSeconds', '2.5'), ('dialogue', []), ('characters', {}),
                             ('characters', [{}]), ('characters', [dict(characterName='', characterDescription='', characterImageUrl='')]),
                             ('characters', [dict(characterName='A', characterDescription=1, characterImageUrl='')]),
                             ('videoReference', {}), ('videoReference', {'videoUrl': 'x'}), ('videoReference', {'referenceFrameImage': []}),
                             ('videoReference', None), ('emotion', []), ('audioEffects', None)]:
            with self.subTest(field=field, value=value):
                package = fixture()
                package['groups'][0]['shots'][0]['row'][field] = value
                self.assertEqual(self.invoke(package)[0], 1)

    def test_package_group_and_shot_metadata(self):
        for level, field, value in [('package', 'schema_version', True), ('package', 'platform', 'other'), ('package', 'aspect_ratio', ''),
                                    ('package', 'style', None), ('package', 'cli_docs_version', ''), ('group', 'episode', True),
                                    ('group', 'group_number', 9), ('group', 'group_id', 'E001-G002'), ('group', 'node_type', 'video'),
                                    ('group', 'negative_prompt', None), ('group', 'node_name', ''), ('shot', 'shot_id', 'E001-G002-S001'),
                                    ('shot', 'action_dialogue_order', 'unknown')]:
            with self.subTest(field=field):
                package = fixture()
                target = package if level == 'package' else package['groups'][0] if level == 'group' else package['groups'][0]['shots'][0]
                target[field] = value
                self.assertEqual(self.invoke(package)[0], 1)
        package = fixture()
        del package['groups'][0]['negative_prompt']
        self.assertEqual(self.invoke(package)[0], 1)

    def test_source_parse_failure_cannot_pass(self):
        status, report = self.invoke(markdown=[MARKDOWN[0].replace('：无', '：') , MARKDOWN[1]])
        self.assertEqual(status, 1, report)
        self.assertIn('empty_audio_field', [e['code'] for e in report['errors']])

    def test_source_empty_group_cannot_be_silently_omitted(self):
        extra = '\n## 第3组（目标00:00-00:30；实际30.0秒）\n负面提示词：\n'
        status, report = self.invoke(markdown=[MARKDOWN[0] + extra, MARKDOWN[1]])
        self.assertEqual(status, 1, report)
        self.assertIn('source_empty_group', [e['code'] for e in report['errors']])

    def test_huge_json_numbers_report_failure_instead_of_crashing(self):
        for group_change in (False, True):
            package = fixture()
            item, field = (package['groups'][0], 'duration_seconds') if group_change else (package['groups'][0]['shots'][0]['row'], 'durationSeconds')
            item[field] = 10 ** 400
            self.rejected(package, 'group_schema' if group_change else 'row_type')


if __name__ == '__main__':
    unittest.main(verbosity=2)

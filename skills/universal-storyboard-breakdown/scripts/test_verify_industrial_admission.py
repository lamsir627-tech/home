"""Offline admission tests; no canvas calls or media generation."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CHECKER = Path(__file__).with_name('verify_industrial_admission.py')


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.snapshot = {
            'group': '18-3', 'target': {'team': '1', 'project': 'test', 'node': 'v-test'},
            'prompt': '### 第1组（00:00-00:30）\n【单镜头1】\n离袖后收手。',
            'references': ['card', 'map'],
            'params': {'model': 'test-model', 'duration': 30, 'ratio': '9:16'},
            'visiblePeople': [{'person': '顾云骧', 'map': 'map', 'card': 'card'}],
        }
        self.write('approved.json', self.snapshot)
        self.write('candidate.json', self.snapshot)
        self.write('script.txt', '原文动作。')
        self.write('card.bin', b'confirmed asset bytes')
        self.write('map.bin', b'confirmed map bytes')
        self.review = {
            'author': 'writer', 'reviewer': 'independent-reader',
            'approvedSHA256': self.digest('approved.json'),
            'checks': {key: {'status': '通过', 'evidence': '已核具体事实及对应原文位置。'}
                       for key in [*(f'P{i:02}' for i in range(1, 9)), 'P09Pre', 'P10Pre']},
            'shots': [{'shot': 1, 'status': '通过',
                       'initial': '右掌接触衣袖。', 'action': '右指松开并撤回。',
                       'final': '右手回到膝前。', 'sourceEvidence': 'script.txt 第一段',
                       'fields': {key: '已比对同一动作阶段的具体原句。'
                                  for key in ['global', 'description', 'single', 'composite']}}],
            'people': [{'person': '顾云骧', 'map': 'map', 'card': 'card',
                        'status': '通过', 'evidence': '原卡与图中脸、发型和衣装逐项核对。'}],
        }
        self.write('review.json', self.review)
        self.package = {
            'schemaVersion': 1, 'approved': self.ref('approved.json'),
            'review': self.ref('review.json'),
            'inputs': [dict(id='script', **self.ref('script.txt')),
                       dict(id='card', **self.ref('card.bin')),
                       dict(id='map', **self.ref('map.bin'))],
            'dependencies': [],
        }
        self.review['inputVersions'] = copy.deepcopy({
            'inputs': self.package['inputs'], 'dependencies': self.package['dependencies']})
        self.refresh_review()

    def write(self, name, value):
        data = value if isinstance(value, bytes) else (
            json.dumps(value, ensure_ascii=False).encode('utf-8') if isinstance(value, dict)
            else value.encode('utf-8'))
        (self.root / name).write_bytes(data)

    def digest(self, name):
        return hashlib.sha256((self.root / name).read_bytes()).hexdigest()

    def ref(self, name):
        return {'path': name, 'sha256': self.digest(name)}

    def run_check(self, expected=1):
        self.assertTrue(CHECKER.is_file(), 'Admission checker is not implemented')
        self.write('package.json', self.package)
        result = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(CHECKER),
                                 '--package', str(self.root / 'package.json'),
                                 '--candidate', str(self.root / 'candidate.json')],
                                capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def refresh_review(self):
        self.write('review.json', self.review)
        self.package['review'] = self.ref('review.json')

    def test_complete_evidence_passes_without_claiming_semantic_or_permission_isolation(self):
        result = self.run_check(0)
        self.assertTrue(result['eligible'])
        self.assertFalse(result['globalWriteIsolation'])
        self.assertFalse(result['automaticallyVerifiedSemantics'])

    def test_edited_prompt_rejected(self):
        candidate = copy.deepcopy(self.snapshot)
        candidate['prompt'] += '改稿'
        self.write('candidate.json', candidate)
        self.run_check()

    def test_reference_order_rejected(self):
        candidate = copy.deepcopy(self.snapshot)
        candidate['references'].reverse()
        self.write('candidate.json', candidate)
        self.run_check()

    def test_changed_model_parameters_rejected(self):
        candidate = copy.deepcopy(self.snapshot)
        candidate['params']['ratio'] = '16:9'
        self.write('candidate.json', candidate)
        self.run_check()

    def test_changed_target_rejected(self):
        candidate = copy.deepcopy(self.snapshot)
        candidate['target']['node'] = 'another-node'
        self.write('candidate.json', candidate)
        self.run_check()

    def test_same_path_replaced_image_rejected(self):
        self.write('map.bin', b'new image at same path')
        self.run_check()

    def test_missing_required_check_rejected(self):
        del self.review['checks']['P06']
        self.refresh_review()
        self.run_check()

    def test_pending_and_failed_checks_rejected(self):
        for state in ['待核', '失败']:
            with self.subTest(state=state):
                self.review['checks']['P06']['status'] = state
                self.refresh_review()
                self.run_check()

    def test_pass_label_without_evidence_rejected(self):
        self.review['checks']['P06']['evidence'] = ''
        self.refresh_review()
        self.run_check()

    def test_missing_shot_coverage_rejected(self):
        self.review['shots'] = []
        self.refresh_review()
        self.run_check()

    def test_missing_field_coverage_rejected(self):
        del self.review['shots'][0]['fields']['description']
        self.refresh_review()
        self.run_check()

    def test_partial_person_review_rejected(self):
        self.review['people'] = []
        self.refresh_review()
        self.run_check()

    def test_author_cannot_be_independent_reviewer(self):
        self.review['reviewer'] = self.review['author']
        self.refresh_review()
        self.run_check()

    def test_previous_version_review_rejected(self):
        self.review['approvedSHA256'] = '0' * 64
        self.refresh_review()
        self.run_check()

    def test_changed_dependency_rejected(self):
        self.write('previous.json', {'end': '手已松开'})
        self.package['dependencies'] = [dict(id='previous-end', **self.ref('previous.json'))]
        self.write('previous.json', {'end': '手仍抓袖'})
        self.run_check()

    def test_no_generation_switch_allowed(self):
        self.snapshot['params']['run'] = True
        self.write('approved.json', self.snapshot)
        self.write('candidate.json', self.snapshot)
        self.package['approved'] = self.ref('approved.json')
        self.review['approvedSHA256'] = self.digest('approved.json')
        self.refresh_review()
        self.run_check()

    def test_nonapplicability_cannot_be_self_confirmed(self):
        self.review['checks']['P04'] = {'status': '不适用', 'reason': '原文无可见人物。',
                                        'confirmedBy': 'writer'}
        self.refresh_review()
        self.run_check()

    def test_report_cannot_overwrite_evidence_when_review_is_malformed(self):
        self.write('review.json', b'not JSON')
        self.package['review'] = self.ref('review.json')
        self.write('package.json', self.package)
        image = (self.root / 'map.bin').read_bytes()
        result = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(CHECKER),
                                 '--package', str(self.root / 'package.json'),
                                 '--candidate', str(self.root / 'candidate.json'),
                                 '--report', str(self.root / 'map.bin')],
                                capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.root / 'map.bin').read_bytes(), image)

    def test_refreshing_image_manifest_requires_new_review(self):
        self.run_check(0)
        self.write('map.bin', b'replacement image; old review not changed')
        self.package['inputs'][2] = dict(id='map', **self.ref('map.bin'))
        self.run_check()

    def test_refreshing_dependency_manifest_requires_new_review(self):
        self.write('previous.json', {'end': 'hand released'})
        self.package['dependencies'] = [dict(id='previous-end', **self.ref('previous.json'))]
        self.review['inputVersions'] = copy.deepcopy({
            'inputs': self.package['inputs'], 'dependencies': self.package['dependencies']})
        self.refresh_review()
        self.run_check(0)
        self.write('previous.json', {'end': 'hand still holding sleeve'})
        self.package['dependencies'][0] = dict(id='previous-end', **self.ref('previous.json'))
        self.run_check()

    def test_report_hardlink_cannot_overwrite_input(self):
        self.write('package.json', self.package)
        image = (self.root / 'map.bin').read_bytes()
        alias = self.root / 'report-alias.json'
        os.link(self.root / 'map.bin', alias)
        result = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(CHECKER),
                                 '--package', str(self.root / 'package.json'),
                                 '--candidate', str(self.root / 'candidate.json'),
                                 '--report', str(alias)],
                                capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.root / 'map.bin').read_bytes(), image)

    def test_truthy_numeric_generation_switch_rejected(self):
        snapshot = copy.deepcopy(self.snapshot)
        snapshot['params']['run'] = 1
        self.write('approved.json', snapshot)
        self.write('candidate.json', snapshot)
        self.package['approved'] = self.ref('approved.json')
        self.review['approvedSHA256'] = self.digest('approved.json')
        self.refresh_review()
        self.run_check()

    def test_visible_person_inventory_cannot_make_P04_nonapplicable(self):
        self.review['checks']['P04'] = {
            'status': '不适用', 'reason': '本组没有可见人物，无需图卡核对。',
            'confirmedBy': self.review['reviewer'],
        }
        self.refresh_review()
        self.run_check()


if __name__ == '__main__':
    unittest.main()

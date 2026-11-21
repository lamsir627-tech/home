"""Portable regression tests; run with python scripts/test_verify_storyboard.py."""
import contextlib
import io
import json
import runpy
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHECKER = runpy.run_path(str(ROOT / 'verify_storyboard.py'))
BUILDER = runpy.run_path(str(ROOT / 'build_source_ledger.py'))


class AudioWhitespaceTests(unittest.TestCase):
    def check_fragments(self, source, fragments, spans, prefix='', multiline=False):
        if multiline:
            audio = '**字幕/角色台词/旁白**：\n' + '\n'.join('  ' + prefix + 'A: ' + f for f in fragments)
            blocks = ['【单镜头1】3.0秒\n' + audio]
        else:
            blocks = [f'【单镜头{i}】3.0秒\n  **字幕/角色台词/旁白**：{prefix}A: {fragment}'
                      for i, fragment in enumerate(fragments, 1)]
        markdown = ('第1集｜测试\n## 第1组（目标00:00-00:15；实际' + str(3.0 * len(blocks)) +
                    '秒）\n' + '\n'.join(blocks) + '\n负面提示词：\n')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'storyboard.md'
            path.write_text(markdown, encoding='utf-8')
            errors = []
            _, entries, _ = CHECKER['parse_storyboards']([path], errors)
        unit = dict(id='U000001', audible=True, spoken_start=0, spoken_end=len(source),
                    speaker='A', episode='1', order=1)
        mapping = dict(schema_version=1, source_sha256='test', fragments=[
            dict(unit_id='U000001', shot_id=f'E001-G001-S{1 if multiline else i:03d}',
                 audio_index=i if multiline else 1, start=start, end=end)
            for i, (start, end) in enumerate(spans, 1)])
        CHECKER['check_mapping'](mapping, {'source': {'sha256': 'test'}}, [unit], entries, source, errors)
        return errors, entries

    def test_trailing_word_separator_survives_shot_cut(self):
        errors, entries = self.check_fragments('We need to leave now.', ['We need ', 'to leave now.'], [(0, 8), (8, 21)])
        self.assertEqual(errors, [])
        self.assertEqual(entries[0]['text'], 'We need ')

    def test_leading_source_separator_survives_after_one_wrapper_space(self):
        errors, entries = self.check_fragments('We need to leave now.', ['We need', ' to leave now.'], [(0, 7), (7, 21)])
        self.assertEqual(errors, [])
        self.assertEqual(entries[1]['text'], ' to leave now.')

    def test_bilingual_multiline_audio_keeps_exact_spaces(self):
        errors, _ = self.check_fragments('We need to leave now.', ['We need ', 'to leave now.'],
                                        [(0, 8), (8, 21)], prefix='英文主声轨（锁定）— ', multiline=True)
        self.assertEqual(errors, [])

    def test_chinese_without_boundary_spaces_still_passes(self):
        errors, _ = self.check_fragments('我们走。', ['我们', '走。'], [(0, 2), (2, 4)])
        self.assertEqual(errors, [])

    def test_internal_space_rewrite_is_rejected(self):
        errors, _ = self.check_fragments('We need to leave now.', ['We  need ', 'to leave now.'], [(0, 8), (8, 21)])
        self.assertIn('dialogue_mismatch', [e['code'] for e in errors])

    def test_missing_boundary_space_is_rejected(self):
        errors, _ = self.check_fragments('We need to leave now.', ['We need', 'to leave now.'], [(0, 8), (8, 21)])
        self.assertIn('dialogue_mismatch', [e['code'] for e in errors])

    def test_extra_trailing_space_is_rejected(self):
        errors, _ = self.check_fragments('我们走。', ['我们 ', '走。'], [(0, 2), (2, 4)])
        self.assertIn('dialogue_mismatch', [e['code'] for e in errors])

    def test_cli_repeated_english_source_passes_then_missing_space_fails(self):
        # The literal fixture contains two distinct occurrences of the same
        # source line: both must survive the builder -> ledger -> output chain.
        original = b'\xe7\xac\xac1\xe9\x9b\x86\r\nA: We need to leave now.\r\nA: We need to leave now.\r\n'
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            source = work / 'source.txt'
            source.write_bytes(original)
            built = BUILDER['build'](source, work / 'records')
            ledger_path = Path(built['ledger'])
            ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
            self.assertEqual([u['kind'] for u in ledger['units']], ['heading', 'dialogue', 'dialogue'])
            self.assertEqual([u['spoken_text'] for u in ledger['units'][1:]],
                             ['We need to leave now.', 'We need to leave now.'])
            # Classification review is explicit for this known three-line fixture.
            for unit in ledger['units']:
                unit['reviewed'] = True
            ledger_path.write_text(json.dumps(ledger, ensure_ascii=False), encoding='utf-8')
            fragments, blocks = [], []
            for occurrence, unit in enumerate(ledger['units'][1:]):
                start = unit['spoken_start']
                for local_index, (offset, end, spoken) in enumerate(
                        [(0, 8, 'We need '), (8, 21, 'to leave now.')], 1):
                    number = occurrence * 2 + local_index
                    fragments.append(dict(unit_id=unit['id'], start=start + offset, end=start + end,
                                          shot_id=f'E001-G001-S{number:03d}', audio_index=1))
                    blocks.append(f'【单镜头{number}】3.0秒\n**字幕/角色台词/旁白**：A: {spoken}')
            storyboard = work / 'storyboard.md'
            markdown = ('第1集｜英文重复台词\n## 第1组（目标00:00-00:15；实际12.0秒）\n' +
                        '\n'.join(blocks) + '\n负面提示词：\n')
            storyboard.write_text(markdown, encoding='utf-8')
            mapping = work / 'storyboard-map.json'
            mapping.write_text(json.dumps(dict(schema_version=1,
                source_sha256=ledger['source']['sha256'], fragments=fragments)), encoding='utf-8')
            report_path = work / 'report.json'
            argv = ['--ledger', str(ledger_path), '--storyboard', str(storyboard),
                    '--mapping', str(mapping), '--report', str(report_path)]
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                code = CHECKER['main'](argv)
            report = json.loads(report_path.read_text(encoding='utf-8'))
            self.assertEqual(code, 0, report)
            self.assertEqual(report['status'], 'pass')
            self.assertEqual(report['mode'], 'rendered_audio')
            self.assertEqual(report['audible_units'], 2)
            self.assertEqual(report['shot_count'], 4)
            self.assertTrue(report['scope']['whole_source'])

            # Omit just the first word-boundary space without touching either
            # source occurrence, the mapping, the speaker, or the shot ordering.
            storyboard.write_text(markdown.replace('A: We need \n', 'A: We need\n', 1), encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                code = CHECKER['main'](argv)
            report = json.loads(report_path.read_text(encoding='utf-8'))
            self.assertEqual(code, 1, report)
            self.assertEqual(report['status'], 'fail')
            self.assertEqual([e['code'] for e in report['errors']], ['dialogue_mismatch'])
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(Path(built['snapshot']).read_bytes(), original)


if __name__ == '__main__':
    unittest.main(verbosity=2)

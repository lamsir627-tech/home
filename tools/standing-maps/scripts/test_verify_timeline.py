"""Boundary tests for the independent strict group timeline gate."""

import contextlib
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import verify_timeline as checker


def group(durations=None, number=1, actual='30.0'):
    durations = durations or ['5.0'] * 6
    lines = [f'## 第{number}组（目标00:00-00:30；实际{actual}秒）']
    cursor = Decimal('0.0')
    for index, duration in enumerate(durations, 1):
        end = cursor + Decimal(duration)
        lines.extend([f'【单镜头{index}】{duration}秒', f'**时间轴**：{cursor}–{end}秒',
                      '**镜头描述**：人物接稳杯子。', '**字幕/角色台词/旁白**：无'])
        cursor = end
    lines.append('负面提示词：口型错配，道具瞬移。')
    return '\n'.join(lines)


class TimelineTests(unittest.TestCase):
    def check(self, text, target='30', state=None):
        return checker.validate_text(text, '<test>', Decimal(target), state)

    def codes(self, text):
        return {e['code'] for e in self.check(text)['errors']}

    def test_exact_thirty_seconds(self):
        result = self.check(group())
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['warnings'], [])
        self.assertEqual(result['groups'][0]['shots'], 6)

    def test_decimal_tenths_are_exact_not_float(self):
        durations = ['0.1', '4.9', '5.1', '4.9', '7.3', '7.7']
        self.assertEqual(self.check(group(durations))['errors'], [])

    def test_long_and_short_silent_shots_are_allowed(self):
        result = self.check(group(['6.0', '1.0', '5.0', '5.0', '5.0', '8.0']))
        self.assertEqual(result['errors'], [])

    def test_count_is_guidance_not_a_hard_gate(self):
        for durations in (['6.0'] * 5, ['2.0'] * 10 + ['10.0']):
            result = self.check(group(durations))
            self.assertEqual(result['errors'], [])
            self.assertEqual(result['warnings'][0]['code'], 'shot_count_guidance')

    def test_group_tail_is_not_exempt(self):
        self.assertIn('group_duration', self.codes(group(['5.0'] * 5, actual='25.0')))
        self.assertIn('timeline_end', self.codes(group(['5.0'] * 5, actual='25.0')))

    def test_actual_title_and_shot_sum_must_both_match(self):
        self.assertIn('group_duration', self.codes(group(actual='29.9')))
        self.assertIn('shot_sum', self.codes(group(['4.9'] + ['5.0'] * 5)))

    def test_no_initial_gap_or_offset(self):
        self.assertIn('timeline_start', self.codes(group().replace('0.0–5.0', '0.1–5.1')))

    def test_no_gap_or_overlap(self):
        for interval in ('5.1–10.1', '4.9–9.9'):
            self.assertIn('timeline_continuity', self.codes(group().replace('5.0–10.0', interval)))

    def test_interval_matches_declared_duration(self):
        self.assertIn('shot_duration', self.codes(group().replace('0.0–5.0', '0.0–4.0')))

    def test_missing_duplicate_and_misplaced_axis(self):
        line = '**时间轴**：0.0–5.0秒'
        self.assertIn('timeline_count', self.codes(group().replace(line, '')))
        self.assertIn('timeline_count', self.codes(group().replace(line, line + '\n' + line)))
        self.assertIn('timeline_placement', self.codes(group().replace(line, '\n' + line)))

    def test_orphan_axis_and_shot_are_rejected(self):
        self.assertIn('orphan_timeline', self.codes('**时间轴**：0.0–5.0秒\n' + group()))
        self.assertIn('orphan_shot', self.codes('【单镜头1】5.0秒\n' + group()))

    def test_malformed_and_nonfinite_axis(self):
        for axis in ('**时间轴**：NaN–5.0秒', '**时间轴**：0.0–Infinity秒',
                     '**时间轴**：-1.0–5.0秒', '**时间轴**：0.0至5.0',
                     '**时间轴**：0.0–0.0秒', '**时间轴**：5.0–4.0秒'):
            self.assertTrue(self.check(group().replace('**时间轴**：0.0–5.0秒', axis))['errors'])

    def test_malformed_shot_header_cannot_disappear(self):
        for header in ('【单镜头1】NaN秒', '【单镜头1】0.0秒', '【单镜头一】5.0秒',
                       '【单镜头1】-5.0秒', '【单镜头1】Infinity秒'):
            self.assertTrue(self.check(group().replace('【单镜头1】5.0秒', header))['errors'])

    def test_malformed_group_heading_cannot_disappear(self):
        for header in ('## 第1组', '## 第1组（实际NaN秒）', '## 第X组（实际30秒）'):
            self.assertIn('group_heading_format', self.codes(group().replace(group().splitlines()[0], header)))

    def test_shot_numbers_start_at_one_and_are_contiguous(self):
        for replacement in ('【单镜头0】', '【单镜头2】'):
            self.assertIn('shot_numbering', self.codes(group().replace('【单镜头1】', replacement)))
        self.assertIn('shot_numbering', self.codes(group().replace('【单镜头2】', '【单镜头1】')))

    def test_groups_can_start_at_selected_number_but_not_skip_or_repeat(self):
        self.assertEqual(self.check(group(number=3) + '\n' + group(number=4))['errors'], [])
        self.assertIn('group_numbering', self.codes(group() + '\n' + group(number=3)))
        self.assertIn('duplicate_group', self.codes(group() + '\n' + group()))

    def test_episode_boundaries_reset_groups_not_timeline_requirements(self):
        text = '第一集｜开场\n' + group(number=2) + '\n第2集｜续场\n' + group()
        self.assertEqual(self.check(text)['errors'], [])

    def test_multi_file_identity_is_shared(self):
        state = {}
        self.check('第一集｜开场\n' + group(), state=state)
        result = self.check('第1集｜开场\n' + group(), state=state)
        self.assertIn('duplicate_group', {e['code'] for e in result['errors']})

    def test_fenced_fake_headers_and_time_fields_fail(self):
        for fence in ('```', '~~~'):
            self.assertIn('no_groups', self.codes(fence + '\n' + group() + '\n' + fence))
            self.assertIn('fenced_timing_syntax', self.codes(group() + '\n' + fence + '\n【单镜头7】1.0秒\n' + fence))
            self.assertIn('fenced_timing_syntax', self.codes(group().replace('**时间轴**：0.0–5.0秒',
                                        fence + '\n**时间轴**：0.0–5.0秒\n' + fence)))

    def test_unclosed_fence_fails(self):
        self.assertIn('unclosed_fence', self.codes(group() + '\n```text\n尾注'))

    def test_negative_prompt_is_terminal_for_shots_and_axes(self):
        for suffix in ('【单镜头7】1.0秒', '**时间轴**：30.0–31.0秒'):
            self.assertIn('timing_after_negative', self.codes(group() + '\n' + suffix))

    def test_normalization_and_dash_variants(self):
        for separator in ('-', '–', '—'):
            candidate = '\ufeff' + group().replace('–', separator).replace('\n', '\r\n')
            self.assertEqual(self.check(candidate)['errors'], [])

    def test_explicit_alternative_group_target(self):
        self.assertEqual(self.check(group(['2.5'] * 6, actual='15.0'), target='15')['errors'], [])


class CLITests(unittest.TestCase):
    def invoke(self, args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                code = checker.main(args)
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue()

    def test_cli_reports_hash_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as root:
            source, report = Path(root) / 'source.md', Path(root) / 'report.json'
            raw = ('\ufeff' + group().replace('\n', '\r\n')).encode('utf-8')
            source.write_bytes(raw)
            self.assertEqual(self.invoke(['--storyboard', str(source), '--report', str(report)])[0], 0)
            data = json.loads(report.read_text(encoding='utf-8'))
            self.assertEqual(data['status'], 'passed')
            self.assertEqual(data['groups_checked'], 1)
            self.assertEqual(data['shots_checked'], 6)
            self.assertEqual(data['artifacts'][0]['sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual(source.read_bytes(), raw)

    def test_cli_alternative_target(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / 'source.md'
            source.write_text(group(['2.5'] * 6, actual='15.0'), encoding='utf-8')
            self.assertEqual(self.invoke(['--storyboard', str(source), '--group-seconds', '15'])[0], 0)
            self.assertEqual(self.invoke(['--storyboard', str(source)])[0], 1)

    def test_bad_target_and_report_overwrite_are_input_errors(self):
        for target in ('0', '-1', 'NaN', 'Infinity', 'bad'):
            self.assertEqual(self.invoke(['--storyboard', 'unused', '--group-seconds', target])[0], 2)
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / 'source.md'
            source.write_text(group(), encoding='utf-8')
            before = source.read_bytes()
            self.assertEqual(self.invoke(['--storyboard', str(source), '--report', str(source)])[0], 2)
            self.assertEqual(source.read_bytes(), before)

    def test_missing_or_non_utf8_input_is_error_not_content_failure(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / 'source.md'
            self.assertEqual(self.invoke(['--storyboard', str(source)])[0], 2)
            source.write_bytes(b'\xff')
            self.assertEqual(self.invoke(['--storyboard', str(source)])[0], 2)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""Tests for verify_scene_state.py (run with: python -B -m unittest test_verify_scene_state)."""

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location('verify_scene_state', HERE / 'verify_scene_state.py')
vss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vss)

LIN_START = '林岚站在书桌外沿，身体朝向落地窗，左手空着，右手握着手机'
LIN_DOOR = '林岚站在入户门内一步，身体朝向落地窗，左手空着，右手握着手机'
ZHOU = '周衡站在落地窗前，身体朝向书桌'
MEI = '小美位于便利店门口'

LEDGER = {
    'schema_version': 1,
    'locations': {
        'L01': {'name': '林家客厅',
                'slots': {'P1': '入户门内一步', 'P2': '书桌外沿', 'P3': '落地窗前'},
                'cameras': {'C1': {'desc': '入户门侧朝落地窗', 'screen': {'P2': '左', 'P3': '右'}},
                            'C2': {'desc': '落地窗侧朝入户门', 'screen': {'P3': '左', 'P1': '右', 'P2': '右'}}}},
        'L02': {'name': '街道', 'slots': {'Q1': '便利店门口'}},
    },
    'instances': {
        'I01': {'location': 'L01', 'label': '当晚争执', 'segments': [
            {'id': 'I01-A', 'group': 'E001-G001', 'entry_from': None, 'entry_basis': 'source:U000003',
             'entry': {'林岚': {'slot': 'P2', 'posture': '站在', 'facing': '落地窗', 'left_hand': '空着', 'right_hand': '握着手机'},
                       '周衡': {'slot': 'P3', 'posture': '站在', 'facing': '书桌'}},
             'changes': [{'shot': 'E001-G001-S002', 'who': '林岚', 'field': 'slot', 'from': 'P2', 'to': 'P1',
                          'basis': 'source:U000010'}]},
            {'id': 'I01-B', 'group': 'E001-G003', 'entry_from': 'I01-A',
             'shots': {'E001-G003-S001': {'camera': 'C2'}}},
        ]},
        'I02': {'location': 'L02', 'label': '同一时刻街道', 'segments': [
            {'id': 'I02-A', 'group': 'E001-G002', 'entry_from': None, 'entry_basis': 'source:U000020',
             'entry': {'小美': {'slot': 'Q1'}}},
        ]},
    },
}


def group(number, scene, shots):
    body = [f'## 第{number}组（目标00:00-00:30；实际30.0秒）', '',
            '- **生成任务**：呈现对峙', f'- **场景与环境状态**：{scene}', '- **分段脚本**：', '']
    for index, text in enumerate(shots, 1):
        body += [f'  【单镜头{index}】15.0秒', '  **时间轴**：0.0–15.0秒', '  **镜头描述**：',
                 f'  - **画面简介**：{text}', '  **字幕/角色台词/旁白**：无', '']
    return '\n'.join(body + ['负面提示词：人物瞬移', ''])


def storyboard(g1_scene=None, g1_s2='林岚走到入户门内一步停住', g3_scene=None,
               g3_s1='周衡在画面左侧，林岚位于画面右侧', extra=''):
    g1_scene = g1_scene or f'客厅夜晚，{LIN_START}；{ZHOU}。'
    g3_scene = g3_scene or f'回到客厅，{LIN_DOOR}；{ZHOU}。'
    return '\n'.join(['第1集｜客厅对峙｜9:16竖屏｜30秒一组｜写实短剧质感', '',
                      group(1, g1_scene, ['林岚看向周衡', g1_s2]),
                      group(2, f'街道，{MEI}。', ['小美等人', '小美看手机']),
                      group(3, g3_scene, [g3_s1, '周衡开口']), extra])


class SceneStateTests(unittest.TestCase):
    def run_tool(self, ledger=None, md=None, extra_args=()):
        with tempfile.TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / 'scene-state.json'
            ledger_path.write_text(json.dumps(ledger or LEDGER, ensure_ascii=False), encoding='utf-8')
            args = ['--ledger', str(ledger_path)]
            if md is not False:
                md_path = Path(tmp) / 'E001.md'
                md_path.write_text(md if md is not None else storyboard(), encoding='utf-8')
                args += ['--storyboard', str(md_path)]
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = vss.main(args + list(extra_args))
            text = out.getvalue()
        report = json.loads(text) if text.lstrip().startswith('{') else None
        return code, report, text

    def codes(self, report):
        return {e['code'] for e in report['errors']}

    def ledger(self):
        return copy.deepcopy(LEDGER)

    def test_valid_nonadjacent_return_passes(self):
        code, report, _ = self.run_tool()
        self.assertEqual(code, 0, report['errors'])
        kinds = {s['id']: s['classification'] for s in report['segments']}
        self.assertEqual(kinds['I01-B'], 'nonadjacent_return')

    def test_ledger_only_mode(self):
        code, report, _ = self.run_tool(md=False)
        self.assertEqual(code, 0, report['errors'])

    def test_return_must_consume_latest_exit_of_same_instance(self):
        data = self.ledger()
        data['instances']['I01']['segments'][1]['entry_from'] = None
        code, report, _ = self.run_tool(data)
        self.assertEqual(code, 1)
        self.assertIn('entry_from_not_latest', self.codes(report))

    def test_written_entry_reset_to_original_blocking_fails(self):
        data = self.ledger()
        data['instances']['I01']['segments'][1]['entry'] = copy.deepcopy(data['instances']['I01']['segments'][0]['entry'])
        code, report, _ = self.run_tool(data)
        self.assertEqual(code, 1)
        self.assertIn('entry_mismatch', self.codes(report))

    def test_markdown_return_using_original_position_fails(self):
        code, report, _ = self.run_tool(md=storyboard(g3_scene=f'回到客厅，{LIN_START}；{ZHOU}。'))
        self.assertEqual(code, 1)
        self.assertIn('entry_text_missing', self.codes(report))

    def test_offscreen_change_requires_evidence(self):
        data = self.ledger()
        data['instances']['I01']['segments'][1]['offscreen_changes'] = [
            {'who': '周衡', 'field': 'facing', 'from': '书桌', 'to': '入户门', 'basis': 'design:顺手'}]
        code, report, _ = self.run_tool(data)
        self.assertIn('offscreen_basis', self.codes(report))

    def test_evidenced_offscreen_change_updates_derived_entry(self):
        data = self.ledger()
        data['instances']['I01']['segments'][1]['offscreen_changes'] = [
            {'who': '周衡', 'field': 'facing', 'from': '书桌', 'to': '入户门', 'basis': 'source:U000030'}]
        code, report, _ = self.run_tool(data)
        self.assertIn('entry_text_missing', self.codes(report))
        md = storyboard(g3_scene=f'回到客厅，{LIN_DOOR}；周衡站在落地窗前，身体朝向入户门。')
        code, report, _ = self.run_tool(data, md)
        self.assertEqual(code, 0, report['errors'])

    def test_change_from_must_match_current_state(self):
        data = self.ledger()
        data['instances']['I01']['segments'][0]['changes'][0]['from'] = 'P3'
        code, report, _ = self.run_tool(data)
        self.assertIn('change_from_mismatch', self.codes(report))

    def test_unknown_slot_fails(self):
        data = self.ledger()
        data['instances']['I01']['segments'][0]['changes'][0]['to'] = 'P9'
        code, report, _ = self.run_tool(data)
        self.assertIn('unknown_slot', self.codes(report))

    def test_change_result_must_be_written_in_carrying_shot(self):
        code, report, _ = self.run_tool(md=storyboard(g1_s2='林岚往前走了几步'))
        self.assertIn('change_result_missing', self.codes(report))

    def test_screen_side_mismatch_detected(self):
        code, report, _ = self.run_tool(md=storyboard(g3_s1='周衡在画面右侧，林岚位于画面左侧'))
        self.assertEqual(code, 1)
        self.assertIn('screen_side_mismatch', self.codes(report))

    def test_written_exit_must_match_derivation(self):
        data = self.ledger()
        data['instances']['I01']['segments'][0]['exit'] = copy.deepcopy(data['instances']['I01']['segments'][0]['entry'])
        code, report, _ = self.run_tool(data)
        self.assertIn('exit_mismatch', self.codes(report))

    def test_require_coverage(self):
        md = storyboard(extra=group(4, '无人空镜', ['窗外夜色']))
        code, report, _ = self.run_tool(md=md)
        self.assertEqual(code, 0, report['errors'])
        code, report, _ = self.run_tool(md=md, extra_args=['--require-coverage'])
        self.assertIn('group_without_state', self.codes(report))
        data = self.ledger()
        data['instances']['I03'] = {'location': 'L02', 'segments': [
            {'id': 'I03-A', 'group': 'E001-G004', 'entry_from': None, 'entry_basis': 'source:U000040', 'entry': {}}]}
        code, report, _ = self.run_tool(data, md, ['--require-coverage'])
        self.assertEqual(code, 0, report['errors'])
        self.assertIn('entry_empty', {w['code'] for w in report['warnings']})

    def test_render_return_card(self):
        code, _, text = self.run_tool(md=False, extra_args=['--render', 'E001-G003'])
        self.assertEqual(code, 0)
        self.assertIn('隔组回场', text)
        self.assertIn(LIN_DOOR, text)
        self.assertIn('画面左：周衡', text)
        self.assertIn('画面右：林岚', text)

    def test_bad_json_is_input_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.json'
            path.write_text('{not json', encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(vss.main(['--ledger', str(path)]), 2)


if __name__ == '__main__':
    unittest.main()

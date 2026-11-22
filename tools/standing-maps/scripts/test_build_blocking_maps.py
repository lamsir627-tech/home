"""Tests for build_blocking_maps.py (run with: python -B -m unittest test_build_blocking_maps)."""
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
spec = importlib.util.spec_from_file_location('build_blocking_maps', HERE / 'build_blocking_maps.py')
bbm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bbm)

LEDGER = {
    'schema_version': 1,
    'cast': {'林岚': {'look': '米白衬衣、灰蓝长裤'}, '周衡': {'look': '深蓝西装'}, '小美': {'look': '红色外套'},
             '店员': {'look': '黑色围裙'}},
    'locations': {
        'L1': {'name': '林家客厅',
               'plan': {'orientation': '图上方为落地窗，下方为入户门，左为书桌，右为沙发',
                        'fixed': ['书桌在左侧中部', '沙发靠右墙']},
               'slots': {'P1': {'label': '入户门内一步', 'plan': '图下方正中'},
                         'P2': {'label': '书桌外沿', 'plan': '图左侧中部'},
                         'P3': {'label': '落地窗前', 'plan': '图上方偏右'}}},
        'L2': {'name': '便利店', 'plan': {'orientation': '图上方为货架，下方为玻璃门'},
               'slots': {'Q1': {'label': '收银台后', 'plan': '图上方偏左'}, 'Q2': '门口'}},
    },
    'instances': {
        'I1': {'location': 'L1', 'segments': [
            {'id': 'I1-A', 'group': 'E001-G001', 'entry_from': None, 'entry_basis': 'source:U1',
             'entry': {'林岚': {'slot': 'P1', 'posture': '站在', 'facing': '落地窗'},
                       '周衡': {'slot': 'P3', 'posture': '站在', 'facing': '入户门'}}},
            {'id': 'I1-B', 'group': 'E001-G002', 'entry_from': 'I1-A',
             'changes': [{'shot': 'E001-G002-S002', 'who': '周衡', 'field': 'slot', 'from': 'P3', 'to': 'P2',
                          'basis': 'source:U2'}]},
            {'id': 'I1-C', 'group': 'E001-G003', 'entry_from': 'I1-B'},
            {'id': 'I1-D', 'group': 'E001-G005', 'entry_from': 'I1-C'},
        ]},
        'I2': {'location': 'L2', 'segments': [
            {'id': 'I2-A', 'group': 'E001-G004', 'entry_from': None, 'entry_basis': 'source:U3', 'voice_only': [],
             'entry': {'店员': {'slot': 'Q1', 'posture': '站在', 'facing': '门口'}},
             'changes': [{'shot': 'E001-G004-S002', 'who': '小美', 'field': 'enter',
                          'to': {'slot': 'Q2', 'posture': '站在', 'facing': '收银台'}, 'basis': 'source:U4'}]},
        ]},
    },
}


def group(number, subjects):
    return '\n'.join([f'## 第{number}组（目标00:00-00:30；实际30.0秒）', '', f'- **主要主体**：{subjects}',
                      '- **分段脚本**：', '', '  【单镜头1】30.0秒', '  **时间轴**：0.0–30.0秒', '  **镜头描述**：',
                      '  - **画面简介**：中景，平视固定拍摄；人物对话。', '  **字幕/角色台词/旁白**：无', '',
                      '负面提示词：人物瞬移', ''])


def storyboard(g4='店员（黑色围裙），小美（红色外套），便利店（夜）', extra=''):
    return '\n'.join(['第1集｜测试｜9:16竖屏｜30秒一组｜写实短剧质感', '',
                      group(1, '林岚（米白衬衣），周衡（深蓝西装），林家客厅（夜）'),
                      group(2, '林岚（米白衬衣），周衡（深蓝西装），林家客厅（夜）'),
                      group(3, '林岚（米白衬衣），周衡（深蓝西装），林家客厅（夜）'),
                      group(4, g4),
                      group(5, '林岚（米白衬衣），周衡（深蓝西装），林家客厅（夜）'), extra])


class BlockingMapTests(unittest.TestCase):
    def run_tool(self, ledger=None, md=None, extra=()):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / 'scene-state.json').write_text(json.dumps(ledger or LEDGER, ensure_ascii=False), encoding='utf-8')
            args = ['--ledger', str(work / 'scene-state.json'), '--json', str(work / 'maps.json'),
                    '--markdown', str(work / 'maps.md'), '--report', str(work / 'report.json')]
            if md is not False:
                (work / 'E001.md').write_text(md if md is not None else storyboard(), encoding='utf-8')
                args += ['--storyboard', str(work / 'E001.md')]
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = bbm.main(args + list(extra))
            out.getvalue().encode('ascii')
            if code == 2:
                return code, None, None, None
            report = json.loads((work / 'report.json').read_text(encoding='utf-8'))
            maps = json.loads((work / 'maps.json').read_text(encoding='utf-8'))
            markdown = (work / 'maps.md').read_text(encoding='utf-8')
        return code, report, maps, markdown

    def index(self, maps):
        return {gid: [r['map'] for r in rows] for gid, rows in maps['group_index'].items()}

    def test_reuse_new_and_nonadjacent(self):
        code, report, maps, _ = self.run_tool()
        self.assertEqual(code, 0, report['errors'])
        idx = self.index(maps)
        self.assertEqual(idx['E001-G001'], ['MAP-E001-G001'])
        self.assertEqual(idx['E001-G002'], ['MAP-E001-G001'])      # unchanged start -> reuse
        self.assertEqual(idx['E001-G003'], ['MAP-E001-G003'])      # 周衡 moved in G2 -> new map
        self.assertEqual(idx['E001-G005'], ['MAP-E001-G005'])      # same start as G3 but not adjacent
        self.assertEqual(maps['maps']['MAP-E001-G001']['groups'], ['E001-G001', 'E001-G002'])

    def test_prompt_lists_every_character_with_plan_and_later_entry(self):
        _, _, maps, markdown = self.run_tool()
        prompt = maps['maps']['MAP-E001-G001']['prompt']
        self.assertIn('本图共2个人物', prompt)
        self.assertIn('林岚（米白衬衣、灰蓝长裤）：站在入户门内一步——图下方正中；身体朝向落地窗', prompt)
        self.assertIn('方位：图上方为落地窗', prompt)
        store = maps['maps']['MAP-E001-G004']['prompt']
        self.assertIn('本图共2个人物', store)
        self.assertIn('小美（红色外套）（本段第2镜才入场', store)
        self.assertIn('| E001-G002 | MAP-E001-G001 | 沿用 |', markdown)

    def test_label_only_slot_warns(self):
        _, report, _, _ = self.run_tool()
        self.assertIn('slot_plan_missing', {w['code'] for w in report['warnings']})

    def test_cast_missing_from_map_and_voice_only(self):
        md = storyboard(g4='店员（黑色围裙），小美（红色外套），林岚（电话声），便利店（夜）')
        code, report, _, _ = self.run_tool(md=md)
        self.assertEqual(code, 1)
        self.assertIn('cast_missing_from_map', {e['code'] for e in report['errors']})
        data = copy.deepcopy(LEDGER)
        data['instances']['I2']['segments'][0]['voice_only'] = ['林岚']
        code, report, _, _ = self.run_tool(data, md)
        self.assertEqual(code, 0, report['errors'])

    def test_group_without_map(self):
        code, report, _, _ = self.run_tool(md=storyboard(extra=group(6, '林岚（米白衬衣）')))
        self.assertIn('group_without_map', {e['code'] for e in report['errors']})

    def test_orientation_required(self):
        data = copy.deepcopy(LEDGER)
        del data['locations']['L2']['plan']
        code, report, _, _ = self.run_tool(data)
        self.assertIn('plan_orientation_missing', {e['code'] for e in report['errors']})

    def test_two_scene_segments_in_one_group(self):
        data = copy.deepcopy(LEDGER)
        data['instances']['I2']['segments'].append(
            {'id': 'I2-B', 'group': 'E001-G005', 'entry_from': 'I2-A', 'entry_shot': 'E001-G005-S001'})
        data['instances']['I1']['segments'][3]['entry_shot'] = 'E001-G005-S001'
        data['instances']['I2']['segments'][1]['entry_shot'] = None
        md = storyboard()
        code, report, maps, _ = self.run_tool(data, md)
        self.assertEqual(len(self.index(maps)['E001-G005']), 2)

    def test_ledger_only_mode_and_diagram_style(self):
        code, report, maps, _ = self.run_tool(md=False, extra=['--style', 'diagram'])
        self.assertEqual(code, 0, report['errors'])
        self.assertIn('平面站位示意图', maps['maps']['MAP-E001-G001']['prompt'])

    def test_explicit_scene_view_uses_registered_camera_without_top_down_constraints(self):
        data = copy.deepcopy(LEDGER)
        for location in data['locations'].values():
            location['cameras'] = {'C1': {'desc': '门内南侧朝北，平视中全景', 'screen': {}}}
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                code, report, maps, markdown = self.run_tool(
                    data, md=False, extra=['--aspect', '16:9', '--view', 'scene', '--camera', 'C1'])
        except SystemExit:
            self.fail('Compiler rejects the requested actual-scene camera mode.')
        self.assertEqual(code, 0, report['errors'])
        prompt = maps['maps']['MAP-E001-G001']['prompt']
        self.assertIn('画幅16:9', prompt)
        self.assertIn('门内南侧朝北，平视中全景', prompt)
        self.assertIn('写实实际场景', markdown)
        for forbidden in ('正俯视', '90°', '透视斜视或侧视角度', '图下方正中'):
            self.assertNotIn(forbidden, prompt)

    def test_scene_view_does_not_invent_an_unregistered_camera(self):
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                code, report, maps, _ = self.run_tool(
                    md=False, extra=['--view', 'scene', '--camera', 'C1'])
        except SystemExit:
            self.fail('Compiler rejects scene mode before checking the ledger camera.')
        self.assertEqual(code, 1)
        self.assertIn('scene_camera_missing', {e['code'] for e in report['errors']})
        self.assertFalse(maps['maps'])

    def test_hand_and_support_changes_require_distinct_start_maps(self):
        cases = [('left_hand', '撑住红毯', '空着'),
                 ('right_hand', '空着', '抓住周衡衣角'),
                 ('contact', '侧髋压在红毯上', '侧髋靠在床沿')]
        for field, before, after in cases:
            with self.subTest(field=field):
                data = copy.deepcopy(LEDGER)
                first = data['instances']['I1']['segments'][0]
                first['entry']['林岚'][field] = before
                first['changes'] = [{'shot': 'E001-G001-S002', 'who': '林岚', 'field': field,
                                     'from': before, 'to': after, 'basis': 'source:U5'}]
                code, report, maps, _ = self.run_tool(data, md=False)
                self.assertEqual(code, 0, report['errors'])
                self.assertNotEqual(self.index(maps)['E001-G001'], self.index(maps)['E001-G002'])
                self.assertIn(after, maps['maps']['MAP-E001-G002']['prompt'])

    def test_prompt_preserves_registered_hands_holding_and_support_only(self):
        data = copy.deepcopy(LEDGER)
        data['instances']['I1']['segments'][0]['entry']['林岚'].update(
            left_hand='握着肚兜上缘', right_hand='撑住红毯', contact='侧髋与伤腿压在红毯上')
        code, report, maps, _ = self.run_tool(data, md=False)
        self.assertEqual(code, 0, report['errors'])
        prompt = maps['maps']['MAP-E001-G001']['prompt']
        self.assertIn('左手握着肚兜上缘', prompt)
        self.assertIn('右手撑住红毯', prompt)
        self.assertIn('侧髋与伤腿压在红毯上', prompt)
        zhou = next(line for line in prompt.splitlines() if '周衡（' in line)
        self.assertNotIn('左手', zhou)
        self.assertNotIn('右手', zhou)

    def test_later_entry_hand_state_is_not_reused_as_another_entry_state(self):
        data = copy.deepcopy(LEDGER)
        for number, segment in enumerate(data['instances']['I1']['segments'][:2], 1):
            segment['changes'] = [
                {'shot': f'E001-G00{number}-S002', 'who': '小美', 'field': 'enter',
                 'to': {'slot': 'P2', 'posture': '站在', 'left_hand': '握着手机' if number == 1 else '空着'},
                 'basis': 'source:U6'},
                {'shot': f'E001-G00{number}-S003', 'who': '小美', 'field': 'leave', 'basis': 'source:U7'}]
        code, report, maps, _ = self.run_tool(data, md=False)
        self.assertEqual(code, 0, report['errors'])
        self.assertNotEqual(self.index(maps)['E001-G001'], self.index(maps)['E001-G002'])
        self.assertIn('左手空着', maps['maps']['MAP-E001-G002']['prompt'])

    def test_gaze_only_change_still_reuses_map_and_default_view_is_unchanged(self):
        data = copy.deepcopy(LEDGER)
        first = data['instances']['I1']['segments'][0]
        first['entry']['林岚']['gaze'] = '周衡的脸'
        first['changes'] = [{'shot': 'E001-G001-S002', 'who': '林岚', 'field': 'gaze',
                             'from': '周衡的脸', 'to': '桌面', 'basis': 'source:U8'}]
        code, report, maps, _ = self.run_tool(data, md=False)
        self.assertEqual(code, 0, report['errors'])
        self.assertEqual(self.index(maps)['E001-G001'], self.index(maps)['E001-G002'])
        prompt = maps['maps']['MAP-E001-G001']['prompt']
        self.assertIn('画幅1:1，正上方90°垂直俯视', prompt)
        self.assertIn('透视斜视或侧视角度', prompt)

    def test_registered_look_and_asset_version_change_the_map_signature(self):
        ledger = bbm.Ledger(copy.deepcopy(LEDGER)).validate()
        cast = copy.deepcopy(LEDGER['cast'])
        cast['林岚']['asset_id'] = 'CHR-001/CST-A-v1'
        for field, value in [('look', '红金喜服'), ('asset_id', 'CHR-001/CST-A-v2')]:
            with self.subTest(field=field):
                changed = copy.deepcopy(cast)
                changed['林岚'][field] = value
                try:
                    before = bbm.signature(ledger.segments[0], cast)
                    after = bbm.signature(ledger.segments[0], changed)
                except TypeError:
                    self.fail('Map signature cannot account for registered character asset versions.')
                self.assertNotEqual(before, after)

    def test_bad_json_is_input_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.json'
            path.write_text('{oops', encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(bbm.main(['--ledger', str(path)]), 2)


if __name__ == '__main__':
    unittest.main()

"""Tests for verify_emphasis_shots.py (run with: python -B -m unittest test_verify_emphasis_shots)."""
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
spec = importlib.util.spec_from_file_location('verify_emphasis_shots', HERE / 'verify_emphasis_shots.py')
ves = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ves)


def shot(number, seconds, desc, audio='无'):
    return '\n'.join([f'  【单镜头{number}】{seconds}秒', f'  **时间轴**：0.0–{seconds}秒', '  **镜头描述**：',
                      f'  - **画面简介**：{desc}', '  **角色情绪**：林岚：克制', '  **表演动作**：林岚：停住',
                      '  **音效/现场声**：脚步声', f'  **字幕/角色台词/旁白**：{audio}', ''])


def group(number, subjects, shots):
    return '\n'.join([f'## 第{number}组（目标00:00-00:30；实际30.0秒）', '', '- **生成任务**：呈现',
                      f'- **主要主体**：{subjects}', '- **分段脚本**：', ''] + shots + ['负面提示词：人物瞬移', ''])


G1_SHOTS = [shot(1, '3.0', '特写，平视，固定机位缓推，焦点落在林岚的眼睛；宴会厅门口逆光，林岚抬眼看向厅内'),
            shot(2, '27.0', '中景，平视固定拍摄，焦点在林岚；林岚走入厅内', '林岚：我来了。')]
G2_SHOTS = [shot(1, '20.0', '中景，平视固定拍摄，焦点在周衡；周衡逼近林岚', '周衡：你还敢来？'),
            shot(2, '2.0', '大特写，平视侧前方固定拍摄，升格慢动作，焦点落在林岚左脸；周衡的右手掌接触林岚左颊'),
            shot(3, '8.0', '特写，平视固定拍摄，焦点在林岚；林岚慢慢转回头看向周衡', '周衡：滚出去。')]


def storyboard(g1=None, g2=None, g1_subjects='林岚（黑色礼服），宴会厅（夜）', g2_subjects='林岚（黑色礼服），周衡（深灰西装）'):
    return '\n'.join(['第1集｜宴会对峙｜9:16竖屏｜30秒一组｜写实短剧质感', '',
                      group(1, g1_subjects, g1 or G1_SHOTS), group(2, g2_subjects, g2 or G2_SHOTS)])


PLAN = {
    'schema_version': 1,
    'main_characters': ['林岚', '周衡'],
    'introduced_before_scope': [],
    'triggers': [
        {'id': 'T01', 'kind': 'first_appearance', 'character': '林岚', 'group': 'E001-G001',
         'basis': 'source:U000003', 'shots': ['E001-G001-S001']},
        {'id': 'T02', 'kind': 'first_appearance', 'character': '周衡', 'group': 'E001-G002',
         'basis': 'source:U000010', 'shots': ['E001-G002-S001'], },
        {'id': 'T03', 'kind': 'conflict', 'group': 'E001-G002', 'basis': 'source:U000012', 'peak': '掌掴',
         'shots': ['E001-G002-S002', 'E001-G002-S003']},
    ],
}


class EmphasisTests(unittest.TestCase):
    def run_tool(self, plan=None, md=None):
        with tempfile.TemporaryDirectory() as tmp:
            plan_path, md_path = Path(tmp) / 'emphasis-plan.json', Path(tmp) / 'E001.md'
            plan_path.write_text(json.dumps(PLAN if plan is None else plan, ensure_ascii=False), encoding='utf-8')
            md_path.write_text(storyboard() if md is None else md, encoding='utf-8')
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = ves.main(['--plan', str(plan_path), '--storyboard', str(md_path)])
        text = out.getvalue()
        text.encode('ascii')
        return code, json.loads(text)

    def codes(self, report, key='errors'):
        return {e['code'] for e in report[key]}

    def plan(self):
        return copy.deepcopy(PLAN)

    def zhou_face(self):
        # Zhou's own first appearance shot must show his face.
        g2 = list(G2_SHOTS)
        g2[0] = shot(1, '20.0', '近景，低角度仰拍，固定机位缓推，焦点在周衡；周衡跨入宴会厅逼近林岚', '周衡：你还敢来？')
        return g2

    def test_valid_plan_passes(self):
        code, report = self.run_tool(md=storyboard(g2=self.zhou_face()))
        self.assertEqual(code, 0, report['errors'])

    def test_main_character_needs_first_appearance(self):
        plan = self.plan()
        del plan['triggers'][1]
        code, report = self.run_tool(plan, storyboard(g2=self.zhou_face()))
        self.assertIn('missing_first_appearance', self.codes(report))
        plan['introduced_before_scope'] = ['周衡']
        code, report = self.run_tool(plan, storyboard(g2=self.zhou_face()))
        self.assertEqual(code, 0, report['errors'])

    def test_registered_shot_needs_rendering_technique(self):
        code, report = self.run_tool()   # G2-S001 is a plain 中景
        self.assertIn('no_rendering_technique', self.codes(report))

    def test_first_appearance_needs_readable_face(self):
        g1 = list(G1_SHOTS)
        g1[0] = shot(1, '3.0', '全景，低角度仰拍，固定机位，焦点在林岚；林岚从门口走入')
        code, report = self.run_tool(md=storyboard(g1=g1, g2=self.zhou_face()))
        self.assertIn('first_appearance_face', self.codes(report))

    def test_conflict_count_bounds(self):
        plan = self.plan()
        plan['triggers'][2]['shots'] = ['E001-G002-S001', 'E001-G002-S002', 'E001-G002-S003', 'E001-G002-S004']
        code, report = self.run_tool(plan, storyboard(g2=self.zhou_face()))
        self.assertIn('trigger_count', self.codes(report))

    def test_group_cap_counts_all_triggers(self):
        plan = self.plan()
        plan['triggers'][1]['shots'] = ['E001-G002-S001', 'E001-G002-S003']
        plan['triggers'][2]['shots'] = ['E001-G002-S002', 'E001-G002-S001']
        g2 = self.zhou_face() + [shot(4, '0.0', '特写，固定机位，焦点在周衡；周衡收手')]
        code, report = self.run_tool(plan, storyboard(g2=g2))
        self.assertNotIn('group_rendering_cap', self.codes(report))
        plan['triggers'][2]['shots'] = ['E001-G002-S002', 'E001-G002-S004']
        code, report = self.run_tool(plan, storyboard(g2=g2))
        self.assertIn('group_rendering_cap', self.codes(report))

    def test_slowmo_cap(self):
        g2 = self.zhou_face()
        g2[2] = shot(3, '8.0', '特写，平视固定拍摄，升格慢动作，焦点在林岚；林岚慢慢转回头')
        code, report = self.run_tool(md=storyboard(g2=g2))
        self.assertIn('group_slowmo_cap', self.codes(report))

    def test_constraint_allows_empty_trigger_but_reason_required(self):
        plan = self.plan()
        plan['triggers'][2]['shots'] = []
        code, report = self.run_tool(plan, storyboard(g2=self.zhou_face()))
        self.assertIn('trigger_empty', self.codes(report))
        plan['triggers'][2]['constraint'] = '本组口播已满'
        code, report = self.run_tool(plan, storyboard(g2=self.zhou_face()))
        self.assertIn('trigger_constrained', self.codes(report, 'warnings'))
        self.assertIn('unregistered_slowmo', self.codes(report, 'warnings'))

    def test_slowmo_dialogue_warning(self):
        g2 = self.zhou_face()
        g2[1] = shot(2, '2.0', '大特写，升格慢动作，焦点落在林岚左脸；周衡的右手掌接触林岚左颊', '周衡：滚。')
        code, report = self.run_tool(md=storyboard(g2=g2))
        self.assertIn('slowmo_dialogue', self.codes(report, 'warnings'))

    def test_possible_earlier_appearance_warning(self):
        code, report = self.run_tool(md=storyboard(g2=self.zhou_face(), g1_subjects='林岚（黑色礼服），周衡（深灰西装）'))
        self.assertIn('possible_earlier_appearance', self.codes(report, 'warnings'))

    def test_bad_plan_is_input_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'plan.json'
            path.write_text('[]', encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(ves.main(['--plan', str(path)]), 2)


if __name__ == '__main__':
    unittest.main()

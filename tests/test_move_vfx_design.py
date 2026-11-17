"""Method delivery contracts, not automatic aesthetic or video evaluation."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w

METHOD = 'references/move-vfx-design.md'
OWNERS = ('action', 'vfx', 'camera', 'compile', 'validate')


class MoveVfxDesign(unittest.TestCase):
    def test_method_reaches_real_context_without_keyword_dependency(self):
        task = {'mode': 'prompt'}
        p = w.init({'sources': [{'id': 'S1', 'text': '甲挡住乙，双方退开。'}],
                    'events': [{'id': 'E1', 'source_ids': ['S1'],
                                'body': '甲挡住乙，双方退开。', 'start': 0, 'end': 3,
                                'requires': ['action', 'vfx']}]}, task)
        for module in OWNERS:
            with self.subTest(module=module):
                ctx = w.context(task, module, p)
                rules = {r['path']: r['text'] for r in ctx['rules']}
                self.assertTrue(METHOD in rules, module + " missing method")
                self.assertEqual(rules[METHOD], (ROOT / METHOD).read_text(encoding='utf-8'))
                self.assertEqual(ctx['receipt']['rules_hash'], w.fingerprint(ctx['rules']))

    def test_method_has_construction_handoff_fidelity_and_negative_examples(self):
        text = (ROOT / METHOD).read_text(encoding='utf-8')
        for cue in ['视觉身份', '内部层次', '人物驱动', '展开与攻击', '碰撞变化', '残留与承接',
                    'design', 'event_id', '提出需求不等于替对方定方案', '编译保真',
                    'requirement_reviews', '不足稿', '合格方向', '万剑', '旋枪', '护层',
                    '不是固定六段', '0.5秒', '未实测']:
            self.assertIn(cue, text)

    def test_entrypoints_and_owned_sections_reference_method(self):
        paths = ['SKILL.md', 'references/design-boundaries.md',
                 'references/vfx-techniques.md', 'references/prompt-backstage-checks.md']
        paths += [f'references/modules/{m}.md' for m in OWNERS]
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue('move-vfx-design.md' in (ROOT / path).read_text(encoding='utf-8'), path)

    def test_template_not_mutated_by_design_checks(self):
        text = (ROOT / 'references/video-prompt-template.txt').read_text(encoding='utf-8')
        for cue in ['表现力复核', '完成检查', '动态元素复核', 'requirement_reviews']:
            self.assertNotIn(cue, text)

    def test_actual_handoff_preserves_concrete_design_for_downstream(self):
        task = {'mode': 'prompt'}
        p = w.init({'sources': [{'id': 'S1', 'text': '甲挥剑，剑群撞上护幕，被挡住。'}],
                    'events': [{'id': 'E1', 'source_ids': ['S1'], 'start': 0, 'end': 4,
                                'body': '甲挥剑，剑群撞上护幕，被挡住。',
                                'requires': ['action', 'vfx']}]}, task)
        ctx = w.context(task, 'source', p)
        p = w.submit(p, 'source', {
            'checked_event_ids': ['E1'],
            'source_coverage': {u['id']: {'event_ids': ['E1'],
                                        'reason': '夹具固定能力与阻挡结果，测试文字传递而非模型创作'}
                                for u in ctx['source_units']}}, ctx['receipt'])
        designs = {
            'action': '甲横引右剑，腕部转向时剑锋由横扫转为前指；乙维持护幕，剑群受阻。',
            'vfx': '剑列展开成扇面，扇缘先折入中轴，数股错层并进；首股碎成薄片，后股继续压幕，幕未破。',
            'camera': '斜侧关系景显示扇面与两人，沿剑锋方向切近接点，保留后股推进及护幕完整。',
        }
        while p['workflow']['plan']['steps'][p['workflow']['cursor']]['module'] != 'compile':
            module = p['workflow']['plan']['steps'][p['workflow']['cursor']]['module']
            ctx = w.context(task, module, p)
            if module in ('vfx', 'camera'):
                upstream = {r['module']: r['payload'] for r in ctx['upstream']}
                self.assertEqual(upstream['action']['design']['E1'], designs['action'])
            if module == 'camera':
                self.assertEqual(upstream['vfx']['design']['E1'], designs['vfx'])
            p = w.submit(p, module, {'design': {
                e['id']: designs.get(module, '夹具其他专业延续既定事件，不另改结果。')
                for e in ctx['events']}}, ctx['receipt'])
        ctx = w.context(task, 'compile', p)
        upstream = {r['module']: r['payload'] for r in ctx['upstream']}
        for module, text in designs.items():
            self.assertEqual(upstream[module]['design']['E1'], text)


if __name__ == '__main__':
    unittest.main()

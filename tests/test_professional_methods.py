"""Local method contracts and real context delivery, not aesthetic/media scoring."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w

METHODS = {
    'references/creation-preparation.md': ('source', ['扩写执行方法', '因果桥', '离别', '纠错']),
    'references/modules/action.md': ('action', ['交锋构造', '距离', '应对', '护送', '纠错']),
    'references/modules/camera.md': ('camera', ['镜头方案的构造', '代价', '前景', '重新建立', '纠错']),
    'references/modules/performance.md': ('performance', ['意图与策略', '掩饰', '听者', '纠错']),
    'references/modules/vfx.md': ('vfx', ['机制到画面', '选择与组合', '供能', '纠错']),
    'references/modules/sound.md': ('sound', ['听觉视点', '主次', '声桥', '纠错']),
    'references/modules/sampling.md': ('sampling', ['观察状态的选择', '冗余', '取舍', '纠错']),
    'references/modules/compile.md': ('compile', ['融合执行方法', '并行', '对照', '纠错']),
    'references/performance-camera-methods.md': ('camera', ['同一情境的方案取舍', '代价', '纠错']),
    'references/visual-impact-design.md': ('vfx', ['材质选择方法', '尺度设计方法', '对照']),
    'references/vfx-techniques.md': ('vfx', ['专项选择方法', '供能', '对照']),
}


def project():
    return {'sources': [{'id': 'S1', 'text': '甲挡住来袭并护送乙离开；甲说：“走。”'}],
            'events': [{'id': 'E1', 'source_ids': ['S1'], 'body': '甲挡住来袭并护送乙离开。',
                        'start': 0, 'end': 8, 'requires': ['action', 'performance', 'vfx', 'sound'],
                        'dialogues': [{'id': 'D1', 'speaker': '甲', 'text': '走。'}]}],
            'requirements': [{'id': 'R:fx', 'kind': 'vfx', 'description': '已确认的护层受压后逐步解体',
                              'source_ids': ['S1'], 'event_ids': ['E1'], 'specialties': ['vfx-techniques']}]}


class MethodContracts(unittest.TestCase):
    def test_creative_priority_is_ordered_and_delivered_to_design_stages(self):
        shared = (ROOT / 'references/design-boundaries.md').read_text(encoding='utf-8')
        headings = ['**主人要求与已定剧情**', '**戏剧目的**', '**观看重点**',
                    '**视听方案**', '**可执行性**', '**防漏交付**']
        positions = [shared.index(h) for h in headings]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('不调整source到validate的调用顺序', shared)
        self.assertIn('未实际比较就不事后声称', shared)
        fixture = project()
        fixture['events'][0]['requires'].append('assets')
        p = w.init(fixture, {'mode': 'prompt'})
        for module in ('assets', 'action', 'performance', 'vfx', 'sound', 'camera', 'compile', 'validate'):
            with self.subTest(module=module):
                packet = w.context({'mode': 'prompt'}, module, p)
                rules = {r['path']: r['text'] for r in packet['rules']}
                self.assertEqual(rules['references/design-boundaries.md'], shared)
        camera = (ROOT / 'references/modules/camera.md').read_text(encoding='utf-8')
        self.assertIn('不将局部同框需求扩大成整段不切', camera)
        self.assertIn('没有通用的秒数与镜头数换算', camera)

    def test_all_eleven_have_selection_construction_and_original_examples(self):
        self.assertEqual(len(METHODS), 11)
        for path, (_, cues) in METHODS.items():
            with self.subTest(path=path):
                text = (ROOT / path).read_text(encoding='utf-8')
                for cue in cues:
                    self.assertIn(cue, text, f'{path}: missing method dimension {cue}')
                self.assertIn('method-evidence.md', text)

    def test_methods_are_delivered_in_actual_owner_context_not_just_indexed(self):
        task = {'mode': 'prompt'}
        p = w.init(project(), task)
        grid = project()
        grid['video_master_prompt'] = '甲挡住来袭并护送乙离开。'
        grid = w.init(grid, {'mode': 'grid'})
        for path, (module, _) in METHODS.items():
            with self.subTest(path=path):
                active = grid if module == 'sampling' else p
                current_task = active['workflow']['plan']['task']
                packet = w.context(current_task, module, active)
                rules = {r['path']: r['text'] for r in packet['rules']}
                self.assertIn(path, rules)
                self.assertEqual(rules[path], (ROOT / path).read_text(encoding='utf-8-sig'))
                self.assertEqual(packet['receipt']['rules_hash'], w.fingerprint(packet['rules']))

    def test_camera_removes_unmotivated_change_requirement(self):
        camera = (ROOT / 'references/modules/camera.md').read_text(encoding='utf-8')
        self.assertNotIn('若整段只有匀速侧看、连续慢镜或无作用快切，重新分配摄影与速度', camera)
        self.assertIn('不因固定或匀速而判错', camera)
        self.assertIn('动作工序', camera)

    def test_local_sources_describe_limits_not_runtime_web_dependencies(self):
        text = (ROOT / 'references/method-evidence.md').read_text(encoding='utf-8')
        for phrase in ['本地执行', '综合设计', '未生成视频', '未完整观看', '检索摘录',
                       'filmanalysis.yale.edu', 'nationaltheatre.org.uk', 'theasc.com',
                       'gdcvault.com', 'docs.volcengine.com', 'sidefx.com']:
            self.assertIn(phrase, text)


if __name__ == '__main__':
    unittest.main()

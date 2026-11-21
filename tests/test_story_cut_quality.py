"""Rule delivery for the story/cut review loop, not automatic aesthetic evaluation."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w


class StoryCutQuality(unittest.TestCase):
    def test_quality_methods_reach_the_stages_that_make_and_review_decisions(self):
        task = {'mode': 'prompt'}
        source = '乙指出封条断了。甲把发货单推回去，决定停发。下一场，他把箱子送去复验。'
        project = w.init({
            'sources': [{'id': 'S1', 'text': source}],
            'events': [{'id': 'E1', 'source_ids': ['S1'], 'body': source,
                        'start': 0, 'end': 10, 'requires': ['action', 'performance', 'camera']}],
        }, task)
        methods = {
            'narrative-event-design.md': (
                ('source', 'compile', 'validate'), ('触发 → 人物判断 → 行动 → 结果', '谁作出决定')),
            'scene-rhythm-planning.md': (
                ('source', 'action', 'camera', 'compile', 'validate'), ('串行时间', '第一次看清')),
            'shot-rhythm-planning.md': (
                ('camera', 'compile', 'validate'), ('切镜收益', '原说话人的声音', '固定或移动')),
            'prompt-backstage-checks.md': (
                ('compile', 'validate'), ('实际采用的前后素材', '上一镜已给', '后一镜新增')),
        }
        for name, (modules, cues) in methods.items():
            path = 'references/' + name
            for module in modules:
                with self.subTest(path=path, module=module):
                    ctx = w.context(task, module, project)
                    rules = {r['path']: r['text'] for r in ctx['rules']}
                    self.assertEqual(rules.get(path), (ROOT / path).read_text(encoding='utf-8'))
                    for cue in cues:
                        self.assertIn(cue, rules[path])
        front_rules = {r['path']: r['text'] for r in w.context(task, 'compile', project)['rules']}
        template = front_rules['references/video-prompt-template.txt']
        for backstage_label in ('切镜收益', '完成检查', '动态元素复核'):
            self.assertNotIn(backstage_label, template)


    def test_dialogue_cutaway_decisions_and_handoffs_reach_their_owners(self):
        task = {'mode': 'prompt'}
        line = '看见窗台那盏灯吗？它亮着，我就不走。'
        p = w.init({
            'sources': [{'id': 'S1', 'text': line}],
            'events': [{'id': 'E1', 'source_ids': ['S1'], 'body': line,
                        'start': 0, 'end': 7.2, 'requires': ['camera', 'sound']}],
        }, task)
        expected = {
            'camera': ('对白中的景物插镜与空镜', '证据', '气氛', '入镜点', '回切点', '可不回切'),
            'sound': ('对白景物插镜', '同场画外对白', '不重播'),
            'compile': ('对白景物插镜', '完整发声单元', '实际切点'),
            'validate': ('对白景物插镜', '入镜点', '回切点'),
        }
        for owner, cues in expected.items():
            with self.subTest(owner=owner):
                ctx = w.context(task, owner, p)
                rules = {rule['path']: rule['text'] for rule in ctx['rules']}
                owner_rule = rules['references/modules/' + owner + '.md']
                for cue in cues:
                    self.assertIn(cue, owner_rule)
                if owner == 'compile':
                    self.assertNotIn('对白景物插镜', rules['references/video-prompt-template.txt'])


    def test_camera_context_plans_long_dialogue_by_changes_in_intent(self):
        task = {'mode': 'prompt'}
        line = '我本来想等雨停才告诉你。可把信藏起来的是我。你要走的话，能不能先听我把这封信念完？'
        project = w.init({
            'sources': [{'id': 'S1', 'text': line}],
            'events': [{'id': 'E1', 'source_ids': ['S1'], 'body': line,
                        'start': 0, 'end': 16, 'requires': ['camera', 'sound']}],
        }, task)
        rules = {r['path']: r['text'] for r in w.context(task, 'camera', project)['rules']}
        camera = rules['references/modules/camera.md']
        self.assertIn('### 长对白排镜', camera)
        section = camera.split('### 长对白排镜', 1)[1].split('景深按当前任务', 1)[0]
        for cue in ('说话意图', '不按句号或秒数', '原镜', '关键反应', '自然停顿'):
            self.assertIn(cue, section)


if __name__ == '__main__':
    unittest.main()

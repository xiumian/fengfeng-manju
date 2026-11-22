"""Actual rule delivery and the structural/semantic review boundary."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w
from workflow_coverage import verify_evidence, verify_reviews


class ScoreCausalReview(unittest.TestCase):
    def test_methods_reach_actual_contexts(self):
        task = {'mode': 'prompt'}
        p = w.init({'sources': [{'id': 'S1', 'text': '托腕撑指，掀潮，采用原创四音主题。'}],
                    'events': [{'id': 'E1', 'source_ids': ['S1'], 'start': 0, 'end': 8,
                                'body': '托腕撑指，掀潮，采用原创四音主题。',
                                'requires': ['action', 'vfx', 'sound']}]}, task)
        owners = {
            'references/layered-sound-design.md': (
                ('sound', 'compile', 'validate'),
                ('配乐主题线', '把音高方向改成上行', '让位与恢复', '厚潮脊实际翻过旧塔后')),
            'references/move-vfx-design.md': (
                ('vfx', 'camera', 'compile', 'validate'),
                ('关键因果逐环取证', '读证据而不是数证据', '同一条泛化结果', '回流后指骨由弯转直')),
        }
        for path, (modules, cues) in owners.items():
            for module in modules:
                with self.subTest(path=path, module=module):
                    c = w.context(task, module, p)
                    rules = {r['path']: r['text'] for r in c['rules']}
                    if module in ('sound', 'vfx'):
                        self.assertEqual(rules[path], (ROOT / path).read_text(encoding='utf-8'))
                    for cue in cues:
                        self.assertIn(cue, rules[path])

    def test_existing_quote_does_not_override_an_unmet_verdict(self):
        items = [{'id': 'R:seal', 'kind': 'vfx', 'event_ids': ['E1']}]
        text = '巨掌掀翻黑潮。'
        verify_evidence(items, {'R:seal': '巨掌掀翻黑潮'}, text)
        with self.assertRaisesRegex(ValueError, 'unresolved requirement'):
            verify_reviews(items, {'R:seal': {
                'status': 'unmet', 'reason': '结果存在，但没有腕甲封缝和金流回注的因果。'}})


if __name__ == '__main__':
    unittest.main()

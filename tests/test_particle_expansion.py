import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w
from workflow_rules import select_rules


class ParticleExpansion(unittest.TestCase):
    def test_sixty_four_distinct_new_schemes(self):
        entries = json.loads((ROOT / 'references/招式特效库/检索索引.json').read_text(encoding='utf-8'))['entries']
        extra = [e for e in entries if int(e['id'][4:6]) >= 11]
        self.assertEqual(len(extra), 64)
        examples = []
        for e in extra:
            text = (ROOT / 'references/招式特效库' / e['file']).read_text(encoding='utf-8')
            block = re.search(r'^## ' + e['id'] + r' .+?\n(.*?)(?=^## |\Z)', text, re.S | re.M)[1]
            for cue in ['粒子结构', '传播', '应对分支', '终态', '正文片段', '纠错', '证据']:
                self.assertIn(cue, block, e['id'])
            examples.append(re.search(r'\*\*正文片段[^\n]*\*\*：([^\n]+)', block)[1])
        self.assertEqual(len(set(examples)), 64)

    def test_user_named_grand_effects_reach_context(self):
        for text, identity in [('万剑归宗', 'VFX-1101'), ('法天相地', 'VFX-1201'),
                               ('能量光炮', 'VFX-1401'), ('连环雷暴', 'VFX-1501'), ('接触爆破', 'VFX-1301')]:
            p = w.init({'sources': [{'id': 'S1', 'text': text}], 'events': [
                {'id': 'E1', 'source_ids': ['S1'], 'body': text, 'start': 0, 'end': 15, 'requires': ['vfx']}]}, {'mode': 'prompt'})
            ctx = w.context({'mode': 'prompt'}, 'vfx', p)
            self.assertIn(identity, ctx['vfx_candidates'])
            self.assertTrue(any(identity in r['text'] for r in ctx['rules']))

    def test_explicit_multifamily_not_silently_truncated(self):
        ids = ['VFX-1101', 'VFX-1201', 'VFX-1301', 'VFX-1501']
        rules, candidates = select_rules('vfx', source_text=' '.join(ids))
        self.assertTrue(set(ids) <= set(candidates))
        selected = [r for r in rules if re.search(r'/招式特效库/\d\d_', r['path'])]
        self.assertEqual(len(selected), 4)
        rules, _ = select_rules('vfx', source_text='剑气 火焰 雷电 护盾 水流 爆炸')
        self.assertLessEqual(len([r for r in rules if re.search(r'/招式特效库/\d\d_', r['path'])]), 2)

    def test_particle_method_does_not_weaken_grand_effects(self):
        text = (ROOT / 'references/vfx-techniques.md').read_text(encoding='utf-8')
        for cue in ['粒子构造', '粒径', '条带', '体积', '密度不是越少越好', '暂时遮挡', '检查表留在后台']:
            self.assertIn(cue, text)


if __name__ == '__main__':
    unittest.main()

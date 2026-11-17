"""Library completeness/retrieval contracts, not generated-video quality."""
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w
from workflow_rules import select_rules


def index(folder):
    return json.loads((ROOT / 'references' / folder / '检索索引.json').read_text(encoding='utf-8'))['entries']


def project(body, kind):
    return {'sources': [{'id': 'S1', 'text': body}], 'events': [
        {'id': 'E1', 'body': body, 'source_ids': ['S1'], 'start': 0, 'end': 10, 'requires': [kind]}]}


class LibraryContracts(unittest.TestCase):
    def check_entries(self, folder, count, prefix):
        entries = index(folder)
        self.assertEqual(len(entries), count)
        self.assertEqual(len({e['id'] for e in entries}), count)
        for e in entries:
            with self.subTest(entry=e['id']):
                self.assertTrue(e['id'].startswith(prefix))
                text = (ROOT / 'references' / folder / e['file']).read_text(encoding='utf-8')
                match = re.search(r'^## ' + re.escape(e['id']) + r' .+?\n(.*?)(?=^## |\Z)', text, re.S | re.M)
                self.assertIsNotNone(match)
                for cue in ('适用', '应对分支', '正文片段', '纠错', '证据'):
                    self.assertIn(cue, match[1])
                self.assertEqual(e['validation_status'], 'adaptation_unverified')
                self.assertTrue(e['evidence_ids'])
                for source in e['evidence_ids']:
                    registry = (ROOT / 'references/combat-vfx-evidence.md').read_text(encoding='utf-8')
                    self.assertIn('| ' + source + ' |', registry)
        return entries

    def test_all_vfx_entries_and_original_ids_survive(self):
        entries = self.check_entries('招式特效库', 128, 'VFX-')
        ids = {e['id'] for e in entries}
        self.assertTrue({f'VFX-{c:02}{i:02}' for c in range(1, 9) for i in range(1, 7)} <= ids)
        self.assertEqual(len({e['file'] for e in entries}), 18)

    def test_action_library_has_nine_concrete_families(self):
        entries = self.check_entries('打斗编排库', 36, 'ACT-')
        self.assertEqual(len({e['file'] for e in entries}), 9)
        for e in entries:
            text = (ROOT / 'references/打斗编排库' / e['file']).read_text(encoding='utf-8')
            self.assertIn('动作链', text)
            self.assertIn('观看需求', text)

    def test_exact_named_action_reaches_real_context(self):
        p = w.init(project('甲护送穿门，乙紧随其后。', 'action'), {'mode': 'prompt'})
        ctx = w.context({'mode': 'prompt'}, 'action', p)
        self.assertIn('ACT-0501', ctx['action_candidates'])
        rules = {r['path']: r['text'] for r in ctx['rules']}
        self.assertIn('references/打斗编排库/05_护送与夺物.md', rules)
        self.assertEqual(ctx['receipt']['rules_hash'], w.fingerprint(ctx['rules']))

    def test_exact_ids_outweigh_incidental_generic_keywords(self):
        for module, identity, folder in [('action', 'ACT-0804', '打斗编排库'), ('vfx', 'VFX-1001', '招式特效库')]:
            rules, candidates = select_rules(module, source_text=f'{identity}。剑气火焰水流雷电护盾。')
            self.assertIn(identity, candidates)
            self.assertLessEqual(len([r for r in rules if r['path'].startswith('references/' + folder + '/') and r['path'].endswith('.md') and '调用规则' not in r['path']]), 2)

    def test_no_match_does_not_dump_library(self):
        for module, folder in [('action', '打斗编排库'), ('vfx', '招式特效库')]:
            rules, candidates = select_rules(module, source_text='纯粹的日常静坐，没有额外要求。')
            self.assertEqual(candidates, [])
            categories = [r for r in rules if r['path'].startswith('references/' + folder + '/') and re.search(r'/\d\d_', r['path'])]
            self.assertEqual(categories, [])

    def test_every_entry_can_be_selected_by_id_with_full_current_text(self):
        for module, folder in [('action', '打斗编排库'), ('vfx', '招式特效库')]:
            for entry in index(folder):
                with self.subTest(entry=entry['id']):
                    rules, candidates = select_rules(module, source_text=entry['id'])
                    self.assertEqual(candidates, [entry['id']])
                    path = 'references/' + folder + '/' + entry['file']
                    selected = {r['path']: r['text'] for r in rules}
                    self.assertEqual(selected[path], (ROOT / path).read_text(encoding='utf-8'))

    def test_new_effects_retrievable_and_not_sent_to_other_professions(self):
        rules, candidates = select_rules('vfx', source_text='治疗光流进入伤处，暂时稳定状态。')
        self.assertIn('VFX-1001', candidates)
        self.assertTrue(any('10_' in r['path'] for r in rules))
        rules, _ = select_rules('camera', source_text='治疗光流与护送穿门')
        self.assertFalse(any('/打斗编排库/' in r['path'] or re.search(r'/招式特效库/\d', r['path']) for r in rules))

    def test_library_receipt_must_be_fresh(self):
        p = w.init(project('甲护送穿门，乙追近。', 'action'), {'mode': 'prompt'})
        old = w.context({'mode': 'prompt'}, 'action', p)['receipt']
        source = w.context({'mode': 'prompt'}, 'source', p)
        p = w.submit(p, 'source', {'checked_event_ids': ['E1'], 'source_coverage': {
            u['id']: {'event_ids': ['E1'], 'reason': '本地结构夹具的原段与事件对应。'} for u in source['source_units']}}, source['receipt'])
        with self.assertRaisesRegex(ValueError, 'context receipt'):
            w.submit(p, 'action', {'design': {'E1': '甲挡住入口并护送乙离开。'}}, old)


if __name__ == '__main__':
    unittest.main()

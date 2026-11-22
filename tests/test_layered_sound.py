"""Layered audio writing and real delivery contracts, not listening tests."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w

PATH = 'references/layered-sound-design.md'
LABELS = ('动作层：', '特效层：', '环境层：', '同步节点：', '主次变化：', '跨镜承接：')


class LayeredSound(unittest.TestCase):
    def test_template_and_compile_keep_frontstage_audio_layers(self):
        template = (ROOT / 'references/video-prompt-template.txt').read_text(encoding='utf-8')
        for label in LABELS:
            self.assertTrue(label in template, label)
        self.assertNotIn('完成检查', template)
        for m in ('sound', 'compile', 'validate'):
            self.assertTrue('layered-sound-design.md' in (ROOT / f'references/modules/{m}.md').read_text(encoding='utf-8'), m)

    def test_real_six_stage_rule_delivery_and_fingerprints(self):
        t = {'mode': 'prompt'}
        p = w.init({'sources': [{'id': 'S1', 'text': '甲开伞，雨落伞面，听见钩撞铜骨。'}],
                    'events': [{'id': 'E1', 'source_ids': ['S1'], 'start': 0, 'end': 2,
                                'body': '甲开伞，雨落伞面，听见钩撞铜骨。',
                                'requires': ['action', 'vfx', 'sound']}]}, t)
        for m in ('sound', 'action', 'vfx', 'camera', 'compile', 'validate'):
            c = w.context(t, m, p); rules = {r['path']: r['text'] for r in c['rules']}
            self.assertTrue(PATH in rules, m)
            cue = {'sound':'连镜对照', 'action':'真实声源', 'vfx':'把每层写成变化',
                   'camera':'同步、主次和跨镜', 'compile':'实际正文保留六项组织', 'validate':'实际复核与返修'}[m]
            self.assertIn(cue,rules[PATH],m)
            if m == 'sound':
                self.assertEqual(rules[PATH], (ROOT / PATH).read_text(encoding='utf-8'))
            self.assertEqual(c['receipt']['rules_hash'], w.fingerprint(c['rules']))

    def test_method_has_sound_construction_not_only_headers(self):
        s = (ROOT / PATH).read_text(encoding='utf-8')
        for cue in ('起声', '持续', '尾响', '同一声源', '不存在', '对白', '画外', '0.5秒',
                    '开伞', '入洞', '普通', '严格响度、声像和帧级同步留给后期', 'unmet', 'requirements'):
            self.assertTrue(cue in s, cue)

    def test_sound_payload_reaches_camera_and_compile_without_flattening(self):
        t = {'mode': 'prompt'}
        p = w.init({'sources': [{'id': 'S1', 'text': '甲开伞，雨敲伞面。'}],
                    'events': [{'id': 'E1', 'source_ids': ['S1'], 'body': '甲开伞，雨敲伞面。',
                                'start': 0, 'end': 2, 'requires': ['sound']}]}, t)
        c = w.context(t, 'source', p)
        p = w.submit(p, 'source', {'checked_event_ids': ['E1'], 'source_coverage': {
            u['id']: {'event_ids': ['E1'], 'reason': '结构夹具的开伞与雨声逐段映射，不声称核听。'}
            for u in c['source_units']}}, c['receipt'])
        audio = '动作层：扣响后骨架弹开。环境层：直落雨转为敲击伞面。同步节点：弹响对应开骨。主次变化：先扣响后雨声。跨镜承接：雨声连续，不重播开骨。'
        while p['workflow']['plan']['steps'][p['workflow']['cursor']]['module'] != 'compile':
            m = p['workflow']['plan']['steps'][p['workflow']['cursor']]['module']; c = w.context(t, m, p)
            if m == 'camera':
                prior = {r['module']: r['payload'] for r in c['upstream']}
                self.assertEqual(prior['sound']['design']['E1'], audio)
            p = w.submit(p, m, {'design': {e['id']: audio if m == 'sound' else '保持开伞、既定声源和观看方向，不改事件。'
                                          for e in c['events']}}, c['receipt'])
        c = w.context(t, 'compile', p)
        prior = {r['module']: r['payload'] for r in c['upstream']}
        self.assertEqual(prior['sound']['design']['E1'], audio)


if __name__ == '__main__':
    unittest.main()

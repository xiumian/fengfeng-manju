"""Verify the three native integrations without running upstream tools or video models."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w
from export_text_rules import assemble

BASE = 'references/production-specialties'
ROUTES = {
    'realistic-fight': ('action', 'choreography.md'),
    'vfx-fight': ('vfx', 'effect-profiles.md'),
    'impact-frame': ('vfx', 'frame-construction.md'),
}


def project(specialty, kind=None):
    first, second = '阿岚看见盾侧裂口，改变扇风方向。', '她从廊下经过。'
    owner = kind or ROUTES[specialty][0]
    return {
        'sources': [{'id': 'S1', 'text': first + '\n' + second}],
        'events': [
            {'id': 'E1', 'body': first, 'source_ids': ['S1'], 'start': 0, 'end': 3},
            {'id': 'E2', 'body': second, 'source_ids': ['S1'], 'start': 3, 'end': 6},
        ],
        'requirements': [{'id': 'R1', 'kind': owner, 'description': '按已定反应交接可见设计',
                          'event_ids': ['E1'], 'source_ids': ['S1'], 'source_quote': first,
                          'specialties': [specialty]}],
    }


def specialty_paths(packet):
    return {rule['path']: rule['text'] for rule in packet['rules']
            if rule['path'].startswith(BASE + '/')}


class ProductionSpecialties(unittest.TestCase):
    def test_each_specialty_loads_native_guide_and_real_reference(self):
        for key, (owner, reference) in ROUTES.items():
            with self.subTest(key=key):
                task = {'mode': 'prompt'}
                packet = w.context(task, owner, w.init(project(key), task))
                rules = specialty_paths(packet)
                entry = f'{BASE}/{key}/guide.md'
                detail = f'{BASE}/{key}/references/{reference}'
                self.assertIn(entry, rules)
                self.assertIn(detail, rules)
                for path, text in rules.items():
                    self.assertTrue(path.startswith(f'{BASE}/{key}/'))
                    self.assertEqual(text, (ROOT / path).read_text(encoding='utf-8-sig'))
                    self.assertNotIn('effect-lexicon.md', path)
                self.assertEqual(packet['receipt']['rules_hash'], w.fingerprint(packet['rules']))

    def test_not_loaded_for_wrong_owner_unrelated_event_or_plain_scene(self):
        for key, (owner, _) in ROUTES.items():
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, 'does not belong'):
                    w.init(project(key, 'performance'), {'mode': 'prompt'})
                task = {'mode': 'revise', 'scope': ['E2'], 'features': [owner]}
                p = project(key)
                p['master_sections'] = {event['id']: event['body'] for event in p['events']}
                self.assertEqual({}, specialty_paths(w.context(task, owner, w.init(p, task))))
                task = {'mode': 'prompt', 'features': [owner]}
                p = project(key)
                p['requirements'] = []
                self.assertEqual({}, specialty_paths(w.context(task, owner, w.init(p, task))))

    def test_vfx_routes_are_independent_can_coexist_and_do_not_replace_template(self):
        task = {'mode': 'prompt'}
        p = project('vfx-fight')
        p['requirements'][0]['specialties'] = ['vfx-fight', 'impact-frame']
        p = w.init(p, task)
        packet = w.context(task, 'vfx', p)
        rules = specialty_paths(packet)
        for key in ('vfx-fight', 'impact-frame'):
            self.assertIn(f'{BASE}/{key}/guide.md', rules)
        camera = w.context(task, 'camera', p)
        self.assertFalse(specialty_paths(camera))
        camera_text = next(r['text'] for r in camera['rules'] if r['path'] == 'references/modules/camera.md')
        self.assertIn('impact-frame/guide.md', camera_text)
        compile_paths = {r['path'] for r in w.context(task, 'compile', p)['rules']}
        self.assertIn('references/video-prompt-template.txt', compile_paths)
        self.assertFalse(any(f'{BASE}/' in path for path in compile_paths))

    def test_release_uses_its_own_specialties_and_catalogues(self):
        for key, (_, detail) in ROUTES.items():
            actual = {p.relative_to(ROOT / BASE / key).as_posix()
                      for p in (ROOT / BASE / key).rglob('*') if p.is_file()}
            self.assertEqual({'guide.md', f'references/{detail}'}, actual)
        self.assertFalse((ROOT / BASE / 'source-map.json').exists())
        for library, count in (('招式特效库', 128), ('打斗编排库', 36)):
            raw = (ROOT / 'references' / library / '检索索引.json').read_text(encoding='utf-8-sig')
            self.assertEqual(count, len(json.loads(raw)['entries']))

    def test_portable_allowlist_keeps_the_existing_template_and_three_guides(self):
        payload = assemble()
        self.assertEqual(len(payload), 5)
        self.assertEqual(payload['01_video-prompt-template.txt'],
                         (ROOT / 'references/video-prompt-template.txt').read_bytes())
        combined = payload['04_combat-vfx-rules.md']
        for key, (_, detail) in ROUTES.items():
            self.assertTrue(f'===== {BASE}/{key}/guide.md ====='.encode() in combined, key)
            self.assertTrue(f'===== {BASE}/{key}/references/{detail} ====='.encode() in combined, key)
        self.assertFalse(b'effect-lexicon.md' in combined)


if __name__ == '__main__':
    unittest.main()

"""Source, storyboard and prompt routes for the second group of specialties."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w
from export_text_rules import assemble

BASE = 'references/production-specialties'
DIRECTOR = f'{BASE}/director-handoff'
STORYBOARD = f'{BASE}/scene-storyboard'
EXPRESSION = f'{BASE}/emotion-expression'
NEW = (DIRECTOR, STORYBOARD, EXPRESSION)


def project():
    first = '铜片落在槽边。他看见缺口，把右手放低。'
    second = '海水退出石台。'
    return {
        'sources': [{'id': 'S1', 'text': first + '\n' + second}],
        'events': [
            {'id': 'E1', 'body': first, 'source_ids': ['S1'], 'start': 0, 'end': 2},
            {'id': 'E2', 'body': second, 'source_ids': ['S1'], 'start': 2, 'end': 4},
        ],
        'requirements': [
            {'id': 'D1', 'kind': 'camera', 'description': '独立段承接已采用的道具状态并验证切口',
             'event_ids': ['E1'], 'source_ids': ['S1'], 'source_quote': first,
             'specialties': ['director-handoff', 'scene-storyboard']},
            {'id': 'P1', 'kind': 'performance', 'description': '把察觉与原手上动作准确交接',
             'event_ids': ['E1'], 'source_ids': ['S1'], 'source_quote': first,
             'specialties': ['emotion-expression']},
        ],
    }


def load(task, module, p):
    packet = w.context(task, module, p)
    rules = {r['path']: r['text'] for r in packet['rules']}
    for path, text in rules.items():
        if path.startswith(NEW):
            assert text == (ROOT / path).read_text(encoding='utf-8-sig'), path
    assert packet['receipt']['rules_hash'] == w.fingerprint(packet['rules'])
    return rules


class StorySpecialties(unittest.TestCase):
    def test_director_handoff_reaches_the_actual_four_stage_packets(self):
        task = {'mode': 'prompt'}
        p = w.init(project(), task)
        expected = {'source': 'prepare.md', 'camera': 'guide.md',
                    'compile': 'compile-bridge.md', 'validate': 'review.md'}
        for phase, file in expected.items():
            with self.subTest(phase=phase):
                rules = load(task, phase, p)
                self.assertEqual([f'{DIRECTOR}/{file}'],
                                 [name for name in rules if name.startswith(DIRECTOR + '/')])
        self.assertIn('references/video-prompt-template.txt', load(task, 'compile', p))
        self.assertFalse(any(path.startswith(DIRECTOR) for path in load(task, 'performance', p)))

    def test_storyboard_and_face_load_only_in_their_owners(self):
        task = {'mode': 'prompt'}
        p = w.init(project(), task)
        camera = load(task, 'camera', p)
        performance = load(task, 'performance', p)
        self.assertIn(f'{STORYBOARD}/guide.md', camera)
        self.assertIn(f'{STORYBOARD}/references/view-reconstruction.md', camera)
        self.assertIn(f'{EXPRESSION}/guide.md', performance)
        self.assertIn(f'{EXPRESSION}/references/cue-selection.md', performance)
        self.assertFalse(any('upstream-entry.md' in name for name in (*camera, *performance)))
        self.assertFalse(any(name.startswith(EXPRESSION) for name in camera))
        self.assertFalse(any(name.startswith(STORYBOARD) for name in performance))
        misplaced = copy.deepcopy(project())
        misplaced['requirements'][1]['kind'] = 'camera'
        with self.assertRaisesRegex(ValueError, 'does not belong'):
            w.init(misplaced, task)

    def test_plain_scene_and_other_event_do_not_inherit_new_rules(self):
        ordinary = project()
        ordinary['requirements'] = []
        task = {'mode': 'prompt'}
        p = w.init(ordinary, task)
        for phase in ('source', 'camera', 'compile', 'validate'):
            self.assertFalse(any(name.startswith(NEW) for name in load(task, phase, p)))
        scoped = project()
        scoped['master_sections'] = {e['id']: e['body'] for e in scoped['events']}
        task = {'mode': 'revise', 'scope': ['E2'], 'features': ['performance']}
        p = w.init(scoped, task)
        for phase in ('source', 'performance', 'camera', 'compile', 'validate'):
            self.assertFalse(any(name.startswith(NEW) for name in load(task, phase, p)))

    def test_grid_uses_master_not_new_director_workflow(self):
        data = project()
        data['video_master_prompt'] = data['sources'][0]['text']
        task = {'mode': 'grid'}
        p = w.init(data, task)
        self.assertNotIn('camera', [step['module'] for step in p['workflow']['plan']['steps']])
        for phase in ('source', 'sampling', 'validate'):
            self.assertFalse(any(name.startswith(NEW) for name in load(task, phase, p)))

    def test_release_contains_only_native_story_specialties(self):
        self.assertFalse((ROOT / BASE / 'story-source-map.json').exists())
        self.assertEqual({p.name for p in (ROOT / DIRECTOR).iterdir()},
                         {'prepare.md', 'guide.md', 'compile-bridge.md', 'review.md'})
        for path, note in ((STORYBOARD, 'view-reconstruction.md'), (EXPRESSION, 'cue-selection.md')):
            self.assertEqual({'guide.md', f'references/{note}'},
                             {p.relative_to(ROOT / path).as_posix()
                              for p in (ROOT / path).rglob('*') if p.is_file()})

    def test_portable_packet_has_native_methods_without_new_formats(self):
        bundle = assemble()
        self.assertEqual(5, len(bundle))
        self.assertEqual((ROOT / 'references/video-prompt-template.txt').read_bytes(),
                         bundle['01_video-prompt-template.txt'])
        chapters = { '02_core-contracts-and-precreation.md': [f'{DIRECTOR}/prepare.md'],
                     '03_rhythm-emotion-sound.md': [f'{DIRECTOR}/guide.md', f'{STORYBOARD}/guide.md',
                                                   f'{STORYBOARD}/references/view-reconstruction.md',
                                                   f'{EXPRESSION}/guide.md', f'{EXPRESSION}/references/cue-selection.md'],
                     '05_modules-and-compile.md': [f'{DIRECTOR}/compile-bridge.md', f'{DIRECTOR}/review.md']}
        for name, docs in chapters.items():
            for doc in docs:
                self.assertTrue(f'===== {doc} ====='.encode() in bundle[name], doc)
        self.assertTrue(all(b'/upstream-entry.md =====' not in text for text in bundle.values()))


if __name__ == '__main__':
    unittest.main()

"""Rules reach specialists without loading unrelated methods or history."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w
import export_text_rules as export


class RuleIsolation(unittest.TestCase):
    def test_context_excludes_old_rules_and_only_repeats_needed_sections(self):
        task = {'mode': 'prompt'}
        project = w.init({
            'sources': [{'id': 'S1', 'text': '甲压低嗓音，施术挡潮。'}],
            'events': [{'id': 'E1', 'source_ids': ['S1'], 'start': 0, 'end': 15,
                        'body': '甲压低嗓音，施术挡潮。',
                        'requires': ['assets', 'action', 'performance', 'sound', 'vfx', 'camera']}],
        }, task)
        rules = {}
        for step in project['workflow']['plan']['steps']:
            m = step['module']
            ctx = w.context(task, m, project)
            rules[m] = {item['path']: item['text'] for item in ctx['rules']}
            self.assertEqual(ctx['receipt']['rules_hash'], w.fingerprint(ctx['rules']))
            self.assertFalse(any('_archive/' in name for name in rules[m]))
        for file in ('director-output-contract.md', 'shot-and-segment.md',
                     'emotion-closeup-conversion.md', 'microexpression-prompt-templates.md'):
            self.assertTrue((ROOT / '_archive/references' / file).is_file(), file)
            self.assertFalse((ROOT / 'references' / file).exists(), file)
        boundary = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('未实际看画面或听声音', boundary)
        checks = [
            ('move-vfx-design.md', 'vfx', 'compile', '编译保真', '三种对照'),
            ('layered-sound-design.md', 'sound', 'validate', '实际复核与返修', '连镜对照'),
            ('emotion-performance-design.md', 'performance', 'camera', '表情设计', '情境对照'),
            ('scene-rhythm-planning.md', 'source', 'compile', '按观看容量', '条件对照'),
            ('shot-rhythm-planning.md', 'camera', 'action', '职责、交接与交付', '切镜收益'),
        ]
        for file, owner, reader, required, omitted in checks:
            with self.subTest(file=file, reader=reader):
                path = 'references/' + file
                full = (ROOT / path).read_text(encoding='utf-8')
                self.assertEqual(rules[owner][path], full)
                view = rules[reader][path]
                self.assertIn(required, view)
                self.assertIn(omitted, full)
                self.assertNotIn(omitted, view)
                self.assertLess(len(view), len(full))

    def test_five_exports_preserve_current_sources_and_exclude_legacy(self):
        outputs = export.assemble()
        self.assertEqual(set(outputs), {
            '01_video-prompt-template.txt', '02_core-contracts-and-precreation.md',
            '03_rhythm-emotion-sound.md', '04_combat-vfx-rules.md', '05_modules-and-compile.md',
        })
        self.assertEqual(outputs['01_video-prompt-template.txt'],
                         (ROOT/'references/video-prompt-template.txt').read_bytes())
        for name, data in outputs.items():
            data.decode('utf-8', errors='strict')
            if name == '01_video-prompt-template.txt':
                continue
            heads = list(re.finditer(rb'^===== (.+?) =====' + bytes([10]), data, re.M))
            paths = [h[1].decode('utf-8') for h in heads]
            self.assertEqual(paths, list(export.EXPORTS[name]))
            self.assertFalse(any(p.split('/')[-1] in export.LEGACY for p in paths))
            for i, head in enumerate(heads):
                end = heads[i+1].start()-2 if i+1 < len(heads) else len(data)
                self.assertEqual(data[head.end():end], (ROOT/paths[i]).read_bytes(), paths[i])
        for forbidden in ('_archive/references/shot-and-segment.md', 'references/emotion-closeup-conversion.md',
                          'assets/default-storyboard-style.png'):
            with self.assertRaisesRegex(ValueError, 'excluded export source'):
                export.load(forbidden)

    def test_offline_export_contains_the_current_workflow_and_handoffs(self):
        outputs = export.assemble()
        core = outputs['02_core-contracts-and-precreation.md'].decode('utf-8')
        final = outputs['05_modules-and-compile.md'].decode('utf-8')
        for path in ('portable-text-usage','routing','project-contract','specialty-selection'):
            self.assertIn(f'===== references/{path}.md =====',core)
        for path in ('modules/source','modules/assets','model-delivery'):
            self.assertIn(f'===== references/{path}.md =====',final)
        for cue in ('无需运行脚本', '未随包附带', '不要声称读过该条目', '逐镜对照'):
            self.assertIn(cue,core)
        self.assertIn('全段显式时码稿须逐镜写出',final)
        self.assertNotIn('===== scripts/',core)

    def test_export_dependency_gate_only_allows_documented_optional_sources(self):
        from unittest.mock import patch
        read_source = export.load
        def inject(path):
            raw = read_source(path)
            return raw + (b'\n[unclassified](not-bundled.md)' if path == 'SKILL.md' else b'')
        with patch.object(export, 'load', side_effect=inject):
            with self.assertRaisesRegex(ValueError,'unclassified export dependency'):
                export.assemble()

if __name__ == '__main__':
    unittest.main()

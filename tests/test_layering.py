"""Layer boundaries and explicit specialist loading; no model/media quality claim."""
import copy
import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w
from workflow_rules import select_rules


def project(kind='performance', specialty='microexpression'):
    return {
        'sources': [{'id': 'S1', 'text': '她接过信，神色如常。\n他离开房间。'}],
        'events': [
            {'id': 'E1', 'source_ids': ['S1'], 'body': '她接过信，神色如常。', 'start': 0, 'end': 3},
            {'id': 'E2', 'source_ids': ['S1'], 'body': '他离开房间。', 'start': 3, 'end': 6}],
        'requirements': [{'id': 'R1', 'kind': kind, 'description': '保持外在平静，呈现短暂的不安。',
                          'source_ids': ['S1'], 'event_ids': ['E1'], 'source_quote': '她接过信，神色如常。',
                          'specialties': [specialty]}]}


def source_submit(p):
    packet = w.context(p['workflow']['plan']['task'], 'source', p)
    return w.submit(p, 'source', {'checked_event_ids': ['E1', 'E2'], 'source_coverage': {
        unit['id']: {'event_ids': ['E1' if unit['id'] == 'S1:L1' else 'E2'], 'reason': '按原句逐项核对事件与来源'}
        for unit in packet['source_units']}}, packet['receipt'])


class ExplicitSpecialties(unittest.TestCase):
    def test_semantic_declaration_without_trigger_words_loads_actual_text(self):
        for kind, specialty, path in [
                ('performance', 'microexpression', 'references/microexpression-cues.md'),
                ('vfx', 'vfx-techniques', 'references/vfx-techniques.md')]:
            with self.subTest(specialty=specialty):
                task = {'mode': 'prompt'}
                p = w.init(project(kind, specialty), task)
                packet = w.context(task, kind, p)
                self.assertEqual([e['id'] for e in packet['events']], ['E1'])
                rules = {rule['path']: rule['text'] for rule in packet['rules']}
                self.assertIn(path, rules)
                self.assertEqual(rules[path], (ROOT / path).read_text(encoding='utf-8-sig'))
                self.assertEqual(packet['receipt']['rules_hash'], w.fingerprint(packet['rules']))

    def test_invalid_declarations_fail_before_plan(self):
        for kind, values in [('performance', ['unknown']), ('sound', ['microexpression']),
                             ('dialogue', ['microexpression']),
                             ('performance', 'microexpression'), ('performance', [True]),
                             ('performance', ['microexpression', 'microexpression']),
                             ('performance', ['../../outside.md'])]:
            with self.subTest(kind=kind, values=values):
                p = project()
                p['requirements'][0].update(kind=kind, specialties=values)
                with self.assertRaisesRegex(ValueError, 'specialt'):
                    w.init(p, {'mode': 'prompt'})

    def test_keyword_fallback_and_explicit_request_are_deduplicated(self):
        rules, _ = select_rules('performance', [{'body': '她的眼神变化。'}],
                                specialties=['microexpression'])
        self.assertEqual([r['path'] for r in rules].count('references/microexpression-cues.md'), 1)

    def test_old_projects_do_not_load_unrequested_specialties(self):
        p = project()
        del p['requirements'][0]['specialties']
        packet = w.context({'mode': 'prompt'}, 'performance', w.init(p, {'mode': 'prompt'}))
        self.assertNotIn('references/microexpression-cues.md', [r['path'] for r in packet['rules']])

    def test_unrelated_owner_and_scope_do_not_load_specialties(self):
        p = project()
        task = {'mode': 'prompt'}
        packet = w.context(task, 'camera', w.init(p, task))
        self.assertNotIn('references/microexpression-cues.md', [r['path'] for r in packet['rules']])
        task = {'mode': 'revise', 'scope': ['E2'], 'features': ['performance']}
        p['master_sections'] = {e['id']: e['body'] for e in p['events']}
        packet = w.context(task, 'performance', w.init(p, task))
        self.assertNotIn('references/microexpression-cues.md', [r['path'] for r in packet['rules']])

    def test_discovery_rewinds_owner_and_rejects_stale_context(self):
        p = project()
        del p['requirements'][0]['specialties']
        p = source_submit(w.init(p, {'mode': 'prompt'}))
        old = w.context({'mode': 'prompt'}, 'performance', p)
        p = w.submit(p, 'performance', {'design': {'E1': '她接信后保持平静。'}}, old['receipt'])
        p = w.discover(p, {'reason': '该反应需要专项设计而非仅写情绪名', 'requirements': [
            dict(project()['requirements'][0], id='R2')]})
        self.assertEqual([r['module'] for r in p['workflow']['results']], ['source'])
        packet = w.context({'mode': 'prompt'}, 'performance', p)
        self.assertIn('references/microexpression-cues.md', [r['path'] for r in packet['rules']])
        with self.assertRaisesRegex(ValueError, 'context receipt'):
            w.submit(p, 'performance', {'design': {'E1': '她接信后保持平静。'}}, old['receipt'])
        w.submit(p, 'performance', {'design': {'E1': '她接信后保持平静。'}}, packet['receipt'])

    def test_invalid_discovery_is_atomic(self):
        p = source_submit(w.init(project(), {'mode': 'prompt'}))
        before = copy.deepcopy(p)
        bad = dict(project()['requirements'][0], id='R2', specialties=['not-a-specialty'])
        with self.assertRaisesRegex(ValueError, 'specialt'):
            w.discover(p, {'reason': '请求未注册资料', 'requirements': [bad]})
        self.assertEqual(p, before)

    def test_explicit_specialty_survives_complete_text_workflow(self):
        p = source_submit(w.init(project(), {'mode': 'prompt'}))
        for module in ['performance', 'camera']:
            packet = w.context({'mode': 'prompt'}, module, p)
            p = w.submit(p, module, {'design': {e['id']: '承接原事件的具体可见设计。'
                                               for e in packet['events']}}, packet['receipt'])
        text = '她接过信，神色如常。她短暂屏息，随即恢复平静。\n他离开房间。'
        proofs = {'event:E1': '她接过信，神色如常。', 'event:E2': '他离开房间。',
                  'R1': '她短暂屏息，随即恢复平静。'}
        packet = w.context({'mode': 'prompt'}, 'compile', p)
        p = w.submit(p, 'compile', {'text': text, 'event_ids': ['E1', 'E2'],
                                   'dialogue_ids': [], 'coverage': proofs}, packet['receipt'])
        packet = w.context({'mode': 'prompt'}, 'validate', p)
        p = w.submit(p, 'validate', {'content_checked': True, 'coverage': proofs,
            'evidence': {'E1': '接信与外在平静均在正文中', 'E2': '离开房间的结果在正文中'},
            'requirement_reviews': {key: {'status': 'met', 'reason': '此处只核验保存文字的结构通路'} for key in proofs},
            'limitations': ['同一执行者手写的回归夹具，非独立模型创作或语义质量验收']}, packet['receipt'])
        self.assertEqual(p['workflow']['status'], 'text_checked')
        self.assertEqual(p['video_master_prompt'], text)

    def test_grid_does_not_restart_specialist_design(self):
        p = project()
        p['video_master_prompt'] = p['sources'][0]['text']
        task = {'mode': 'grid'}
        p = w.init(p, task)
        self.assertEqual([step['module'] for step in p['workflow']['plan']['steps']],
                         ['source', 'sampling', 'validate'])
        self.assertNotIn('references/microexpression-cues.md',
                         [r['path'] for r in w.context(task, 'sampling', p)['rules']])

    def test_old_rule_plan_requires_reinit_and_archives_without_losing_facts(self):
        task = {'mode': 'prompt'}
        p = w.init(project(), task)
        # Simulate an old saved rule-path registration rather than forging new approval.
        p['workflow']['plan']['steps'][0]['rules'] = ['references/modules/source.md']
        old_workflow = copy.deepcopy(p['workflow'])
        with self.assertRaisesRegex(ValueError, 'reinitialize'):
            w.context(task, 'source', p)
        new = w.init(p, task)
        self.assertEqual(new['workflow_archives'][-1], old_workflow)
        self.assertEqual(new['sources'], p['sources'])
        self.assertEqual(new['events'], p['events'])
        self.assertEqual(new['workflow']['results'], [])


class InstructionContracts(unittest.TestCase):
    def test_user_prompt_template_is_loaded_verbatim(self):
        path = 'references/video-prompt-template.txt'
        p = w.init(project(), {'mode': 'prompt'})
        packet = w.context({'mode': 'prompt'}, 'compile', p)
        rules = {rule['path']: rule['text'] for rule in packet['rules']}
        self.assertIn(path, rules)
        template = (ROOT / path).read_text(encoding='utf-8')
        self.assertEqual(rules[path], template)
        self.assertEqual(packet['receipt']['rules_hash'], w.fingerprint(packet['rules']))
        for heading in ['【项目名称】：[填写名称]', '━━━━━━━━━━ 全局设定 ━━━━━━━━━━',
                        '━━━━━━━━━━ 场景与资产 ━━━━━━━━━━', '━━━━━━━━━━ 片段设定 ━━━━━━━━━━',
                        '━━━━━━━━━━ 逐镜时间轴 ━━━━━━━━━━', '【台词】〔无则删除〕', '【音效】']:
            self.assertIn(heading, template)
        for backstage in ['动态元素复核', '完成检查']:
            self.assertNotIn(backstage, template)
        self.assertTrue(template.rstrip().endswith('[按上述单镜格式继续，直至覆盖片段总时长。]'))
        compile_rules = (ROOT / 'references/modules/compile.md').read_text(encoding='utf-8')
        self.assertIn('video-prompt-template.txt', compile_rules)
        self.assertIn('当前用户明确格式优先', compile_rules)

    def test_continuous_timeline_preserves_globals_and_moves_fields_backstage(self):
        template = (ROOT / 'references/video-prompt-template.txt').read_text(encoding='utf-8')
        global_part, timeline = template.split('━━━━━━━━━━ 逐镜时间轴 ━━━━━━━━━━', 1)
        self.assertEqual(hashlib.sha256(global_part.encode()).hexdigest(),
                         'f9e3cab20d061f28e5b9ff6f020cb6f3d0d765395bddc0d407d6f520f72c3dc9')
        for form in ['【摄影】', '【画面与动作】', '【镜间衔接】', '先以[身体动作',
                     '景别：', '运镜：', '发声设计：']:
            self.assertNotIn(form, timeline)
        # Current explicit authorization restores audio subfields only.
        visual, audio = timeline.split('【音效】', 1)
        self.assertNotIn('同步节点：', visual)
        self.assertIn('同步节点：', audio)
        self.assertIn('动作层：', audio)
        self.assertIn('连续画面描述', timeline)
        task = {'mode': 'prompt'}
        p = w.init(project(), task)
        for module in ['compile', 'validate']:
            rules = {r['path']: r['text'] for r in w.context(task, module, p)['rules']}
            backend = rules['references/prompt-backstage-checks.md']
            for phrase in ['连续表达', '景别', '构图', '景深', '运动模糊', '口型', '跨镜', '声源']:
                self.assertIn(phrase, backend)
        compile_rules = (ROOT / 'references/modules/compile.md').read_text(encoding='utf-8')
        self.assertIn('不按专业模块逐栏拼接', compile_rules)
        self.assertIn('不强制', compile_rules)

    def test_backstage_checks_are_separate_and_supplied_to_compile_and_validate(self):
        path = 'references/prompt-backstage-checks.md'
        p = w.init(project(), {'mode': 'prompt'})
        for module in ['compile', 'validate']:
            rules = {r['path']: r['text'] for r in w.context({'mode': 'prompt'}, module, p)['rules']}
            self.assertIn(path, rules)
            for phrase in ['【动态元素复核】', '完成检查', '不进入投喂正文', '融入',
                           '主体：[核心动作与表情变化]。',
                           '规则：全局与局部要求一致，删除互相冲突及不适用的指令。']:
                self.assertIn(phrase, rules[path])
        compile_rules = (ROOT / 'references/modules/compile.md').read_text(encoding='utf-8')
        self.assertIn('prompt-backstage-checks.md', compile_rules)
        self.assertNotIn('逐镜时间轴和完成检查结构', compile_rules)

    def test_preparation_contract_is_in_entry_and_source_context(self):
        path = 'references/creation-preparation.md'
        self.assertIn(path, (ROOT / 'SKILL.md').read_text(encoding='utf-8'))
        p = w.init(project(), {'mode': 'prompt'})
        rules = {r['path']: r['text'] for r in w.context({'mode': 'prompt'}, 'source', p)['rules']}
        self.assertIn(path, rules)
        for phrase in ['忠实改编', '授权扩写', '仅补拍法', '只要求扩写', '不冒充原文', '待确认']:
            self.assertIn(phrase, rules[path])

    def test_shared_boundaries_and_camera_methods_are_supplied(self):
        p = w.init(project('vfx', 'vfx-techniques'), {'mode': 'prompt', 'features': ['action', 'performance']})
        for module in ['action', 'performance', 'vfx', 'camera']:
            rules = {r['path']: r['text'] for r in w.context(p['workflow']['plan']['task'], module, p)['rules']}
            self.assertIn('references/design-boundaries.md', rules)
            self.assertIn('references/specialty-selection.md', rules)
        camera = {r['path']: r['text'] for r in w.context(p['workflow']['plan']['task'], 'camera', p)['rules']}
        self.assertIn('references/performance-camera-methods.md', camera)
        self.assertIn('凤凰掠过', camera['references/performance-camera-methods.md'])
        performance = (ROOT / 'references/modules/performance.md').read_text(encoding='utf-8')
        self.assertNotIn('## 凤凰掠过的条件示例', performance)
        self.assertIn('观看需求', performance)
        action = (ROOT / 'references/modules/action.md').read_text(encoding='utf-8')
        self.assertNotIn('编排动作、特效/变身与摄影', action)


if __name__ == '__main__':
    unittest.main()

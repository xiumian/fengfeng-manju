"""Verify actual rule packets and keeping valid old work."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w
import workflow_rules as rules

VFX = 'references/move-vfx-design.md'
SOUND = 'references/layered-sound-design.md'
EMOTION = 'references/emotion-performance-design.md'


def fixture(body='走廊一盏灯在风里轻轻摇晃。', *, requires=(), features=()):
    task = {'mode': 'prompt', **({'features': list(features)} if features else {})}
    p = w.init({'sources': [{'id': 'S1', 'text': body}],
                'events': [{'id': 'E1', 'source_ids': ['S1'], 'body': body, 'start': 0,
                            'end': 6, **({'requires': list(requires)} if requires else {})}]}, task)
    return task, p


def packet(task,p,m):
    return w.context(task,m,p)


def source_submit(task,p):
    ctx = packet(task,p,'source')
    return w.submit(p,'source',{'checked_event_ids':['E1'], 'source_coverage':{
        u['id']:{'event_ids':['E1'],'reason':'保持灯的初始状态与实际动作。'} for u in ctx['source_units']
    }}, ctx['receipt'])


def design_submit(task,p,m):
    ctx = packet(task,p,m)
    return w.submit(p,m,{'design':{'E1':'保留原场景，灯在走廊里轻轻摇晃。'}},ctx['receipt'])


def finish(task,p):
    c=packet(task,p,'compile')
    body=p['events'][0]['body']
    proofs={item['id']:body for item in c['coverage']}
    p=w.submit(p,'compile',{'text':body,'event_ids':['E1'],'dialogue_ids':[], 'coverage':proofs},c['receipt'])
    c=packet(task,p,'validate')
    return w.submit(p,'validate',{'content_checked':True,'evidence':{'E1':'已对照来源的灯在走廊轻晃。'},
        'coverage':proofs,'limitations':['只核对文字。'],
        'requirement_reviews':{identity:{'status':'met','reason':'最终文字保留了原来走廊的灯与轻晃。'}
                               for identity in proofs}},c['receipt'])


class OnDemandRules(unittest.TestCase):
    def test_simple_silent_packet_does_not_load_specialist_books(self):
        t,p=fixture()
        stages=[s['module'] for s in p['workflow']['plan']['steps']]
        self.assertEqual(stages,['source','camera','compile','validate'])
        for m in stages:
            rules={row['path'] for row in packet(t,p,m)['rules']}
            self.assertFalse(rules & {VFX,SOUND,EMOTION,'references/performance-camera-methods.md'},m)
        self.assertIn('references/video-prompt-template.txt',
                      {row['path'] for row in packet(t,p,'compile')['rules']})

    def test_explicit_and_structured_needs_are_not_dropped_even_for_one_event(self):
        t,p=fixture(requires=['performance'],features=['vfx','sound'])
        for m,path in [('vfx',VFX),('sound',SOUND),('performance',EMOTION),
                       ('camera',VFX),('compile',SOUND),('validate',EMOTION)]:
            self.assertIn(path,{row['path'] for row in packet(t,p,m)['rules']},m)

    def test_registered_dialogue_loads_performance_and_sound_without_vfx(self):
        t, p = fixture()
        p['events'][0]['dialogues'] = [{'id':'D1','speaker':'小梨','text':'灯还亮着。'}]
        p = w.init(p, t)
        self.assertEqual([step['module'] for step in p['workflow']['plan']['steps']],
                         ['source','performance','sound','camera','compile','validate'])
        compiled = {row['path'] for row in packet(t,p,'compile')['rules']}
        self.assertTrue({EMOTION, SOUND} <= compiled)
        self.assertNotIn(VFX, compiled)

    def test_late_discovery_enables_method_without_marking_retained_source_as_old(self):
        body='灯影从墙角剥离，沿地面滑走。'
        t,p=fixture(body)
        p=source_submit(t,p)
        p=w.discover(p,{'reason':'应设计灯影的形态与走向','requirements':[
            {'id':'R:shadow','kind':'vfx','description':'描述剥离与传播的过程',
             'source_ids':['S1'],'event_ids':['E1'],'source_quote':body}]})
        self.assertEqual([r['module'] for r in p['workflow']['results']],['source'])
        self.assertIn(VFX,{row['path'] for row in packet(t,p,'vfx')['rules']})
        self.assertEqual(w.rules_review(p)['changed_modules'],[])
        design_submit(t,p,'vfx')


class SavedRules(unittest.TestCase):
    def test_old_completed_review_retains_valid_prefix_and_can_complete_again(self):
        t,p=fixture()
        done=finish(t,design_submit(t,source_submit(t,p),'camera'))
        old=copy.deepcopy(done)
        original=w.stage_rules
        def changed(project,task,module,coverage):
            rs,candidates=original(project,task,module,coverage)
            if module=='compile':
                rs=[{**row,'text':row['text']+'\n更新：编译核对局部证据。'} if row['path']=='references/modules/compile.md' else row for row in rs]
            return rs,candidates
        with patch.object(w,'stage_rules',side_effect=changed):
            report=w.rules_review(done)
            self.assertEqual(report['state'],'checked_under_older_rules')
            self.assertEqual(report['changed_modules'],['compile'])
            self.assertEqual(report['rerun_modules'],['compile','validate'])
            self.assertEqual(packet(t,done,'validate')['rules_review'],report)
            restarted=w.refresh_rules(done)
            self.assertEqual(w.rules_review(restarted)['state'],'rule_refresh_required')
            self.assertEqual(restarted['workflow']['results'],done['workflow']['results'][:2])
            self.assertEqual(restarted['workflow']['history'][-1]['previous_status'],'text_checked')
            self.assertEqual(restarted['workflow']['history'][-1]['invalidated'],done['workflow']['results'][2:])
            self.assertEqual(restarted['workflow']['repairs'],done['workflow']['repairs'])
            self.assertEqual(w.rules_review(finish(t,restarted))['state'],'current_rules')
        self.assertEqual(done,old)

    def test_old_partial_workflow_cannot_resume_with_a_fresh_receipt_alone(self):
        t,p=fixture()
        p=source_submit(t,p)
        p['workflow']['results'][0]['context_receipt']['rules_hash']='obsolete'
        ctx=packet(t,p,'camera')
        with self.assertRaisesRegex(ValueError,'refresh-rules'):
            w.submit(p,'camera',{'design':{'E1':'保持固定镜头。'}},ctx['receipt'])

    def test_current_workflow_is_not_restarted(self):
        t,p=fixture()
        done=finish(t,design_submit(t,source_submit(t,p),'camera'))
        self.assertEqual(w.rules_review(done)['state'],'current_rules')
        self.assertEqual(w.refresh_rules(done),done)

    def test_change_to_unused_specialist_rule_does_not_trigger_rerun(self):
        t,p=fixture()
        done=finish(t,design_submit(t,source_submit(t,p),'camera'))
        original = rules.rule_text
        def changed(path, module):
            value = original(path, module)
            return value + '\n更新特效规则。' if path == VFX else value
        with patch.object(rules,'rule_text',side_effect=changed):
            self.assertEqual(w.rules_review(done)['state'],'current_rules')
            self.assertEqual(w.refresh_rules(done),done)


if __name__ == '__main__':
    unittest.main()

import copy
import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('workflow',Path(__file__).resolve().parents[1]/'scripts/workflow.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

def project():
    return {'sources':[{'id':'S1','text':'乙先尝试夺剑；甲保剑、推退乙。甲说：退后，我不想伤你。'}],
            'constraints':['无新增人物或武器'],
            'events':[{'id':'E1','source_ids':['S1'],'start':0,'end':2,'body':'乙尝试夺剑','end_state':'甲右手握剑'},
                      {'id':'E2','source_ids':['S1'],'start':2,'end':5,'body':'甲保剑并说话','dialogues':[{'id':'D1','speaker':'甲','text':'退后，我不想伤你。','kind':'dialogue'}]},
                      {'id':'E3','source_ids':['S1'],'start':5,'end':12,'body':'甲推退乙，两人站在桥上'}]}

class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.task={'mode':'prompt','features':['action','performance']}
        self.p=w.init(project(),self.task)
    def source(self):
        self.p=w.submit(self.p,'source',{'checked_event_ids':['E1','E2','E3']})
    def designs(self):
        self.source()
        for m in ['action','performance','camera']:
            self.p=w.submit(self.p,m,{'design':{e['id']:m+'具体动作与观察设计' for e in self.p['events']}})
    def test_routes(self):
        modules=lambda t:[s['module'] for s in w.plan(t)['steps']]
        self.assertEqual(modules({'mode':'prompt','features':[]}),['source','camera','compile','validate'])
        self.assertEqual(modules(self.task),['source','action','performance','camera','compile','validate'])
        self.assertEqual(modules({'mode':'grid','features':['assets','action']}),['source','assets','sampling','validate'])
        self.assertEqual(modules({'mode':'discuss'}),[])
    def test_maintenance_requires_record(self):
        with self.assertRaises(ValueError): w.plan({'mode':'maintain'})
        self.assertEqual(w.plan({'mode':'maintain','authorization':{'explicit':True,'user_request':'按方案修改'}})['steps'][0]['module'],'maintenance')
    def test_unknown_feature(self):
        with self.assertRaises(ValueError): w.plan({'mode':'prompt','features':['whatever']})
    def test_rules_exist(self):
        for paths in w.RULES.values():
            for path in paths: self.assertTrue((w.ROOT/path).is_file(),path)
    def test_no_skipping(self):
        with self.assertRaises(ValueError): w.submit(self.p,'camera',{'design':{}})
    def test_upstream_write_rejected_atomically(self):
        self.source();before=copy.deepcopy(self.p)
        with self.assertRaises(ValueError): w.submit(self.p,'action',{'design':{},'events':[]})
        self.assertEqual(self.p,before)
    def test_unknown_event_design(self):
        self.source()
        with self.assertRaises(ValueError): w.submit(self.p,'action',{'design':{'E9':'不允许'}})
    def test_missing_source(self):
        p=project();p['events'][0]['source_ids']=['not-found']
        with self.assertRaises(ValueError): w.init(p,self.task)
    def test_nan_and_overlap(self):
        for value in (float('nan'),True,-1):
            p=project();p['events'][1]['start']=value
            with self.assertRaises(ValueError): w.validate_project(p)
    def test_upstream_hash_change(self):
        self.p['events'][0]['body']='偷偷改事实'
        with self.assertRaises(ValueError): w.context(self.task,'camera',self.p)
    def test_context_scope_and_neighbors(self):
        p=project();p['master_sections']={e['id']:e['body'] for e in p['events']}
        task={'mode':'revise','scope':['E2'],'features':['performance']}
        p=w.init(p,task);ctx=w.context(task,'performance',p)
        self.assertEqual([e['id'] for e in ctx['events']],['E2'])
        self.assertEqual([e['id'] for e in ctx['adjacent_states']],['E1','E3'])
        self.assertNotIn('sources',ctx)
    def test_wrong_context_task(self):
        with self.assertRaises(ValueError):w.context({'mode':'prompt','features':[]},'camera',self.p)
    def test_compile_preserves_dialogue(self):
        self.designs()
        payload={'text':'甲推退乙。','event_ids':['E1','E2','E3'],'dialogue_ids':['D1']}
        with self.assertRaises(ValueError):w.submit(self.p,'compile',payload)
        payload['text']='甲说：“退后，我不想伤你。”甲推退乙。'
        self.p=w.submit(self.p,'compile',payload)
        self.assertIn('退后，我不想伤你。',self.p['video_master_prompt'])
    def test_missing_event(self):
        self.designs()
        with self.assertRaises(ValueError):w.submit(self.p,'compile',{'text':'退后，我不想伤你。','event_ids':['E1'],'dialogue_ids':['D1']})
    def test_repair_preserves_history_and_invalidates_downstream(self):
        self.designs();before=copy.deepcopy(self.p['events'])
        self.p=w.repair(self.p,'action','动作支撑无法完成，需要改编排')
        self.assertEqual([r['module'] for r in self.p['workflow']['results']],['source'])
        self.assertEqual(len(self.p['workflow']['history'][0]['invalidated']),3)
        self.assertEqual(self.p['events'],before)
        with self.assertRaises(ValueError):w.submit(self.p,'camera',{'design':{}})
    def test_repair_budget(self):
        self.source()
        for i in range(2):
            self.p=w.repair(self.p,'source','需要重新核对来源')
            self.source()
        with self.assertRaises(ValueError):w.repair(self.p,'source','再来一次')
    def test_sampling_does_not_replace_events(self):
        p=project();p['video_master_prompt']='完整主稿'
        task={'mode':'grid'};p=w.init(p,task);p=w.submit(p,'source',{'checked_event_ids':['E1','E2','E3']})
        before=copy.deepcopy(p['events'])
        panels=[{'id':f'P{i}','event_ids':['E1'],'sample_time':i/8,'prompt':'甲乙交锋的不同观察状态'} for i in range(9)]
        p=w.submit(p,'sampling',{'panels':panels})
        self.assertEqual(p['events'],before)
        self.assertEqual(len(p['panels']),9)
    def test_bad_sample(self):
        p=project();p['video_master_prompt']='完整主稿';p=w.init(p,{'mode':'grid'});p=w.submit(p,'source',{'checked_event_ids':['E1','E2','E3']})
        with self.assertRaises(ValueError):w.submit(p,'sampling',{'panels':[{'id':str(i),'event_ids':['E1'],'sample_time':99,'prompt':'越界'} for i in range(9)]})
    def test_workbench_bridge_requires_planning_then_preserves_events(self):
        p=project();p['video_master_prompt']='完整主稿';p=w.init(p,{'mode':'grid'})
        with self.assertRaises(ValueError):w.to_workbench(p)
        p=w.submit(p,'source',{'checked_event_ids':['E1','E2','E3']})
        p=w.submit(p,'sampling',{'panels':[{'id':f'P{i}','event_ids':['E1'],'sample_time':i/8,'prompt':'不同的采样状态'} for i in range(9)]})
        p=w.submit(p,'validate',{'content_checked':True,'evidence':{e['id']:'主稿与采样映射有具体核对证据' for e in p['events']},'limitations':['尚未出图']})
        output=w.to_workbench(p);board=output['segments'][0]
        self.assertEqual(board['events'],p['events']);self.assertEqual(len(board['panels']),9)
        self.assertFalse(board['completed']);self.assertEqual(board['image_data_url'],'')
    def test_single_panel_preserves_others(self):
        p=project();p['video_master_prompt']='完整主稿';p['panels']=[{'id':f'P{i}','event_ids':['E1'],'sample_time':1,'prompt':'原图'} for i in range(9)]
        task={'mode':'edit_grid','target_panel_id':'P3','image_version':'v1','coordinates':[0,0,100,100]}
        p=w.init(p,task);p=w.submit(p,'source',{'checked_event_ids':['E1','E2','E3']})
        old=copy.deepcopy(p['panels']);p=w.submit(p,'sampling',{'panels':[{'id':'P3','event_ids':['E1'],'sample_time':1,'prompt':'仅改此格'}]})
        self.assertEqual([x for x in p['panels'] if x['id']!='P3'],[x for x in old if x['id']!='P3'])
    def test_validation_needs_evidence(self):
        self.designs();self.p=w.submit(self.p,'compile',{'text':'退后，我不想伤你。','event_ids':['E1','E2','E3'],'dialogue_ids':['D1']})
        with self.assertRaises(ValueError):w.submit(self.p,'validate',{'content_checked':True,'evidence':{},'limitations':[]})
        self.p=w.submit(self.p,'validate',{'content_checked':True,'evidence':{i:'正文与原文已逐项核对的证据记录' for i in ('E1','E2','E3')},'limitations':['未成片']})
        self.assertEqual(self.p['workflow']['status'],'text_checked')
    def test_revision_preserves_other_sections(self):
        p=project();p['master_sections']={'E1':'旧第一段','E2':'旧第二段','E3':'旧第三段'}
        task={'mode':'revise','scope':['E2'],'features':[]};p=w.init(p,task)
        p=w.submit(p,'source',{'checked_event_ids':['E2']});p=w.submit(p,'camera',{'design':{'E2':'保持当前双人关系景，连续动作'}})
        p=w.submit(p,'compile',{'text':'新第二段：退后，我不想伤你。','event_ids':['E2'],'dialogue_ids':['D1']})
        self.assertEqual(p['master_sections']['E1'],'旧第一段');self.assertEqual(p['master_sections']['E3'],'旧第三段')
        self.assertIn('新第二段',p['video_master_prompt'])

if __name__=='__main__':unittest.main()

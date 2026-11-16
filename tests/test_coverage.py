import copy,importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('coverage_flow',Path(__file__).resolve().parents[1]/'scripts/workflow.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

def base():
    return {'sources':[{'id':'S1','text':'甲挥剑，乙格挡。\n甲说：车票收好。\n乙说：好。\n此处另有内心独白。'}],
    'events':[{'id':'E1','start':0,'end':5,'source_ids':['S1'],'body':'甲挥剑，乙格挡','dialogues':[{'id':'D1','speaker':'甲','text':'车票收好。'},{'id':'D2','speaker':'乙','text':'好。'}]}]}
def packet(p,m):return w.context(p['workflow']['plan']['task'],m,p)['receipt']
def source(p,covered=None):
    return w.submit(p,'source',{'checked_event_ids':['E1'],'source_coverage':covered if covered is not None else {u['id']:{'event_ids':['E1'],'reason':'原段落事实已对应E1，发声与动作继续保留'} for u in w.source_units(p,p['workflow']['plan']['task'])}},packet(p,'source'))
def design(p,m):return w.submit(p,m,{'design':{'E1':'原文关联的具体专业设计，不改剧情及对白'}},packet(p,m))
def compile_payload(p,text):
    cursor=0;utterances=[]
    for d in p['events'][0]['dialogues']:
        a=text.find(d['text'],cursor);b=a+len(d['text']);utterances.append({'id':d['id'],'speaker':d['speaker'],'start':a,'end':b});cursor=b
    return {'text':text,'event_ids':['E1'],'dialogue_ids':['D1','D2'],'utterances':utterances,'coverage':{r['id']:{'start':0,'end':len(text)} for r in p['workflow']['plan']['coverage']}}

class CoverageTest(unittest.TestCase):
    def setUp(self):self.task={'mode':'prompt','features':[]};self.p=w.init(base(),self.task)
    def to_compile(self):
        p=source(self.p)
        for m in ['action','performance','sound','camera']:p=design(p,m)
        return p
    def test_omitted_flags_are_filled_from_dialogue_and_action_signal(self):
        self.assertEqual([s['module'] for s in self.p['workflow']['plan']['steps']],['source','action','performance','sound','camera','compile','validate'])
        self.assertTrue(any('auto requirement' in s['reason'] for s in self.p['workflow']['plan']['steps']))
    def test_explicit_non_keyword_capability_is_covered(self):
        p=base();p['events'][0]['body']='两人按约定完成变化';p['events'][0]['requires']=['vfx']
        self.assertIn('vfx',[s['module'] for s in w.init(p,self.task)['workflow']['plan']['steps']])
    def test_os_requires_sound(self):
        p=base();p['events'][0]['dialogues'][0]['kind']='OS'
        self.assertIn('sound',[s['module'] for s in w.init(p,self.task)['workflow']['plan']['steps']])
    def test_asset_catalog_requires_asset_matching(self):
        p=base();p['assets']=[{'id':'CH01','path':'reference.jpg'}]
        self.assertIn('assets',[s['module'] for s in w.init(p,self.task)['workflow']['plan']['steps']])
    def test_requirement_added_to_existing_module_invalidates_that_module(self):
        p=self.to_compile()
        p=w.discover(p,{'reason':'表演需要补核对已知原句态度','requirements':[{'id':'R:performance','kind':'performance','description':'原句的回应关系','event_ids':['E1'],'source_ids':['S1'],'source_quote':'乙说：好。'}]})
        self.assertEqual([r['module'] for r in p['workflow']['results']],['source','action'])
    def test_reinit_archives_old_results(self):
        p=source(self.p);old=copy.deepcopy(p['workflow']);p=w.init(p,self.task)
        self.assertEqual(p['workflow_archives'][-1],old)
        self.assertEqual(p['workflow']['cursor'],0)
    def test_old_receipt_rejected_after_new_rule_revision(self):
        p=self.to_compile();old=packet(p,'compile')
        p=w.discover(p,{'reason':'补入原文声音','requirements':[{'id':'R:late','kind':'sound','description':'独白关系','event_ids':['E1'],'source_ids':['S1'],'source_quote':'内心独白'}]})
        p=design(p,'sound');p=design(p,'camera')
        with self.assertRaisesRegex(ValueError,'receipt'):w.submit(p,'compile',compile_payload(p,'甲：“车票收好。”\n乙：“好。”'),old)
    def test_no_receipt_rejected(self):
        with self.assertRaisesRegex(ValueError,'context receipt'):w.submit(self.p,'source',{'checked_event_ids':['E1']})
    def test_missing_source_paragraph_is_blocked(self):
        units=w.source_units(self.p,self.task)
        self.assertEqual(len(units),4)
        with self.assertRaisesRegex(ValueError,'paragraph coverage'):source(self.p,{units[0]['id']:{'event_ids':['E1'],'reason':'仅登记第一段'}})
    def test_stale_receipt_rejected_after_repair(self):
        old=packet(self.p,'source');p=source(self.p);p=w.repair(p,'source','重新复核来源')
        with self.assertRaisesRegex(ValueError,'receipt'):w.submit(p,'source',{'checked_event_ids':['E1']},old)
    def test_late_sound_discovery_refreshes_affected_stage_and_keeps_prior_design(self):
        p=self.to_compile();before=copy.deepcopy(p['events'])
        p=w.discover(p,{'reason':'摄影发现内心独白需要核对口型','requirements':[{'id':'R:OS','kind':'sound','description':'内心独白声画关系','event_ids':['E1'],'source_ids':['S1'],'source_quote':'此处另有内心独白。'}]})
        self.assertEqual([r['module'] for r in p['workflow']['results']],['source','action','performance'])
        self.assertEqual(p['workflow']['plan']['steps'][p['workflow']['cursor']]['module'],'sound')
        self.assertEqual(p['events'],before);self.assertEqual([r['module'] for r in p['workflow']['history'][-1]['invalidated']],['sound','camera'])
        with self.assertRaises(ValueError):w.submit(p,'camera',{'design':{'E1':'试图跳过新声音工序'}},packet(p,'camera'))
        p=design(p,'sound');p=design(p,'camera');self.assertEqual(p['workflow']['plan']['steps'][p['workflow']['cursor']]['module'],'compile')
    def test_discovery_cannot_invent_ability(self):
        with self.assertRaisesRegex(ValueError,'existing source'):w.discover(self.p,{'reason':'乱加能力','requirements':[{'id':'R:fake','kind':'vfx','description':'新增龙形法术','event_ids':['E1'],'source_ids':['S1'],'source_quote':'龙形法术'}]})
    def test_discovery_outside_scope_and_duplicate_rejected(self):
        request={'reason':'补调','requirements':[{'id':'R:new','kind':'sound','description':'声音关系','event_ids':['unknown'],'source_ids':['S1'],'source_quote':'内心独白'}]}
        with self.assertRaises(ValueError):w.discover(self.p,request)
    def test_nested_dialogue_no_false_positive(self):
        p=self.to_compile();text='甲：“车票收好。”\n乙：“好。”'
        p=w.submit(p,'compile',compile_payload(p,text),packet(p,'compile'))
        self.assertEqual(p['video_master_prompt'],text)
    def test_extra_spoken_line_rejected(self):
        p=self.to_compile();text='甲：“车票收好。”\n乙：“好。”\n乙：“好。”'
        with self.assertRaisesRegex(ValueError,'spoken dialogue'):w.submit(p,'compile',compile_payload(p,text),packet(p,'compile'))
    def test_unquoted_duplicate_of_registered_dialogue_rejected(self):
        p=self.to_compile();text='甲：“车票收好。”\n乙：“好。”\n乙又低声说：好。'
        with self.assertRaisesRegex(ValueError,'unregistered repeated spoken dialogue'):
            w.submit(p,'compile',compile_payload(p,text),packet(p,'compile'))
    def test_bad_or_missing_output_evidence_is_blocked(self):
        p=self.to_compile();text='甲：“车票收好。”\n乙：“好。”';payload=compile_payload(p,text)
        payload['coverage'].pop(next(iter(payload['coverage'])))
        with self.assertRaisesRegex(ValueError,'coverage missing'):w.submit(p,'compile',payload,packet(p,'compile'))
        payload=compile_payload(p,text);payload['coverage'][next(iter(payload['coverage']))]='不在正文里的伪造引文'
        with self.assertRaisesRegex(ValueError,'actual output'):w.submit(p,'compile',payload,packet(p,'compile'))
    def test_unknown_requirement_links_blocked(self):
        p=base();p['requirements']=[{'id':'R1','kind':'performance','description':'人物反应','source_ids':['S1'],'event_ids':['bad']}]
        with self.assertRaisesRegex(ValueError,'unknown events'):w.init(p,self.task)
    def test_full_coverage_reaches_text_state_only(self):
        p=self.to_compile();text='甲：“车票收好。”\n乙：“好。”';payload=compile_payload(p,text)
        p=w.submit(p,'compile',payload,packet(p,'compile'))
        with self.assertRaisesRegex(ValueError,'validation fields'):w.submit(p,'validate',{'content_checked':True,'evidence':{'E1':'真实的语义核对仍需模型执行'},'limitations':[]},packet(p,'validate'))
        p=w.submit(p,'validate',{'content_checked':True,'evidence':{'E1':'负向测试夹具只验证结构门禁，不代表语义事实通过'},'coverage':payload['coverage'],'requirement_reviews':{k:{'status':'met','reason':'测试使用具有原文联系的完整句子'} for k in payload['coverage']},'limitations':['结构测试，未验证成片']},packet(p,'validate'))
        self.assertEqual(p['workflow']['status'],'text_checked')
    def test_legacy_state_cannot_silently_pass(self):
        p=copy.deepcopy(self.p);p['workflow'].pop('contract_version')
        with self.assertRaisesRegex(ValueError,'legacy workflow'):w.state(p)

if __name__=='__main__':unittest.main()

"""Six creative methods reach owners and final prose; not aesthetic scoring."""
import copy
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w

METHODS = {
 'narrative-event-design': ('source',),
 'dialogue-relationship-design': ('source', 'performance', 'sound'),
 'character-prop-design': ('assets', 'action'),
 'scene-space-design': ('assets', 'action', 'camera'),
 'art-style-material-design': ('assets', 'vfx', 'camera'),
 'lighting-color-design': ('assets', 'vfx', 'camera'),
}

def fixture():
 return {'sources':[{'id':'C1','origin':'creative_addition','text':'甲搬开已有木箱取得通道；他说：“请让开。”；铜钥匙缺角，门在西侧，3D硬边漆木，门缝暖光被身体挡住。'}],
         'events':[{'id':'E1','source_ids':['C1'],'start':0,'end':5,'body':'甲搬箱取得通道，门缝光被身体挡住。',
                    'dialogues':[{'id':'D1','speaker':'甲','text':'请让开。'}],
                    'requires':['assets','action','performance','vfx','sound']}],
         'requirements':[{'id':'R:'+str(i),'kind':k,'source_ids':['C1'],'event_ids':['E1'],'description':d} for i,(k,d) in enumerate([
             ('plot','搬箱改变通道'),('performance','请让开是请求而非吼令'),('asset','铜钥匙缺角'),
             ('asset','门在西侧'),('asset','3D硬边漆木'),('camera','门缝暖光被身体挡住')])],
         'globals':{'style':'风格化3D，不是写实真人'}}

class PrepromptSix(unittest.TestCase):
 def test_all_owner_and_final_contexts_receive_current_full_rules(self):
  t={'mode':'prompt'};p=w.init(fixture(),t)
  for name,owners in METHODS.items():
   path='references/'+name+'.md'
   for m in (*owners,'compile','validate'):
    c=w.context(t,m,p);r={x['path']:x['text'] for x in c['rules']}
    self.assertTrue(path in r,(name,m));self.assertEqual(r[path],(ROOT/path).read_text(encoding='utf-8'))
    self.assertEqual(c['receipt']['rules_hash'],w.fingerprint(c['rules']))
 def test_each_method_has_choices_interfaces_cases_and_repair(self):
  for name in METHODS:
   s=(ROOT/('references/'+name+'.md')).read_text(encoding='utf-8')
   for cue in ['设计方法','交接','不足','方向','返修','不']:
    self.assertTrue(cue in s,(name,cue))
  s=(ROOT/'references/creation-preparation.md').read_text(encoding='utf-8')
  for name in METHODS:self.assertTrue(name+'.md' in s,name)
 def test_actual_handoff_and_six_distinct_prose_proofs(self):
  t={'mode':'prompt'};p=w.init(fixture(),t);c=w.context(t,'source',p)
  p=w.submit(p,'source',{'checked_event_ids':['E1'],'source_coverage':{u['id']:{'event_ids':['E1'],'reason':'原创夹具明确六项已有事实，不增加人物关系或改原句。'} for u in c['source_units']}},c['receipt'])
  design='铜钥匙缺角；门在西侧；风格化3D硬边漆木；甲搬开已有木箱取得通道，身体挡住门缝暖光。'
  while p['workflow']['plan']['steps'][p['workflow']['cursor']]['module']!='compile':
   m=p['workflow']['plan']['steps'][p['workflow']['cursor']]['module'];c=w.context(t,m,p)
   if m=='camera':
    prior={r['module']:r['payload'] for r in c['upstream']};self.assertEqual(prior['assets']['design']['E1'],design)
   p=w.submit(p,m,{'design':{e['id']:design for e in c['events']}},c['receipt'])
  c=w.context(t,'compile',p)
  text='甲搬开已有木箱取得通道，手持缺角铜钥匙走向西侧的门。造型保持风格化3D硬边漆木，门缝暖光被身体挡住。\n甲（轻声请求，不是吼令）：“请让开。”'
  proofs={r['id']:'甲搬开已有木箱取得通道' for r in c['coverage']}
  for i,q in enumerate(['甲搬开已有木箱取得通道','轻声请求，不是吼令','缺角铜钥匙','西侧的门','风格化3D硬边漆木','门缝暖光被身体挡住']):proofs['R:'+str(i)]=q
  proofs['dialogue:D1']='请让开。';a=text.index('请让开。')
  payload={'text':text,'event_ids':['E1'],'dialogue_ids':['D1'],'coverage':proofs,'utterances':[{'id':'D1','speaker':'甲','start':a,'end':a+4}]}
  bad=copy.deepcopy(payload);del bad['coverage']['R:4']
  with self.assertRaises(ValueError):w.submit(copy.deepcopy(p),'compile',bad,c['receipt'])
  p=w.submit(p,'compile',payload,c['receipt']);c=w.context(t,'validate',p)
  self.assertEqual(p['video_master_prompt'],text)
  self.assertTrue({f'R:{i}' for i in range(6)}<={r['id'] for r in c['coverage']})

if __name__=='__main__':unittest.main()

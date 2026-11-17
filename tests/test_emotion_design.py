import sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
import workflow as w
class EmotionDesign(unittest.TestCase):
 def test_real_context(self):
  t={'mode':'prompt'};p=w.init({'sources':[{'id':'S1','text':'甲发现乙回来，继续手上任务。'}],'events':[{'id':'E1','source_ids':['S1'],'start':0,'end':4,'body':'甲发现乙回来，继续手上任务。','requires':['action','performance','sound']}]},t)
  for m in ['performance','action','sound','camera','compile','validate']:
   c=w.context(t,m,p);rules={r['path']:r['text'] for r in c['rules']};path='references/emotion-performance-design.md'
   self.assertTrue(path in rules,m);self.assertEqual(rules[path],(R/path).read_text(encoding='utf-8'));self.assertEqual(c['receipt']['rules_hash'],w.fingerprint(c['rules']))
 def test_actual_emotion_handoff(self):
  t={'mode':'prompt'};p=w.init({'sources':[{'id':'S1','text':'甲看见乙回来，没有说话，继续折衣。'}],'events':[{'id':'E1','source_ids':['S1'],'start':0,'end':4,'body':'甲看见乙回来，没有说话，继续折衣。','requires':['performance','sound']}]},t)
  c=w.context(t,'source',p)
  p=w.submit(p,'source',{'checked_event_ids':['E1'],'source_coverage':{u['id']:{'event_ids':['E1'],'reason':'夹具保存静默任务与原事件，不新增关系或心理事实'} for u in c['source_units']}},c['receipt'])
  performance='甲听到门响才抬眼，认出乙后下颌略松；笑意未完全展开便回到折衣，下一镜保留放松后的状态。'
  while p['workflow']['plan']['steps'][p['workflow']['cursor']]['module']!='compile':
   m=p['workflow']['plan']['steps'][p['workflow']['cursor']]['module'];c=w.context(t,m,p)
   if m=='camera':
    prior={r['module']:r['payload'] for r in c['upstream']};self.assertEqual(prior['performance']['design']['E1'],performance)
   d=performance if m=='performance' else '沿用已定静默事件，保留门响、任务和表演可见条件，不新增台词。'
   p=w.submit(p,m,{'design':{e['id']:d for e in c['events']}},c['receipt'])
  c=w.context(t,'compile',p);prior={r['module']:r['payload'] for r in c['upstream']};self.assertEqual(prior['performance']['design']['E1'],performance)
 def test_method_and_cues(self):
  s=(R/'references/emotion-performance-design.md').read_text(encoding='utf-8')
  for cue in ['眉与眼睑','嘴唇、口角、下颌','混合情绪','跨镜','无对白','闭眼呼气','编译保真','0.5秒','requirement_reviews','fix_scope']:
   self.assertIn(cue,s)
  s=(R/'references/microexpression-cues.md').read_text(encoding='utf-8');self.assertIn('不固定通道数',s);self.assertNotIn('2-4',s)
 def test_roles_and_template(self):
  for m in ['performance','action','sound','camera','compile','validate','assets','vfx','sampling']:
   self.assertIn('emotion-performance-design.md',(R/f'references/modules/{m}.md').read_text(encoding='utf-8'))
  a=R/'references/video-prompt-template.txt';self.assertNotIn('情绪复核',a.read_text(encoding='utf-8'))
if __name__=='__main__':unittest.main()

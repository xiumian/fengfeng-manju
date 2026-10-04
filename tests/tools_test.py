import unittest,importlib.util,sys,tempfile,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_prompt import validate_text
class Tools(unittest.TestCase):
 def test_good_prompt(self):
  t='【全局基调设定】：国漫。\n【片段1】【4秒】\n——[0—2秒]：【起身】\n甲起身。\n动态元素：起身。\n【音效】脚步。\n——[2—4秒]：【回望】\n甲回头。\n【台词】[2—3秒] 甲：“谁？”\n【音效】说话。'
  self.assertFalse(validate_text(t,4)['errors'])
 def test_bad_timing(self):
  r=validate_text('——[0—2秒]：【甲】\n动作。\n——[1—4秒]：【乙】\n动作。',4)
  self.assertTrue(any('重叠' in e for e in r['errors']))
 def test_bad_dialogue(self):
  r=validate_text('——[0—2秒]：【甲】\n动作。\n【台词】[3—4秒] 甲：“谁？”',2)
  self.assertTrue(any('台词' in e for e in r['errors']))
 def test_tools_exist(self):
  for name in ['serve_workbench.py','check_package.py','build_board_lite.py','generate_emotion_curve.py']:
   self.assertTrue((ROOT/'scripts'/name).is_file(),name)

class SourceChecks(unittest.TestCase):
 def test_os_warning(self):
  r=validate_text('【全局基调设定】：16:9。\n——[0—3秒]：【独白】\n甲嘴唇开合说话。OS内心独白：“离开。”\n【音效】风声。',3)
  self.assertTrue(any('画外' in x for x in r['warnings']))
 def test_missing_aspect_warning(self):
  self.assertTrue(any('画幅' in x for x in validate_text('——[0—3秒]：【动作】\n甲抬手。\n【音效】风声。',3)['warnings']))
 def test_missing_tone_and_speech_budget(self):
  r=validate_text('——[0—2秒]：【说话】\n甲开口。\n【台词】[0—1秒] 甲：“这一段很长的台词不应该被塞进一秒里面。”\n【音效】对白。',2)
  self.assertTrue(any('语气' in x for x in r['warnings']));self.assertTrue(any('容量' in x for x in r['warnings']))


class FurtherSourceChecks(unittest.TestCase):
 def test_tone_prop_conflict_is_warned(self):
  t='【全局基调设定】：16:9。\n——[0—3秒]：【宣判】\n甲把玩玉佩。\n【台词】[1—2秒] 甲（厉声宣判）：“跪下。”\n【音效】风声。'
  self.assertTrue(any('语气' in x and '道具' in x for x in validate_text(t,3)['warnings']))
 def test_reflection_mapping_is_warned(self):
  t='【全局基调设定】：16:9。\n——[0—3秒]：【玉佩】\n甲举起玉佩对着灯，玉佩映出火苗。\n【音效】风声。'
  self.assertTrue(any('光路' in x for x in validate_text(t,3)['warnings']))

if __name__=='__main__':unittest.main()

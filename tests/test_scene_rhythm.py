"""Scene planning guidance and actual delivery, not aesthetic scoring."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import workflow as w

PATH='references/scene-rhythm-planning.md'


class SceneRhythm(unittest.TestCase):
    def test_method_has_scene_pressure_turn_budget_and_shot_distinction(self):
        text=(ROOT/PATH).read_text(encoding='utf-8')
        for cue in ['剧情目标','强弱变化','转折','时间预算','节奏段不等于镜头','不固定九段','不机械均分',
                    '并行','容量冲突','不以不等长作为合格条件','后台']:
            self.assertIn(cue,text)

    def test_five_stages_receive_relevant_method_sections(self):
        task={'mode':'prompt'}
        p=w.init({'sources':[{'id':'S1','text':'甲护送乙离开，受阻后借空当脱身。'}],
            'events':[{'id':'E1','source_ids':['S1'],'body':'甲护送乙离开，受阻后借空当脱身。',
                       'start':0,'end':12,'requires':['action']}]},task)
        for module in ['source','action','camera','compile','validate']:
            with self.subTest(module=module):
                ctx=w.context(task,module,p)
                rules={r['path']:r['text'] for r in ctx['rules']}
                self.assertIn(PATH,rules)
                self.assertIn('按观看容量分配时间预算',rules[PATH])
                if module == 'source':
                    self.assertEqual(rules[PATH],(ROOT/PATH).read_text(encoding='utf-8'))
                self.assertEqual(ctx['receipt']['rules_hash'],w.fingerprint(ctx['rules']))

    def test_entry_preparation_and_owners_reference_unique_method(self):
        for path in ['SKILL.md','references/creation-preparation.md','references/modules/action.md',
                     'references/modules/camera.md','references/modules/compile.md','references/modules/validate.md']:
            self.assertIn('scene-rhythm-planning.md',(ROOT/path).read_text(encoding='utf-8'))


if __name__=='__main__':unittest.main()

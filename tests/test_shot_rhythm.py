"""Shot-duration guidance, real rule delivery and existing subsecond metadata."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import workflow as w
from workflow_delivery import timing_node_ranges

PATH='references/shot-rhythm-planning.md'


class ShotRhythm(unittest.TestCase):
    def test_subsecond_readability_continuity_and_long_shot_review(self):
        text=(ROOT/PATH).read_text(encoding='utf-8')
        for cue in ['0.5秒','1.5—3.5秒','6秒','没有通用下限或上限','动作节点','信息可读性','前后承接',
                    '整场节奏','单镜节奏','不是越短越好','动作尚未结束','观看收益','后台']:
            self.assertIn(cue,text)

    def test_four_owners_receive_the_relevant_method_sections(self):
        task={'mode':'prompt'}
        p=w.init({'sources':[{'id':'S1','text':'来袭被挡，掌心初裂，甲继续推进。'}],
            'events':[{'id':'E1','source_ids':['S1'],'body':'来袭被挡，掌心初裂，甲继续推进。',
                       'start':0,'end':3,'requires':['action']}]},task)
        for module in ['action','camera','compile','validate']:
            with self.subTest(module=module):
                ctx=w.context(task,module,p)
                rule={r['path']:r['text'] for r in ctx['rules']}
                self.assertIn(PATH,rule)
                self.assertIn('职责、交接与交付',rule[PATH])
                if module in ('camera','validate'):
                    self.assertEqual(rule[PATH],(ROOT/PATH).read_text(encoding='utf-8'))
                self.assertEqual(ctx['receipt']['rules_hash'],w.fingerprint(ctx['rules']))

    def test_half_second_cut_is_accepted_by_existing_timing_contract(self):
        headings=['——0—1.2秒：【受阻】','——1.2—1.7秒：【初裂】','——1.7—2.2秒：【察觉】','——2.2—3秒：【推进】']
        text='\n'.join(h+'\n连续动作与实际接触。' for h in headings)
        nodes=[{'heading':h,'start':a,'end':b} for h,a,b in zip(headings,[0,1.2,1.7,2.2],[1.2,1.7,2.2,3])]
        result=timing_node_ranges(text,nodes,3)
        self.assertEqual(len(result),4)

    def test_separate_scene_method_and_role_interfaces(self):
        for path in ['SKILL.md','references/scene-rhythm-planning.md','references/modules/action.md',
                     'references/modules/camera.md','references/modules/compile.md','references/modules/validate.md']:
            self.assertIn('shot-rhythm-planning.md',(ROOT/path).read_text(encoding='utf-8'))


if __name__=='__main__':unittest.main()

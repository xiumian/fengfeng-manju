"""Re-run the audit's scope, provenance, and delivery counterexamples."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import workflow as w


def project():
    return {'sources': [{'id':'S1', 'text':'一束幻想光焰散成粒子。\n门铃响起。'}],
            'events': [{'id':'E1', 'body':'一束幻想光焰散成粒子。', 'source_ids':['S1'], 'start':0, 'end':2},
                       {'id':'E2', 'body':'门铃响起。', 'source_ids':['S1'], 'start':2, 'end':5}]}


def submit(p, module, payload):
    task = p['workflow']['plan']['task']
    return w.submit(p, module, payload, w.context(task, module, p)['receipt'])


def source_payload(p):
    task = p['workflow']['plan']['task']
    return {'checked_event_ids':['E1','E2'], 'source_coverage': {
        unit['id']: {'event_ids':['E1' if unit['id']=='S1:L1' else 'E2'], 'reason':'来源与事件逐句核对'}
        for unit in w.source_units(p, task)}}


class AuditRegressions(unittest.TestCase):
    def test_source_cannot_skip_or_relabel_a_whole_unlinked_document(self):
        p = project()
        p['sources'].append({'id':'S2','text':'她留下一把钥匙。'})
        p = w.init(p, {'mode':'prompt'})
        packet = w.context({'mode':'prompt'}, 'source', p)
        self.assertEqual([s['id'] for s in packet['sources']], ['S1','S2'])
        payload = source_payload(p)
        with self.assertRaisesRegex(ValueError, 'not linked'):
            submit(p, 'source', payload)
        del payload['source_coverage']['S2:L1']
        with self.assertRaisesRegex(ValueError, 'paragraph coverage'):
            submit(p, 'source', payload)

    def test_asset_registry_and_specialized_rules_are_delivered_by_owner(self):
        p = project()
        p['assets'] = [{'id':'A','name':'蓝色光焰','description':'在末态中极小'}]
        p = w.init(p, {'mode':'prompt'})
        self.assertEqual(w.context({'mode':'prompt'}, 'assets', p)['assets'][0]['name'], '蓝色光焰')
        for module, identity in (('vfx','E1'), ('sound','E2')):
            packet = w.context({'mode':'prompt'}, module, p)
            self.assertEqual([e['id'] for e in packet['events']], [identity])
        packet = w.context({'mode':'prompt'}, 'vfx', p)
        self.assertIn('references/vfx-techniques.md', [rule['path'] for rule in packet['rules']])
        self.assertEqual(packet['receipt']['rules_hash'], w.fingerprint(packet['rules']))

    def test_module_rejects_unassigned_padding_and_accepts_owned_event(self):
        p = w.init(project(), {'mode':'prompt'})
        p = submit(p, 'source', source_payload(p))
        with self.assertRaisesRegex(ValueError, 'assigned events'):
            submit(p, 'vfx', {'design': {'E1':'粒子轻微离散', 'E2':'N/A'}})
        self.assertEqual(set(submit(p,'vfx',{'design':{'E1':'粒子轻微离散'}})['workflow']['results'][-1]['payload']['design']), {'E1'})

    def test_reused_or_spoken_only_coverage_rejected(self):
        items = [{'id':'R1','kind':'action','event_ids':['E1'],'origin':'explicit'},
                 {'id':'R2','kind':'plot','event_ids':['E2'],'origin':'explicit'}]
        with self.assertRaisesRegex(ValueError, 'unrelated'):
            w.verify_evidence(items, {'R1':'光焰散开。', 'R2':'光焰散开。'}, '灯响。光焰散开。')
        with self.assertRaisesRegex(ValueError, 'spoken words'):
            w.verify_evidence(items, {'R1':'好。', 'R2':'灯响。'}, '好。灯响。', [{'start':0,'end':2}])
        with self.assertRaisesRegex(ValueError, 'unresolved'):
            w.verify_reviews(items[:1], {'R1':{'status':'unresolved','reason':'未描述必要的画面结果'}})

    def test_grid_rejects_identical_observations_and_preserves_camera_metadata(self):
        p = project()
        p['video_master_prompt'] = p['sources'][0]['text']
        p = w.init(p, {'mode':'grid'})
        p = submit(p, 'source', source_payload(p))
        rows = [{'id':f'P{i}', 'event_ids':['E1'], 'sample_time':0.5, 'prompt':'同样画面',
                 'shot_size':'特写', 'camera_move':'横移'} for i in range(9)]
        with self.assertRaisesRegex(ValueError,'distinct sample times'):
            submit(p,'sampling',{'panels':rows})
        for i, row in enumerate(rows):
            row['sample_time'] = i / 5
        with self.assertRaisesRegex(ValueError,'distinct observation descriptions'):
            submit(p,'sampling',{'panels':rows})
        for i, row in enumerate(rows):
            row['prompt'] = f'光焰处于第 {i+1} 个观察状态。'
        p = submit(p,'sampling',{'panels':rows})
        proofs={item['id']: item['description'] for item in p['workflow']['plan']['coverage']}
        p = submit(p, 'validate', {'content_checked':True, 'evidence':{'E1':'取样来自光焰消散的实际过程','E2':'源文和主稿均保留门铃响起'},
              'coverage':proofs, 'limitations':['静态采样方案'], 'requirement_reviews':{
                  key:{'status':'met','reason':'对应主稿可明确定位的原文事实'} for key in proofs}})
        row = w.to_workbench(p)['segments'][0]['panels'][0]
        self.assertEqual((row['shot_size'],row['camera_move'],row['duration']),('特写','横移',None))

    def test_model_duration_is_distinct_from_editorial_plan(self):
        with self.assertRaisesRegex(ValueError, 'split'):
            w.plan({'mode':'prompt','delivery':{'model':'seedance-2.0','duration':30}})
        w.plan({'mode':'prompt','delivery':{'model':'seedance-2.5','duration':30}})
        text = '前言\n——【节点1】\n光焰散开。\n——【节点2】\n门铃响起。'
        nodes = [{'heading':'——【节点1】','start':0,'end':2}, {'heading':'——【节点2】','start':2,'end':5}]
        self.assertEqual(w.timing_node_ranges(text,nodes,5)[-1][1],5)
        with self.assertRaisesRegex(ValueError, 'requested delivery duration'):
            w.timing_node_ranges(text,nodes,4)

    def test_discovered_camera_uses_the_existing_stage_once(self):
        p = w.init(project(), {'mode':'prompt'})
        p = submit(p,'source',source_payload(p))
        p = w.discover(p, {'reason':'确保光焰的变化可见','requirements':[
            {'id':'R:camera','kind':'camera','source_ids':['S1'],'event_ids':['E1'],
             'source_quote':'一束幻想光焰散成粒子。','description':'观众需要看清粒子离开主形'}]})
        plan = p['workflow']['plan']
        self.assertEqual([step['module'] for step in plan['steps']].count('camera'), 1)
        self.assertEqual([result['module'] for result in p['workflow']['results']], ['source'])
        item = next(item for item in plan['coverage'] if item['id']=='R:camera')
        w.verify_evidence([item], {'R:camera':'粒子离开主形'}, '画面表现为粒子离开主形')


if __name__ == '__main__':
    unittest.main()

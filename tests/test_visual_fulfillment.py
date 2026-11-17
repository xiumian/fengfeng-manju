"""Visual requirements reach real handoffs; not an automatic aesthetic judge."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w

METHOD = 'references/move-vfx-design.md'


def fixture():
    return {'sources': [{'id': 'C1', 'origin': 'creative_addition',
                         'text': '甲引剑群挡住来袭，剑列先展开扇面再折入中轴；首股碎裂，后股继续，未新增破盾。'}],
            'events': [{'id': 'E1', 'source_ids': ['C1'], 'start': 0, 'end': 4,
                        'body': '甲引剑群挡住来袭，双方存活。', 'requires': ['action', 'vfx']}],
            'requirements': [
                {'id': 'R:fan', 'kind': 'vfx', 'source_ids': ['C1'], 'event_ids': ['E1'],
                 'description': '剑列先展开扇面再折入中轴，不能只有扇面终态。'},
                {'id': 'R:wave', 'kind': 'vfx', 'source_ids': ['C1'], 'event_ids': ['E1'],
                 'description': '首股碎裂、后股继续，不是全海一起爆炸。'}]}


class VisualFulfillment(unittest.TestCase):
    def test_source_and_five_owners_get_construction_and_evidence_method(self):
        p = w.init(fixture(), {'mode': 'prompt'})
        for module in ('source', 'action', 'vfx', 'camera', 'compile', 'validate'):
            c = w.context({'mode': 'prompt'}, module, p)
            rules = {x['path']: x['text'] for x in c['rules']}
            self.assertTrue(METHOD in rules, module)
            self.assertEqual(rules[METHOD], (ROOT / METHOD).read_text(encoding='utf-8'))
            self.assertEqual(c['receipt']['rules_hash'], w.fingerprint(c['rules']))
            self.assertTrue({'R:fan', 'R:wave'} <= {x['id'] for x in c['coverage']})

    def test_method_is_process_not_layer_list_or_fixed_quota(self):
        text = (ROOT / METHOD).read_text(encoding='utf-8')
        for cue in ['先设计观看内容，再分配时间', '变化前', '驱动', '变化后', '层间联动',
                    '新增对白', 'R:fan', 'unmet', 'content_checked', '不设字数',
                    '不能声称程序识别了空泛表达']:
            self.assertTrue(cue in text, cue)
        self.assertTrue('move-vfx-design.md' in (ROOT / 'references/creation-preparation.md').read_text(encoding='utf-8'))

    def test_missing_visual_requirement_evidence_is_rejected_at_real_compile(self):
        task = {'mode': 'prompt'}; p = w.init(fixture(), task)
        c = w.context(task, 'source', p)
        p = w.submit(p, 'source', {'checked_event_ids': ['E1'], 'source_coverage': {
            u['id']: {'event_ids': ['E1'], 'reason': '已授权视觉变化与固定结果分别核对，非自动美感判定。'}
            for u in c['source_units']}}, c['receipt'])
        while p['workflow']['plan']['steps'][p['workflow']['cursor']]['module'] != 'compile':
            m = p['workflow']['plan']['steps'][p['workflow']['cursor']]['module']
            c = w.context(task, m, p)
            p = w.submit(p, m, {'design': {e['id']: '剑列先展开扇面再折入中轴；首股碎裂，后股继续，挡住来袭。'
                                          for e in c['events']}}, c['receipt'])
        c = w.context(task, 'compile', p)
        text = '甲引剑群挡住来袭，双方存活。剑列先展开扇面再折入中轴；首股碎裂，后股继续。'
        payload = {'text': text, 'event_ids': ['E1'], 'dialogue_ids': [],
                   'coverage': {r['id']: '甲引剑群挡住来袭' for r in c['coverage']}}
        del payload['coverage']['R:fan']
        with self.assertRaises(ValueError):
            w.submit(copy.deepcopy(p), 'compile', payload, c['receipt'])
        payload['coverage']['R:fan'] = '剑列先展开扇面再折入中轴'
        payload['coverage']['R:wave'] = '首股碎裂，后股继续'
        p = w.submit(p, 'compile', payload, c['receipt'])
        c = w.context(task, 'validate', p)
        self.assertTrue({'R:fan', 'R:wave'} <= {r['id'] for r in c['coverage']})
        review = {'content_checked': True, 'coverage': payload['coverage'],
                  'evidence': {'E1': '扇面展开到折入以及首股碎裂后股继续均有正文过程，固定阻挡结果保留。'},
                  'requirement_reviews': {r['id']: {'status': 'met', 'reason': '这是已保存的结构夹具，不是模型语义或审美判定。'}
                                          for r in c['coverage']},
                  'limitations': ['仅测试声明和交接；真实语义需执行者逐句核对。']}
        review['requirement_reviews']['R:fan'] = {'status': 'unmet', 'reason': '假设执行者发现只有终态，未落实展开关系，不应进入已验收状态。'}
        with self.assertRaises(ValueError):
            w.submit(copy.deepcopy(p), 'validate', review, c['receipt'])
        review['requirement_reviews']['R:fan'] = {'status': 'met', 'reason': '夹具正文先展开扇面再折入中轴，明确两状态之间变化。'}
        review['requirement_reviews']['R:wave'] = {'status': 'met', 'reason': '夹具正文首股碎裂后股继续，非整海同爆，定位句可查。'}
        p = w.submit(p, 'validate', review, c['receipt'])
        self.assertEqual(p['workflow']['status'], 'text_checked')

    def test_examples_include_named_only_overload_and_simple_case(self):
        text = (ROOT / 'references/visual-fulfillment-examples.md').read_text(encoding='utf-8')
        for cue in ['法相', '剑海', '对白', '只有层名', '普通小招', '文字判定', '未成片验证']:
            self.assertTrue(cue in text, cue)


if __name__ == '__main__':
    unittest.main()

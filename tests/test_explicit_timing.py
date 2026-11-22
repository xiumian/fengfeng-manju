"""Test the real compile boundary, not only the timing helper."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w


def prepare(timing='explicit'):
    body = '人物停在原处。'
    task = {'mode': 'prompt', 'delivery': {'duration': 15, 'timing': timing}}
    project = w.init({
        'sources': [{'id': 'S1', 'text': body}],
        'events': [{'id': 'E1', 'source_ids': ['S1'], 'start': 0, 'end': 15, 'body': body}],
    }, task)
    ctx = w.context(task, 'source', project)
    project = w.submit(project, 'source', {
        'checked_event_ids': ['E1'],
        'source_coverage': {u['id']: {'event_ids': ['E1'], 'reason': '唯一源文与固定事件一致。'}
                            for u in ctx['source_units']},
    }, ctx['receipt'])
    ctx = w.context(task, 'camera', project)
    project = w.submit(project, 'camera', {'design': {'E1': '固定机位拍人物站在原处。'}}, ctx['receipt'])
    ctx = w.context(task, 'compile', project)
    common = {'event_ids': ['E1'], 'dialogue_ids': [],
              'coverage': {item['id']: body for item in ctx['coverage']}}
    return body, project, ctx['receipt'], common


class ExplicitTiming(unittest.TestCase):
    def test_compile_rejects_two_second_heading_with_fifteen_second_node(self):
        body, project, receipt, common = prepare()
        heading = '——0—2秒：【结束】'
        with self.assertRaisesRegex(ValueError, 'heading times do not match'):
            w.submit(project,'compile',dict(common,text=f'{heading}\n{body}',
                     timing_nodes=[{'heading':heading,'start':0,'end':15}]),receipt)

    def test_compile_rejects_missing_timing_nodes_in_explicit_mode(self):
        body, project, receipt, common = prepare()
        with self.assertRaisesRegex(ValueError, 'explicit timing requires timing_nodes'):
            w.submit(project,'compile',dict(common,text=f'——0—15秒：【结束】\n{body}'),receipt)

    def test_consistent_explicit_decimal_nodes_still_compile(self):
        body, project, receipt, common = prepare()
        first, last = '——0—14.8秒：【主戏】', '——14.8—15秒：【段尾交接镜】'
        nodes = [{'heading':first,'start':0,'end':14.8},{'heading':last,'start':14.8,'end':15}]
        result = w.submit(project,'compile',dict(common,
            text=f'{first}\n{body}\n{last}\n固定高位与地标同框。',timing_nodes=nodes),receipt)
        self.assertEqual(result['timing_nodes'],nodes)

    def test_explicit_timing_does_not_accept_an_unregistered_shot(self):
        body, project, receipt, common = prepare()
        first, unregistered = '——0—15秒：【主戏】', '——2—3秒：【插镜】'
        with self.assertRaisesRegex(ValueError, 'visible shot heading missing'):
            w.submit(project,'compile',dict(common,text=f'{first}\n{body}\n{unregistered}\n人物仍在原处。',
                     timing_nodes=[{'heading':first,'start':0,'end':15}]),receipt)

    def test_explicit_mode_cannot_hide_times_in_metadata_only(self):
        body, project, receipt, common = prepare()
        heading = '——【结束】'
        with self.assertRaisesRegex(ValueError, 'explicit timing needs visible heading times'):
            w.submit(project,'compile',dict(common,text=f'{heading}\n{body}',
                     timing_nodes=[{'heading':heading,'start':0,'end':15}]),receipt)

    def test_relative_untimed_prompt_still_compiles_without_nodes(self):
        body, project, receipt, common = prepare('relative')
        result = w.submit(project,'compile',dict(common,text=body),receipt)
        self.assertEqual(result['video_master_prompt'],body)
        self.assertNotIn('timing_nodes',result)


if __name__ == '__main__':
    unittest.main()

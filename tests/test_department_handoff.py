"""Exercise a real prompt run; rules and results must arrive at different stages."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_delivery_gate import ENDING, REACTION_PAYOFF, candidate
import workflow as w
from workflow_gate import DeliveryBlocked


ROOT = Path(__file__).resolve().parents[1]
LINE = '窗还亮着。'
SCRIPT = '石阶下的守灯人示意窗还亮着。另一人伸向窗，听见扣响而停手。帘后铃槌仍悬空。'


def new_run():
    task = {'mode': 'prompt', 'handoff': 'departments',
            'delivery': {'duration': 15, 'timing': 'explicit'}}
    return w.init({'sources': [{'id': 'S', 'text': SCRIPT}],
                   'events': [{'id': 'E', 'source_ids': ['S'], 'body': SCRIPT, 'start': 0, 'end': 15,
                               'end_state': '二人仍在原位；敲铃留给下段。',
                               'dialogues': [{'id': 'D', 'speaker': '守灯人', 'text': LINE}]}]}, task)


def next_context(run, module):
    return w.context(run['workflow']['plan']['task'], module, run)


def data_for(module, packet):
    card = candidate()
    draft = card['drafts']['direct']
    visual = {'design': {'E': '听者的手终于停在窗把下方，铃槌全程未触铃。'}}
    proof = {'event:E': REACTION_PAYOFF, 'dialogue:D': LINE, 'voice:D': '守灯人：“窗还亮着。”',
             'signal:sound:E': '她听见扣响'}
    if module == 'source':
        return {**visual, 'checked_event_ids': ['E'],
                'source_coverage': {'S:L1': {'event_ids': ['E'], 'reason': '保留先听见扣响才停手。'}}}
    if module == 'camera':
        frame = {'view_plan': card['view_plan'], 'design': card['design']}
        preflight = w.storyboard_plan({'source': packet['camera_source'], 'view_plan': frame['view_plan']})
        return {**visual, 'camera_plan': {**frame, 'plan_receipt': preflight['plan_receipt']}}
    if module == 'sound':
        audio = {}
        for shot in card['design']:
            body = draft.split(shot['heading'], 1)[1].split('——', 1)[0]
            audio[shot['heading']] = dict(line.split('：', 1) for line in
                                           body.split('【音效】\n', 1)[1].strip().splitlines())
        return {**visual, 'shot_audio': audio}
    if module == 'compile':
        pos = draft.index(LINE)
        nodes = [{k: shot[k] for k in ('heading', 'start', 'end')} for shot in card['design']]
        return {'text': draft, 'event_ids': ['E'], 'dialogue_ids': ['D'], 'coverage': proof,
                'timing_nodes': nodes, 'utterances': [{'id': 'D', 'speaker': '守灯人',
                                                      'start': pos, 'end': pos+len(LINE)}]}
    if module == 'validate':
        reviews = {k: row for k, row in copy.deepcopy(card['review']).items()
                   if k not in card['source']['requirements']}
        for row in reviews.values():
            row['evidence']['master'] = row['evidence'].pop('direct')
        reviews['continuity'] = {'status': 'met', 'reason': '留铃未敲。', 'evidence': {'master': ENDING}}
        return {'content_checked': True, 'evidence': {'E': '听者的手在窗把下方停住。'},
                'coverage': proof, 'limitations': ['只验文字'],
                'requirement_reviews': {k: {'status': 'met', 'reason': '在本段正文中逐项核对已定事件。'}
                                        for k in proof},
                'camera_review': reviews}
    return visual


def apply_next(run, module):
    packet = next_context(run, module)
    return w.submit(run, module, data_for(module, packet), packet['receipt'])


def run_until(stop=''):
    run = new_run()
    for step in run['workflow']['plan']['steps']:
        if step['module'] == stop:
            break
        run = apply_next(run, step['module'])
    return run


class DepartmentHandoff(unittest.TestCase):
    def test_next_department_gets_only_completed_input_not_a_preview(self):
        run = new_run()
        with self.assertRaises(DeliveryBlocked) as error:
            next_context(run, 'camera')
        self.assertEqual(error.exception.return_to, 'source')
        packet = next_context(run, 'source')
        with self.assertRaises(ValueError):
            w.submit(run, 'source', {}, packet['receipt'])
        with self.assertRaises(DeliveryBlocked):
            next_context(run, 'assets')
        result = data_for('source', packet)
        run = w.submit(run, 'source', result, packet['receipt'])
        self.assertEqual(next_context(run, 'assets')['upstream'][-1]['payload'], result)

    def test_unused_departments_skip_and_sound_waits_for_camera_output(self):
        run = new_run()
        self.assertEqual([s['module'] for s in run['workflow']['plan']['steps']],
                         ['source', 'assets', 'performance', 'camera', 'sound', 'compile', 'validate'])
        run = run_until('camera')
        camera = next_context(run, 'camera')
        with self.assertRaises(ValueError):
            w.submit(run, 'camera', {'design': {'E': '没有实际镜头'}}, camera['receipt'])
        with self.assertRaises(DeliveryBlocked) as e:
            next_context(run, 'sound')
        self.assertEqual(e.exception.return_to, 'camera')
        planned = data_for('camera', camera)
        run = w.submit(run, 'camera', planned, camera['receipt'])
        self.assertEqual(next_context(run, 'sound')['upstream'][-1]['payload']['camera_plan'],
                         planned['camera_plan'])

    def test_compile_cannot_replace_camera_or_sound_decisions(self):
        run = run_until('compile')
        context = next_context(run, 'compile')
        valid = data_for('compile', context)
        for before, after in [('沿帘侧向右贴近', '缓推一点'), ('风声贴着石墙。', '风声重起。')]:
            with self.subTest(before=before):
                bad = copy.deepcopy(valid)
                # Recompute dialogue spans if an earlier replacement shifts them.
                bad['text'] = bad['text'].replace(before, after, 1)
                pos = bad['text'].index(LINE)
                bad['utterances'][0].update(start=pos, end=pos+len(LINE))
                with self.assertRaises(DeliveryBlocked) as error:
                    w.submit(run, 'compile', bad, context['receipt'])
                self.assertEqual(error.exception.return_to, 'compile')

    def test_complete_template_dialogue_time_span_does_not_become_the_speaker(self):
        run = run_until('compile')
        packet = next_context(run, 'compile')
        compiled = data_for('compile', packet)
        compiled['text'] = compiled['text'].replace(
            '守灯人：“窗还亮着。”', '【台词】\n04.00—05.30秒 守灯人（同场画内）：“窗还亮着。”')
        pos = compiled['text'].index(LINE)
        compiled['utterances'][0].update(start=pos, end=pos+len(LINE))
        compiled['coverage']['voice:D'] = '守灯人（同场画内）'
        accepted = w.submit(run, 'compile', compiled, packet['receipt'])
        self.assertIn('04.00—05.30秒 守灯人', accepted['video_master_prompt'])

    def test_final_evidence_failure_and_rollback_do_not_release_stale_text(self):
        run = run_until('validate')
        review = next_context(run, 'validate')
        bad = data_for('validate', review)
        bad['camera_review']['hold:2'] = {'status': 'unmet', 'return_to': 'camera',
                                         'reason': '前后不是同一个可观察过程。'}
        with self.assertRaises(DeliveryBlocked) as error:
            w.submit(run, 'validate', bad, review['receipt'])
        self.assertEqual(error.exception.return_to, 'camera')
        with self.assertRaises(ValueError):
            w.deliver(run)
        accepted = apply_next(run, 'validate')
        self.assertEqual(w.deliver(accepted)['production_master'], candidate()['drafts']['direct'])
        rewind = w.repair(accepted, 'camera', '按实际观看变化重新选机位。')
        self.assertEqual(rewind['workflow']['results'], accepted['workflow']['results'][:3])
        with self.assertRaises(ValueError):
            w.deliver(rewind)
        with self.assertRaises(DeliveryBlocked):
            next_context(rewind, 'sound')
        new_camera = next_context(rewind, 'camera')
        old_camera = accepted['workflow']['results'][3]['context_receipt']
        with self.assertRaisesRegex(ValueError, 'current context receipt'):
            w.submit(rewind, 'camera', data_for('camera', new_camera), old_camera)

    def test_cli_cannot_use_a_passable_direct_card_to_skip_departments(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet, out = Path(tmp)/'direct.json', Path(tmp)/'released.json'
            packet.write_text(json.dumps(candidate(), ensure_ascii=False), encoding='utf-8')
            result = subprocess.run([sys.executable, '-B', str(ROOT/'scripts/workflow.py'), 'light-deliver',
                                     str(packet), '--out', str(out)], encoding='utf-8', capture_output=True)
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertIn('department', result.stderr)
            self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()

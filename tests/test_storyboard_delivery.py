"""A storyboard needs its own second pass; it is not a video prompt."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import workflow_gate as gate
from workflow_gate import DeliveryBlocked, light_deliver


OUT = '她先松开票角，抬起手腕。'
IN = '同一只手腕从画面右上落向案面。'


def lock_plan(card):
    receipt = gate.storyboard_plan({key: card[key] for key in ('source', 'view_plan')})
    card['plan_receipt'] = receipt['plan_receipt']
    return card


def storyboard():
    h1, h2 = '**01｜0–1.5 秒**', '**02｜1.5–3 秒**'
    title = '# 案前对证'
    a = '50 mm，斜侧中景，固定机位。'+OUT+'台词：“看这张。”'
    b = '85 mm，斜俯细节镜，手腕下落时启动，沿案沿横移，纸角入画时停。'+IN
    text = f'{title}\n| {h1} | {a} |\n| {h2} | {b} |\n'
    return lock_plan({
        'source': {'scope': '交付三秒分镜，不编译视频提示词', 'duration': 3,
                   'timing': 'explicit', 'outputs': ['storyboard'],
                   'dialogues': ['看这张。'], 'requirements': {'intent': '保留同一只手腕的动作承接'}},
        'view_plan': [
            {'id': 'show', 'change': '她从藏着票变成主动出示', 'see': '松开票角后抬起手腕',
             'choice': '关系镜看得见她的主动，不用先拍票据上的内容'},
            {'id': 'land', 'change': '证物从手上交到案前', 'see': '同一只手腕延续下落',
             'choice': '跟到落点才停，避免切掉物件位置变化'},
        ],
        'design': [
            {'heading': h1, 'watch': '看人主动出示证据', 'beats': ['show'], 'start': 0, 'end': 1.5,
             'focal': '50 mm', 'framing': '斜侧中景', 'motion': {'fixed': '固定机位'}},
            {'heading': h2, 'watch': '接住下落的手和票角', 'beats': ['land'], 'start': 1.5, 'end': 3,
             'focal': '85 mm', 'framing': '斜俯细节镜', 'motion': {'trigger': '手腕下落时启动', 'path': '沿案沿横移',
                                            'stop': '纸角入画时停'}},
        ],
        'drafts': {'storyboard': text},
        'review': {
            'intent': {'status': 'met', 'reason': '出示与承接由同一手腕完成。', 'evidence': {'storyboard': IN}},
            'beat:show': {'status': 'met', 'reason': '可以直接看到她主动抬腕。', 'evidence': {'shot:1': OUT}},
            'beat:land': {'status': 'met', 'reason': '明白物件沿同一动作交到案面。', 'evidence': {'shot:2': IN}},
            'shot:1': {'status': 'met', 'reason': '抬腕先于下一镜下落。', 'evidence': {'storyboard': OUT}},
            'shot:2': {'status': 'met', 'reason': '下落途中才交到案面的票。', 'evidence': {'storyboard': IN}},
            'cut:1': {'status': 'met', 'reason': '首镜抬腕，次镜接同一手腕进入案面。',
                      'evidence': {'out': OUT, 'in': IN}},
        },
    })


class StoryboardFirstReview(unittest.TestCase):
    def block(self, card, stage, message):
        with self.assertRaisesRegex(DeliveryBlocked, message) as error:
            light_deliver(card)
        self.assertEqual(error.exception.return_to, stage)

    def test_delivers_only_the_checked_storyboard_without_prompt_fields(self):
        card = storyboard()
        self.assertEqual(light_deliver(card),
                         {'status': 'ready_to_deliver', 'outputs': card['drafts']})

    def test_first_draft_cannot_skip_a_shot_or_cut_review(self):
        for missing in ('review', 'cut:1', 'shot:2'):
            card = storyboard()
            if missing == 'review':
                del card['review']
            else:
                del card['review'][missing]
            with self.subTest(missing=missing):
                self.block(card, 'validate', 'review coverage')

    def test_only_a_size_or_vague_movement_does_not_pass(self):
        for key in ('固定机位', '沿案沿横移', '纸角入画时停'):
            card = storyboard()
            card['drafts']['storyboard'] = card['drafts']['storyboard'].replace(key, '中近景')
            with self.subTest(missing=key):
                self.block(card, 'camera', 'motion')

    def test_focal_and_cited_motion_must_appear_in_the_corresponding_shot(self):
        card = storyboard()
        card['design'][0]['focal'] = '85 mm'
        self.block(card, 'camera', 'shot:1.*focal')
        card['design'][0]['focal'] = '中景'
        self.block(card, 'camera', 'shot:1.*focal')
        card = storyboard()
        card['design'][0]['framing'] = '桌边反打双人近景'
        self.block(card, 'camera', 'shot:1.*framing')
        card = storyboard()
        card['design'][0]['motion'] = {'trigger': '手腕下落时启动', 'path': '沿案沿横移', 'stop': '纸角入画时停'}
        self.block(card, 'camera', 'shot:1.*motion')

    def test_visual_timecodes_and_locked_duration(self):
        card = storyboard()
        card['source']['duration'] = 4
        lock_plan(card)
        self.block(card, 'camera', 'duration')
        card = storyboard()
        old = card['design'][1]['heading']
        new = old.replace('–3 秒', '–4 秒')
        card['design'][1]['heading'] = new
        card['drafts']['storyboard'] = card['drafts']['storyboard'].replace(old, new)
        self.block(card, 'camera', 'heading times')

    def test_cut_evidence_has_to_cite_both_sides(self):
        card = storyboard()
        card['review']['cut:1']['evidence']['out'] = IN
        self.block(card, 'validate', 'cut:1.*out.*evidence')

    def test_reported_continuity_failure_returns_before_any_storyboard_is_released(self):
        card = storyboard()
        card['review']['cut:1'] = {'status': 'unmet', 'return_to': 'camera',
                                  'reason': '上一镜手还在衣袖里，下一镜已在案面'}
        with tempfile.TemporaryDirectory() as tmp:
            packet, old = Path(tmp)/'card.json', Path(tmp)/'approved.json'
            packet.write_text(json.dumps(card, ensure_ascii=False), encoding='utf-8')
            old.write_text('quietly preserve previous approved cut', encoding='utf-8')
            proc = subprocess.run([sys.executable, '-B', str(ROOT/'scripts/workflow.py'), 'light-deliver',
                                   str(packet), '--out', str(old)], capture_output=True, encoding='utf-8')
            self.assertEqual(proc.returncode, 2)
            result = json.loads(proc.stderr)
            self.assertEqual(result['return_to'], 'camera')
            self.assertIn('衣袖', result['reason'])
            self.assertNotIn('outputs', result)
            self.assertEqual(proc.stdout, '')
            self.assertEqual(old.read_text(encoding='utf-8'), 'quietly preserve previous approved cut')

    def test_relative_single_shot_can_omit_visible_seconds_and_adjacent_cut(self):
        card = storyboard()
        card['source'].update(timing='relative', duration=1.5, requirements={'intent': '保持一次抬腕'})
        card['design'] = card['design'][:1]
        shot = card['design'][0]
        card['drafts']['storyboard'] = '\n'.join(card['drafts']['storyboard'].splitlines()[:2]).replace(
            shot['heading'], '**01｜出示原件**').replace('台词：“看这张。”', '台词：“看这张。”'+IN)
        shot['heading'] = '**01｜出示原件**'
        shot['beats'].append('land')
        del card['review']['cut:1']
        del card['review']['shot:2']
        card['review']['intent']['evidence']['storyboard'] = OUT
        card['review']['beat:land']['evidence'] = {'shot:1': IN}
        lock_plan(card)
        self.assertEqual(light_deliver(card)['outputs'], card['drafts'])

    def test_no_plan_receipt_no_release_even_with_complete_shot_fields(self):
        card = storyboard()
        del card['plan_receipt']
        self.block(card, 'camera', 'plan receipt')
        del card['view_plan']
        self.block(card, 'camera', 'viewing plan')

    def test_cannot_change_a_locked_beat_or_source_to_fit_the_draft(self):
        card = storyboard()
        card['view_plan'][0]['see'] = '只拍桌面，暂不让人看到她的选择'
        self.block(card, 'camera', 'plan receipt')
        card = storyboard()
        card['source']['dialogues'] = []
        self.block(card, 'camera', 'plan receipt')

    def test_individually_valid_shots_can_still_drop_the_whole_scene_payoff(self):
        card = storyboard()
        card['design'][1]['beats'] = ['show']
        self.block(card, 'camera', 'uncovered viewing beat.*land')
        card = storyboard()
        card['review']['beat:land'] = {'status': 'unmet', 'return_to': 'camera',
                                      'reason': '只跟着脸说话，没拍到证物交到案面'}
        self.block(card, 'camera', 'beat:land.*案面')

    def test_whole_scene_evidence_checks_linked_shot_and_intended_reveal_order(self):
        card = storyboard()
        card['review']['beat:land']['evidence'] = {'shot:1': OUT}
        self.block(card, 'validate', 'beat:land.*linked')
        card = storyboard()
        card['review']['beat:land']['evidence'] = {'shot:2': OUT}
        self.block(card, 'validate', 'beat:land.*actual')
        card = storyboard()
        card['design'][0]['beats'], card['design'][1]['beats'] = ['land'], ['show']
        card['review']['beat:show']['evidence'] = {'shot:2': IN}
        card['review']['beat:land']['evidence'] = {'shot:1': OUT}
        self.block(card, 'camera', 'reveal order')

    def test_storyboard_plan_cli_only_returns_a_small_receipt_before_drafting(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'preflight.json'
            card = storyboard()
            p.write_text(json.dumps({key: card[key] for key in ('source', 'view_plan')}, ensure_ascii=False),
                         encoding='utf-8')
            cmd = [sys.executable, '-B', str(ROOT/'scripts/workflow.py'), 'storyboard-plan', str(p)]
            result = subprocess.run(cmd, capture_output=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(set(payload), {'status', 'beats', 'plan_receipt'})
            self.assertEqual(payload['beats'], ['show', 'land'])
            self.assertEqual(payload['plan_receipt'], card['plan_receipt'])
            p.write_text(json.dumps(card, ensure_ascii=False), encoding='utf-8')
            late = subprocess.run(cmd, capture_output=True, encoding='utf-8')
            self.assertEqual(late.returncode, 2)
            self.assertEqual(late.stdout, '')


if __name__ == '__main__':
    unittest.main()

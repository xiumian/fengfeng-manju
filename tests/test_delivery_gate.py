"""Test what can be withheld or released, not whether a video looks good."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w
from workflow_gate import viewing_plan_fingerprint


OPENING = '沿用确认首帧：石阶下的两人仍在原位。'
REACTION = '镜头留在听者侧脸；她听见扣响，视线越过同伴肩头。'
REVEAL = '切到帘后握住铃柄的手，铃槌悬空，尚未敲落。'
ENDING = '固定俯视，两人仍在原位，第一次敲击留给下段。'
OPENING_PAYOFF = '提灯绕开阶柱，光落到空着的阶口，去路逐渐露全。'
REACTION_PAYOFF = '听者伸向窗的手慢下来，最终停在窗把下方。'


def legacy_candidate():
    # Local regression surrogate for 15s, a withheld action and a 0.1s handoff.
    beats = [
        (0, 6, '起镜', OPENING + '\n守灯人：“窗还亮着。”'),
        (6, 12, '听者反应', REACTION),
        (12, 14.9, '揭示铃柄', REVEAL),
        (14.9, 15, '交接镜', ENDING),
    ]
    nodes = [{'heading': f'——{a}—{b}秒：【{title}】', 'start': a, 'end': b, 'watch': beat.splitlines()[0]}
             for a, b, title, beat in beats]
    audio = ('【音效】\n动作层：衣袖轻擦。\n特效层：本镜无新增特效声。\n环境层：风声贴着石墙。\n'
             '同步节点：衣袖拨开时有轻响。\n主次变化：远风让位给近声。\n跨镜承接：保留未断的风声。')
    text = ('【项目名称】：石阶\n【总时长】：15秒\n'
            '━━━━━━━━━━ 全局设定 ━━━━━━━━━━\n国风3D。\n'
            '━━━━━━━━━━ 场景与资产 ━━━━━━━━━━\n石阶与帘。\n'
            '━━━━━━━━━━ 片段设定 ━━━━━━━━━━\n【片段时长】：15秒\n'
            '━━━━━━━━━━ 逐镜时间轴 ━━━━━━━━━━\n'
            + '\n\n'.join(node['heading']+'\n'+beat[3]+'\n'+audio for node, beat in zip(nodes, beats)))
    locks = {'opening': '保留已确认首帧', 'defer': '本段不响第一声铃，留给下段', 'line': '保留原句及归属'}
    quotes = dict(opening=OPENING, defer=ENDING, line='守灯人：“窗还亮着。”')
    quotes.update({f'shot:{i}': node['watch'] for i, node in enumerate(nodes, 1)})
    return {
        'source': {'scope': '仅调整景别和节奏，不改事实与锁定总长', 'requirements': locks,
                   'duration': 15, 'timing': 'explicit', 'dialogues': ['窗还亮着。'], 'outputs': ['direct']},
        'design': nodes,
        'drafts': {'direct': text},
        'review': {key: {'status': 'met', 'reason': f'复查正文的已锁状态和发生时机：{quote}',
                         'evidence': {'direct': quote}} for key, quote in quotes.items()},
    }


def candidate():
    card = legacy_candidate()
    shots = [
        ('stairs', '看阶口是通的', '32 mm', '左侧低位双人全景', {'fixed': '固定机位'}, OPENING, OPENING_PAYOFF),
        ('listen', '看听者从伸手到停住', '85 mm', '越肩听者近景', {'fixed': '固定机位'}, REACTION, REACTION_PAYOFF),
        ('bell', '看见铃槌悬空，并非已经敲响', '55 mm', '帘侧斜拍中近景',
         {'trigger': '帘角开始掀动时启动', 'path': '沿帘侧向右贴近', 'stop': '铃槌和铃口的空隙同框时停'}, REVEAL, ''),
        ('keep', '交接双方站位和未敲的铃', '28 mm', '同侧高角度全景', {'fixed': '固定俯视'}, ENDING, ''),
    ]
    card['view_plan'] = []
    review = card['review']
    for i, (beat, watch, focal, frame, motion, start, later) in enumerate(shots, 1):
        key = f'shot:{i}'
        card['view_plan'].append({'id': beat, 'change': watch, 'see': later or start,
                                  'choice': '留镜拍完整变化' if later else '让下一拍的新证据单独可读'})
        card['design'][i-1].update(watch=watch, beats=[beat], focal=focal, framing=frame, motion=motion)
        camera = '，'.join([focal, frame] + [x for x in motion.values() if x not in start])
        card['drafts']['direct'] = card['drafts']['direct'].replace(start, camera+'。'+start+later)
        review[f'beat:{beat}'] = {'status': 'met', 'reason': watch, 'evidence': {'direct': {key: later or start}}}
        if later:
            review[f'hold:{i}'] = {'status': 'met', 'reason': '当前取景看得见这个变化，无须为台词断开。',
                                   'evidence': {'direct': {'first': start, 'last': later}}}
        if i > 1:
            previous = shots[i-2]
            review[f'cut:{i-1}'] = {'status': 'met', 'reason': '下一拍改变观察重点并承接已知状态。',
                                     'evidence': {'direct': {'out': previous[-1] or previous[-2], 'in': start}}}
    card['plan_receipt'] = viewing_plan_fingerprint(card)
    return card


class LightDelivery(unittest.TestCase):
    def blocked(self, card, stage, message):
        with self.assertRaisesRegex(w.DeliveryBlocked, message) as raised:
            w.light_deliver(card)
        self.assertEqual(raised.exception.return_to, stage)

    def test_checked_text_only_has_requested_output(self):
        card = candidate()
        result = w.light_deliver(card)
        self.assertEqual(result, {'status': 'ready_to_deliver', 'outputs': card['drafts']})
        self.assertNotIn('review', result)

    def test_missing_step_cannot_pass(self):
        for key, stage in [('source', 'source'), ('design', 'camera'), ('drafts', 'compile'), ('review', 'validate')]:
            card = candidate()
            del card[key]
            with self.subTest(step=key):
                self.blocked(card, stage, key)

    def test_cannot_replan_fifteen_seconds_as_twelve(self):
        card = candidate()
        for node in card['design']:
            node['start'] = round(node['start'] * .8, 4)
            node['end'] = round(node['end'] * .8, 4)
            node['heading'] = f'——{node["start"]:g}—{node["end"]:g}秒：【重排{node["start"]:g}】'
        self.blocked(card, 'camera', 'requested delivery duration')

    def test_declared_duration_and_visible_cuts_must_match(self):
        for original, changed in [('【片段时长】：15秒', '【片段时长】：12秒'), ('12—14.9秒', '12—14秒')]:
            card = candidate()
            card['drafts']['direct'] = card['drafts']['direct'].replace(original, changed)
            with self.subTest(changed=changed):
                self.blocked(card, 'compile', 'duration|headings')

    def test_each_shot_keeps_audio_even_for_handoff(self):
        card = candidate()
        last_label = card['drafts']['direct'].rindex('跨镜承接：')
        card['drafts']['direct'] = card['drafts']['direct'][:last_label]
        self.blocked(card, 'compile', '交接镜.*跨镜承接')

    def test_prompt_cannot_release_after_all_camera_directions_are_removed(self):
        card = legacy_candidate()
        for a, b in {
            REACTION: '她听见扣响，视线越过同伴肩头。',
            REVEAL: '帘后的人握住铃柄，铃槌悬空，尚未敲落。',
            ENDING: '两人仍在原位，第一次敲击留给下段。',
        }.items():
            card['drafts']['direct'] = card['drafts']['direct'].replace(a, b)
            for shot in card['design']:
                shot['watch'] = shot['watch'].replace(a, b)
            for row in card['review'].values():
                row['evidence']['direct'] = row['evidence']['direct'].replace(a, b)
        self.blocked(card, 'camera', 'viewing plan')

    def test_complete_prompt_checks_plan_before_compiling_and_requires_its_receipt(self):
        card = candidate()
        plan = {k: card[k] for k in ('source', 'view_plan')}
        self.assertEqual(w.storyboard_plan(plan)['plan_receipt'], card['plan_receipt'])
        del card['plan_receipt']
        self.blocked(card, 'camera', 'plan receipt')

    def test_compiler_cannot_drop_camera_direction_or_put_it_only_in_sound(self):
        for field, phrase in (('focal', '85 mm'), ('framing', '越肩听者近景'), ('motion path', '沿帘侧向右贴近')):
            with self.subTest(field=field):
                card = candidate()
                card['drafts']['direct'] = card['drafts']['direct'].replace(phrase, '').replace(
                    '同步节点：衣袖拨开时有轻响。', '同步节点：衣袖拨开时有轻响。'+phrase, 1)
                self.blocked(card, 'compile', field)

    def test_direct_and_master_need_their_own_camera_evidence(self):
        card = candidate()
        card['source']['outputs'] = ['master', 'direct']
        card['plan_receipt'] = viewing_plan_fingerprint(card)
        card['drafts']['master'] = str(card['drafts']['direct'])
        for row in card['review'].values():
            row['evidence']['master'] = copy.deepcopy(row['evidence']['direct'])
        self.assertEqual(w.light_deliver(card)['outputs'], card['drafts'])
        card['drafts']['direct'] = card['drafts']['direct'].replace('铃槌和铃口的空隙同框时停', '只写缓推')
        self.blocked(card, 'compile', 'direct.*motion stop')

    def test_repeat_watch_does_not_justify_two_six_second_shots(self):
        card = candidate()
        card['design'][1]['watch'] = card['design'][0]['watch']
        self.blocked(card, 'camera', 'repeat.*viewing task')

    def test_six_seconds_with_only_a_stated_hold_and_no_visual_progress_is_withheld(self):
        card = candidate()
        card['review']['hold:2']['evidence']['direct']['last'] = REACTION
        self.blocked(card, 'camera', 'hold:2.*distinct')
        card = candidate()
        card['review']['hold:2'] = {'status': 'unmet', 'return_to': 'camera',
                                    'reason': '固定近景只拍嘴动，动作与注意力没有推进。'}
        self.blocked(card, 'camera', 'hold:2.*只拍嘴动')

    def test_valid_six_second_fixed_shots_can_keep_distinct_full_beat_and_transition(self):
        card = candidate()
        self.assertEqual(w.light_deliver(card)['outputs'], card['drafts'])
        del card['review']['hold:1']
        self.blocked(card, 'validate', 'review coverage')

    def test_one_relative_shot_needs_no_invented_cut_or_timestamps(self):
        card = candidate()
        card['source'].update(scope='只交单镜无时码提示词', duration=None, timing='relative',
                              requirements={'opening': '沿用已锁首帧'})
        first = card['design'][0]
        old, following = first['heading'], card['design'][1]['heading']
        card['drafts']['direct'] = card['drafts']['direct'].split(following, 1)[0].replace(
            old, '——【阶口逐渐露出】').replace('【总时长】：15秒', '').replace('【片段时长】：15秒', '')
        card['view_plan'] = card['view_plan'][:1]
        card['design'] = [first]
        first.update(heading='——【阶口逐渐露出】')
        del first['start'], first['end']
        for k in set(card['review']) - {'opening', 'beat:stairs', 'shot:1'}:
            del card['review'][k]
        card['plan_receipt'] = viewing_plan_fingerprint(card)
        self.assertEqual(w.light_deliver(card)['outputs'], card['drafts'])

    def test_prompt_need_actual_linked_beat_and_cut_evidence(self):
        card = candidate()
        card['design'][2]['beats'] = []
        self.blocked(card, 'camera', 'uncovered viewing beat.*bell')
        card = candidate()
        card['review']['beat:bell']['evidence']['direct'] = {'shot:2': REACTION}
        self.blocked(card, 'validate', 'beat:bell.*linked')
        card = candidate()
        card['review']['cut:2']['evidence']['direct']['out'] = REVEAL
        self.blocked(card, 'validate', 'cut:2.*out.*passage')

    def test_original_line_cannot_be_dropped(self):
        card = candidate()
        card['drafts']['direct'] = card['drafts']['direct'].replace('窗还亮着。', '窗灭了。')
        self.blocked(card, 'compile', 'original dialogue')

    def test_evidence_must_be_in_actual_shot_not_just_in_prompt(self):
        card = candidate()
        card['review']['shot:2']['evidence']['direct'] = REVEAL
        self.blocked(card, 'validate', 'shot:2.*evidence')

    def test_missing_or_failed_review_withholds_draft_and_does_not_mutate_input(self):
        card = candidate()
        approved = copy.deepcopy(card)
        card['drafts']['direct'] = card['drafts']['direct'].replace('尚未敲落', '提前敲落')
        card['review']['defer'] = {'status': 'unmet', 'return_to': 'camera', 'reason': '第一声铃在当前分镜已提前发生'}
        self.blocked(card, 'camera', '提前发生')
        self.assertEqual(w.light_deliver(approved)['outputs'], approved['drafts'])
        del card['review']['defer']
        self.blocked(card, 'validate', 'review coverage')

    def test_blocked_cli_returns_only_location_and_does_not_touch_approved_file(self):
        card = candidate()
        card['review']['defer'] = {'status': 'unmet', 'return_to': 'compile', 'reason': '直投稿把下段事件提前写了'}
        with tempfile.TemporaryDirectory() as temp:
            source, out = Path(temp) / 'candidate.json', Path(temp) / 'approved.json'
            source.write_text(json.dumps(card, ensure_ascii=False), encoding='utf-8')
            out.write_text('previous confirmed text', encoding='utf-8')
            proc = subprocess.run(
                [sys.executable, '-B', str(ROOT/'scripts/workflow.py'), 'light-deliver', str(source), '--out', str(out)],
                capture_output=True, encoding='utf-8', check=False)
            self.assertEqual(proc.returncode, 2)
            blocked = json.loads(proc.stderr)
            self.assertEqual(blocked['return_to'], 'compile')
            self.assertNotIn('outputs', blocked)
            self.assertEqual(proc.stdout, '')
            self.assertEqual(out.read_text(encoding='utf-8'), 'previous confirmed text')


if __name__ == '__main__':
    unittest.main()

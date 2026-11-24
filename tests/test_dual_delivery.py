import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import workflow as w


class DualDelivery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ex = ROOT/'examples'/'dual-delivery'
        cls.master = (ex/'雨渡-制片主稿.md').read_text(encoding='utf-8')
        cls.direct = (ex/'雨渡-SEG01直投.txt').read_text(encoding='utf-8')
        cls.marker = '━━━━━━━━━━ 片段设定 ━━━━━━━━━━'

    def run_segment(self, master, direct, copy_format=None, stop_before_review=False,
                    direct_evidence=None):
        line = '别急，还没到呢。'
        speaker = '阿岚'
        body = f'{speaker}用扇托起水灯，对岸方窗亮起。'
        task = {'mode':'prompt','delivery':{'outputs':'dual','timing':'explicit','duration':15}}
        if copy_format:
            task['delivery']['copy_format'] = copy_format
        event = {'id':'E','source_ids':['S'],'body':body,'start':0,'end':15,
                 'dialogues':[{'id':'D','speaker':speaker,'text':line}]}
        p = w.init({'sources':[{'id':'S','text':body}], 'events':[event]},task)
        stages = p['workflow']['plan']['steps']
        for step in stages:
            m = step['module']
            c = w.context(task,m,p)
            evidence = {i['id']:line if i['kind']=='dialogue' else '窗里挑亮一点暖黄' for i in c['coverage']}
            if m == 'source':
                payload = {'checked_event_ids':['E'],'source_coverage':{'S:L1':{'event_ids':['E'],'reason':body}}}
            elif m == 'compile':
                starts = [0,2.5,4.5,5,11,15]
                nodes = [{'heading':h,'start':a,'end':b} for h,a,b in zip(
                    [l for l in master.splitlines() if l.startswith('——')], starts, starts[1:])]
                a = master.index(line)
                payload = {'text':master,'event_ids':['E'],'dialogue_ids':['D'],'coverage':evidence,
                           'timing_nodes':nodes,'utterances':[{'id':'D','speaker':speaker,'start':a,'end':a+len(line)}]}
                if direct is not None:
                    payload['model_ready_prompt'] = direct
            elif m == 'validate':
                if stop_before_review:
                    return p
                if direct_evidence is None:
                    direct_evidence = {k: line if k.startswith('dialogue:') else '黑方窗里挑亮一星暖黄'
                                       for k in evidence}
                payload = {'content_checked':True,'evidence':{'E':'灯口转正，烛焰由蓝返黄'},'limitations':['仅文字'],
                           'coverage':evidence,'direct_coverage':direct_evidence,
                           'requirement_reviews':{k:{'status':'met','reason':body} for k in evidence}}
            else:
                payload = {'design':{'E':body}}
            p = w.submit(p,m,payload,c['receipt'])
        return p

    def test_two_runs_can_share_one_asset_page(self):
        one = self.run_segment(self.master,self.direct)
        two = self.run_segment(self.master[self.master.index(self.marker):].replace('SEG01','SEG02'),self.direct)
        bundle = w.episode([one,two])
        self.assertEqual(bundle['production_master'].count('【场景全局设定】'),1)
        self.assertEqual(bundle['production_master'].count(self.marker),2)
        self.assertEqual(bundle['model_ready_prompts'],{'SEG01':self.direct,'SEG02':self.direct})
        with self.assertRaisesRegex(ValueError,'duplicate'):
            w.episode([one,one])
        conflict = self.run_segment(self.master.replace('白石渡','回雁渡').replace('SEG01','SEG02'),self.direct)
        with self.assertRaisesRegex(ValueError,'disagree'):
            w.episode([one,conflict])

    def test_rejects_missing_derivative_dialogue_and_shifted_cut(self):
        for direct in [None,self.direct.replace('别急，还没到呢。','别急。'),
                       self.direct.replace('5—11秒','5—12秒')]:
            with self.subTest(direct=str(direct)[:12]), self.assertRaises(ValueError):
                self.run_segment(self.master,direct)

    def test_full_copy_keeps_audio_even_on_half_second_insert(self):
        bad = self.direct.replace('特效层：雨珠分流后贴着扇面细嘶。','')
        with self.assertRaisesRegex(ValueError,'扣响.*特效层'):
            self.run_segment(self.master,bad)
        with self.assertRaisesRegex(ValueError,'shot audio block'):
            self.run_segment(self.master,self.direct.replace('【音效】','',1))
        with self.assertRaisesRegex(ValueError,'跨镜承接'):
            self.run_segment(self.master,self.direct.replace('跨镜承接：末镜让箫尾融入雨声，不另起节拍。','跨镜承接：'))

    def test_compact_only_by_explicit_choice(self):
        import re
        compact = re.sub(r'【音效】\n(?:[^\n]+\n){6}', '', self.direct)
        with self.assertRaisesRegex(ValueError,'shot audio block'):
            self.run_segment(self.master,compact)
        self.run_segment(self.master,compact,'compact')

    def test_delivery_withheld_before_validation_and_after_rollback(self):
        pending = self.run_segment(self.master, self.direct, stop_before_review=True)
        with self.assertRaisesRegex(ValueError, 'checked'):
            w.deliver(pending)
        approved = self.run_segment(self.master, self.direct)
        self.assertEqual(w.deliver(approved)['model_ready_prompt'], self.direct)
        rewound = w.repair(approved, 'camera', '检查发现上一版没给听者反应留下可见时间')
        self.assertNotIn('model_ready_prompt', rewound)
        self.assertEqual([r['module'] for r in rewound['workflow']['results']],
                         ['source', 'performance', 'sound'])
        with self.assertRaisesRegex(ValueError, 'checked'):
            w.deliver(rewound)
        self.assertEqual(w.deliver(approved)['model_ready_prompt'], self.direct)

    def test_master_only_quote_cannot_validate_direct_copy(self):
        bad = self.direct.replace('黑方窗里挑亮一星暖黄', '窗稍亮')
        with self.assertRaisesRegex(ValueError, 'direct.*evidence'):
            self.run_segment(self.master, bad)

    def test_review_receipt_is_bound_to_exact_checked_draft(self):
        run = self.run_segment(self.master, self.direct)
        compiled = next(r['payload'] for r in run['workflow']['results'] if r['module']=='compile')
        compiled['model_ready_prompt'] = compiled['model_ready_prompt'].replace('黑方窗里挑亮一星暖黄', '窗稍亮')
        with self.assertRaisesRegex(ValueError, 'review.*changed'):
            w.deliver(run)

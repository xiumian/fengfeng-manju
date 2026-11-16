"""Run saved model-authored handoffs through the real CLI; no hidden model call."""
from pathlib import Path
import json,subprocess,sys,hashlib
ROOT=Path(__file__).resolve().parents[1]

def main(out):
    out.mkdir(parents=True,exist_ok=True)
    task=ROOT/'examples/layered-12s-task.json'
    project=ROOT/'examples/layered-12s-project.json'
    payloads=json.loads((ROOT/'examples/layered-12s-handoffs.json').read_text(encoding='utf-8'))
    payloads['sound'] = {'design': {'E02': '同期对白由甲在画内发声一次，衣料声和呼吸延续，乙保持静默。'}}
    event_quotes = {
        'E01':'乙沿桥中线跨向甲，左手从外侧扣住甲的右腕，右手随即探向剑柄。',
        'E02':'甲右肘贴肋向右下收回，左掌抵着乙的右前臂，阻住其伸向剑柄',
        'E03':'乙上身向东后仰，先后撤开双脚找支撑。',
        'E04':'双方仍是甲西乙东，站在桥面中线附近，身后桥面连续可见，无人死亡或坠桥。',
    }
    log=[]
    def call(args,dest):
        run=subprocess.run([sys.executable,str(ROOT/'scripts/workflow.py'),*map(str,args),'--out',str(dest)],capture_output=True,text=True,encoding='utf-8')
        if run.returncode:raise RuntimeError(run.stderr)
        log.append({'command':[str(x) for x in args[:2]],'output':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
        return json.loads(dest.read_text(encoding='utf-8'))
    plan=call(['plan',task,'--project',project],out/'plan.json')
    path=out/'run-00.json';call(['init',project,task],path)
    serial=0
    for step in plan['steps']:
        module=step['module']
        packet_path=out/('context-'+module+'.json')
        packet=call(['context',task,module,'--project',path],packet_path)
        payload_data=payloads[module]
        # 将旧保存样例升级为新交接格式；不把此转换称为新模型生成。
        if module=='source':payload_data['source_coverage']={u['id']:{'event_ids':payload_data['checked_event_ids'],'reason':'保存样例原文段落与事件人工对应'} for u in packet['source_units']}
        if 'design' in payload_data:
            payload_data = {'design': {e['id']: payload_data['design'][e['id']] for e in packet['events']}}
        if module in ('compile','validate'):
            text=payloads['compile']['text']
            proofs = {}
            for item in packet['coverage']:
                if item['kind']=='dialogue':
                    quote = item['description']
                elif item['origin']=='structured_voice':
                    quote = '甲的对白在近处，衣料拉紧声和短促呼吸持续。'
                else:
                    quote = event_quotes[item['event_ids'][0]]
                assert quote in text, (item['id'], quote)
                proofs[item['id']] = quote
            payload_data['coverage'] = proofs
            if module=='validate':
                payload_data['requirement_reviews'] = {key:{'status':'met','reason':'历史样例重放使用一处局部见证，复核通路测试用'}
                                                       for key in proofs}
        if module=='compile':
            payload_data['utterances']=[];cursor=0
            for e in packet['events']:
                for d in e.get('dialogues',[]):
                    a=text.find(d['text'],cursor);b=a+len(d['text']);payload_data['utterances'].append({'id':d['id'],'speaker':d['speaker'],'start':a,'end':b});cursor=b
        payload=out/(module+'-result.json');payload.write_text(json.dumps(payload_data,ensure_ascii=False,indent=2),encoding='utf-8')
        serial+=1;dest=out/f'run-{serial:02}.json'
        result=call(['submit',path,module,payload,'--context',packet_path],dest);path=dest
    assert result['workflow']['status']=='text_checked'
    assert result['video_master_prompt'].count('退后，我不想伤你。')==1
    assert len(result['events'])==4
    (out/'trace.json').write_text(json.dumps({'scope':'真实CLI串跑、保存的模型编写交接；非独立模型盲测','calls':log,'status':result['workflow']['status']},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'video-prompt.md').write_text(result['video_master_prompt'],encoding='utf-8')
    print(f'PASS: plan + init + {serial} contexts + {serial} checked handoffs; source events retained.')

if __name__=='__main__':main(Path(sys.argv[1]).resolve())

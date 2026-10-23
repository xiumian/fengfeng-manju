"""Run saved model-authored handoffs through the real CLI; no hidden model call."""
from pathlib import Path
import json,subprocess,sys,hashlib
ROOT=Path(__file__).resolve().parents[1]

def main(out):
    out.mkdir(parents=True,exist_ok=True)
    task=ROOT/'examples/layered-12s-task.json'
    project=ROOT/'examples/layered-12s-project.json'
    payloads=json.loads((ROOT/'examples/layered-12s-handoffs.json').read_text(encoding='utf-8'))
    log=[]
    def call(args,dest):
        run=subprocess.run([sys.executable,str(ROOT/'scripts/workflow.py'),*map(str,args),'--out',str(dest)],capture_output=True,text=True,encoding='utf-8')
        if run.returncode:raise RuntimeError(run.stderr)
        log.append({'command':[str(x) for x in args[:2]],'output':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
        return json.loads(dest.read_text(encoding='utf-8'))
    plan=call(['plan',task],out/'plan.json')
    path=out/'run-00.json';call(['init',project,task],path)
    serial=0
    for step in plan['steps']:
        module=step['module']
        call(['context',task,module,'--project',path],out/('context-'+module+'.json'))
        payload=out/(module+'-result.json');payload.write_text(json.dumps(payloads[module],ensure_ascii=False,indent=2),encoding='utf-8')
        serial+=1;dest=out/f'run-{serial:02}.json'
        result=call(['submit',path,module,payload],dest);path=dest
    assert result['workflow']['status']=='text_checked'
    assert result['video_master_prompt'].count('退后，我不想伤你。')==1
    assert len(result['events'])==4
    (out/'trace.json').write_text(json.dumps({'scope':'真实CLI串跑、保存的模型编写交接；非独立模型盲测','calls':log,'status':result['workflow']['status']},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'video-prompt.md').write_text(result['video_master_prompt'],encoding='utf-8')
    print('PASS: plan + init + 6 contexts + 6 checked handoffs; source events retained.')

if __name__=='__main__':main(Path(sys.argv[1]).resolve())

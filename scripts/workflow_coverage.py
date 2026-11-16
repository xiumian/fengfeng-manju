"""Coverage inventory from declared facts, structural signals and explicit discoveries.

Signals are conservative hints, not semantic comprehension or proof of completeness.
"""
import copy
import re

KINDS = {'plot', 'constraint', 'dialogue', 'performance', 'action', 'vfx', 'asset', 'sound', 'camera'}
FEATURE_MAP = {'dialogue':'performance','performance':'performance','action':'action','vfx':'vfx','asset':'assets','sound':'sound','camera':'camera'}
ACTION = re.compile(r'夺剑|挥剑|挥刀|格挡|踢击|拳击|搏斗|兵器交锋|近身攻防|出拳|挥斩')
VFX = re.compile(r'施法|变身|剑气|法阵|法术|护盾破碎|能量冲击|冲击帧|粒子|闪白')
SOUND = re.compile(r'门铃|电话铃|警报声|音乐|配乐|声桥|口型|音色|音效|响起|听见')
PERFORMANCE = re.compile(r'微表情|欲言又止|压笑|眼神|嘴角|隐忍')


def need(ok, message):
    if not ok: raise ValueError(message)


def inventory(project, task):
    events = project.get('events', [])
    wanted = task.get('scope', [])
    chosen = [e for e in events if not wanted or e['id'] in wanted]
    known = {e['id'] for e in events}
    source_ids = {s['id'] for s in project.get('sources', [])}
    result = []
    for e in chosen:
        common = {'event_ids':[e['id']], 'source_ids':e['source_ids']}
        result.append(dict(common, id='event:'+e['id'], kind='plot', description=e['body'], origin='registered_event'))
        for d in e.get('dialogues', []):
            result.append(dict(common, id='dialogue:'+d['id'], kind='dialogue', description=d['text'], origin='registered_dialogue'))
            voice = d.get('kind','dialogue')
            result.append(dict(common, id='voice:'+d['id'], kind='sound',
                               description=f'{d["speaker"]} 的 {voice}、发声与口型归属', origin='structured_voice'))
        for kind, pattern in [('action', ACTION), ('vfx', VFX), ('sound', SOUND), ('performance', PERFORMANCE)]:
            if kind not in e.get('requires', []) and pattern.search(e['body']):
                result.append(dict(common,id='signal:'+kind+':'+e['id'],kind=kind,description=e['body'],origin='conservative_text_signal'))
        for feature in e.get('requires', []):
            kind = 'asset' if feature == 'assets' else feature
            need(kind in FEATURE_MAP, 'unknown event requires feature')
            result.append(dict(common,id='requires:'+kind+':'+e['id'],kind=kind,description=e['body'],origin='declared_event_capability'))
    for i, text in enumerate(project.get('constraints', [])):
        need(isinstance(text,str) and text.strip(), 'constraint must be text')
        result.append({'id':'constraint:'+str(i+1),'kind':'constraint','description':text,'event_ids':[e['id'] for e in chosen],'source_ids':sorted(source_ids),'origin':'registered_constraint'})
    assets=project.get('assets',[])
    need(isinstance(assets,list), 'assets must be a list')
    if assets:
        need(all(isinstance(a,dict) and isinstance(a.get('id'),str) and a['id'] for a in assets),'registered assets require ids')
        result.append({'id':'assets:registry','kind':'asset','description':'核对已登记资产的适配与实际使用职责','event_ids':[e['id'] for e in chosen],'source_ids':sorted(source_ids),'origin':'registered_asset_catalog'})
    need(isinstance(project.get('requirements', []), list), 'requirements must be a list')
    for item in project.get('requirements', []):
        need(isinstance(item,dict), 'requirement must be object')
        need(isinstance(item.get('id'),str) and item['id'] and item.get('kind') in KINDS, 'requirement id/kind invalid')
        need(isinstance(item.get('description'),str) and item['description'].strip(), 'requirement description missing')
        need(isinstance(item.get('event_ids'),list) and item['event_ids'] and set(item['event_ids'])<=known,'requirement has unknown events')
        need(isinstance(item.get('source_ids'),list) and item['source_ids'] and set(item['source_ids'])<=source_ids,'requirement has unknown sources')
        if not wanted or set(item['event_ids']) & set(wanted): result.append(copy.deepcopy(item))
    need(len({i['id'] for i in result})==len(result),'duplicate requirement ids')
    return result


def features(items):
    return {FEATURE_MAP[i['kind']] for i in items if i['kind'] in FEATURE_MAP}


def source_units(project, task):
    wanted=task.get('scope',[])
    ids=({sid for e in project['events'] if e['id'] in wanted for sid in e['source_ids']}
         if wanted else {s['id'] for s in project['sources']})
    units=[]
    for source in project['sources']:
        if source['id'] not in ids:continue
        cursor=0
        for index,line in enumerate(source['text'].splitlines(keepends=True)):
            if line.strip():units.append({'id':source['id']+':L'+str(index+1),'source_id':source['id'],'start':cursor,'end':cursor+len(line)})
            cursor+=len(line)
    return units


def completion(items, task):
    """Owner means current deliverable responsibility, not a new design obligation."""
    mode = task['mode']
    result=[]
    for item in items:
        module=FEATURE_MAP.get(item['kind'])
        if mode in ('grid','edit_grid'):
            owner='assets' if module=='assets' else 'sampling'
        elif mode == 'workbench': owner='workbench'
        else:
            owner=module or 'compile'
        result.append(dict(item, owner=owner))
    return result


def evidence_valid(proof, text):
    if isinstance(proof,str): return bool(proof.strip()) and proof in text
    if isinstance(proof,dict) and set(proof)=={'start','end'}:
        a,b=proof['start'],proof['end']
        return type(a) is int and type(b) is int and 0<=a<b<=len(text)
    return False


def verify_evidence(items, proofs, text, utterances=()):
    need(isinstance(proofs,dict) and set(proofs)=={i['id'] for i in items}, 'requirement coverage missing or unknown ids')
    need(all(evidence_valid(proof,text) for proof in proofs.values()),'coverage evidence must reference actual output text')
    evidence_groups = {}
    for item in items:
        proof = proofs[item['id']]
        quote = text[proof['start']:proof['end']] if isinstance(proof, dict) else proof
        quote = quote.strip()
        need(len(quote) <= 240, 'coverage evidence is too broad; cite a local passage')
        evidence_groups.setdefault(quote, []).append(item)
        if item['kind'] in ('plot','action','vfx','asset','camera'):
            occurrences = ([proof['start']] if isinstance(proof, dict)
                           else [match.start() for match in re.finditer(re.escape(quote), text)])
            need(occurrences and any(not any(u['start'] <= a and a + len(quote) <= u['end'] for u in utterances)
                                    for a in occurrences), 'spoken words alone cannot prove a visual event')
    for quote, group in evidence_groups.items():
        event_groups = [set(item['event_ids']) for item in group
                        if item['kind'] not in ('constraint', 'dialogue') and item.get('origin') != 'structured_voice']
        if len(event_groups) > 1:
            need(set.intersection(*event_groups), 'same coverage evidence reused for unrelated events')


def verify_reviews(items, reviews):
    need(isinstance(reviews, dict) and set(reviews) == {i['id'] for i in items},
         'a review verdict and reason are required for every requirement')
    for item_id, review in reviews.items():
        need(isinstance(review, dict) and set(review) == {'status', 'reason'}
             and review['status'] == 'met' and isinstance(review['reason'], str)
             and len(review['reason'].strip()) >= 8, 'unresolved requirement or missing review reason: ' + item_id)

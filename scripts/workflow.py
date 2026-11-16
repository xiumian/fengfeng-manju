"""Deterministic routing, bounded context and checked handoffs; no model/API calls."""
import argparse
import copy
import hashlib
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workflow_coverage import inventory, features as inventory_features, completion, verify_evidence, verify_reviews, source_units
from workflow_delivery import check_delivery, timing_node_ranges
from workflow_rules import DESIGN, RULES, select_rules

ROOT = Path(__file__).resolve().parents[1]
MODES = {'prompt', 'revise', 'grid', 'edit_grid', 'workbench', 'discuss', 'maintain'}
FEATURES = set(DESIGN) - {'camera'}
CONTRACT_VERSION = '8.2'
RULES_VERSION = '8.2.0'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()).hexdigest()


def plan(task, project=None):
    require(isinstance(task, dict), 'task must be an object')
    mode = task.get('mode')
    require(mode in MODES, 'unknown mode')
    check_delivery(task.get('delivery', {}))
    features = task.get('features', [])
    require(isinstance(features, list) and all(f in FEATURES for f in features), 'unknown features')
    declared = set(features)
    items = inventory(project, task) if project is not None else []
    features = declared | inventory_features(items)
    scope = task.get('scope', [])
    require(isinstance(scope, list) and all(isinstance(s, str) for s in scope), 'scope must be event ids')
    require(len(scope) == len(set(scope)), 'duplicate scope')
    require(mode != 'revise' or scope, 'revise needs explicit scope')
    require(mode != 'revise' or len(scope) == 1, 'use one event per revise task; multi-event changes need separate tasks or a full prompt route')
    if mode == 'maintain':
        auth = task.get('authorization', {})
        require(auth.get('explicit') is True and isinstance(auth.get('user_request'), str) and auth['user_request'].strip(), 'explicit maintenance authorization record required')
        modules = ['maintenance']
    elif mode == 'discuss':
        modules = []
    elif mode == 'workbench':
        modules = ['workbench', 'validate']
    elif mode in ('grid', 'edit_grid'):
        modules = ['source'] + (['assets'] if 'assets' in features else []) + ['sampling', 'validate']
        if mode == 'edit_grid':
            require(isinstance(task.get('target_panel_id'), str) and task['target_panel_id'], 'edit_grid needs target_panel_id')
            require(task.get('image_version') and isinstance(task.get('coordinates'), list) and len(task['coordinates']) == 4, 'edit_grid needs image version and coordinates')
    else:
        modules = ['source'] + [m for m in DESIGN if m in features and m != 'camera'] + ['camera', 'compile', 'validate']
    return {'task': copy.deepcopy(task), 'coverage': completion(items,task), 'steps': [{'module': m, 'rules': RULES[m], 'reason': 'mode=' + mode + ('; declared feature' if m in declared else '; auto requirement: '+','.join(i['id'] for i in items if m in inventory_features([i])) if m in features else '; required stage')} for m in modules]}


def selected(project, task):
    events = project.get('events', [])
    wanted = task.get('scope', [])
    known = {e['id'] for e in events}
    require(set(wanted) <= known, 'scope contains unknown events')
    return [e for e in events if not wanted or e['id'] in wanted]


def stage_events(project, task, module, coverage):
    events = selected(project, task)
    if module not in DESIGN or module == 'camera':
        return events
    assigned = {identity for item in coverage if item['owner'] == module for identity in item['event_ids']}
    return [event for event in events if not assigned or event['id'] in assigned]


def stage_rules(project, task, module, coverage):
    events = stage_events(project, task, module, coverage)
    relevant = [item['description'] for item in coverage if item['owner'] == module]
    return select_rules(module, events, [*project.get('constraints', []), *relevant])


def validate_project(project):
    require(isinstance(project.get('sources'), list) and project['sources'], 'complete sources required')
    sources = project['sources']
    require(all(isinstance(s, dict) and isinstance(s.get('id'), str) and isinstance(s.get('text'), str) and s['text'].strip() for s in sources), 'source id/text required')
    ids = [s['id'] for s in sources]
    require(len(ids) == len(set(ids)), 'duplicate source ids')
    events = project.get('events')
    require(isinstance(events, list) and events, 'complete events required')
    ids = [e.get('id') for e in events]
    require(all(isinstance(i, str) and i for i in ids) and len(ids) == len(set(ids)), 'unique event ids required')
    source_ids = {s['id'] for s in sources}
    dialogue_ids = []
    previous = None
    for e in events:
        require(isinstance(e.get('body'), str) and e['body'].strip(), 'event body required')
        require(isinstance(e.get('source_ids'), list) and e['source_ids'] and set(e['source_ids']) <= source_ids, 'unknown/missing source reference')
        for field in ('start_state', 'end_state'):
            if field in e:
                require(isinstance(e[field], str) and e[field].strip(), 'continuity state must be nonempty text')
        start, end = e.get('start'), e.get('end')
        require(all(type(n) in (int, float) and math.isfinite(n) for n in (start, end)) and 0 <= start < end, 'invalid event time')
        require(previous is None or abs(start - previous) < 1e-6, 'event timeline gap/overlap')
        previous = end
        require(isinstance(e.get('dialogues', []), list), 'dialogues must be list')
        for d in e.get('dialogues', []):
            require(all(isinstance(d.get(k), str) and d[k].strip() for k in ('id', 'speaker', 'text')), 'dialogue fields missing')
            require(d.get('kind', 'dialogue') in ('dialogue', 'OS', 'VO'), 'unknown voice kind')
            dialogue_ids.append(d['id'])
    require(abs(events[0]['start']) < 1e-6, 'timeline must start at zero')
    require(len(dialogue_ids) == len(set(dialogue_ids)), 'duplicate dialogue ids')


def init(project, task):
    p = copy.deepcopy(project)
    validate_project(p)
    selected(p, task)
    if 'workflow' in p:
        p.setdefault('workflow_archives', []).append(p['workflow'])
    p['workflow'] = {'contract_version': CONTRACT_VERSION, 'revision': 1, 'plan': plan(task,p), 'cursor': 0, 'results': [], 'history': [], 'repairs': 0, 'source_hash': fingerprint({k: p.get(k) for k in ('sources', 'events', 'constraints', 'globals', 'requirements', 'assets')}), 'status': 'ready'}
    if task['mode'] == 'revise':
        require(isinstance(p.get('master_sections'), dict) and set(p['master_sections']) == {e['id'] for e in p['events']}, 'revise needs event-indexed master_sections; migrate existing text without guessing')
    return p


def state(project):
    w = project['workflow']
    require(w.get('contract_version') == CONTRACT_VERSION, 'legacy workflow: save old file and reinitialize with ' + CONTRACT_VERSION)
    require(w['source_hash'] == fingerprint({k: project.get(k) for k in ('sources', 'events', 'constraints', 'globals', 'requirements', 'assets')}), 'upstream changed; archive and reinitialize affected task')
    require(w['plan'] == plan(w['plan']['task'],project),'coverage/plan changed outside discovery; reinitialize')
    return w


def receipt(project, module):
    w = state(project)
    rules, _ = stage_rules(project, w['plan']['task'], module, w['plan']['coverage'])
    return {'module': module, 'cursor': w['cursor'], 'revision': w['revision'], 'source_hash': w['source_hash'], 'coverage_hash': fingerprint(w['plan']['coverage']), 'upstream_hash': fingerprint(w['results']), 'rules_hash': fingerprint(rules)}


def context(task, module, project=None):
    route = state(project)['plan'] if project is not None else plan(task)
    require(module in [s['module'] for s in route['steps']], 'module not in selected route')
    rules, candidates = (stage_rules(project, task, module, route['coverage'])
                         if project is not None else select_rules(module))
    result = {'module': module, 'task': task, 'rules': rules}
    if module == 'vfx':
        result['vfx_candidates'] = candidates
    if project is not None:
        w = state(project)
        require(w['plan']['task'] == task, 'task differs from active workflow')
        events = stage_events(project, task, module, route['coverage'])
        chosen = {e['id'] for e in events}
        all_events = project['events']
        neighbors = set()
        for i, e in enumerate(all_events):
            if e['id'] in chosen:
                neighbors.update(j for j in (i-1, i+1) if 0 <= j < len(all_events) and all_events[j]['id'] not in chosen)
        result.update(events=events, adjacent_states=[{k: all_events[j].get(k) for k in ('id', 'start_state', 'end_state')} for j in sorted(neighbors)], constraints=project.get('constraints', []), globals=project.get('globals', {}), upstream=[r for r in w['results'] if r['module'] != module])
        result['coverage'] = w['plan']['coverage']
        result['receipt'] = receipt(project,module)
        if module in ('source', 'validate'):
            units = source_units(project, task)
            source_ids = {u['source_id'] for u in units}
            result['sources'] = [s for s in project['sources'] if s['id'] in source_ids]
            result['source_units'] = units
        if module in ('assets', 'compile', 'sampling', 'validate'):
            result['assets'] = project.get('assets', [])
        if module == 'sampling':
            result['video_master_prompt'] = project.get('video_master_prompt', '')
            result['panels'] = project.get('panels', [])
    return result


def submit(project, module, payload, context_receipt=None):
    p = copy.deepcopy(project)
    w = state(p)
    steps = [s['module'] for s in w['plan']['steps']]
    require(w['cursor'] < len(steps) and steps[w['cursor']] == module, 'out-of-order or unplanned submission')
    require(context_receipt == receipt(p,module), 'current context receipt required; load module context after any upstream change')
    require(isinstance(payload, dict), 'payload must be object')
    task = w['plan']['task']
    events = stage_events(p, task, module, w['plan']['coverage'])
    ids = {e['id'] for e in events}
    if module == 'source':
        require(set(payload) == {'checked_event_ids','source_coverage'} and set(payload['checked_event_ids']) == ids, 'source must explicitly check scope')
        units=source_units(p,task);mapping=payload['source_coverage']
        require(isinstance(mapping,dict) and set(mapping)=={u['id'] for u in units},'source paragraph coverage missing')
        require(all(isinstance(v,dict) and set(v)=={'event_ids','reason'} and isinstance(v['event_ids'],list) and v['event_ids'] and set(v['event_ids'])<=ids and isinstance(v['reason'],str) and v['reason'].strip() for v in mapping.values()), 'source coverage must map each paragraph to events with a reason')
        by_id = {e['id']: e for e in events}
        require(all(all(u['source_id'] in by_id[identity]['source_ids'] for identity in mapping[u['id']]['event_ids'])
                    for u in units), 'source paragraph refers to an event that is not linked to that source; reconcile the source before continuing')
        if task['mode'] in ('grid', 'edit_grid'):
            require(isinstance(p.get('video_master_prompt'), str) and p['video_master_prompt'].strip(), 'sampling needs saved master')
    elif module in DESIGN:
        require(set(payload) == {'design'} and isinstance(payload['design'], dict) and set(payload['design']) == ids and all(isinstance(v, str) and v.strip() for v in payload['design'].values()), 'design must cover assigned events only and cannot write upstream fields')
    elif module == 'compile':
        require({'text', 'event_ids', 'dialogue_ids', 'coverage'} <= set(payload)
                <= {'text', 'event_ids', 'dialogue_ids', 'coverage', 'utterances', 'timing_nodes'}, 'compile fields not allowed')
        require(set(payload['event_ids']) == ids, 'missing event coverage')
        text = payload['text']
        require(isinstance(text, str) and text.strip(), 'empty master')
        require(not any(line.strip() in ('undefined','null','NaN') for line in text.splitlines()), 'invalid placeholder')
        require(not re.search(r'<[^<>\n]+>|\{\{|\$\{', text), 'unreplaced template variable')
        dialogues = [d for e in events for d in e.get('dialogues', [])]
        require(set(payload['dialogue_ids']) == {d['id'] for d in dialogues}, 'missing dialogue coverage')
        utterances = payload.get('utterances', [])
        if dialogues:
            require(isinstance(utterances,list) and len(utterances)==len(dialogues), 'exact utterance spans required')
            last_end = -1
            for d, u in zip(dialogues, utterances):
                require(isinstance(u,dict) and set(u)=={'id','speaker','start','end'}, 'utterance fields invalid')
                a,b=u['start'],u['end']
                require(type(a) is int and type(b) is int and last_end<=a<b<=len(text), 'utterance spans overlap or out of order')
                require(u['id']==d['id'] and u['speaker']==d['speaker'] and text[a:b]==d['text'],'utterance does not match original dialogue')
                last_end=b
            # 若采用明确的台词行，再检查全文台词行，防止登记一次而实际写两次。
            lines=re.findall(r'^([^\n：:（）]{1,40})(?:（[^）\n]*）)?[：:]\s*[“\"]([^”\"\n]*)[”\"]',text,re.M)
            if lines:
                known_speakers={d['speaker'] for d in dialogues}
                normalize_speaker=lambda name:name.strip() if name.strip() in known_speakers else name.strip().removesuffix('台词').removesuffix('说')
                require([(normalize_speaker(speaker),line) for speaker,line in lines]==[(d['speaker'],d['text']) for d in dialogues], 'spoken dialogue lines missing/repeated or wrong speaker')
            for speaker in sorted({d['speaker'] for d in dialogues}):
                for marker in re.finditer(re.escape(speaker) + r'[^\n：:]{0,12}(?:说|问|答|补充|对白|台词|独白)[：:]\s*(?![“"「『‘])', text):
                    if any(u['start'] == marker.end() for u in utterances):
                        continue
                    # Detect an original spoken line repeated without quote marks.
                    require(not any(text.startswith(d['text'], marker.end()) for d in dialogues if d['speaker'] == speaker),
                            'unregistered repeated spoken dialogue')
        else:
            require(not utterances, 'unexpected utterance entries')
        verify_evidence(w['plan']['coverage'], payload['coverage'], text, utterances)
        if 'timing_nodes' in payload:
            timing_node_ranges(text, payload['timing_nodes'], task.get('delivery', {}).get('duration'))
        executed = {r['module'] for r in w['results']}
        require(all(i['owner']=='compile' or i['owner'] in executed for i in w['plan']['coverage']), 'required module coverage not executed')
        p.setdefault('video_master_history', []).append(p.get('video_master_prompt', ''))
        if task['mode'] == 'revise':
            require('timing_nodes' not in payload, 'a local revision cannot replace the complete delivery timing plan')
            p.setdefault('master_patches', []).append({'scope': sorted(ids), 'text': text})
            require(len(ids) == 1, 'multi-event revision must be submitted as separate event-scoped tasks')
            p['master_sections'][next(iter(ids))] = text
            p['video_master_prompt'] = p.get('master_prefix', '') + '\n' + '\n'.join(p['master_sections'][e['id']] for e in p['events'])
            p.pop('timing_nodes', None)  # The previous headings belonged to a different master.
            p.pop('master_utterances', None)
        else:
            p['video_master_prompt'] = text
            p['master_utterances'] = copy.deepcopy(utterances)
            if 'timing_nodes' in payload:
                p['timing_nodes'] = copy.deepcopy(payload['timing_nodes'])
            else:
                p.pop('timing_nodes', None)
    elif module == 'sampling':
        require(set(payload) == {'panels'} and isinstance(payload['panels'], list), 'sampling can only write panels')
        panels = payload['panels']
        require(len(panels) == (1 if task['mode'] == 'edit_grid' else 9), 'wrong panel count')
        require(len({x.get('id') for x in panels}) == len(panels), 'duplicate panels')
        by_id = {e['id']: e for e in p['events']}
        for panel in panels:
            require(isinstance(panel.get('id'), str) and panel['id'], 'panel id required')
            refs = panel.get('event_ids', [])
            require(isinstance(refs, list) and refs and set(refs) <= ids, 'panel references unknown/out-of-scope events')
            t = panel.get('sample_time')
            require(type(t) in (int, float) and math.isfinite(t) and any(by_id[i]['start'] <= t <= by_id[i]['end'] for i in refs), 'sample outside referenced event')
            require(isinstance(panel.get('prompt'), str) and panel['prompt'].strip(), 'panel prompt missing')
        if task['mode'] == 'edit_grid':
            require(panels[0]['id'] == task['target_panel_id'], 'wrong target panel')
            old = p.get('panels', [])
            require(any(x['id'] == panels[0]['id'] for x in old), 'target not in project')
            p['panels'] = [panels[0] if x['id'] == panels[0]['id'] else x for x in old]
        else:
            require(len({round(panel['sample_time'], 6) for panel in panels}) == 9,
                    'grid requires nine distinct sample times')
            require(len({re.sub(r'\s+', '', panel['prompt']) for panel in panels}) == 9,
                    'grid requires nine distinct observation descriptions')
            p['panels'] = panels
    elif module == 'validate':
        require(set(payload) == {'content_checked', 'evidence', 'limitations','coverage','requirement_reviews'}, 'validation fields not allowed')
        require(payload['content_checked'] is True and isinstance(payload['evidence'], dict) and set(payload['evidence']) == ids and all(isinstance(v,str) and len(v.strip()) >= 8 for v in payload['evidence'].values()), 'content evidence required')
        require(isinstance(payload['limitations'], list), 'limitations must be list')
        text = p.get('video_master_prompt','') if task['mode'] not in ('grid','edit_grid') else '\n'.join(x['prompt'] for x in p.get('panels',[]))+'\n'+p.get('video_master_prompt','')
        if task['mode']=='workbench': text='\n'.join(r['payload'].get('record','') for r in w['results'])
        verify_evidence(w['plan']['coverage'], payload['coverage'], text,
                        p.get('master_utterances', []) if task['mode'] == 'prompt' else [])
        verify_reviews(w['plan']['coverage'], payload['requirement_reviews'])
        executed = {r['module'] for r in w['results']}
        require(all(i['owner'] in executed for i in w['plan']['coverage']), 'coverage owner not executed')
    elif module in ('workbench', 'maintenance'):
        require(set(payload) == {'record'} and isinstance(payload['record'], str) and payload['record'].strip(), 'execution record required')
    w['results'].append({'module': module, 'payload': copy.deepcopy(payload), 'context_receipt': copy.deepcopy(context_receipt)})
    w['cursor'] += 1
    w['status'] = 'text_checked' if w['cursor'] == len(steps) else 'ready'
    if w['cursor'] == len(steps) and task['mode'] in ('workbench', 'maintain'):
        w['status'] = 'recorded_not_media_verified'
    if w['cursor'] == len(steps) and task['mode'] in ('grid', 'edit_grid'):
        w['status'] = 'awaiting_actual_image_and_user_acceptance'
    return p


def repair(project, target, reason):
    p = copy.deepcopy(project)
    w = state(p)
    require(isinstance(reason, str) and reason.strip(), 'repair reason required')
    modules = [s['module'] for s in w['plan']['steps']]
    require(target in modules and modules.index(target) < w['cursor'], 'repair target must be previously executed')
    require(w['repairs'] < 2, 'repair budget exhausted; report unresolved issue')
    index = modules.index(target)
    w['history'].append({'reason': reason, 'target': target, 'invalidated': w['results'][index:]})
    w['results'] = w['results'][:index]
    w['cursor'] = index
    w['repairs'] += 1
    w['revision'] += 1
    w['status'] = 'repair_required'
    return p


def discover(project, request):
    """Add processing needs anchored in existing sources, without editing story facts."""
    p=copy.deepcopy(project);w=state(p)
    require(w['plan']['task']['mode'] in ('prompt','revise','grid','edit_grid'), 'discovery applies to production tasks only')
    require(isinstance(request,dict) and set(request)=={'reason','requirements'}, 'discovery needs reason and requirements')
    require(isinstance(request['reason'],str) and request['reason'].strip(), 'discovery reason missing')
    require(isinstance(request['requirements'],list) and request['requirements'], 'new requirements missing')
    require(w['repairs']<2, 'repair/discovery budget exhausted; report unresolved issue')
    sources={s['id']:s['text'] for s in p['sources']}
    old_ids={i['id'] for i in w['plan']['coverage']}
    scope={e['id'] for e in selected(p,w['plan']['task'])}
    for item in request['requirements']:
        require(isinstance(item,dict) and item.get('id') not in old_ids,'duplicate discovery requirement')
        require(set(item.get('event_ids',[]))<=scope,'discovery outside active scope')
        quote=item.get('source_quote')
        require(isinstance(quote,str) and quote.strip() and any(sid in sources and quote in sources[sid] for sid in item.get('source_ids',[])), 'discovery must cite existing source text, not invent facts')
        old_ids.add(item.get('id'))
    p.setdefault('requirements',[]).extend(copy.deepcopy(request['requirements']))
    new_plan=plan(w['plan']['task'],p)  # Validates new requirements before mutation is returned.
    old_modules=[s['module'] for s in w['plan']['steps']];new_modules=[s['module'] for s in new_plan['steps']]
    keep=0
    while keep<min(w['cursor'],len(old_modules),len(new_modules)) and old_modules[keep]==new_modules[keep]:keep+=1
    added_ids={i['id'] for i in request['requirements']}
    for item in new_plan['coverage']:
        if item['id'] in added_ids and item['owner'] in new_modules:
            keep=min(keep,new_modules.index(item['owner']))
    w['history'].append({'type':'discovery','reason':request['reason'],'added_requirements':copy.deepcopy(request['requirements']),'old_plan':w['plan'],'invalidated':w['results'][keep:]})
    w['results']=w['results'][:keep];w['cursor']=keep;w['plan']=new_plan
    w['repairs']+=1;w['revision']+=1;w['status']='discovery_required'
    w['source_hash']=fingerprint({k:p.get(k) for k in ('sources','events','constraints','globals','requirements','assets')})
    return p


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def to_workbench(project):
    validate_project(project)
    w = state(project)
    require(w['status'] == 'awaiting_actual_image_and_user_acceptance', 'complete grid planning and text checks first')
    require(not w['plan']['task'].get('scope'), 'export a complete segment, not a partial scope')
    panels = project.get('panels', [])
    require(len(panels) == 9 and project.get('video_master_prompt'), 'nine samples and saved master required')
    board = {'segment_id': project.get('segment_id', 'SEG01'), 'title': project.get('title', '分层项目'), 'events': copy.deepcopy(project['events']), 'events_complete': True, 'source_coverage_checked': True, 'video_master_prompt': project['video_master_prompt'], 'video_master_history': project.get('video_master_history', []), 'versions': [], 'image_data_url': '', 'image_name': '', 'completed': False, 'generation_state': 'prompt_ready', 'panels': [], 'global_constraints': '；'.join(project.get('constraints', []))}
    for panel in panels:
        row = {key: '' for key in ('expected','actual','change','edit_prompt','reverse_note','reverse_prompt_note','performance','character_anchor','scene_anchor','continuity','asset_refs')}
        row.update(copy.deepcopy(panel))
        row.update(action=panel['prompt'], shot_ref=panel.get('shot_ref',''), observation_state=panel.get('observation_state', '采样状态'), reverse_status='pending')
        row.setdefault('duration', None)
        row.setdefault('shot_size', '未记录')
        row.setdefault('camera_move', '未记录')
        board['panels'].append(row)
    return {'package_type': 'open-cowart-nine-grid-project', 'script_name': project.get('title', '分层项目'), 'source_text': '\n'.join(s['text'] for s in project['sources']), 'sources': copy.deepcopy(project['sources']), 'pipeline_stage': 3, 'last_packaged_at': '', 'project_options': {'emotion_closeup_mode':'off'}, 'segments': [board]}


def main():
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=['plan','context','init','submit','repair','discover','check','workbench-json'])
    ap.add_argument('input')
    ap.add_argument('extra', nargs='*')
    ap.add_argument('--project')
    ap.add_argument('--context', dest='context_file')
    ap.add_argument('--out')
    args = ap.parse_args()
    try:
        data = load(args.input)
        if args.command == 'plan': result = plan(data,load(args.project) if args.project else None)
        elif args.command == 'context': result = context(data, args.extra[0], load(args.project) if args.project else None)
        elif args.command == 'init': result = init(data, load(args.extra[0]))
        elif args.command == 'submit':
            packet=load(args.context_file) if args.context_file else {}
            result = submit(data, args.extra[0], load(args.extra[1]),packet.get('receipt'))
        elif args.command == 'repair': result = repair(data, args.extra[0], args.extra[1])
        elif args.command == 'discover': result = discover(data,load(args.extra[0]))
        elif args.command == 'workbench-json': result = to_workbench(data)
        else:
            validate_project(data)
            if 'workflow' in data: state(data)
            result = {'structure': 'passed', 'semantic_and_media': 'not automatically verified'}
        text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
        if args.out:
            out = Path(args.out)
            require(out.resolve() != Path(args.input).resolve(), 'write a new version; do not overwrite input')
            out.write_text(text + '\n', encoding='utf-8')
        else: print(text)
    except (ValueError, KeyError, IndexError, TypeError) as error:
        ap.exit(2, 'ERROR: ' + str(error) + '\n')


if __name__ == '__main__': main()

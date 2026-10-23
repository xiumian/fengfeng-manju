"""Deterministic routing, bounded context and checked handoffs; no model/API calls."""
import argparse
import copy
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODES = {'prompt', 'revise', 'grid', 'edit_grid', 'workbench', 'discuss', 'maintain'}
FEATURES = {'assets', 'action', 'performance', 'vfx', 'sound'}
DESIGN = ('assets', 'action', 'performance', 'vfx', 'sound', 'camera')
RULES = {m: ['references/modules/' + m + '.md'] for m in (*DESIGN, 'source', 'compile', 'sampling', 'validate')}
RULES['compile'].append('references/video-prompt-template.txt')
RULES.update(workbench=['references/workbench-v8.md'], maintenance=['maintenance/change-control.md'])


def require(ok, message):
    if not ok:
        raise ValueError(message)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()).hexdigest()


def plan(task):
    require(isinstance(task, dict), 'task must be an object')
    mode = task.get('mode')
    require(mode in MODES, 'unknown mode')
    features = task.get('features', [])
    require(isinstance(features, list) and all(f in FEATURES for f in features), 'unknown features')
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
        modules = ['source'] + [m for m in DESIGN if m in features] + ['camera', 'compile', 'validate']
    return {'task': copy.deepcopy(task), 'steps': [{'module': m, 'rules': RULES[m], 'reason': 'mode=' + mode + ('; feature=' + m if m in features else '; required stage')} for m in modules]}


def selected(project, task):
    events = project.get('events', [])
    wanted = task.get('scope', [])
    known = {e['id'] for e in events}
    require(set(wanted) <= known, 'scope contains unknown events')
    return [e for e in events if not wanted or e['id'] in wanted]


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
    p['workflow'] = {'plan': plan(task), 'cursor': 0, 'results': [], 'history': [], 'repairs': 0, 'source_hash': fingerprint({k: p.get(k) for k in ('sources', 'events', 'constraints', 'globals')}), 'status': 'ready'}
    if task['mode'] == 'revise':
        require(isinstance(p.get('master_sections'), dict) and set(p['master_sections']) == {e['id'] for e in p['events']}, 'revise needs event-indexed master_sections; migrate existing text without guessing')
    return p


def state(project):
    w = project['workflow']
    require(w['source_hash'] == fingerprint({k: project.get(k) for k in ('sources', 'events', 'constraints', 'globals')}), 'upstream changed; archive and reinitialize affected task')
    return w


def context(task, module, project=None):
    route = plan(task)
    require(module in [s['module'] for s in route['steps']], 'module not in selected route')
    result = {'module': module, 'task': task, 'rules': [{'path': path, 'text': (ROOT / path).read_text(encoding='utf-8')} for path in RULES[module]]}
    if project is not None:
        w = state(project)
        require(w['plan']['task'] == task, 'task differs from active workflow')
        events = selected(project, task)
        chosen = {e['id'] for e in events}
        all_events = project['events']
        neighbors = set()
        for i, e in enumerate(all_events):
            if e['id'] in chosen:
                neighbors.update(j for j in (i-1, i+1) if 0 <= j < len(all_events) and all_events[j]['id'] not in chosen)
        result.update(events=events, adjacent_states=[{k: all_events[j].get(k) for k in ('id', 'start_state', 'end_state')} for j in sorted(neighbors)], constraints=project.get('constraints', []), globals=project.get('globals', {}), upstream=[r for r in w['results'] if r['module'] != module])
        if module == 'source':
            source_ids = {sid for e in events for sid in e['source_ids']}
            result['sources'] = [s for s in project['sources'] if s['id'] in source_ids]
        if module == 'sampling':
            result['video_master_prompt'] = project.get('video_master_prompt', '')
            result['panels'] = project.get('panels', [])
    return result


def submit(project, module, payload):
    p = copy.deepcopy(project)
    w = state(p)
    steps = [s['module'] for s in w['plan']['steps']]
    require(w['cursor'] < len(steps) and steps[w['cursor']] == module, 'out-of-order or unplanned submission')
    require(isinstance(payload, dict), 'payload must be object')
    task = w['plan']['task']
    events = selected(p, task)
    ids = {e['id'] for e in events}
    if module == 'source':
        require(set(payload) == {'checked_event_ids'} and set(payload['checked_event_ids']) == ids, 'source must explicitly check scope')
        if task['mode'] in ('grid', 'edit_grid'):
            require(isinstance(p.get('video_master_prompt'), str) and p['video_master_prompt'].strip(), 'sampling needs saved master')
    elif module in DESIGN:
        require(set(payload) == {'design'} and isinstance(payload['design'], dict) and set(payload['design']) == ids and all(isinstance(v, str) and v.strip() for v in payload['design'].values()), 'design must cover scope and cannot write upstream fields')
    elif module == 'compile':
        require(set(payload) == {'text', 'event_ids', 'dialogue_ids'}, 'compile fields not allowed')
        require(set(payload['event_ids']) == ids, 'missing event coverage')
        text = payload['text']
        require(isinstance(text, str) and text.strip(), 'empty master')
        require(not any(line.strip() in ('undefined','null','NaN') for line in text.splitlines()), 'invalid placeholder')
        require(not re.search(r'<[^<>\n]+>|\{\{|\$\{', text), 'unreplaced template variable')
        dialogues = [d for e in events for d in e.get('dialogues', [])]
        require(set(payload['dialogue_ids']) == {d['id'] for d in dialogues}, 'missing dialogue coverage')
        # 同文台词可来自不同发声事件；按登记次数检查，不误判为一律只能发声一次。
        expected = {}
        for d in dialogues:
            expected[d['text']] = expected.get(d['text'], 0) + 1
        require(all(text.count(t) == count for t, count in expected.items()), 'original dialogue missing/repeated')
        p.setdefault('video_master_history', []).append(p.get('video_master_prompt', ''))
        if task['mode'] == 'revise':
            p.setdefault('master_patches', []).append({'scope': sorted(ids), 'text': text})
            require(len(ids) == 1, 'multi-event revision must be submitted as separate event-scoped tasks')
            p['master_sections'][next(iter(ids))] = text
            p['video_master_prompt'] = p.get('master_prefix', '') + '\n' + '\n'.join(p['master_sections'][e['id']] for e in p['events'])
        else:
            p['video_master_prompt'] = text
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
            p['panels'] = panels
    elif module == 'validate':
        require(set(payload) == {'content_checked', 'evidence', 'limitations'}, 'validation fields not allowed')
        require(payload['content_checked'] is True and isinstance(payload['evidence'], dict) and set(payload['evidence']) == ids and all(isinstance(v,str) and len(v.strip()) >= 8 for v in payload['evidence'].values()), 'content evidence required')
        require(isinstance(payload['limitations'], list), 'limitations must be list')
    elif module in ('workbench', 'maintenance'):
        require(set(payload) == {'record'} and isinstance(payload['record'], str) and payload['record'].strip(), 'execution record required')
    w['results'].append({'module': module, 'payload': copy.deepcopy(payload)})
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
    w['status'] = 'repair_required'
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
        row.update(action=panel['prompt'], duration=1, shot_size='中景', camera_move='固定镜头', shot_ref=panel.get('shot_ref',''), observation_state=panel.get('observation_state', '采样状态'), reverse_status='pending')
        board['panels'].append(row)
    return {'package_type': 'open-cowart-nine-grid-project', 'script_name': project.get('title', '分层项目'), 'source_text': '\n'.join(s['text'] for s in project['sources']), 'sources': copy.deepcopy(project['sources']), 'pipeline_stage': 3, 'last_packaged_at': '', 'project_options': {'emotion_closeup_mode':'off'}, 'segments': [board]}


def main():
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=['plan','context','init','submit','repair','check','workbench-json'])
    ap.add_argument('input')
    ap.add_argument('extra', nargs='*')
    ap.add_argument('--project')
    ap.add_argument('--out')
    args = ap.parse_args()
    try:
        data = load(args.input)
        if args.command == 'plan': result = plan(data)
        elif args.command == 'context': result = context(data, args.extra[0], load(args.project) if args.project else None)
        elif args.command == 'init': result = init(data, load(args.extra[0]))
        elif args.command == 'submit': result = submit(data, args.extra[0], load(args.extra[1]))
        elif args.command == 'repair': result = repair(data, args.extra[0], args.extra[1])
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

"""One transient handoff for short text jobs; not a semantic judge."""
import hashlib
import json
import math
import re

from workflow_delivery import SHOT_TIME, check_delivery, check_direct, shot_blocks, timing_node_ranges


class DeliveryBlocked(ValueError):
    def __init__(self, return_to, reason):
        self.return_to = return_to
        super().__init__(reason)


def require(ok, stage, reason):
    if not ok:
        raise DeliveryBlocked(stage, reason)


def text_value(value):
    return isinstance(value, str) and bool(value.strip())


def reviewed(card, review_ids):
    review = card.get('review')
    require(isinstance(review, dict) and set(review) == review_ids, 'validate', 'review coverage is incomplete')
    stages = ('source', 'assets', 'action', 'performance', 'vfx', 'sound', 'camera', 'compile')
    failures = []
    for key, row in review.items():
        require(isinstance(row, dict) and text_value(row.get('reason')), 'validate', f'{key}: review reason is missing')
        if row.get('status') == 'unmet':
            target = row.get('return_to')
            require(target in stages, 'validate', f'{key}: review needs a responsible stage')
            failures.append((target, f'{key}: '+row['reason']))
        else:
            require(row.get('status') == 'met', 'validate', f'{key}: review verdict is missing')
    if failures:
        target, reason = min(failures, key=lambda item: stages.index(item[0]))
        raise DeliveryBlocked(target, reason)
    return review


def cite(quote, reference, label, stage='validate'):
    require(text_value(quote) and len(quote) <= 240 and quote in reference,
            stage, f'{label} must cite the actual passage')


BOARD_TIME = re.compile(r'(?<![0-9.])([0-9]+(?:\.[0-9]+)?)\s*(?:秒|s)?\s*[-—–~～至]\s*'
                        r'([0-9]+(?:\.[0-9]+)?)\s*(?:秒|s)', re.I)
FOCAL_FEEL = re.compile(r'[0-9]+(?:\.[0-9]+)?\s*(?:mm\b|毫米)|广角|[宽窄]视[角野]|标准(?:视角|焦段|镜头)'
                        r'|中焦|中长焦|长焦|短焦|wide[- ]angle|normal perspective|telephoto', re.I)


def viewing_plan_ids(card):
    beats = card.get('view_plan')
    require(isinstance(beats, list) and beats, 'camera', 'a whole-scene viewing plan is required')
    ids = []
    for beat in beats:
        require(isinstance(beat, dict) and set(beat) == {'id', 'change', 'see', 'choice'}
                and all(text_value(v) for v in beat.values())
                and re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]*', beat['id']),
                'camera', 'a viewing plan beat needs id, change, see and choice')
        ids.append(beat['id'])
    require(len(ids) == len(set(ids)), 'camera', 'duplicate viewing plan beat ids')
    return ids


def viewing_plan_fingerprint(card):
    value = {key: card[key] for key in ('source', 'view_plan')}
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def storyboard_plan(card):
    """Check the planning handoff before it has any drafted shots."""
    require(isinstance(card, dict) and set(card) == {'source', 'view_plan'}, 'camera',
            'storyboard-plan accepts only source and view_plan, before the storyboard draft')
    light_source(card)
    return {'status': 'storyboard_plan_checked', 'beats': viewing_plan_ids(card),
            'plan_receipt': viewing_plan_fingerprint(card)}


def locked_view_plan(card):
    planned = {i: set() for i in viewing_plan_ids(card)}
    require(card.get('plan_receipt') == viewing_plan_fingerprint(card), 'camera',
            'viewing plan receipt missing or changed; check the viewing plan before drafting')
    return planned


def link_view_plan(design, planned):
    last_watch = None
    for i, shot in enumerate(design, 1):
        key = f'shot:{i}'
        watch = re.sub(r'\s+', '', shot['watch'])
        require(watch != last_watch, 'camera', f'{key}: adjacent shots repeat the same viewing task')
        last_watch = watch
        beats = shot.get('beats')
        require(isinstance(beats, list) and all(isinstance(b, str) and b in planned for b in beats),
                'camera', f'{key}: beats must refer to the viewing plan')
        for beat in beats:
            planned[beat].add(key)
    missing = [key for key, shots in planned.items() if not shots]
    require(not missing, 'camera', 'uncovered viewing beat: '+', '.join(missing))


def camera_terms(shot, key):
    focal, framing = shot.get('focal'), shot.get('framing')
    require(text_value(focal) and FOCAL_FEEL.search(focal), 'camera',
            f'{key}: focal or lens feel is required, not only shot size')
    require(text_value(framing), 'camera', f'{key}: framing and camera position are required')
    motion = shot.get('motion')
    require(isinstance(motion, dict) and set(motion) in ({'fixed'}, {'trigger', 'path', 'stop'})
            and all(text_value(value) for value in motion.values()), 'camera',
            f'{key}: motion needs fixed or trigger/path/stop')
    if 'fixed' in motion:
        require(re.search(r'固定|不动|不移|锁定机位|\b(?:static|locked|fixed)\b', motion['fixed'], re.I),
                'camera', f'{key}: motion must explicitly describe a fixed camera')
    else:
        require(len({value.strip() for value in motion.values()}) == 3, 'camera',
                f'{key}: motion trigger, path and stop must not be the same phrase')
    return {'focal': focal, 'framing': framing, **{f'motion {k}': v for k, v in motion.items()}}


def verify_reveal_order(planned, evidence_for, bodies):
    reveal = (0, 0)
    for beat, shots in planned.items():
        key = f'beat:{beat}'
        evidence = evidence_for(key)
        require(isinstance(evidence, dict) and evidence and set(evidence) <= shots,
                'validate', f'{key}: evidence must cite linked shots')
        for name, quote in evidence.items():
            cite(quote, bodies[name], f'{key}: {name} evidence')
        resolved_at = max((int(name.split(':', 1)[1]), bodies[name].index(quote))
                          for name, quote in evidence.items())
        require(resolved_at >= reveal, 'camera', f'{key}: the draft changes the planned reveal order')
        reveal = resolved_at


def storyboard_deliver(card, requirements, dialogues, duration, timing):
    planned = locked_view_plan(card)
    design = card.get('design')
    require(isinstance(design, list) and design and all(isinstance(s, dict) for s in design),
            'camera', 'storyboard design is missing')
    drafts = card.get('drafts')
    require(isinstance(drafts, dict) and set(drafts) == {'storyboard'} and text_value(drafts['storyboard']),
            'camera', 'a storyboard draft is required')
    draft = drafts['storyboard']
    explicit = timing == 'explicit'
    timed = duration is not None or explicit or any('start' in s or 'end' in s for s in design)
    anchors = []
    last_time, cursor = 0, 0
    for i, shot in enumerate(design, 1):
        key = f'shot:{i}'
        heading = shot.get('heading')
        require(text_value(heading) and len(heading.splitlines()) == 1 and draft.count(heading) == 1,
                'camera', f'{key}: a unique heading must appear in the draft')
        start = draft.index(heading)
        end = start+len(heading)
        require(start >= cursor and text_value(shot.get('watch')),
                'camera', f'{key}: headings must be ordered and each shot needs a viewing task')
        anchors.append((start, end))
        cursor = end
        if timed:
            a, b = shot.get('start'), shot.get('end')
            require(all(type(n) in (int, float) and math.isfinite(n) for n in (a, b))
                    and math.isclose(a, last_time, abs_tol=1e-6, rel_tol=0) and b > a,
                    'camera', f'{key}: timing must be continuous from zero')
            span = BOARD_TIME.search(heading)
            require(not explicit or span, 'camera', f'{key}: explicit heading times are missing')
            if span:
                require(all(math.isclose(float(s), n, abs_tol=1e-6, rel_tol=0) for s, n in zip(span.groups(), (a, b))),
                        'camera', f'{key}: heading times differ from the planned interval')
            last_time = b
    require(duration is None or math.isclose(last_time, duration, abs_tol=1e-6, rel_tol=0),
            'camera', 'storyboard does not cover the locked duration')
    link_view_plan(design, planned)

    bodies = {}
    for i, (shot, (_, end)) in enumerate(zip(design, anchors), 1):
        key = f'shot:{i}'
        body = bodies[key] = draft[end:anchors[i][0] if i < len(anchors) else len(draft)]
        for field, phrase in camera_terms(shot, key).items():
            cite(phrase, body, f'{key}: {field}', 'camera')

    cursor = 0
    shot_text = draft[anchors[0][0]:]
    for line in dialogues:
        start = shot_text.find(line, cursor)
        require(start >= 0, 'camera', 'storyboard missing original dialogue or wrong order')
        cursor = start+len(line)

    cuts = {f'cut:{i}': {'out': bodies[f'shot:{i}'], 'in': bodies[f'shot:{i+1}']}
            for i in range(1, len(design))}
    beat_ids = {f'beat:{key}' for key in planned}
    review = reviewed(card, set(requirements) | set(bodies) | set(cuts) | beat_ids)
    verify_reveal_order(planned, lambda key: review[key].get('evidence'), bodies)
    for key, row in review.items():
        if key in beat_ids:
            continue
        references = cuts[key] if key in cuts else {'storyboard': bodies.get(key, draft)}
        evidence = row.get('evidence')
        require(isinstance(evidence, dict) and set(evidence) == set(references),
                'validate', f'{key}: missing evidence for the actual storyboard')
        for name, reference in references.items():
            cite(evidence[name], reference, f'{key}: {name} evidence')
    return {'status': 'ready_to_deliver', 'outputs': {'storyboard': draft}}


def light_source(card):
    require(isinstance(card, dict), 'source', 'source handoff is missing')
    source = card.get('source')
    require(isinstance(source, dict) and text_value(source.get('scope')), 'source', 'source scope is missing')
    requirements = source.get('requirements')
    require(isinstance(requirements, dict) and requirements
            and all(text_value(k) and not k.startswith(('shot:', 'beat:', 'cut:', 'hold:')) and text_value(v)
                    for k, v in requirements.items()), 'source', 'source requirements are missing or invalid')
    duration, timing = source.get('duration'), source.get('timing', 'relative')
    outputs = source.get('outputs', ['master', 'direct'])
    copy_format = source.get('copy_format', 'full')
    dialogues = source.get('dialogues')
    board = outputs == ['storyboard']
    require(board or (isinstance(outputs, list) and outputs and all(key in ('master', 'direct') for key in outputs)
            and len(outputs) == len(set(outputs))), 'source', 'source delivery selection is invalid')
    require(copy_format == 'full' or (copy_format == 'compact' and 'direct' in outputs),
            'source', 'invalid copy format')
    require(isinstance(dialogues, list) and all(text_value(line) for line in dialogues),
            'source', 'source dialogues must be registered in order, or explicitly empty')
    try:
        check_delivery({'duration': duration, 'timing': timing})
    except ValueError as error:
        raise DeliveryBlocked('source', str(error)) from error
    return source


def prompt_camera_plan(card, source=None):
    """Check the camera handoff before seeing a compiled prompt."""
    if source is None:
        source = light_source(card)
    duration, timing = source.get('duration'), source.get('timing', 'relative')
    planned = locked_view_plan(card)
    design = card.get('design')
    require(isinstance(design, list) and design, 'camera', 'design handoff is missing')
    required = {'heading', 'watch', 'beats', 'focal', 'framing', 'motion'}
    for shot in design:
        require(isinstance(shot, dict) and set(shot) in (required, required | {'start', 'end'})
                and text_value(shot['heading']) and text_value(shot['watch'])
                and shot['heading'] != shot['watch'], 'camera', 'design needs camera terms and a concrete viewing task')
        require(len(shot['heading'].splitlines()) == 1
                and (shot['heading'].startswith('——') or SHOT_TIME.match(shot['heading'])),
                'camera', 'invalid design heading')
    headings = [shot['heading'] for shot in design]
    require(len(headings) == len(set(headings)), 'camera', 'duplicate design headings')
    explicit = timing == 'explicit'
    timed = (explicit or duration is not None
             or any('start' in shot or SHOT_TIME.match(shot['heading']) for shot in design))
    nodes = [{k: shot[k] for k in ('heading', 'start', 'end') if k in shot} for shot in design]
    if timed:
        try:
            timing_node_ranges('\n'.join(shot['heading']+'\n'+shot['watch'] for shot in design),
                               nodes, duration, explicit=explicit)
        except ValueError as error:
            raise DeliveryBlocked('camera', str(error)) from error
    link_view_plan(design, planned)
    camera = {f'shot:{i}': camera_terms(shot, f'shot:{i}') for i, shot in enumerate(design, 1)}
    cuts = {f'cut:{i}': (f'shot:{i}', f'shot:{i+1}') for i in range(1, len(design))}
    # Six seconds is a review trigger, not a maximum shot duration.
    holds = {f'hold:{i}': f'shot:{i}' for i, node in enumerate(nodes, 1)
             if timed and node['end'] - node['start'] >= 6 - 1e-6}
    return {'headings': headings, 'nodes': nodes, 'timed': timed, 'explicit': explicit,
            'planned': planned, 'camera': camera, 'cuts': cuts, 'holds': holds}


def prompt_passages(card, source, plan):
    """Check that compiling did not change the previously decided shot plan."""
    duration = source.get('duration')
    outputs = source.get('outputs', ['master', 'direct'])
    copy_format = source.get('copy_format', 'full')
    drafts = card.get('drafts')
    expected_drafts = set(outputs) | ({'master'} if copy_format == 'compact' else set())
    require(isinstance(drafts, dict) and set(drafts) == expected_drafts and all(map(text_value, drafts.values())),
            'compile', 'drafts are missing or differ from the requested outputs')
    originals = [{'text': line} for line in source['dialogues']]
    shot_bodies = {}
    for name, draft in drafts.items():
        try:
            if name == 'direct' and copy_format == 'compact':
                check_direct(draft, drafts['master'], originals, 'compact')
            else:
                check_direct(draft, draft, originals)
            blocks = shot_blocks(draft)
            if [heading for heading, _ in blocks] != plan['headings']:
                raise ValueError('draft headings differ from the shot plan')
            if plan['timed']:
                timing_node_ranges(draft, plan['nodes'], duration, explicit=plan['explicit'])
            if duration is not None and (name != 'direct' or copy_format == 'full'):
                values = re.findall(r'^【片段时长】[：:]\s*([0-9]+(?:\.[0-9]+)?)\s*(?:秒|s)\s*$', draft, re.M)
                if len(values) != 1 or not math.isclose(float(values[0]), duration, rel_tol=0, abs_tol=1e-6):
                    raise ValueError('declared segment duration differs from the locked duration')
            shot_bodies[name] = {}
            for index, (_, lines) in enumerate(blocks, 1):
                end = next((i for i, line in enumerate(lines) if line.startswith(('【台词】', '【音效】'))), len(lines))
                shot_bodies[name][f'shot:{index}'] = '\n'.join(lines[:end])
        except ValueError as error:
            raise DeliveryBlocked('compile', f'{name}: {error}') from error
        for key, terms in plan['camera'].items():
            for term, quote in terms.items():
                cite(quote, shot_bodies[name][key], f'{name}: {key}: {term}', 'compile')
    return shot_bodies


def light_deliver(card):
    source = light_source(card)
    requirements = source['requirements']
    outputs = source.get('outputs', ['master', 'direct'])
    if outputs == ['storyboard']:
        return storyboard_deliver(card, requirements, source['dialogues'],
                                  source.get('duration'), source.get('timing', 'relative'))
    plan = prompt_camera_plan(card, source)
    shot_bodies = prompt_passages(card, source, plan)
    planned, camera, cuts, holds = (plan[k] for k in ('planned', 'camera', 'cuts', 'holds'))
    drafts = card['drafts']
    expected_drafts = set(drafts)
    beats = {f'beat:{key}' for key in planned}
    review_ids = set(requirements) | set(camera) | set(cuts) | set(holds) | beats
    review = reviewed(card, review_ids)
    for key, row in review.items():
        evidence = row.get('evidence')
        require(isinstance(evidence, dict) and set(evidence) == expected_drafts,
                'validate', f'{key}: missing evidence for an actual draft')
        if key in beats:
            continue
        for name, quote in evidence.items():
            label, bodies = f'{key}: {name}', shot_bodies[name]
            if key in cuts:
                a, b = cuts[key]
                require(isinstance(quote, dict) and set(quote) == {'out', 'in'}, 'validate',
                        f'{label}: provide evidence on both sides of the transition')
                cite(quote['out'], bodies[a], f'{label} out evidence')
                cite(quote['in'], bodies[b], f'{label} in evidence')
            elif key in holds:
                body = bodies[holds[key]]
                require(isinstance(quote, dict) and set(quote) == {'first', 'last'}, 'validate',
                        f'{label}: show what sustains the shot from beginning to end')
                first, last = quote['first'], quote['last']
                cite(first, body, f'{label} first evidence')
                cite(last, body, f'{label} last evidence')
                require(first != last and body.find(last, body.index(first)+len(first)) >= 0, 'camera',
                        f'{label}: a long shot needs distinct ordered visual evidence')
            else:
                cite(quote, bodies.get(key, drafts[name]), f'{label} evidence')
    for name, bodies in shot_bodies.items():
        verify_reveal_order(planned, lambda key: review[key]['evidence'][name], bodies)
    return {'status': 'ready_to_deliver', 'outputs': {name: drafts[name] for name in outputs}}

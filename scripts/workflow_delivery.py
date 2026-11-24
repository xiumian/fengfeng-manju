"""Check planning metadata separately from the words sent to a video model."""
import math
import re

MODELS = {'seedance-2.0': (4, 15), 'seedance-2.5': (4, 30), 'runway-gen4': (5, 10)}


def check_delivery(value):
    if not isinstance(value, dict) or not set(value) <= {'model', 'mode', 'duration', 'timing', 'outputs', 'copy_format'}:
        raise ValueError('invalid delivery profile')
    if value.get('outputs', 'master') not in ('master', 'dual'):
        raise ValueError('unknown delivery outputs')
    if 'copy_format' in value and (value.get('outputs') != 'dual' or value['copy_format'] not in ('full','compact')):
        raise ValueError('copy_format requires dual delivery and full or compact')
    model = value.get('model', 'generic')
    mode = value.get('mode', 'create')
    timing = value.get('timing', 'relative')
    if model not in {*MODELS, 'generic'} or mode not in ('create', 'reference', 'edit', 'extend'):
        raise ValueError('unknown delivery model or mode')
    if timing not in ('relative', 'explicit'):
        raise ValueError('unknown delivery timing style')
    duration = value.get('duration')
    if duration is not None and (type(duration) not in (int, float) or not math.isfinite(duration) or duration <= 0):
        raise ValueError('invalid delivery duration')
    if model == 'runway-gen4' and (mode != 'reference' or duration not in (5, 10, None)):
        raise ValueError('Runway Gen-4 requires a reference image and 5 or 10 seconds')
    if model == 'seedance-2.0' and mode in ('edit', 'extend'):
        raise ValueError('use a verified edit or extend profile rather than the Seedance 2.0 create profile')
    if model == 'seedance-2.5' and mode == 'edit' and duration is not None:
        raise ValueError('Seedance 2.5 edit uses the source duration, not fixed output seconds')
    if model in MODELS and duration is not None and mode in ('create', 'reference', 'extend'):
        low, high = MODELS[model]
        if duration != int(duration) or not low <= duration <= high:
            raise ValueError(f'{model} single generation needs {low}–{high} seconds; split at an event boundary')


# Match a shot heading (not a bare time range used for dialogue).
def shot_blocks(text):
    parts = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith('——') or SHOT_TIME.match(line):
            parts.append((line, []))
        elif parts:
            parts[-1][1].append(line)
    return parts


AUDIO_FIELDS = ('动作层','特效层','环境层','同步节点','主次变化','跨镜承接')


def shot_audio_details(text):
    parts = shot_blocks(text)
    if not parts:
        raise ValueError('full audio needs shot headings')
    result = {}
    for heading, lines in parts:
        if heading in result:
            raise ValueError('duplicate shot audio heading: '+heading)
        if lines.count('【音效】') != 1:
            raise ValueError(heading+' needs one shot audio block')
        body = lines[lines.index('【音效】')+1:]
        result[heading] = {}
        for label in AUDIO_FIELDS:
            hits = [line for line in body if re.match('^'+label+r'\s*[：:]',line)]
            if len(hits) != 1 or not re.split('[：:]',hits[0],maxsplit=1)[1].strip():
                raise ValueError(heading+' missing or duplicate audio field: '+label)
            result[heading][label] = re.split('[：:]',hits[0],maxsplit=1)[1].strip()
    return result


def shot_audio(text):
    return list(shot_audio_details(text))


def check_direct(text, master, dialogues, copy_format='full'):
    if not isinstance(text, str) or not text.strip() or (copy_format=='compact' and text.strip()==master.strip()):
        raise ValueError('dual delivery needs a separate model-ready prompt')
    if any(word in text for word in ('【完成检查】','【动态元素复核】','见资产表','同上段设定')):
        raise ValueError('model-ready prompt contains production metadata or an unresolved reference')
    master_shots = shot_audio(master)
    if copy_format == 'full':
        for section in ('全局设定','场景与资产','片段设定','逐镜时间轴'):
            if not re.search(r'^━+\s*'+section+r'\s*━+\s*$',text,re.M):
                raise ValueError('full copy missing template section: '+section)
        if shot_audio(text) != master_shots:
            raise ValueError('full copy shot headings differ from master')
    cursor = 0
    for line in dialogues:
        start = text.find(line['text'], cursor)
        if start < 0:
            raise ValueError('model-ready prompt missing original dialogue or wrong order')
        cursor = start + len(line['text'])


# Accept the template's leading dashes, optional Markdown markup, and seconds
# written in Chinese or as "s".
SHOT_TIME = re.compile(
    r'^[ \t]*(?:#{1,6}[ \t]+)?(?:\*\*)?(?:[—–-]{1,3}[ \t]*)?'
    r'([0-9]+(?:\.[0-9]+)?)[ \t]*(?:秒|s)?[ \t]*[-—–~～至][ \t]*'
    r'([0-9]+(?:\.[0-9]+)?)[ \t]*(?:秒|s)[ \t]*(?:[:：][ \t]*\S|【)',
    re.IGNORECASE,
)


def timing_node_ranges(text, nodes, expected_duration=None, *, explicit=False):
    if not isinstance(nodes, list) or not nodes:
        raise ValueError('timing_nodes must contain at least one ordered heading')
    ranges = []
    previous = 0.0
    previous_end = 0
    for node in nodes:
        if not isinstance(node, dict) or set(node) != {'heading', 'start', 'end'}:
            raise ValueError('timing node needs heading/start/end')
        a, b = node['start'], node['end']
        if (any(type(n) not in (int, float) or not math.isfinite(n) for n in (a, b))
                or abs(a - previous) > 1e-6 or b <= a):
            raise ValueError('timing nodes must be continuous from zero')
        heading = node['heading']
        if not isinstance(heading, str) or not heading.strip() or '\n' in heading:
            raise ValueError('timing node needs a nonempty single-line heading')
        span = SHOT_TIME.match(heading)
        if explicit and not span:
            raise ValueError(f'explicit timing needs visible heading times: {heading}')
        if span and any(not math.isclose(float(label), actual, rel_tol=0.0, abs_tol=1e-6)
                        for label, actual in zip(span.groups(), (a, b))):
            raise ValueError(f'heading times do not match timing_nodes: {heading} vs {a:g}–{b:g}s')
        hits = list(re.finditer(r'^' + re.escape(heading) + r'\r?$', text, re.M))
        if len(hits) != 1 or hits[0].start() < previous_end:
            raise ValueError('timing node heading is not unique or is out of order in the master')
        match = hits[0]
        line_end = match.end() + (text[match.end():match.end()+1] == '\n')
        if ranges and not text[previous_end:match.start()].strip():
            raise ValueError('timing node has no body')
        ranges.append((a, b, match.start(), line_end))
        previous, previous_end = b, line_end
    if explicit:
        registered = {node['heading'] for node in nodes}
        for line in text.splitlines():
            # Standard bracketed shot headings, not bare dialogue time ranges.
            if (SHOT_TIME.match(line)
                    and re.search(r'【[^】]+】(?:\*\*)?[ \t]*$', line)
                    and line not in registered):
                raise ValueError(f'visible shot heading missing from timing_nodes: {line}')
    if not text[previous_end:].strip():
        raise ValueError('final timing node has no body')
    if expected_duration is not None and abs(previous - expected_duration) > 1e-6:
        raise ValueError('timing nodes do not cover the requested delivery duration')
    return ranges

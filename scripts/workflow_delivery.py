"""Check planning metadata separately from the words sent to a video model."""
import math
import re

MODELS = {'seedance-2.0': (4, 15), 'seedance-2.5': (4, 30), 'runway-gen4': (5, 10)}


def check_delivery(value):
    if not isinstance(value, dict) or not set(value) <= {'model', 'mode', 'duration', 'timing'}:
        raise ValueError('invalid delivery profile')
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


def timing_node_ranges(text, nodes, expected_duration=None):
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
        hits = list(re.finditer(r'^' + re.escape(heading) + r'\r?$', text, re.M))
        if len(hits) != 1 or hits[0].start() < previous_end:
            raise ValueError('timing node heading is not unique or is out of order in the master')
        match = hits[0]
        line_end = match.end() + (text[match.end():match.end()+1] == '\n')
        if ranges and not text[previous_end:match.start()].strip():
            raise ValueError('timing node has no body')
        ranges.append((a, b, match.start(), line_end))
        previous, previous_end = b, line_end
    if not text[previous_end:].strip():
        raise ValueError('final timing node has no body')
    if expected_duration is not None and abs(previous - expected_duration) > 1e-6:
        raise ValueError('timing nodes do not cover the requested delivery duration')
    return ranges

"""Select the rule files supplied to each stage, including targeted references."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ('assets', 'action', 'performance', 'vfx', 'sound', 'camera')
RULES = {module: [f'references/modules/{module}.md']
         for module in (*DESIGN, 'source', 'compile', 'sampling', 'validate')}
for module in (*DESIGN, 'compile', 'validate'):
    RULES[module] += ['references/design-boundaries.md', 'references/specialty-selection.md']
RULES['source'] += ['references/move-vfx-design.md', 'references/project-contract.md', 'references/coverage-contract.md',
                    'references/creation-preparation.md', 'references/specialty-selection.md']
RULES['camera'] += ['references/performance-camera-methods.md']
RULES['compile'] += ['references/model-delivery.md', 'references/video-prompt-template.txt',
                     'references/prompt-backstage-checks.md']
RULES['validate'] += ['references/model-delivery.md', 'references/prompt-backstage-checks.md']
RULES['vfx'] += ['references/visual-impact-design.md', 'references/招式特效库/调用规则.md']
RULES['action'] += ['references/打斗编排库/调用规则.md']
for module in ('source', 'action', 'camera', 'compile', 'validate'):
    RULES[module] += ['references/scene-rhythm-planning.md']
for module in ('action', 'camera', 'compile', 'validate'):
    RULES[module] += ['references/shot-rhythm-planning.md']
for module in ('action', 'vfx', 'camera', 'compile', 'validate'):
    RULES[module] += ['references/move-vfx-design.md']
for module in ('performance', 'action', 'sound', 'camera', 'compile', 'validate'):
    RULES[module] += ['references/emotion-performance-design.md']
for module in ('sound', 'action', 'vfx', 'camera', 'compile', 'validate'):
    RULES[module] += ['references/layered-sound-design.md']
# Creative methods are explicit owner rules, not keyword-dependent suggestions.
PREPROMPT_METHODS = {
    'narrative-event-design': ('source',),
    'dialogue-relationship-design': ('source', 'performance', 'sound'),
    'character-prop-design': ('assets', 'action'),
    'scene-space-design': ('assets', 'action', 'camera'),
    'art-style-material-design': ('assets', 'vfx', 'camera'),
    'lighting-color-design': ('assets', 'vfx', 'camera'),
}
for name, owners in PREPROMPT_METHODS.items():
    for module in (*owners, 'compile', 'validate'):
        RULES[module] += ['references/' + name + '.md']
RULES.update(workbench=['references/workbench-v8.md'], maintenance=['maintenance/change-control.md'])

SPECIALTIES = {
    'microexpression': ('performance', 'references/microexpression-cues.md'),
    'vfx-techniques': ('vfx', 'references/vfx-techniques.md'),
}


def validate_specialties(module, specialties):
    """Only registered, owner-compatible rule identifiers; never arbitrary paths."""
    if not isinstance(specialties, list) or not all(isinstance(s, str) for s in specialties):
        raise ValueError('specialties must be a list of registered identifiers')
    if len(specialties) != len(set(specialties)):
        raise ValueError('duplicate specialty identifiers')
    for specialty in specialties:
        if specialty not in SPECIALTIES:
            raise ValueError('unknown specialty: ' + specialty)
        if SPECIALTIES[specialty][0] != module:
            raise ValueError('specialty does not belong to module: ' + specialty)


def library_matches(library, text):
    """Bounded candidate retrieval, not semantic understanding or ability approval."""
    entries = json.loads((ROOT / library / '检索索引.json').read_text(encoding='utf-8-sig'))['entries']
    def explicit(entry):
        return bool(re.search(r'(?<![A-Za-z0-9-])' + re.escape(entry['id']) + r'(?![A-Za-z0-9-])', text, re.I))
    def score(entry):
        return (explicit(entry), entry['name'] in text, sum(len(word) for word in entry['keywords'] if word in text))
    # Two classes for automatic suggestions; do not drop explicitly requested families.
    limit = max(2, len({e['file'] for e in entries if explicit(e)}))
    files, candidates = [], []
    for entry in sorted(entries, key=score, reverse=True):
        if not any(score(entry)):
            break
        path = library + '/' + entry['file']
        if path not in files:
            if len(files) >= limit:
                continue
            files.append(path)
        candidates.append(entry['id'])
    return files, candidates


def select_rules(module, events=(), constraints=(), source_text='', specialties=()):
    if specialties == ():
        specialties = []
    validate_specialties(module, specialties)
    paths = list(RULES[module])
    paths.extend(SPECIALTIES[s][1] for s in specialties)
    text = '\n'.join([source_text, *(event['body'] for event in events), *constraints])
    candidates = []
    if module == 'action':
        files, candidates = library_matches('references/打斗编排库', text)
        paths.extend(files)
    if module == 'vfx':
        if re.search(r'粒子|碎屑|材质|拖尾|消散|冲击帧|剪影|闪白|火星|烟尘', text):
            paths.append('references/vfx-techniques.md')
        files, candidates = library_matches('references/招式特效库', text)
        paths.extend(files)
    if module == 'performance' and re.search(r'微表情|欲言又止|隐忍|克制|眼神|压笑|嘴角', text):
        paths.append('references/microexpression-cues.md')
    return [{'path': path, 'text': (ROOT / path).read_text(encoding='utf-8-sig')}
            for path in dict.fromkeys(paths)], candidates

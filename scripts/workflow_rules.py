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

# Keep the registry stable for existing plans; restrict only the actual packets.
# Unbound previews have no inventory and still show the full candidate rules.
OPTIONAL_METHOD_FEATURES = {
    'references/move-vfx-design.md': {'vfx'},
    'references/layered-sound-design.md': {'sound'},
    'references/emotion-performance-design.md': {'performance'},
    'references/performance-camera-methods.md': {'performance'},
    'references/dialogue-relationship-design.md': {'performance', 'sound'},
}


# Canonical documents stay complete. A role not listed here receives the full
# document. Listed roles get the introduction and the exact owned handoff
# sections, not paraphrases or upstream examples. Rules receipts hash the
# actual delivered text.
RULE_VIEWS = {
    'references/move-vfx-design.md': {
        'source': ('先分能力事实与视觉空间', '先设计观看内容，再分配时间', '主特效的可见变化链',
                   '观看内容与兑现证据：用现有需求，不另造评分表'),
        'action': ('先分能力事实与视觉空间', '构造方法：六种关系，不是固定六段',
                   '专业交接：提出需求不等于替对方定方案', '先设计观看内容，再分配时间',
                   '主特效的可见变化链'),
        'camera': ('专业交接：提出需求不等于替对方定方案', '先设计观看内容，再分配时间',
                   '主特效的可见变化链', '观看内容与兑现证据：用现有需求，不另造评分表',
                   '关键因果逐环取证'),
        'compile': ('主特效的可见变化链', '观看内容与兑现证据：用现有需求，不另造评分表',
                    '关键因果逐环取证', '编译保真：合并措辞，不合并不同信息',
                    '表现力复核：引用差异，不给空泛分数'),
        'validate': ('主特效的可见变化链', '观看内容与兑现证据：用现有需求，不另造评分表',
                     '关键因果逐环取证', '编译保真：合并措辞，不合并不同信息',
                     '表现力复核：引用差异，不给空泛分数'),
    },
    'references/layered-sound-design.md': {
        'action': ('一、先从事件建立真实声源', '四、交接与编译：实际正文保留六项组织'),
        'vfx': ('一、先从事件建立真实声源', '二、把每层写成变化，不是素材名清单',
                '四、交接与编译：实际正文保留六项组织'),
        'camera': ('三、同步、主次和跨镜是具体关系', '四、交接与编译：实际正文保留六项组织'),
        'compile': ('二、把每层写成变化，不是素材名清单', '三、同步、主次和跨镜是具体关系',
                    '配乐主题线：主题、变奏、高潮、让位', '四、交接与编译：实际正文保留六项组织'),
        'validate': ('三、同步、主次和跨镜是具体关系', '配乐主题线：主题、变奏、高潮、让位',
                     '五、实际复核与返修'),
    },
    'references/emotion-performance-design.md': {
        'action': ('跨镜情绪轨迹：从任务与信息出发', '全身与行动共同表达', '专业交接：需求不是替对方定方案'),
        'sound': ('跨镜情绪轨迹：从任务与信息出发', '全身与行动共同表达', '专业交接：需求不是替对方定方案'),
        'camera': ('跨镜情绪轨迹：从任务与信息出发', '表情设计：局部关系，不是脸谱', '专业交接：需求不是替对方定方案'),
        'compile': ('专业交接：需求不是替对方定方案', '编译保真与表现力复核'),
        'validate': ('专业交接：需求不是替对方定方案', '编译保真与表现力复核'),
    },
    'references/scene-rhythm-planning.md': {
        'action': ('二、按观看容量分配时间预算', '三、由节奏节点形成镜头，而不是反过来'),
        'camera': ('一、从整场变化确定节奏节点', '二、按观看容量分配时间预算',
                   '三、由节奏节点形成镜头，而不是反过来'),
        'compile': ('二、按观看容量分配时间预算', '三、由节奏节点形成镜头，而不是反过来'),
        'validate': ('二、按观看容量分配时间预算', '三、由节奏节点形成镜头，而不是反过来', '四、条件对照与纠错'),
    },
    'references/shot-rhythm-planning.md': {
        'action': ('先判断观看任务，再决定镜长', '职责、交接与交付'),
        'compile': ('切镜收益：上一镜已交代什么，下一镜多给什么', '职责、交接与交付'),
    },
}


def rule_text(path, module):
    """Deliver the original rule or an exact, source-ordered section view."""
    text = (ROOT / path).read_text(encoding='utf-8-sig')
    wanted = RULE_VIEWS.get(path, {}).get(module)
    if wanted is None:
        return text
    headings = list(re.finditer(r'^## ([^\n]+)$', text, re.M))
    parts = {}
    for index, heading in enumerate(headings):
        title = heading[1].strip()
        if title in parts:
            raise ValueError(f'duplicate rule section in {path}: {title}')
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        parts[title] = text[heading.start():end]
    absent = set(wanted) - parts.keys()
    if absent:
        raise ValueError(f'missing rule sections for {module} in {path}: {sorted(absent)}')
    return text[:headings[0].start()] + ''.join(body for title, body in parts.items() if title in wanted)

PRODUCTION_SPECIALTIES = 'references/production-specialties'
DIRECTOR_HANDOFF_METHODS = {
    'source': f'{PRODUCTION_SPECIALTIES}/director-handoff/prepare.md',
    'compile': f'{PRODUCTION_SPECIALTIES}/director-handoff/compile-bridge.md',
    'validate': f'{PRODUCTION_SPECIALTIES}/director-handoff/review.md',
}


def production_specialty(owner, key, *references):
    base = f'{PRODUCTION_SPECIALTIES}/{key}'
    return owner, (f'{base}/guide.md', *(f'{base}/references/{name}.md' for name in references))


SPECIALTIES = {
    'microexpression': ('performance', ('references/microexpression-cues.md',)),
    'vfx-techniques': ('vfx', ('references/vfx-techniques.md',)),
    'realistic-fight': production_specialty('action', 'realistic-fight', 'choreography'),
    'vfx-fight': production_specialty('vfx', 'vfx-fight', 'effect-profiles'),
    'impact-frame': production_specialty('vfx', 'impact-frame', 'frame-construction'),
    'director-handoff': production_specialty('camera', 'director-handoff'),
    'scene-storyboard': production_specialty('camera', 'scene-storyboard', 'view-reconstruction'),
    'emotion-expression': production_specialty('performance', 'emotion-expression', 'cue-selection'),
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


def select_rules(module, events=(), constraints=(), source_text='', specialties=(), capabilities=None,
                 *, director_handoff=False):
    if specialties == ():
        specialties = []
    validate_specialties(module, specialties)
    paths = [path for path in RULES[module]
             if capabilities is None or path not in OPTIONAL_METHOD_FEATURES
             or OPTIONAL_METHOD_FEATURES[path] & capabilities]
    paths.extend(path for specialty in specialties for path in SPECIALTIES[specialty][1])
    if director_handoff and module in DIRECTOR_HANDOFF_METHODS:
        paths.append(DIRECTOR_HANDOFF_METHODS[module])
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
    return [{'path': path, 'text': rule_text(path, module)}
            for path in dict.fromkeys(paths)], candidates

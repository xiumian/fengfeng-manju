"""Select the rule files supplied to each stage, including targeted references."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ('assets', 'action', 'performance', 'vfx', 'sound', 'camera')
RULES = {module: [f'references/modules/{module}.md']
         for module in (*DESIGN, 'source', 'compile', 'sampling', 'validate')}
RULES['source'] += ['references/project-contract.md', 'references/coverage-contract.md']
RULES['compile'] += ['references/model-delivery.md', 'references/video-prompt-template.txt']
RULES['validate'] += ['references/model-delivery.md']
RULES['vfx'] += ['references/visual-impact-design.md', 'references/招式特效库/调用规则.md']
RULES.update(workbench=['references/workbench-v8.md'], maintenance=['maintenance/change-control.md'])


def select_rules(module, events=(), constraints=(), source_text=''):
    paths = list(RULES[module])
    text = '\n'.join([source_text, *(event['body'] for event in events), *constraints])
    candidates = []
    if module == 'vfx':
        library = 'references/招式特效库/'
        files = []
        if re.search(r'粒子|碎屑|材质|拖尾|消散|冲击帧|剪影|闪白|火星|烟尘', text):
            paths.append('references/vfx-techniques.md')
        entries = json.loads((ROOT / (library + '检索索引.json')).read_text(encoding='utf-8-sig'))['entries']
        ranking = [(sum(word in text for word in entry['keywords']), entry) for entry in entries]
        for score, entry in sorted(ranking, key=lambda pair: pair[0], reverse=True):
            if not score:
                break
            path = library + entry['file']
            if path not in files and len(files) < 2:
                files.append(path)
            if path in files:
                candidates.append(entry['id'])
        paths.extend(files)
    if module == 'performance' and re.search(r'微表情|欲言又止|隐忍|克制|眼神|压笑|嘴角', text):
        paths.append('references/microexpression-cues.md')
    return [{'path': path, 'text': (ROOT / path).read_text(encoding='utf-8-sig')} for path in paths], candidates

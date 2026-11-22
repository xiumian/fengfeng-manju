"""Check active instructions, local links, Python syntax and rule registrations."""
from pathlib import Path
import ast,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from workflow import RULES, RULES_VERSION
from workflow_rules import DIRECTOR_HANDOFF_METHODS, RULE_VIEWS, SPECIALTIES, rule_text
from export_text_rules import assemble

def main():
    errors=[]
    active = {ROOT / path for paths in RULES.values() for path in paths if path.endswith('.md')}
    active.update(ROOT / path for _, paths in SPECIALTIES.values() for path in paths)
    active.update(ROOT / path for path in DIRECTOR_HANDOFF_METHODS.values())
    active.update(ROOT / path for path in ('SKILL.md', 'references/routing.md', 'references/tool-interface.md',
                                          'references/vfx-techniques.md', 'references/microexpression-cues.md'))
    for file in active:
        if not file.is_file(): errors.append('missing '+str(file));continue
        for target in re.findall(r'\]\(([^)]+)\)',file.read_text(encoding='utf-8')):
            if '://' in target:continue
            if target.startswith('#'):continue
            if not (file.parent/target.split('#')[0]).exists(): errors.append('broken link: '+str(file.relative_to(ROOT))+' -> '+target)
    for module,paths in RULES.items():
        for path in paths:
            if not (ROOT/path).is_file(): errors.append('missing module '+module+': '+path)
    for path, viewers in RULE_VIEWS.items():
        for module in viewers:
            if path not in RULES.get(module, []):
                errors.append('unregistered rule view: '+module+': '+path)
                continue
            try: rule_text(path, module)
            except (OSError, ValueError) as e: errors.append(str(e))
    if any(path.startswith(('_archive/', 'references/storyboard-prompter-v2.9/'))
           for paths in RULES.values() for path in paths):
        errors.append('history must not be registered as an active rule')
    try: assemble()
    except (OSError, ValueError) as e: errors.append(str(e))
    for file in [*ROOT.glob('scripts/*.py'),*ROOT.glob('tests/*.py')]:
        try:ast.parse(file.read_text(encoding='utf-8'))
        except SyntaxError as e:errors.append(str(e))
    version=json.loads((ROOT/'版本信息.json').read_text(encoding='utf-8'))['version']
    if version != RULES_VERSION or f"version: '{RULES_VERSION}'" not in (ROOT/'SKILL.md').read_text(encoding='utf-8'):
        errors.append('version mismatch')
    print(json.dumps({'errors':errors,'scope':'active links, syntax, module registrations, version; not semantic/media verification'},ensure_ascii=False,indent=2))
    return bool(errors)

if __name__=='__main__':raise SystemExit(main())

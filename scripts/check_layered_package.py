"""Check active instructions, local links, Python syntax and rule registrations."""
from pathlib import Path
import ast,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from workflow import RULES, RULES_VERSION

def main():
    errors=[]
    active = {ROOT / path for paths in RULES.values() for path in paths if path.endswith('.md')}
    active.update(ROOT / path for path in ('SKILL.md', 'references/routing.md', 'references/tool-interface.md',
                                          'references/vfx-techniques.md', 'references/microexpression-cues.md'))
    for file in active:
        if not file.is_file(): errors.append('missing '+str(file));continue
        for target in re.findall(r'\]\(([^)]+)\)',file.read_text(encoding='utf-8')):
            if '://' in target:continue
            if not (file.parent/target.split('#')[0]).exists(): errors.append('broken link: '+str(file.relative_to(ROOT))+' -> '+target)
    for module,paths in RULES.items():
        for path in paths:
            if not (ROOT/path).is_file(): errors.append('missing module '+module+': '+path)
    for file in [*ROOT.glob('scripts/*.py'),*ROOT.glob('tests/*.py')]:
        try:ast.parse(file.read_text(encoding='utf-8'))
        except SyntaxError as e:errors.append(str(e))
    version=json.loads((ROOT/'版本信息.json').read_text(encoding='utf-8'))['version']
    if version != RULES_VERSION or f"version: '{RULES_VERSION}'" not in (ROOT/'SKILL.md').read_text(encoding='utf-8'):
        errors.append('version mismatch')
    print(json.dumps({'errors':errors,'scope':'active links, syntax, module registrations, version; not semantic/media verification'},ensure_ascii=False,indent=2))
    return bool(errors)

if __name__=='__main__':raise SystemExit(main())

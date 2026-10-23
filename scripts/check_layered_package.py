"""Check active instructions, local links, Python syntax and rule registrations."""
from pathlib import Path
import ast,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from workflow import RULES

def main():
    errors=[]
    active=[ROOT/'SKILL.md',ROOT/'references/routing.md',ROOT/'references/project-contract.md',ROOT/'references/tool-interface.md',ROOT/'references/workbench-v8.md',ROOT/'maintenance/change-control.md',*list((ROOT/'references/modules').glob('*.md'))]
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
    if version!='8.0.0' or "version: '8.0.0'" not in (ROOT/'SKILL.md').read_text(encoding='utf-8'):errors.append('version mismatch')
    print(json.dumps({'errors':errors,'scope':'active links, syntax, module registrations, version; not semantic/media verification'},ensure_ascii=False,indent=2))
    return bool(errors)

if __name__=='__main__':raise SystemExit(main())

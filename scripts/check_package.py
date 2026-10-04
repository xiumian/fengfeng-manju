"""fengfeng: package structure, Python syntax and shared-core regression; not 100-point scoring."""
import ast,json,subprocess,sys,re
from pathlib import Path
def main():
 root=Path(__file__).resolve().parents[1];errors=[]
 for f in ['SKILL.md','references/contracts.md','references/video-template.md','references/combat-vfx-library.md','assets/workbench/core.js','assets/workbench/nine-grid-app.js','启动工作台.cmd','scripts/production.cjs','scripts/production_cli.cjs','references/asset-production.md','references/production-pipeline.md','references/quality-workflow.md','references/platform-handoff.md','assets/default-storyboard-style.png','scripts/migrate_legacy.cjs']:
  if not (root/f).is_file():errors.append('缺文件：'+f)
 for f in (root/'scripts').rglob('*.py'):
  try:ast.parse(f.read_text(encoding='utf-8'))
  except SyntaxError as e:errors.append(str(e))
 for f in [root/'SKILL.md',root/'references/craft-routing.md',root/'references/action-routing.md',root/'references/workbench.md',root/'references/production-pipeline.md',root/'references/asset-production.md',root/'references/platform-handoff.md',root/'references/quality-workflow.md',root/'references/capability-index.md',root/'references/storyboard-contract.md',root/'references/source-check-migration.md']:
  text=f.read_text(encoding='utf-8')
  for link in re.findall(r'\]\(([^)]+)\)',text):
   if '://' not in link and not (f.parent/link.split('#')[0]).exists():errors.append('链接缺失：'+link)
 if any(f.name.lower().startswith('license') for f in root.rglob('*')):errors.append('包含不在当前范围的原许可文件')
 if errors:print(json.dumps({'errors':errors},ensure_ascii=False,indent=2));return 1
 for cmd in [['node','--check',str(root/'assets/workbench/nine-grid-app.js')],['node','--test',str(root/'tests/core.test.cjs')],['node','--test',str(root/'tests/production.test.cjs')],['node','--test',str(root/'tests/merge-contract.test.cjs')],['node','--test',str(root/'tests/migration.test.cjs')],['node','--test',str(root/'tests/final-source-review.test.cjs')],['node','--test',str(root/'tests/source-coverage.test.cjs')],['node','--test',str(root/'tests/source-matrix.test.cjs')],['node','--test',str(root/'tests/character-card.test.cjs')],['node','--test',str(root/'tests/critical-gates.test.cjs')],['node','--test',str(root/'tests/branch-handoff.test.cjs')],['node','--test',str(root/'tests/video-sync.test.cjs')],['node','--test',str(root/'tests/annotations.test.cjs')],['node','--check',str(root/'scripts/production_cli.cjs')],[sys.executable,str(root/'tests/tools_test.py')]]:
  r=subprocess.run(cmd,cwd=root,capture_output=True,text=True,encoding='utf-8');print(r.stdout);print(r.stderr)
  if r.returncode:return r.returncode
 print('PASS: structure, active links, syntax and tool/core tests. Behavioral/image review remains separate.');return 0
if __name__=='__main__':raise SystemExit(main())

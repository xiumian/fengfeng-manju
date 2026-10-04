const test=require('node:test'),a=require('node:assert/strict'),C=require('../assets/workbench/core.js');
let P;try{P=require('../scripts/production.cjs');}catch{}
const project=()=>C.parseScript('——[0—3秒]：【递信】\n甲递给乙一封信。\n动态元素：递信。\n【音效】纸响。','测试');
test('生产包保持主稿并导出真实任务，不伪装出图',()=>{const p=project(),before=JSON.stringify(p);const out=P.plan(p,{model:'seedance2.0',entities:[{id:'CHR_A',kind:'character',name:'甲',description:'青衣青年'}]});a.equal(JSON.stringify(p),before);a.equal(out.video_prompt,C.videoPrompt(p.segments[0],p));a.equal(out.asset_requests[0].status,'planned');a(out.asset_requests[0].prompt.includes('4 个完整全身视图'));a.equal(out.completed,false);});
test('无实体清单标待补，不捏造人物',()=>{const out=P.plan(project(),{model:'seedance2.5'});a.equal(out.asset_requests.length,0);a(out.pending.includes('实体清单待提取并核对'));});
test('H3停用、未知亲缘和循环依赖拒绝',()=>{a.throws(()=>P.plan(project(),{model:'h3'}),/H3|停用/);a.throws(()=>P.plan(project(),{entities:[{id:'A',kind:'character',name:'甲',description:'青衣',parent_ids:['B']}]}),/依赖/);a.throws(()=>P.plan(project(),{entities:[{id:'A',kind:'character',name:'甲',description:'青衣',parent_ids:['A']}]}),/循环/);});
test('缺文件素材不登记',()=>{const p=project();a.throws(()=>P.registerAsset(p,{id:'X',path:'Z:/definitely-missing-asset.png'}));a.equal(p.assets.length,0);});
test('真实素材登记保留未审核状态并取消相关旧审核',()=>{const fs=require('fs'),os=require('os'),path=require('path'),dir=fs.mkdtempSync(path.join(os.tmpdir(),'production-test-'));try{const file=path.join(dir,'sound.wav');fs.writeFileSync(file,'test');const p=project();p.segments[0].completed=true;P.registerAsset(p,{id:'AUD_1',path:file,kind:'audio'});a.equal(p.assets[0].status,'registered-unreviewed');a.equal(p.assets[0].sha256.length,64);a.equal(p.segments[0].completed,false);}finally{fs.unlinkSync(path.join(dir,'sound.wav'));fs.rmdirSync(dir);}});

test('未选择模型不默认锁定2.5',()=>{const out=P.plan(project(),{});a.equal(out.model,'unspecified');a(out.pending.includes('目标模型待选择'));});
test('错误实体清单不静默转换成空数组',()=>{for(const entities of [null,'',false,0])a.throws(()=>P.plan(project(),{entities}),/entities/);});

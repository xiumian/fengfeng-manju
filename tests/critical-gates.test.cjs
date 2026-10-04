const test=require('node:test'),a=require('node:assert/strict'),fs=require('fs'),C=require('../assets/workbench/core.js');
const make=()=>C.parseScript('——[0—3秒]：【站立】\n甲持信站立。\n——[3—6秒]：【继续】\n甲望向门。','门禁',{segmentSeconds:3});
function seam(){const p=make();p.state_snapshots={T1:{holder:'甲',pose:'站立',screen_position:'左'},T2:{holder:'乙',pose:'站立',screen_position:'右'}};p.segments[0].panels[8].end_state='T1';p.segments[1].panels[0].start_state='T2';p.segments[1].join_mode='continuous';return p;}
test('完成前最终检查阻断漏覆盖且不修改项目',()=>{const p=make();p.source_units=[{id:'U1'}];const before=JSON.stringify(p);a(C.validate(p,{finalize:true}).errors.some(x=>x.includes('U1')));a.equal(JSON.stringify(p),before);a(C.validate(p).warnings.some(x=>x.includes('U1')));});
test('连续段缝持物突变草稿告警、最终阻断',()=>{const p=seam();a(C.validate(p).warnings.some(x=>x.includes('段缝')&&x.includes('holder')));a(C.validate(p,{finalize:true}).errors.some(x=>x.includes('holder')));});
test('机位屏幕位置变化及硬切不误判持物连续',()=>{const p=seam();p.state_snapshots.T2.holder='甲';a(!C.validate(p,{finalize:true}).errors.some(x=>x.includes('段缝')));p.state_snapshots.T2.holder='乙';p.segments[1].join_mode='hard-cut';a(!C.validate(p,{finalize:true}).errors.some(x=>x.includes('段缝')));});
test('连续模式快照缺失或不明确转人工核对而非静默通过',()=>{const p=make();p.segments[1].join_mode='continuous';a(C.validate(p,{finalize:true}).errors.some(x=>x.includes('段缝')));});
test('其他故事没有声明连续模式不强制追加状态图',()=>a(C.validate(make(),{finalize:true}).valid));
test('工作台完成按钮调用最终模式',()=>a(fs.readFileSync(require('path').join(__dirname,'../assets/workbench/nine-grid-app.js'),'utf8').includes('DramaCore.validate(project,{finalize:true})')));

const test=require('node:test');const assert=require('node:assert/strict');
const C=require('../assets/workbench/core.js');
const source=`【全局基调设定】：16:9，3D国漫。
【场景全局设定】：石殿，桌在东，门在南。
【角色生物全局设定】：甲青衣，乙白衣。
【总道具 / 武器全局设定】：信件一封。
——[0—3秒]：【递信】
甲把信件递给乙。乙接过。
【台词】[1—2秒] 甲（低声）：“收好。”
动态元素：递信、接信。
【音效】纸张摩擦。
——[3—7秒]：【看信】
乙展开信纸，甲注视乙。
动态元素：展开信纸。
【音效】纸张展开。`;
function project(s=source,opt={}){return require('./annotation-fixture.cjs')(C.parseScript(s,'测试',opt));}
test('T01 文戏保留事件与对白，不强加特效/切镜',()=>{const p=project();assert.equal(p.segments.length,1);assert.equal(p.segments[0].events.length,2);assert.equal(p.segments[0].panels.length,9);const t=C.videoPrompt(p.segments[0],p);assert.match(t,/收好/);assert.match(t,/0—3/);assert.doesNotMatch(t,/【站位声明】|【资产绑定】|SHOT|REF|\[VFX|TMP-|来源:/);});
test('T02 14事件不会被9格截断，大招只在对应节点',()=>{let s='【全局基调设定】：3D国漫。\n';for(let i=0;i<14;i++)s+=`——[${i*2}—${i*2+2}秒]：【事件${i}】\n${i===13?'终局雷龙释放。':'剑刃短光轨。'}\n动态元素：挥剑。\n【音效】剑鸣。\n`;const p=project(s),b=p.segments[0];assert.equal(b.events.length,14);assert.equal(b.panels.length,9);assert.equal(C.duration(b),28);assert.equal((C.videoPrompt(b,p).match(/——\[/g)||[]).length,14);assert.equal(new Set(b.panels.flatMap(x=>x.event_ids)).size,14);});
test('T03 机关事件顺序与道具状态保留',()=>{const p=project('——[0—2秒]：【转动】\n转动机关。\n——[2—4秒]：【开启】\n石门打开。\n——[4—6秒]：【取物】\n拿走盒子。');const t=C.videoPrompt(p.segments[0],p);assert(t.indexOf('转动机关')<t.indexOf('石门打开'));assert(t.indexOf('石门打开')<t.indexOf('拿走盒子'));});
test('T04 显式多SEG保留跨段时间顺序及总时长',()=>{const p=project(source,{segmentSeconds:4});assert.equal(p.segments.length,2);assert.equal(C.duration(p.segments[0]),3);assert.equal(C.duration(p.segments[1]),4);assert.equal(p.segments[1].events[0].start,3);assert.match(C.videoPrompt(p.segments[1],p),/0—4/);});
test('T05 文字起步不虚构资产；纯剧本需确认自动估算',()=>{const p=project('甲走进房间。乙把杯子放下。');assert.equal(p.assets.length,0);assert.equal(p.timing_confirmed,false);assert.equal(p.segments[0].completed,false);assert.doesNotMatch(JSON.stringify(p),/TMP-CH|TMP-SC/);assert(C.validate(p).warnings.some(x=>x.includes('估算')));});
test('T06 修改传播失效、保存恢复与审核门禁',()=>{const p=project();p.timing_confirmed=true;const b=p.segments[0];assert.throws(()=>C.reviewedResults(p),/审核/);b.image_data_url='data:image/png;base64,eA==';b.image_reviewed=true;b.mapping_confirmed=true;b.completed=true;assert.equal(C.reviewedResults(p).segments.length,1);const restored=C.restore(JSON.stringify(p));assert.equal(restored.segments[0].events[0].body,b.events[0].body);C.updateEvent(restored,b.segment_id,b.events[0].id,{body:'甲将信放在桌上。'});assert.equal(restored.segments[0].completed,false);assert.equal(restored.segments[0].image_reviewed,false);assert(restored.segments[0].panels.some(x=>x.action.includes('甲将信放在桌上')));assert.throws(()=>C.reviewedResults(restored),/审核/);});
test('时间错误和漂移对白必须报错',()=>{const p=project();p.segments[0].events[1].start=2;assert(C.validate(p).errors.some(x=>x.includes('重叠')));const q=project(source.replace('[1—2秒]','[8—9秒]'));assert(C.validate(q).errors.some(x=>x.includes('台词')));});
test('不把结果JSON伪装成可编辑项目',()=>assert.throws(()=>C.restore(JSON.stringify({package_type:'reviewed-results',segments:[{final_video_prompt:'x'}]})),/工作项目/));
test('结果排除内部草稿，保留事件与对应表',()=>{const p=project();p.timing_confirmed=true;for(const b of p.segments){b.completed=true;b.mapping_confirmed=true;b.image_reviewed=true;b.image_data_url='data:image/png;base64,eA==';}const r=C.reviewedResults(p);assert.equal(r.segments[0].storyboard_reference.panel_map.length,9);assert(!('panels' in r.segments[0]));assert.match(r.segments[0].final_video_prompt,/看信/);});

test('导出HTML所需字段完整',()=>{const p=project();p.timing_confirmed=true;for(const b of p.segments){b.completed=true;b.mapping_confirmed=true;b.image_reviewed=true;b.image_data_url='data:image/png;base64,eA==';}const r=C.reviewedResults(p);assert(Array.isArray(r.segments[0].change_notes));assert.equal(typeof r.segments[0].source_range,'string');});

test('格观察时刻不能脱离关联事件',()=>{const p=project();p.segments[0].panels[0].sample_time=999;assert(C.validate(p).errors.some(x=>x.includes('观察时刻')));});

const interleaved='——[0—6秒]：【读信】\n甲递出信件。\n【台词】[1—2秒] 甲（低声）：“先别打开。”\n乙抬起头。\n【台词】[3—4秒] 乙（疑惑）：“为什么？”\n甲收回信件。\n动态元素：递信、抬头、收信。\n【音效】纸张声。';
test('R01 两处对白保持动作前后顺序',()=>{const p=project(interleaved),t=C.videoPrompt(p.segments[0],p);const labels=['甲递出信件','先别打开','乙抬起头','为什么','甲收回信件'];for(let i=1;i<labels.length;i++)assert(t.indexOf(labels[i-1])<t.indexOf(labels[i]),labels[i]);});
test('R02 每个资产引用单独检查并阻断未知引用导出',()=>{const p=project();p.assets=[{id:'CH01',path:'char.png',status:'confirmed'}];const b=p.segments[0];b.panels[0].asset_refs=' CH01 + MISSING_SCENE ';const v=C.validate(p);assert(v.errors.some(e=>e.includes('MISSING_SCENE')));b.completed=b.image_reviewed=b.mapping_confirmed=true;b.image_data_url='data:image/png;base64,eA==';assert.throws(()=>C.reviewedResults(p),/MISSING_SCENE/);});
test('R03 全部有效引用及无资产模式均可用',()=>{const p=project();p.assets=[{id:'CH01'},{id:'SC01'}];p.segments[0].panels[0].asset_refs=' CH01 + SC01 ';assert.deepEqual(C.validate(p).errors,[]);assert.deepEqual(C.validate(project()).errors,[]);});
test('R04 非法正文导入被拒绝且validate不崩溃',()=>{const p=project();p.segments[0].events[0].body=null;assert.throws(()=>C.restore(JSON.stringify(p)),/正文|body/);assert.equal(C.validate(p).valid,false);});
test('R05 异常数组、时间类型与对白字段导入被拒绝',()=>{for(const mutate of [p=>p.segments[0].events[0].dialogues={},p=>p.segments[0].events[0].start='0',p=>p.segments[0].panels[0]=null,p=>p.segments[0].panels[0].event_ids='EV001',p=>p.assets={},p=>p.segments[0].events[0].dialogues=[null]]){const p=project();mutate(p);assert.throws(()=>C.restore(JSON.stringify(p)));assert.equal(C.validate(p).valid,false);}});
test('R06 修改动作保留对白插入位置',()=>{const p=project(interleaved),b=p.segments[0];C.updateEvent(p,b.segment_id,b.events[0].id,{body:'甲放下信件。\n乙望向门口。\n甲拿回信件。'});const t=C.videoPrompt(b,p);assert(t.indexOf('甲放下信件')<t.indexOf('先别打开'));assert(t.indexOf('先别打开')<t.indexOf('乙望向门口'));assert(t.indexOf('为什么')<t.indexOf('甲拿回信件'));});
test('R07 无法容纳旧对白位置的修改拒绝且不污染原事件',()=>{const p=project(interleaved),b=p.segments[0],before=JSON.stringify(b.events[0]);assert.throws(()=>C.updateEvent(p,b.segment_id,b.events[0].id,{body:'甲离开。'}),/位置|顺序/);assert.equal(JSON.stringify(b.events[0]),before);});
test('R08 旧项目可从未修改源文本恢复对白顺序',()=>{const p=project(interleaved);for(const d of p.segments[0].events[0].dialogues)delete d.after_body_line;const restored=C.restore(JSON.stringify(p)),t=C.videoPrompt(restored.segments[0],restored);assert(t.indexOf('先别打开')<t.indexOf('乙抬起头'));assert(t.indexOf('为什么')<t.indexOf('甲收回信件'));});

test('R09 源文已改时不猜测旧对白位置，必须确认',()=>{const p=project(interleaved);for(const d of p.segments[0].events[0].dialogues)delete d.after_body_line;p.segments[0].events[0].body='甲离开。';const restored=C.restore(JSON.stringify(p));assert(C.validate(restored).errors.some(e=>e.includes('插入位置')));assert.throws(()=>C.videoPrompt(restored.segments[0],restored),/插入位置/);});
test('R10 非法输入顶层不引发TypeError',()=>{for(const value of [null,[],{},42]){assert.equal(C.validate(value).valid,false);assert.throws(()=>C.restore(JSON.stringify(value)),/工作项目/);}});
test('R11 普通生图传递表演与期望末态',()=>{const p=project(),b=p.segments[0],x=b.panels[0];x.performance='停在门槛外';x.expected='右手持一枚玉盘';const t=C.panelPrompt(x,b,p);assert(t.includes(x.performance));assert(t.includes(x.expected));assert(C.gridPrompt(b,p).includes(x.expected));});
test('R12 单格纠错复用普通生图事实描述',()=>{const p=project(),b=p.segments[0],x=b.panels[0];x.expected='三人均已进入走廊';x.actual='仍在门外';x.change='仅修正位置';const t=C.editPrompt(x,b,p);assert(t.includes(C.panelPrompt(x,b,p)));assert(t.includes(x.actual));assert(t.includes(x.change));});

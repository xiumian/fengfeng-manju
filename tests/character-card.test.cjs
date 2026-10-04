const test=require('node:test'),a=require('node:assert/strict'),C=require('../assets/workbench/core.js'),P=require('../scripts/production.cjs');const p=()=>C.parseScript('——[0—3秒]：【站立】\n甲站立。','角色卡');const e={id:'A',kind:'character',name:'甲',description:'青衣青年'};
test('默认角色卡走主人展示板，不混入旧无头及HEX要求',()=>{const s=P.plan(p(),{entities:[e]}).asset_requests[0].prompt;for(const t of ['55%','四分之三侧面','动态姿势','黑灰色半透明','不要额外小头像组'])a(s.includes(t),t);a(!s.includes('无头'));a(!s.includes('HEX'));});
test('明确选择legacy保留源资产卡',()=>{const s=P.plan(p(),{entities:[{...e,asset_card_template:'legacy'}]}).asset_requests[0].prompt;a(s.includes('无头'));a(s.includes('HEX'));a(!s.includes('55%'));});
test('未知模板拒绝，不静默回落默认',()=>a.throws(()=>P.plan(p(),{entities:[{...e,asset_card_template:'wrong'}]}),/模板/));

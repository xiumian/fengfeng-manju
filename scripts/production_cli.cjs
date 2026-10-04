#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),C=require('../assets/workbench/core.js'),P=require('./production.cjs');
const [command,input,configFile,output]=process.argv.slice(2);
try{if(!input||!configFile||!output)throw Error('用法：plan|register|handoff PROJECT.json CONFIG.json OUTPUT.json');const p=C.restore(fs.readFileSync(input,'utf8'));const cfg=JSON.parse(fs.readFileSync(configFile,'utf8').replace(/^\uFEFF/,''));let result;if(command==='plan')result=P.plan(p,cfg);else if(command==='register'){P.registerAsset(p,cfg);result=p;}else if(command==='handoff')result=P.handoff(p);else throw Error('未知命令');fs.writeFileSync(output,JSON.stringify(result,null,2),'utf8');console.log(output);}catch(e){console.error(e.message);process.exitCode=1;}

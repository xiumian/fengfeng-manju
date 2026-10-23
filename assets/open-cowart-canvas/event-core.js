(function(root,factory){
  if(typeof module==='object'&&module.exports)module.exports=factory();
  else root.NineGridEvents=factory();
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  function refresh(board){
    let cursor=0;
    // 仅用于旧网页观察预览；绝不写events、event_ids、sample_time。
    board.observation_draft=(board.panels||[]).map(panel=>{
      const raw=Number(panel.duration),duration=Number.isFinite(raw)&&raw>0?raw:0.1;
      const item={panel_id:panel.id,start:cursor,end:cursor+duration,body:panel.action||''};
      cursor+=duration;return item;
    });
    if(board.events_complete!==true||board.source_coverage_checked!==true)board.completed=false;
    return board.observation_draft;
  }
  function eventErrors(board){
    const errors=[];
    if(board.events_complete!==true||board.source_coverage_checked!==true)errors.push('完整事件与源文覆盖尚未核对');
    const events=board.events;
    if(!Array.isArray(events)||!events.length)return errors.concat('缺少完整事件时间轴；九格草稿不能代替');
    const ids=new Set();let cursor=0;
    for(const e of events){
      if(!e.id||ids.has(e.id))errors.push('事件ID缺失或重复');
      ids.add(e.id);
      if(typeof e.start!=='number'||typeof e.end!=='number'||!Number.isFinite(e.start)||!Number.isFinite(e.end)||e.start<0||e.end<=e.start||Math.abs(e.start-cursor)>1e-6)errors.push('事件时间有缺口、重叠或非法值');
      cursor=e.end;
      if(typeof e.body!=='string'||!e.body.trim())errors.push('事件正文缺失');
      if(!Array.isArray(e.source_ids)||!e.source_ids.length)errors.push('事件缺少来源映射');
    }
    for(const panel of board.panels||[]){
      const refs=panel.event_ids;
      if(!Array.isArray(refs)||!refs.length||refs.some(id=>!ids.has(id)))errors.push('采样引用缺失或悬空');
      else if(typeof panel.sample_time!=='number'||!Number.isFinite(panel.sample_time)||!events.some(e=>refs.includes(e.id)&&panel.sample_time>=e.start&&panel.sample_time<=e.end))errors.push('采样时刻不在关联事件内');
    }
    return [...new Set(errors)];
  }
  function duration(board){
    const events=board.events;
    if(Array.isArray(events)&&events.length&&events.every(e=>typeof e.end==='number'&&Number.isFinite(e.end)))return Math.max(...events.map(e=>e.end));
    return Number((board.panels||[]).reduce((sum,p)=>sum+(Number.isFinite(Number(p.duration))?Number(p.duration):0),0).toFixed(2));
  }
  return {refresh,eventErrors,duration};
});

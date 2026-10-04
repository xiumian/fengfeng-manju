const STORAGE_KEY = "fengfeng-drama-grid-project-v1";

const DEFAULT_STYLE = "画风由当前视频项目确定。";
const DEFAULT_SCENE = "保持剧本确认的场景布局、主要光源、家具和道具位置连续。";
const DEFAULT_CONTINUITY = "只出现剧本确认的人物；保持角色区分、左右关系、服装、发型、视线、道具状态和空间轴线连续；无字幕、无水印、无新增或复制角色。";

function createDefaultBoard(){return createDefaultProject().segments[0];}

function createBoardFromRows(segmentId, rows, options = {}) {
  const defaultRefs = options.asset_refs || "TMP-CH01+TMP-SC01+TMP-PR01";
  return {
    segment_id: segmentId,
    title: options.title || segmentId,
    source_range: options.source_range || "",
    style_lock: options.style_lock || DEFAULT_STYLE,
    validation_mode: options.validation_mode || "临时写意Prompt校验；九宫格不是最终角色定稿",
    global_constraints: options.global_constraints || "不新增剧本外人物、事件或道具；无字幕、无水印。",
    panels: rows.slice(0,9).map((row,index) => ({
      id:`${segmentId}-P${String(index+1).padStart(2,"0")}`,
      shot_ref:row[0] || `SHOT ${String(index+1).padStart(2,"0")}`,
      duration:Number(row[1]) || 1.5,
      shot_size:row[2] || "中景",
      camera_move:row[3] || "固定镜头",
      action:row[4] || "保持当前动作节拍",
      performance:row[5] || "表演克制、动作因果清楚",
      asset_refs:row[6] || defaultRefs,
      character_anchor:options.character_anchor || "使用TMP-CHxx临时角色区分造型，仅用于Prompt验证",
      scene_anchor:options.scene_anchor || DEFAULT_SCENE,
      continuity:options.continuity || DEFAULT_CONTINUITY,
      expected:"", actual:"", change:"", edit_prompt:""
    })),
    versions:[], image_data_url:"", image_name:"", completed:false, generation_state:"prompt_ready"
  };
}

function createDefaultProject(){const p=DramaCore.parseScript('导入剧本后规划事件与九格。','尚未导入剧本');p.source_text='';p.is_empty=true;p.timing_confirmed=false;return p;}

function loadProject() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (saved?.package_type===DramaCore.TYPE && saved.segments?.length) return DramaCore.restore(saved);
  } catch (error) { console.warn("Could not restore project", error); }
  return createDefaultProject();
}

function openProjectDatabase() {
  return new Promise((resolve,reject)=>{
    const request=indexedDB.open("fengfeng-drama-grid-projects",1);
    request.onupgradeneeded=()=>request.result.createObjectStore("projects");
    request.onsuccess=()=>resolve(request.result);
    request.onerror=()=>reject(request.error);
  });
}
async function readSavedProject() {
  const database=await openProjectDatabase();
  return new Promise((resolve,reject)=>{
    const transaction=database.transaction("projects","readonly");
    const request=transaction.objectStore("projects").get("current");
    request.onsuccess=()=>resolve(request.result||null);
    request.onerror=()=>reject(request.error);
    transaction.oncomplete=()=>database.close();
  });
}
async function writeSavedProject(snapshot) {
  const database=await openProjectDatabase();
  return new Promise((resolve,reject)=>{
    const transaction=database.transaction("projects","readwrite");
    transaction.objectStore("projects").put(snapshot,"current");
    transaction.oncomplete=()=>{database.close();resolve();};
    transaction.onerror=()=>{database.close();reject(transaction.error);};
  });
}

let project = loadProject();
let activeSegmentId = project.segments[0].segment_id;
let activePanelId = project.segments[0].panels[0].id;
const el = (id) => document.getElementById(id);
const fields = { angle:el("angleInput"), source_ids:el("sourceIdsInput"), start_state:el("startStateInput"),end_state:el("endStateInput"),performance_provenance:el("performanceProvenanceInput"),performance_sequence:el("performanceSequenceInput"), duration:el("durationInput"), shot_size:el("shotSizeInput"), camera_move:el("cameraMoveInput"), shot_ref:el("shotRefInput"), asset_refs:el("assetRefsInput"), action:el("actionInput"), character_anchor:el("characterAnchorInput"), scene_anchor:el("sceneAnchorInput"), performance:el("performanceInput"), continuity:el("continuityInput"), expected:el("expectedInput"), actual:el("actualInput"), change:el("changeInput") };

function escapeHtml(value) { return String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char])); }
function currentBoard() { return project.segments.find((item) => item.segment_id===activeSegmentId) || project.segments[0]; }
function currentPanel() { const board=currentBoard(); return board.panels.find((item)=>item.id===activePanelId) || board.panels[0]; }
function totalDuration(board=currentBoard()){return DramaCore.duration(board);}
function normalizeSegmentId(index) { return `SEG${String(index+1).padStart(2,"0")}`; }

function parseScriptToProject(source,name="导入剧本"){return DramaCore.parseScript(source,name,{segmentSeconds:Number(el('segmentSeconds')?.value)||0});}

function buildPanelPrompt(panel,board=currentBoard()){return DramaCore.panelPrompt(panel,board,project);}
function buildSegmentPrompt(board=currentBoard()){return DramaCore.gridPrompt(board,project);}
function buildFinalVideoPrompt(board=currentBoard()){return DramaCore.videoPrompt(board,project);}

function buildEditPrompt(panel,board=currentBoard()) { return DramaCore.editPrompt(panel,board,project); }

function syncFields(){const b=currentBoard(),p=currentPanel(),before=JSON.stringify(p);let semantic=false;for(const [key,field] of Object.entries(fields)){const v=key==='duration'?Number(field.value):key==='source_ids'?field.value.split(',').map(x=>x.trim()).filter(Boolean):field.value.trim();if(JSON.stringify(p[key])!==JSON.stringify(v)&&!['expected','actual','change','duration'].includes(key)){semantic=true;if(['action','shot_size','angle','camera_move','performance','performance_sequence','start_state','end_state'].includes(key))p.video_sync_pending=true;}p[key]=v;}if(JSON.stringify(p)!==before){if(semantic)p.display_text_pending=true;if(semantic&&p.annotation_plan){p.annotation_plan_pending=true;p.annotation_review=[];}DramaCore.invalidate(project,b);if(semantic)b.semantics_pending=true;saveState();}updateDerived();}

function loadFields(){const panel=currentPanel();Object.entries(fields).forEach(([key,field])=>{const value=String(panel[key]??'');if(field.tagName==='SELECT'&&![...field.options].some(o=>o.value===value)){const option=document.createElement('option');option.value=value;option.textContent=value;field.appendChild(option);}field.value=value;});if(el('annotationPlanInput')){el('annotationPlanInput').value=JSON.stringify(panel.annotation_plan||[],null,2);el('annotationReviewInput').value=JSON.stringify(panel.annotation_review||[],null,2);el('displayTitleEn').value=panel.display_title_en||'';el('displayCaptionEn').value=panel.display_caption_en||'';el('visualCheckList').textContent='内部画面核对（不进生图稿）：'+DramaCore.visualChecks(panel).join('；');el('annotationRequirements').textContent='本格需要：'+DramaCore.annotationRequirements(panel,currentBoard()).join('、');}el('panelSelect').value=panel.id;updateDerived();drawCrop();}

function updateDerived(){
  const board=currentBoard(), panel=currentPanel(), index=project.segments.indexOf(board);
  el("scriptName").textContent=project.script_name||"未命名"; el("segmentId").textContent=board.segment_id; el("currentPanel").textContent=panel.id; el("totalDuration").textContent=`${totalDuration(board).toFixed(2)}s`; el("completionState").textContent=board.completed?"已完成":"检视中";
  el("segmentProgress").textContent=`${index+1} / ${project.segments.length}`; el("toggleComplete").textContent=board.completed?"取消完成":"确认图片并标记完成"; el("panelPrompt").textContent=buildPanelPrompt(panel,board); el("segmentPrompt").textContent=buildSegmentPrompt(board); el("videoPrompt").textContent=board.completed?buildFinalVideoPrompt(board):"本段仍在9宫调试；继续使用九宫格生图Prompt、逐格修改和视觉校验。明确确认并标记完成后，才清除作图指令并转换为最终视频生成Prompt。"; el("copyVideoPrompt").disabled=!board.completed; el("editPrompt").textContent=panel.edit_prompt||"尚未生成"; el("generationState").textContent=board.image_data_url&&board.last_replaced_panel?`${board.last_replaced_panel} 已替换 · v${String(board.image_revision||2).padStart(2,"0")}`:(board.image_data_url?"九宫格已回填":"Prompt已准备，等待$imagegen");
  const hasEdit=Boolean(panel.expected||panel.actual||panel.change); el("editPanel").classList.toggle("ready",hasEdit); el("editStatus").textContent=hasEdit?`${panel.id} 已预填`:`${panel.id} 待填写`;
  renderPipeline();
}

function renderPipeline(){
  const anyImage=project.segments.some(item=>item.image_data_url), allDone=project.segments.length>0&&project.segments.every(item=>item.completed&&item.image_data_url), stage=allDone?6:(anyImage?5:project.pipeline_stage||1);
  document.querySelectorAll("[data-stage]").forEach((item,index)=>{item.classList.toggle("done",index+1<stage);item.classList.toggle("active",index+1===stage);});
  const status=stage===1?"剧本已载入":stage===2?"正在自动拆段":stage===3?"九格Prompt已准备，等待$imagegen":stage===4?"九宫格已回填":stage===5?"平台审核中：请逐段检视并处理问题":project.last_packaged_at?"最终成果已输出":"平台审核已结束，请选择最终交付格式";
  el("pipelineStatus").textContent=status;
  el("resultOutputStage").hidden=!allDone;
}

function renderSegmentSelect(){ el("segmentSelect").innerHTML=project.segments.map(item=>`<option value="${item.segment_id}">${item.segment_id} · ${escapeHtml(item.title||item.source_range||"段落")}${item.completed?" · 已完成":""}</option>`).join(""); el("segmentSelect").value=activeSegmentId; }
function renderPanelSelect(){ const board=currentBoard(); el("panelSelect").innerHTML=board.panels.map(panel=>`<option value="${panel.id}">${panel.id} · ${escapeHtml(panel.shot_ref)} · ${escapeHtml(panel.asset_refs)}</option>`).join(""); }
function renderHitGrid(){ const board=currentBoard(); el("hitGrid").innerHTML=board.panels.map((panel,index)=>`<button type="button" data-index="${index}" class="${panel.id===activePanelId?"active":""}">${panel.id}</button>`).join(""); el("hitGrid").querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>selectPanel(board.panels[Number(button.dataset.index)].id))); }
function renderLookup(query=""){ const board=currentBoard(), normalized=query.trim().toLowerCase(); const matches=board.panels.filter(panel=>!normalized||[panel.id,panel.shot_ref,panel.asset_refs,panel.action,panel.performance,buildPanelPrompt(panel,board)].join(" ").toLowerCase().includes(normalized)); el("lookupResults").innerHTML=matches.map(panel=>`<button type="button" data-panel="${panel.id}"><b>${panel.id}</b><span>${escapeHtml(panel.shot_ref)} · ${escapeHtml(panel.asset_refs)}</span></button>`).join("")||`<span class="muted">没有匹配结果</span>`; el("lookupResults").querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>selectPanel(button.dataset.panel))); }
function renderVersions(){ const board=currentBoard(); el("versionList").innerHTML=board.versions.length?board.versions.slice().reverse().map(version=>`<button type="button" class="version-item" data-version="${version.id}"><b>${escapeHtml(version.id)}</b><span>${escapeHtml(version.panel_id)} · ${Number(version.duration).toFixed(2)}s · ${escapeHtml(version.shot_size)}</span></button>`).join(""):`<p class="muted">当前SEG尚未保存逐格版本。</p>`; el("versionList").querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>loadVersion(button.dataset.version))); }

function renderImage(){ const board=currentBoard(), hasImage=Boolean(board.image_data_url); el("imageStage").classList.toggle("has-image",hasImage); el("visualColumn").classList.toggle("has-image",hasImage); el("downloadCurrent").disabled=!hasImage; el("downloadAll").disabled=!hasImage; el("downloadBoard").disabled=!hasImage; el("panelReplaceInput").disabled=!hasImage; el("replacePanelLabel").classList.toggle("disabled",!hasImage); if(hasImage){el("storyboardImage").src=board.image_data_url;}else{el("storyboardImage").removeAttribute("src");el("cropMeta").textContent=`${board.segment_id}尚未回填九宫格图片`; const canvas=el("cropCanvas");canvas.getContext("2d").clearRect(0,0,canvas.width,canvas.height);}}
function renderAll(){ renderEventEditor();renderSegmentSelect(); renderPanelSelect(); renderHitGrid(); renderLookup(el("lookupQuery").value||""); renderVersions(); renderImage(); loadFields(); saveState(); }

function selectPanel(panelId){ syncFields(); activePanelId=panelId; renderHitGrid(); loadFields(); }
function selectSegment(segmentId){ syncFields(); activeSegmentId=segmentId; activePanelId=currentBoard().panels[0].id; el("lookupQuery").value=""; renderAll(); }

function drawCrop(){ const board=currentBoard(),image=el("storyboardImage"),canvas=el("cropCanvas"); if(!board.image_data_url||!image.complete||!image.naturalWidth)return; const index=board.panels.findIndex(panel=>panel.id===activePanelId), width=image.naturalWidth/3,height=image.naturalHeight/3,col=index%3,row=Math.floor(index/3); canvas.width=Math.floor(width);canvas.height=Math.floor(height);const context=canvas.getContext("2d");context.clearRect(0,0,canvas.width,canvas.height);context.drawImage(image,col*width,row*height,width,height,0,0,canvas.width,canvas.height);el("cropMeta").textContent=`${activePanelId} · 第${row+1}行第${col+1}列 · ${canvas.width}×${canvas.height}px`;}

let saveTimer;
let persistQueue=Promise.resolve();
function saveState(){const snapshot=structuredClone(project);try{const light=structuredClone(snapshot);light.segments.forEach(b=>b.image_data_url='');localStorage.setItem(STORAGE_KEY,JSON.stringify(light));}catch(e){console.warn('轻量缓存失败',e);}persistQueue=persistQueue.then(()=>writeSavedProject(snapshot)).catch(e=>{console.warn('完整项目缓存失败，请保存项目JSON',e);});return persistQueue;}
function saveVersion(){syncFields();const board=currentBoard(),panel=currentPanel();panel.edit_prompt=buildEditPrompt(panel,board);const serial=board.versions.filter(item=>item.panel_id===panel.id).length+1;board.versions.push({...JSON.parse(JSON.stringify(panel)),id:`${panel.id}-R${String(serial).padStart(2,"0")}`,panel_id:panel.id,panel_prompt:buildPanelPrompt(panel,board),segment_duration:totalDuration(board),storyboard_image:board.image_name||"prompt-only",saved_at:new Date().toISOString()});saveState();renderVersions();updateDerived();}
function loadVersion(versionId){const board=currentBoard(),version=board.versions.find(item=>item.id===versionId);if(!version)return;const panel=board.panels.find(item=>item.id===version.panel_id);["angle","source_ids","start_state","end_state","performance_provenance","performance_sequence","shot_ref","asset_refs","duration","shot_size","camera_move","action","character_anchor","scene_anchor","performance","continuity","expected","actual","change","edit_prompt","annotation_plan"].forEach(key=>{panel[key]=version[key];});DramaCore.invalidate(project,board);panel.video_sync_pending=true;panel.video_sync_audit=null;panel.annotation_plan_pending=!!panel.annotation_plan;panel.annotation_review=[];board.semantics_pending=true;activePanelId=panel.id;renderHitGrid();loadFields();}

function downloadBlob(blob,fileName){const url=URL.createObjectURL(blob),link=document.createElement("a");link.href=url;link.download=fileName;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function cleanFileStem(value){return String(value||"项目").replace(/\.[^.]+$/,"").replace(/[\\/:*?"<>|]/g,"-").trim()||"项目";}
function downloadCanvas(fileName){el("cropCanvas").toBlob(blob=>{if(blob)downloadBlob(blob,fileName);},"image/png");}
function downloadBoardImage(){const board=currentBoard(),link=document.createElement("a");link.href=board.image_data_url;link.download=board.image_name||`${board.segment_id}-storyboard.png`;link.click();}
function loadImageSource(src){return new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>resolve(image);image.onerror=reject;image.src=src;});}
async function replaceCurrentPanel(file){
  const board=currentBoard(); if(!board.image_data_url){alert("请先回填完整九宫格图");return;}
  const replacementUrl=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=reject;reader.readAsDataURL(file);});
  const [base,replacement]=await Promise.all([loadImageSource(board.image_data_url),loadImageSource(replacementUrl)]);
  const canvas=document.createElement("canvas"),context=canvas.getContext("2d");canvas.width=base.naturalWidth;canvas.height=base.naturalHeight;context.drawImage(base,0,0);
  const index=board.panels.findIndex(panel=>panel.id===activePanelId),cellWidth=canvas.width/3,cellHeight=canvas.height/3,col=index%3,row=Math.floor(index/3),targetRatio=cellWidth/cellHeight,sourceRatio=replacement.naturalWidth/replacement.naturalHeight;
  let sx=0,sy=0,sw=replacement.naturalWidth,sh=replacement.naturalHeight;
  if(sourceRatio>targetRatio){sw=sh*targetRatio;sx=(replacement.naturalWidth-sw)/2;}else{sh=sw/targetRatio;sy=(replacement.naturalHeight-sh)/2;}
  context.save();context.beginPath();context.rect(col*cellWidth,row*cellHeight,cellWidth,cellHeight);context.clip();context.drawImage(replacement,sx,sy,sw,sh,col*cellWidth,row*cellHeight,cellWidth,cellHeight);context.restore();
  board.image_revision=Number(board.image_revision||1)+1;board.image_name=`${board.segment_id}-storyboard-v${String(board.image_revision).padStart(2,"0")}.png`;board.image_data_url=canvas.toDataURL("image/png");board.last_replaced_panel=activePanelId;board.generation_state="panel_replaced";board.image_reviewed=false;board.mapping_confirmed=false;board.completed=false;board.panels.forEach(p=>p.annotation_review=[]);project.last_packaged_at="";renderImage();loadFields();updateDerived();drawCrop();saveState();
}
async function portableProject() {
  const snapshot=structuredClone(project);
  await Promise.all(snapshot.segments.map(async board=>{
    if(!board.image_data_url||board.image_data_url.startsWith("data:"))return;
    const response=await fetch(board.image_data_url);
    if(!response.ok)throw new Error(`${board.segment_id} 图片读取失败：HTTP ${response.status}`);
    const blob=await response.blob();
    board.image_data_url=await new Promise((resolve,reject)=>{
      const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=()=>reject(reader.error);reader.readAsDataURL(blob);
    });
  }));
  return snapshot;
}
async function saveProjectFile(){
  syncFields();
  try{
    const snapshot=await portableProject();
    downloadBlob(new Blob([JSON.stringify(snapshot,null,2)],{type:"application/json"}),`${(project.script_name||"九宫项目").replace(/\.[^.]+$/ ,"")}-工作项目.json`);
  }catch(error){alert(`保存失败：${error.message}`);}
}
function buildResultsHtml(payload){
  const segmentCards=payload.segments.map(segment=>{
    const rows=segment.storyboard_reference.panel_map.map(panel=>`<tr><td>${escapeHtml(panel.panel_id)}</td><td>${escapeHtml(panel.shot_ref)}</td><td>${escapeHtml(panel.asset_refs)}</td><td>${Number(panel.sample_time).toFixed(2)}s</td><td>${escapeHtml(panel.display_title_en||'')}<br>${escapeHtml(panel.display_caption_en||'')}</td><td>${escapeHtml(panel.meaning)}</td><td>${escapeHtml(panel.performance)}</td></tr>`).join("");
    const notes=segment.change_notes.length?`<details><summary>修改记录（${segment.change_notes.length}）</summary>${segment.change_notes.map(note=>`<article class="note"><b>${escapeHtml(note.panel_id)}</b><p><strong>期望：</strong>${escapeHtml(note.expected||"—")}</p><p><strong>偏差：</strong>${escapeHtml(note.actual||"—")}</p><p><strong>修改：</strong>${escapeHtml(note.change||"—")}</p></article>`).join("")}</details>`:"";
    return `<section class="segment"><header><div><span>${escapeHtml(segment.segment_id)}</span><h2>${escapeHtml(segment.title||segment.segment_id)}</h2></div><em>${Number(segment.segment_duration).toFixed(2)} 秒</em></header><p class="source">来源：${escapeHtml(segment.source_range||"未标注")}</p><img src="${escapeHtml(segment.storyboard_reference.image_data_url)}" alt="${escapeHtml(segment.segment_id)} 九宫格故事板"><h3>最终视频生成 Prompt</h3><pre>${escapeHtml(segment.final_video_prompt)}</pre><h3>逐格对照</h3><div class="table-wrap"><table><thead><tr><th>宫格</th><th>SHOT</th><th>资产 REF</th><th>观察时刻</th><th>画内英文</th><th>画面含义</th><th>表演</th></tr></thead><tbody>${rows}</tbody></table></div>${notes}</section>`;
  }).join("");
  return `<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escapeHtml(payload.script_name)} · 九宫格成果</title><style>:root{--bg:#f2efe8;--paper:#fffdf8;--ink:#20252a;--muted:#65707a;--line:#d8d0c0;--accent:#0f766e}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.65 Inter,"PingFang SC","Microsoft YaHei",sans-serif}main{width:min(1180px,calc(100% - 32px));margin:36px auto 64px}.hero,.segment{background:var(--paper);border:1px solid var(--line);border-radius:14px;box-shadow:0 8px 26px #352b2010}.hero{padding:26px;margin-bottom:20px}.hero h1{margin:4px 0 8px;font-size:28px}.hero p,.source{color:var(--muted)}.meta{display:flex;gap:10px;flex-wrap:wrap}.meta span,.segment header span{padding:4px 9px;border-radius:999px;background:#dff3ef;color:var(--accent);font-size:12px;font-weight:700}.segment{padding:22px;margin-top:18px}.segment header{display:flex;align-items:center;justify-content:space-between;gap:16px}.segment header div{display:flex;align-items:center;gap:10px}.segment h2,.segment h3{margin:0}.segment h2{font-size:20px}.segment h3{margin-top:20px;font-size:15px}.segment header em{color:var(--accent);font-style:normal;font-weight:700}.segment img{display:block;width:100%;height:auto;margin-top:14px;border-radius:10px;background:#161616}pre{margin:8px 0 0;padding:14px;overflow:auto;border-radius:9px;background:#f4f7f5;color:#35423f;white-space:pre-wrap;word-break:break-word;font:12px/1.65 ui-monospace,SFMono-Regular,Menlo,monospace}.table-wrap{overflow:auto;margin-top:8px}table{width:100%;border-collapse:collapse;font-size:12px}th,td{padding:9px 10px;border:1px solid var(--line);text-align:left;vertical-align:top}th{background:#f4f1ea;white-space:nowrap}details{margin-top:16px;padding:10px;border:1px solid var(--line);border-radius:8px}.note{padding:8px 0;border-top:1px solid var(--line)}.note:first-of-type{margin-top:8px}.note p{margin:3px 0}@media(max-width:700px){main{width:min(100% - 20px,1180px);margin-top:10px}.hero,.segment{padding:15px}.segment header,.segment header div{align-items:flex-start;flex-direction:column;gap:6px}}</style></head><body><main><section class="hero"><div class="meta"><span>九宫格成果</span><span>${payload.completed_segment_count} 个已完成 SEG</span></div><h1>${escapeHtml(payload.script_name||"未命名项目")}</h1><p>导出时间：${escapeHtml(new Date(payload.exported_at).toLocaleString("zh-CN"))}。本网页为离线浏览包，九宫格图片、逐格对照和最终视频 Prompt 均已内嵌。</p></section>${segmentCards}</main></body></html>`;
}

async function exportProject(){syncFields();try{const snapshot=await portableProject();const payload=DramaCore.reviewedResults(snapshot);project.last_packaged_at=payload.exported_at;if(el('exportFormat').value==='html')downloadBlob(new Blob([buildResultsHtml(payload)],{type:'text/html;charset=utf-8'}),cleanFileStem(project.script_name)+'-最终成果.html');else downloadBlob(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}),cleanFileStem(project.script_name)+'-最终成果.json');renderPipeline();saveState();}catch(error){alert('结果输出失败：'+error.message);}}

async function copyText(value){try{await navigator.clipboard.writeText(value);}catch{const box=document.createElement("textarea");box.value=value;document.body.appendChild(box);box.select();document.execCommand("copy");box.remove();}}

async function importScriptText(text,name){ if(!text.trim()){alert("剧本内容为空");return;} project=parseScriptToProject(text,name);loadProjectSettings();activeSegmentId=project.segments[0].segment_id;activePanelId=project.segments[0].panels[0].id;el("scriptTextInput").value=text;renderAll(); }

el("scriptFileInput").addEventListener("change",async()=>{const file=el("scriptFileInput").files?.[0];if(file)await importScriptText(await file.text(),file.name);});
el("parseScriptButton").addEventListener("click",()=>importScriptText(el("scriptTextInput").value,"粘贴剧本"));
el("segmentSelect").addEventListener("change",event=>selectSegment(event.target.value));
el("previousSegment").addEventListener("click",()=>{const index=project.segments.findIndex(item=>item.segment_id===activeSegmentId);if(index>0)selectSegment(project.segments[index-1].segment_id);});
el("nextSegment").addEventListener("click",()=>{const index=project.segments.findIndex(item=>item.segment_id===activeSegmentId);if(index<project.segments.length-1)selectSegment(project.segments[index+1].segment_id);});
el("toggleComplete").addEventListener("click",()=>{syncFields();const b=currentBoard();if(b.completed){b.completed=false;renderAll();return;}const ann=DramaCore.annotationPreflight(b,{review:true});const v=DramaCore.validate(project,{finalize:true});v.errors.push(...ann.errors);if(v.errors.length||project.is_empty||!project.timing_confirmed||!b.image_data_url){alert('尚不能完成：'+[...v.errors,!project.timing_confirmed?'时间未确认':'',!b.image_data_url?'未回填图片':''].filter(Boolean).join('；'));return;}if(!confirm('已逐格查看线标对象/方向/颜色/标签、人物、空间、道具、技能、时间及本段真实素材身份/用途，并确认九格代表状态与完整事件一致？'))return;for(const ref of new Set(b.panels.flatMap(p=>p.asset_refs.split('+').map(x=>x.trim()).filter(Boolean)))){const asset=project.assets.find(a=>a.id.trim()===ref);if(asset){asset.status='confirmed';asset.confirmation_source='explicit-board-review';}}b.image_reviewed=true;b.mapping_confirmed=true;b.completed=true;b.panels.forEach(p=>p.stale=false);renderAll();saveState();});
el("panelSelect").addEventListener("change",event=>selectPanel(event.target.value));
Object.values(fields).forEach(field=>{field.addEventListener("input",()=>{syncFields();});field.addEventListener("change",()=>{syncFields();});});
el("lookupQuery").addEventListener("input",event=>renderLookup(event.target.value));
el("saveVersion").addEventListener("click",saveVersion);
el("buildEditPrompt").addEventListener("click",()=>{syncFields();const panel=currentPanel();const gate=DramaCore.feedingPreflight({...currentBoard(),panels:[panel]});if(!gate.valid){alert(gate.errors.join("；"));return;}panel.edit_prompt=buildEditPrompt(panel,currentBoard());el("editPrompt").textContent=panel.edit_prompt;});
el("copyPanelPrompt").addEventListener("click",()=>{const b=currentBoard(),gate=DramaCore.feedingPreflight({...b,panels:[currentPanel()]});if(!gate.valid){alert(gate.errors.join('；'));return;}copyText(buildPanelPrompt(currentPanel(),b));});
el("copySegmentPrompt").addEventListener("click",async()=>{const gate=DramaCore.feedingPreflight(currentBoard());if(!gate.valid){alert(gate.errors.join('；'));return;}await copyText(buildSegmentPrompt(currentBoard()));el("copySegmentPrompt").textContent="已复制当前SEG Prompt";setTimeout(()=>{el("copySegmentPrompt").textContent="复制当前SEG生图Prompt";},1000);});
el("copyVideoPrompt").addEventListener("click",async()=>{const board=currentBoard();if(!board.completed)return;await copyText(buildFinalVideoPrompt(board));el("copyVideoPrompt").textContent="已复制";setTimeout(()=>{el("copyVideoPrompt").textContent="复制视频Prompt";},1000);});
el("saveProject").addEventListener("click",saveProjectFile);
el("exportFormat").addEventListener("change",()=>{el("exportPackage").textContent=el("exportFormat").value==="html"?"输出网页成果":"输出 JSON 成果";});
el("exportPackage").addEventListener("click",exportProject);
el("imageInput").addEventListener("change",()=>{const file=el("imageInput").files?.[0];if(!file)return;const reader=new FileReader();reader.onload=()=>{const board=currentBoard();board.image_data_url=reader.result;board.image_name=file.name;board.image_revision=Number(file.name.match(/-v(\d+)/i)?.[1]||1);board.last_replaced_panel="";board.generation_state="image_ready";board.image_reviewed=false;board.mapping_confirmed=false;board.completed=false;board.panels.forEach(p=>p.annotation_review=[]);project.last_packaged_at="";renderImage();loadFields();updateDerived();saveState();};reader.readAsDataURL(file);});
el("panelReplaceInput").addEventListener("change",async()=>{const file=el("panelReplaceInput").files?.[0];if(file)await replaceCurrentPanel(file);el("panelReplaceInput").value="";});
el("storyboardImage").addEventListener("load",drawCrop);
el("packageInput").addEventListener("change",async()=>{const file=el("packageInput").files?.[0];if(!file)return;try{project=DramaCore.restore(await file.text());activeSegmentId=project.segments[0].segment_id;activePanelId=project.segments[0].panels[0].id;renderAll();loadProjectSettings();}catch(e){alert('导入失败：'+e.message);}finally{el('packageInput').value='';}});
el("downloadCurrent").addEventListener("click",()=>{drawCrop();downloadCanvas(`${activePanelId}.png`);});
el("downloadBoard").addEventListener("click",downloadBoardImage);
el("downloadAll").addEventListener("click",async()=>{const board=currentBoard(),initial=activePanelId;for(const panel of board.panels){activePanelId=panel.id;drawCrop();downloadCanvas(`${panel.id}.png`);await new Promise(resolve=>setTimeout(resolve,120));}activePanelId=initial;renderHitGrid();drawCrop();});

async function bootstrapProject(){try{const saved=await readSavedProject();if(saved?.package_type===DramaCore.TYPE){project=DramaCore.restore(saved);activeSegmentId=project.segments[0].segment_id;activePanelId=project.segments[0].panels[0].id;}}catch(e){console.warn('恢复失败',e);}renderAll();loadProjectSettings();}

bootstrapProject();

function renderEventEditor(){const b=currentBoard(),select=el('eventSelect');if(!select)return;const before=select.value;select.innerHTML=b.events.map(e=>`<option value="${e.id}">${escapeHtml(e.id+' '+e.title+' '+e.start+'—'+e.end+'s')}</option>`).join('');select.value=b.events.some(e=>e.id===before)?before:b.events[0].id;loadEventFields();el('validationOutput').textContent=JSON.stringify(DramaCore.validate(project),null,2);}
function loadEventFields(){const e=currentBoard().events.find(e=>e.id===el('eventSelect').value);if(!e)return;for(const k of ['title','body','dynamic','sound','start','end'])el('event_'+k).value=e[k]??'';el('event_dialogues').value=JSON.stringify(e.dialogues||[],null,2);}
function loadProjectSettings(){el('storyboardStyleInput').value=project.storyboard_style||'';for(const k of Object.keys(DramaCore.headings))el('global_'+k).value=project.globals[k]||'';el('timingConfirmed').checked=project.timing_confirmed;}
el('eventSelect').addEventListener('change',loadEventFields);
el('saveEvent').addEventListener('click',()=>{try{const patch={};for(const k of ['title','body','dynamic','sound'])patch[k]=el('event_'+k).value.trim();for(const k of ['start','end'])patch[k]=Number(el('event_'+k).value);patch.dialogues=JSON.parse(el('event_dialogues').value||'[]');DramaCore.updateEvent(project,currentBoard().segment_id,el('eventSelect').value,patch);renderAll();saveState();}catch(e){alert('事件保存失败：'+e.message);}});
el('saveAnnotations').addEventListener('click',()=>{try{DramaCore.updateAnnotations(project,currentBoard().segment_id,currentPanel().id,JSON.parse(el('annotationPlanInput').value));renderAll();saveState();}catch(e){alert('线标保存失败：'+e.message);}});
el('saveAnnotationReview').addEventListener('click',()=>{try{const b=currentBoard(),p=currentPanel();if(!b.image_data_url)throw Error('先回填实际图片，再逐条查看线标');const rows=JSON.parse(el('annotationReviewInput').value);if(!Array.isArray(rows)||rows.some(x=>!x||typeof x.id!=='string'||!['ok','issue','accepted'].includes(x.status)))throw Error('核验须为id/status数组，状态ok/issue/accepted');p.annotation_review=rows.map(x=>({...x,image_revision:b.image_revision||1}));b.annotation_contract=1;b.completed=false;b.image_reviewed=false;b.mapping_confirmed=false;renderAll();saveState();}catch(e){alert('线标核验保存失败：'+e.message);}});
el('syncPanelVideo').addEventListener('click',()=>{syncFields();const b=currentBoard(),p=currentPanel(),eventId=el('eventSelect').value,e=b.events.find(e=>e.id===eventId);if(!e||!p.event_ids.includes(eventId)){alert('请在事件下拉框选择本格对应事件：'+p.event_ids.join('、'));return;}const notes=[p.camera_move,p.performance,p.performance_sequence,p.expected,p.start_state,p.end_state].filter(Boolean).join('；');const body=prompt('将本格修订写入该事件的最终连续画面正文。保留动作顺序；不更改台词与时间。参考：'+notes,e.body);if(body===null)return;try{DramaCore.applyPanelVideoRevision(project,b.segment_id,p.id,eventId,{body});renderAll();saveState();}catch(e){alert('同步失败：'+e.message);}});
el('retainPanelVideo').addEventListener('click',()=>{syncFields();const reason=prompt('仅调整分镜检查图、保留视频原稿的原因（不能用于掩盖剧情矛盾）：');if(reason===null)return;try{DramaCore.retainPanelVideoSource(project,currentBoard().segment_id,currentPanel().id,reason);renderAll();saveState();}catch(e){alert(e.message);}});
el('confirmPanelFacts').addEventListener('click',()=>{syncFields();if(currentBoard().panels.some(p=>p.video_sync_pending)){alert('请先同步待处理格的视频修订，或说明仅调整分镜并保留视频原稿。');return;}if(!confirm('已核对九格修改与事件正文，必要变化已在事件编辑器同步？'))return;currentBoard().semantics_pending=false;renderAll();saveState();});
el('timingConfirmed').addEventListener('change',()=>{project.timing_confirmed=el('timingConfirmed').checked;project.segments.forEach(b=>b.completed=false);project.last_packaged_at='';renderAll();saveState();});
el('saveGlobals').addEventListener('click',()=>{const patch={};for(const k of Object.keys(DramaCore.headings))patch[k]=el('global_'+k).value.trim();DramaCore.updateGlobals(project,patch);renderAll();saveState();});
el('newProject').addEventListener('click',()=>{if(!confirm('新建项目？请先保存当前项目JSON。'))return;project=createDefaultProject();activeSegmentId=project.segments[0].segment_id;activePanelId=project.segments[0].panels[0].id;renderAll();loadProjectSettings();saveState();});

el('storyboardStyleInput').value=project.storyboard_style||'';el('storyboardStyleInput').addEventListener('change',()=>{project.storyboard_style=el('storyboardStyleInput').value.trim();project.segments.forEach(b=>DramaCore.invalidate(project,b));renderAll();});

const legendBox=document.querySelector('.line-legend');legendBox.innerHTML='<b>线标图例</b>'+DramaCore.STORYBOARD_LABELS.map(([css,label])=>'<span><i class="'+(css==='green'?'legend-box ':'legend-line ')+css+'"></i>'+label+'</span>').join('')+'<em>仅画已明确的标注；动作红、视线青，不能用蓝色箭头替代视线。</em>';

el('saveDisplayText').addEventListener('click',()=>{const p=currentPanel();p.display_title_en=el('displayTitleEn').value.trim();p.display_caption_en=el('displayCaptionEn').value.trim();p.display_text_pending=false;p.annotation_review=[];DramaCore.invalidate(project,currentBoard());renderAll();saveState();});

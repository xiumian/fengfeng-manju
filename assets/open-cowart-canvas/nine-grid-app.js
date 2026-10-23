const STORAGE_KEY = "open-cowart-nine-grid-project-v3";

const DEFAULT_STYLE = "Cinematic storyboard visualization, physically coherent lighting and materials, controlled highlights, readable silhouettes, stable spatial depth and scale, 16:9 composition. Preserve the source-defined world, palette and genre; do not introduce unrelated locations, lighting motifs or props.";
const DEFAULT_SCENE = "保持剧本确认的场景布局、主要光源、家具和道具位置连续。";
const DEFAULT_CONTINUITY = "只出现剧本确认的人物；保持角色区分、左右关系、服装、发型、视线、道具状态和空间轴线连续；无字幕、无水印、无新增或复制角色。";
const OBSERVATION_STATES = ["建立状态","触发出现","动作启动","过程推进","关键接触","即时反馈","人物反应","环境与道具结果","稳定终态"];
const DEFAULT_PROJECT_OPTIONS = {grid_mode:"full_unique",style_mode:"project",label_mode:"ids_only",workflow_mode:"ninegrid",video_mode:"project",emotion_closeup_mode:"enhanced",custom_storyboard_style:""};
const EMOTION_CHANNELS = [
  {name:"眼神",pattern:/眼神|视线|瞳孔|眼睛|眨眼|眼睑|杏眼|目光/},
  {name:"眉部",pattern:/眉|眉头|眉目/},
  {name:"口部与下颌",pattern:/嘴角|唇|抿|下颌|咬紧|张口|闭口/},
  {name:"呼吸与吞咽",pattern:/呼吸|吸气|吐气|屏息|吞咽|鼻息/},
  {name:"手部",pattern:/手指|指节|握紧|收紧|攥|捂住|按住|触碰|掌心/},
  {name:"肩颈与姿态",pattern:/肩|颈|头轻|歪头|低头|抬头|僵住|绷紧|微颤/}
];
const EMOTION_TRIGGER_PATTERN=/听见|看见|发现|认出|意识到|确认|被推|落音|问|喊|台词|异响|疼|受伤|停顿|突然|一瞬/;
const SPATIAL_PRIORITY_PATTERN=/空间|全貌|建立|走位|路径|来向|退路|包围|群体|路面|全身|弓步|命中|撞击|爆炸|光柱|环境结果|展开/;

function analyzeEmotionDetail(panel) {
  const text=[panel.action,panel.performance,panel.continuity].filter(Boolean).join("；");
  const channels=EMOTION_CHANNELS.filter(item=>item.pattern.test(text)).map(item=>item.name);
  const parts=String(panel.performance||panel.action||"").split(/→|->|；/).map(item=>item.trim()).filter(Boolean);
  const triggerIndex=parts.findIndex(item=>EMOTION_TRIGGER_PATTERN.test(item));
  const trigger=triggerIndex>=0?parts[triggerIndex]:(parts[1]||"承接当前事件刺激");
  const baseline=triggerIndex>0?(parts[0]||"保持上一格状态"):"承接上一格稳定状态";
  const endState=parts[parts.length-1]||"形成可读终态";
  const hasTrigger=EMOTION_TRIGGER_PATTERN.test(text),concealed=/压住|克制|忍|不出声|闭口|掩饰|收住|不让|不动/.test(text);
  const spatialPriority=SPATIAL_PRIORITY_PATTERN.test(text)&&/(大远景|远景|全景|中全景)/.test(panel.shot_size||"");
  const score=channels.length+(hasTrigger?1:0)+(concealed?1:0)-(spatialPriority?2:0);
  const handOnly=channels.includes("手部")&&!channels.some(item=>["眼神","眉部","口部与下颌"].includes(item));
  const recommended=handOnly?"手部特写":channels.filter(item=>["眼神","眉部","口部与下颌"].includes(item)).length>=2?"特写":channels.length>=2?"近景":panel.shot_size;
  const detected=score>=2&&channels.length>=1;
  const eligible=detected&&!spatialPriority;
  const focus=channels.length?channels.slice(0,3).join(" + "):"保持原叙事主体";
  return {detected,eligible,score,channels,baseline,trigger,leak:channels.length?`${focus}出现短暂可见变化`:"无额外微表情推断",mask:concealed?"角色主动压住外化反应":"不额外添加掩饰动作",end_state:endState,visual_focus:focus,recommended_shot:recommended,focus_reason:eligible?`该格的剧情信息主要由${focus}承担，特写可把观众注意力落到情绪变化上。`:spatialPriority?"本格优先交代空间、走位或动作因果，不自动收紧景别。":"微表情证据不足，保持原景别。",negative_constraints:"不冻结中性脸、不夸张瞪眼、不机械眨眼、不突然甩头、不强行微笑、不脸部变形、不身份漂移"};
}

function refreshEmotionMetadata(board,mode="enhanced",applyShot=false) {
  if(applyShot)board.panels.forEach(panel=>{if(panel.closeup_applied&&panel.pre_closeup_shot_size)panel.shot_size=panel.pre_closeup_shot_size;panel.closeup_applied=false;});
  const analyses=board.panels.map(panel=>({panel,detail:analyzeEmotionDetail(panel)}));
  analyses.forEach(({panel,detail})=>{panel.emotion_detail=mode==="off"?{...detail,detected:false,eligible:false,focus_reason:"情绪细节自动分析已关闭。"}:detail;});
  if(mode!=="enhanced"||!applyShot)return;
  const selected=analyses.filter(item=>item.detail.eligible).sort((a,b)=>b.detail.score-a.detail.score).slice(0,3);
  selected.forEach(({panel,detail})=>{
    if(!panel.pre_closeup_shot_size)panel.pre_closeup_shot_size=panel.shot_size;
    if(!["特写","手部特写"].includes(panel.shot_size)&&detail.recommended_shot)panel.shot_size=detail.recommended_shot;
    panel.closeup_applied=true;
  });
}

function createDefaultBoard() {
  const characterAnchor = "临时写意验证：A=TMP-CH01容嬷嬷（代替待补图片2）；B=TMP-CH02成年宫女一（代替待补图片3）。只要求本九宫格内可区分与相对一致，不作为最终角色定稿。";
  const sceneAnchor = "员工休息包厢；暖黄色台灯为唯一实际光源；深蓝灰色绒面沙发；圆形茶几固定摆放温水、剥好葡萄、干净手帕、黑色练习本和事故记录。";
  const rows = [
    ["SHOT 01",1.6,"桌面特写","固定镜头","A从宽大袖口取出事故记录，平整放在茶几上；冷静说：充电归充电。","目光降温，嘴角归平；动作平稳克制","TMP-CH01+TMP-SC01+TMP-PR01"],
    ["SHOT 01",1.6,"桌面特写","固定镜头","A把黑色练习本推到B面前，用手指点一下；说：规矩归规矩。","A威严不动；B有限度地注视练习本"],
    ["SHOT 02",1.8,"近景","固定镜头","B笑容僵住，视线从练习本移到A；问：还是十遍吗？","笑容停住→视线转移→浅吸气"],
    ["SHOT 03",2.1,"近景","固定镜头","A端起温水，淡淡看B一眼；说：方才本是十遍。B眼睛短暂亮起。","A侧目一瞥；B只出现短暂希望"],
    ["SHOT 03",2.1,"近景","固定镜头","A停顿后清楚落字：二十遍。","A不提高音量；B希望消退"],
    ["SHOT 04",1.7,"中近景","轻微手持微颤","B瞬间垮下脸：嬷嬷……；A闭眼靠回沙发。","B嘴角下沉；A威严不动"],
    ["SHOT 04",1.7,"中近景","轻微手持微颤","A闭眼说：再撒娇，三十遍。B立刻捂住嘴。","B快速止住反应；A姿势不变"],
    ["SHOT 05",1.2,"手部特写","受控焦点/构图转移","B翻开练习本开始写，偷偷把一颗葡萄放进A手里。","B低头罚抄；A闭眼接受葡萄"],
    ["SHOT 05",1.2,"手部特写","固定镜头","A手指收紧握住葡萄，嘴角极轻微抬起；B继续写；随后瞬间切黑。","A不睁眼、不扩大笑容；切黑瞬间完成"]
  ];
  return createBoardFromRows("SEG01", rows, {
    style_lock: DEFAULT_STYLE + " TVB palace comedy final punchline, deadpan rule-enforcement gag, warm emotional residue under strict discipline, shallow depth of field, 16:9 anamorphic.",
    character_anchor: characterAnchor,
    scene_anchor: sceneAnchor,
    global_constraints: "只出现容嬷嬷和宫女一；事故记录和练习本文字模糊不可读；结尾瞬间切黑；不要BGM、字幕、全剧终、水印、新增或复制角色。"
  });
}

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
      observation_state:row[7] || OBSERVATION_STATES[index],
      expected:"", actual:"", change:"", edit_prompt:"", reverse_status:"pending", reverse_note:"", reverse_prompt_note:"", reverse_checked_at:""
    })),
    versions:[], image_data_url:"", image_name:"", completed:false, generation_state:"prompt_ready"
  };
}

function createDefaultProject() {
  return { package_type:"open-cowart-nine-grid-project", script_name:"内置测试", source_text:"", pipeline_stage:3, last_packaged_at:"", project_options:{...DEFAULT_PROJECT_OPTIONS}, segments:[createDefaultBoard()] };
}

function readEmbeddedWorkspace() {
  const node=document.getElementById("embeddedWorkspace");
  if(!node)return null;
  try{
    const snapshot=JSON.parse(node.textContent||"null");
    return Array.isArray(snapshot?.project?.segments)&&snapshot.project.segments.length?snapshot:null;
  }catch(error){console.warn("Could not restore embedded workspace",error);return null;}
}

const embeddedWorkspace=readEmbeddedWorkspace();

function loadProject() {
  if(embeddedWorkspace)return embeddedWorkspace.project;
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (Array.isArray(saved?.segments) && saved.segments.length) return saved;
  } catch (error) { console.warn("Could not restore project", error); }
  return createDefaultProject();
}

function deriveEventTimeline(board) {
  let cursor=0;
  const events=[];
  board.panels.forEach((panel,index)=>{
    const duration=Math.max(.1,Number(panel.duration)||.1),eventId=`${board.segment_id}-EV${String(index+1).padStart(2,"0")}`;
    panel.observation_state=panel.observation_state||OBSERVATION_STATES[index]||`观察状态${index+1}`;
    panel.event_ids=[eventId];
    panel.sample_time=Number((cursor+duration/2).toFixed(2));
    events.push({id:eventId,start:Number(cursor.toFixed(2)),end:Number((cursor+duration).toFixed(2)),shot_ref:panel.shot_ref,observation_state:panel.observation_state,body:panel.action});
    cursor+=duration;
  });
  board.events=events;
}

function normalizeReverseValidation(snapshot) {
  snapshot.project_options={...DEFAULT_PROJECT_OPTIONS,...(snapshot.project_options||{})};
  snapshot.segments.forEach((board)=>{
    board.panels.forEach((panel)=>{
      if(!["pending","accepted","revise"].includes(panel.reverse_status))panel.reverse_status="pending";
      panel.reverse_note=panel.reverse_note||"";
      panel.reverse_prompt_note=panel.reverse_prompt_note||"";
      panel.reverse_checked_at=panel.reverse_checked_at||"";
    });
    deriveEventTimeline(board);
    refreshEmotionMetadata(board,snapshot.project_options.emotion_closeup_mode,false);
    if(board.completed&&!board.panels.every(panel=>panel.reverse_status==="accepted"))board.completed=false;
  });
  return snapshot;
}

function openProjectDatabase() {
  return new Promise((resolve,reject)=>{
    const request=indexedDB.open("nine-grid-projects",1);
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

let project = normalizeReverseValidation(loadProject());
let activeSegmentId = project.segments.some(item=>item.segment_id===embeddedWorkspace?.active_segment_id)?embeddedWorkspace.active_segment_id:project.segments[0].segment_id;
let activePanelId = currentBoardForStartup().panels.some(item=>item.id===embeddedWorkspace?.active_panel_id)?embeddedWorkspace.active_panel_id:currentBoardForStartup().panels[0].id;
function currentBoardForStartup(){return project.segments.find(item=>item.segment_id===activeSegmentId)||project.segments[0];}
const el = (id) => document.getElementById(id);
const fields = { duration:el("durationInput"), shot_size:el("shotSizeInput"), camera_move:el("cameraMoveInput"), shot_ref:el("shotRefInput"), asset_refs:el("assetRefsInput"), action:el("actionInput"), character_anchor:el("characterAnchorInput"), scene_anchor:el("sceneAnchorInput"), performance:el("performanceInput"), continuity:el("continuityInput"), expected:el("expectedInput"), actual:el("actualInput"), change:el("changeInput"), reverse_note:el("reverseNoteInput"), reverse_prompt_note:el("reversePromptNoteInput") };
const optionFields={grid_mode:el("gridModeInput"),style_mode:el("styleModeInput"),label_mode:el("labelModeInput"),workflow_mode:el("workflowModeInput"),video_mode:el("videoModeInput"),emotion_closeup_mode:el("emotionCloseupModeInput"),custom_storyboard_style:el("customStoryboardStyleInput")};

function escapeHtml(value) { return String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char])); }
function currentBoard() { return project.segments.find((item) => item.segment_id===activeSegmentId) || project.segments[0]; }
function currentPanel() { const board=currentBoard(); return board.panels.find((item)=>item.id===activePanelId) || board.panels[0]; }
function totalDuration(board=currentBoard()) { return Number(board.panels.reduce((sum,panel)=>sum+(Number(panel.duration)||0),0).toFixed(2)); }
function normalizeSegmentId(index) { return `SEG${String(index+1).padStart(2,"0")}`; }

function extractBlock(source,label) {
  const pattern=new RegExp(`【${label}】\\s*([\\s\\S]*?)(?=【|$)`);
  return (source.match(pattern)?.[1]||"").trim();
}

function parseCamera(text) {
  return {
    shot_size:text.match(/桌面特写|手部特写|大远景|中近景|远景|近景|中景|全景|特写/)?.[0]||"中景",
    camera_move:/handheld|手持|呼吸感/i.test(text)?"轻微手持微颤":
      (/跟移/i.test(text)?"缓慢跟移":
      (/横移/i.test(text)?"缓慢横移":
      (/推近/i.test(text)?"缓慢推近":
      (/拉远/i.test(text)?"缓慢拉远":
      (/转|焦点/i.test(text)?"受控焦点/构图转移":"固定镜头")))))
  };
}

function estimateBeatSeconds(text) {
  const dialogueLength=[...text.matchAll(/[“\"]([^”\"]+)[”\"]/g)].reduce((sum,item)=>sum+item[1].length,0);
  const actionLength=text.replace(/台词[:：][^\n]+/g,"").length;
  return Math.max(2,Math.min(6,dialogueLength/5.5+actionLength/45+1));
}

function parseCharacterAssets(source) {
  return [...source.matchAll(/图片(\d+)\s*作为(.+?)的视觉锚定\+([^\n。]+)[。]?/g)].map((match,index)=>({
    image:match[1], name:match[2].trim(), id:`TMP-CH${String(index+1).padStart(2,"0")}`, description:match[3].replace(/严格按此图渲染/g,"").trim()
  }));
}

function parseCharacterAnchor(source,assets=parseCharacterAssets(source)) {
  if (!assets.length) return "临时写意验证：使用TMP-CH01、TMP-CH02等临时角色造型；只保证本九宫格内可区分和相对一致。";
  return assets.map((asset,index)=>`${String.fromCharCode(65+index)}=${asset.id} ${asset.name}（代替待补图片${asset.image}）：${asset.description}`).join("；")+"。临时造型只用于Prompt验证。";
}

function parseShots(source,characterAssets=[]) {
  const inferRefs=(text)=>{
    const explicit=text.match(/REF[:：]\s*([A-Z0-9+_-]+)/i)?.[1];
    if(explicit)return explicit;
    const characters=characterAssets.filter(asset=>text.includes(asset.name)).map(asset=>asset.id);
    return [...new Set([...characters,"TMP-SC01","TMP-PR01"])].join("+");
  };
  const structuredHeader=source.match(/(?:^|\n)\s*分镜\s*([A-Za-z0-9_-]+)\s*[｜|]/);
  const timedActionBlock=extractBlock(source,"动作与时间");
  if(structuredHeader&&timedActionBlock){
    const timedParts=timedActionBlock.split(/\n+/).map(item=>item.trim()).filter(Boolean).map(item=>item.replace(/^(\d+(?:\.\d+)?)\s*[—–-]\s*(\d+(?:\.\d+)?)\s*秒\s*[:：]\s*/,"$1—$2秒："));
    const camera=extractBlock(source,"镜头")||"固定中景";
    const characterBlock=extractBlock(source,"人物、对白与OS");
    const provisionalRefs=characterBlock?"TMP-CH01+TMP-CH02+TMP-SC01+TMP-VFX01":"TMP-SC01+TMP-VFX01";
    return [{id:`SHOT ${structuredHeader[1]}`,title:`分镜${structuredHeader[1]}`,body:source,action:timedParts.join("；"),parts:timedParts,dialogue:[],camera,asset_refs:characterAssets.length?inferRefs(source):provisionalRefs,...parseCamera(camera),weight:estimateBeatSeconds(timedActionBlock)}];
  }
  const explicit=[...source.matchAll(/【([^】]*镜头\s*([A-Z0-9]+)[^】]*)】\s*([\s\S]*?)(?=【[^】]*镜头\s*[A-Z0-9]+[^】]*】|【声音设计|【关键约束|$)/g)];
  if (explicit.length) return explicit.map((match,index)=>{
    const body=match[3].trim();
    const camera=(body.match(/机位[:：]\s*([^\n]+)/)?.[1]||"固定中景").replace(/[。；]+$/,"");
    const actionLines=[...body.matchAll(/画面[:：]\s*([^\n]+)/g)].map(item=>item[1].replace(/[。；]+$/,"").split(/[+；，,]/)).flat().map(item=>item.trim()).filter(Boolean);
    const dialogue=[...body.matchAll(/台词[:：]\s*([^\n]+)/g)].map(item=>item[1].trim());
    const action=(actionLines.length?actionLines:[match[1].trim()]).join("；")+(dialogue.length?`；台词：${dialogue.join("；")}`:"");
    return { id:`SHOT ${String(index+1).padStart(2,"0")}`, title:match[1].trim(), body, action, parts:actionLines.length?actionLines:[action], dialogue, camera, asset_refs:inferRefs(`${match[1]} ${body}`), ...parseCamera(camera), weight:estimateBeatSeconds(body) };
  });
  const paragraphs=source.split(/\n{2,}|(?<=[。！？])\s*/).map(item=>item.trim()).filter(item=>item.length>2);
  return paragraphs.map((text,index)=>({ id:`SHOT ${String(index+1).padStart(2,"0")}`, title:`镜头${index+1}`, body:text, action:text, parts:[text], dialogue:[], camera:"固定中景", asset_refs:inferRefs(text), ...parseCamera(text), weight:estimateBeatSeconds(text) }));
}

function groupShots(shots,totalHint) {
  if (totalHint>0 && totalHint<=15 && shots.length<=6) return [{shots,total:totalHint}];
  const groups=[]; let current=[]; let seconds=0;
  shots.forEach((shot)=>{
    if (current.length && (current.length>=9 || (seconds+shot.weight>15 && seconds>=8))) { groups.push({shots:current,total:Math.max(10,Math.min(15,seconds))}); current=[]; seconds=0; }
    current.push(shot); seconds+=shot.weight;
  });
  if (current.length) groups.push({shots:current,total:Math.max(10,Math.min(15,seconds))});
  return groups.length?groups:[{shots:[{id:"SHOT 01",action:"空镜建立",parts:["空镜建立"],shot_size:"中景",camera_move:"固定镜头",weight:10}],total:10}];
}

function allocateDurations(shots,total) {
  const weightTotal=shots.reduce((sum,shot)=>sum+shot.weight,0)||1;
  const values=shots.map(shot=>Number((total*shot.weight/weightTotal).toFixed(1)));
  values[values.length-1]=Number((values[values.length-1]+total-values.reduce((a,b)=>a+b,0)).toFixed(1));
  return values;
}

function panelsFromShots(segmentId,shots,total,options) {
  const distribution=Array(shots.length).fill(1);
  while (distribution.reduce((a,b)=>a+b,0)<9) {
    const candidates=shots.map((shot,index)=>shot.weight/distribution[index]);
    distribution[candidates.indexOf(Math.max(...candidates))]+=1;
  }
  const shotDurations=allocateDurations(shots,total);
  const rows=[];
  shots.forEach((shot,shotIndex)=>{
    const count=distribution[shotIndex];
    for(let index=0;index<count;index+=1){
      const start=Math.floor(shot.parts.length*index/count);
      const end=Math.max(start+1,Math.ceil(shot.parts.length*(index+1)/count));
      const part=shot.parts.slice(start,end).join("；")||shot.action;
      const duration=Number((shotDurations[shotIndex]/count).toFixed(2));
      const state=OBSERVATION_STATES[rows.length]||`观察状态${rows.length+1}`;
      rows.push([shot.id,duration,shot.shot_size,shot.camera_move,part,index===0?"建立动作与视线；表演克制可读":"承接上一格状态并完成本节拍",shot.asset_refs||options.asset_refs,state]);
    }
  });
  const selected=rows.slice(0,9);
  while(selected.length<9){
    const index=selected.length,previous=selected[selected.length-1]||["SHOT 01",1,"中景","固定镜头","保持已确认事件状态","表演克制可读",options.asset_refs];
    selected.push([...previous.slice(0,7),OBSERVATION_STATES[index]]);
  }
  const difference=Number((total-selected.reduce((sum,row)=>sum+Number(row[1]),0)).toFixed(2));
  selected[selected.length-1][1]=Number((Number(selected[selected.length-1][1])+difference).toFixed(2));
  return createBoardFromRows(segmentId,selected,options);
}

function parseScriptToProject(source,name="导入剧本") {
  const characterAssets=parseCharacterAssets(source);
  const shots=parseShots(source,characterAssets);
  const totalHint=Number(source.match(/(?:整段|目标时长)\s*[:：]?\s*(\d+(?:\.\d+)?)\s*秒/)?.[1]||0);
  const groups=groupShots(shots,totalHint);
  const style=(source.match(/\[STYLE LOCK\]\s*([\s\S]*?)(?=\n\s*图片\d+|【)/)?.[1]||DEFAULT_STYLE).trim();
  const scene=extractBlock(source,"场景与空间")||extractBlock(source,"场景物理设置")||DEFAULT_SCENE;
  const sourceConstraints=extractBlock(source,"一致性与执行限制")||extractBlock(source,"关键约束");
  const constraints=[sourceConstraints,"不新增剧本外人物、事件或道具；无字幕、无水印。"].filter(Boolean).join("；");
  const characterAnchor=extractBlock(source,"人物、对白与OS")||parseCharacterAnchor(source,characterAssets);
  const opening=extractBlock(source,"开场承接"),ending=extractBlock(source,"结尾接口"),audio=extractBlock(source,"声音"),referenceDuty=extractBlock(source,"参考图职责"),purpose=extractBlock(source,"本镜头目的");
  const continuity=[opening&&`开场：${opening}`,ending&&`结尾：${ending}`,DEFAULT_CONTINUITY].filter(Boolean).join("；");
  const assetRefs=(characterAnchor.match(/TMP-CH\d+/g)||["TMP-CH01"]).filter((item,index,array)=>array.indexOf(item)===index).join("+")+"+TMP-SC01+TMP-PR01";
  const segments=groups.map((group,index)=>{
    const board=panelsFromShots(normalizeSegmentId(index),group.shots,Number(group.total.toFixed(1)),{
      title:purpose||group.shots.map(item=>item.title).join(" / "),source_range:`${group.shots[0].id}–${group.shots[group.shots.length-1].id}`,
      style_lock:style,character_anchor:characterAnchor,scene_anchor:scene,continuity,global_constraints:constraints,asset_refs:assetRefs,validation_mode:referenceDuty||"九宫格Prompt校验；成图须逐格审核"
    });
    const structuredShot=Boolean(source.match(/(?:^|\n)\s*分镜\s*[A-Za-z0-9_-]+\s*[｜|]/)&&extractBlock(source,"动作与时间"));
    const stagedPush=/稳定[\s\S]*(?:再|随)[\s\S]*推近/.test(extractBlock(source,"镜头"));
    board.panels.forEach((panel,panelIndex)=>{
      panel.dialogue_audio=audio||"仅保持已确认环境声";
      panel.source_ids=[panel.shot_ref];
      panel.start_state=`${board.segment_id}-T${String(panelIndex).padStart(2,"0")}`;
      panel.end_state=`${board.segment_id}-T${String(panelIndex+1).padStart(2,"0")}`;
      if(structuredShot){
        panel.performance="能量、碎屑与余烬变化连续可读；人物仅保持剧本规定状态";
        if(stagedPush&&panel.action.startsWith("0.0")&&!panel.action.includes("2.5—"))panel.camera_move="固定镜头";
      }
    });
    return board;
  });
  return { package_type:"open-cowart-nine-grid-project", script_name:name, source_text:source, pipeline_stage:3, last_packaged_at:"", project_options:{...DEFAULT_PROJECT_OPTIONS}, segments };
}

function resolvedStyle(board=currentBoard()) {
  const options=project.project_options||DEFAULT_PROJECT_OPTIONS;
  if(options.style_mode==="custom"&&options.custom_storyboard_style.trim())return options.custom_storyboard_style.trim();
  if(options.style_mode==="graphite")return "灰阶铅笔故事板，电影分镜草图，清晰轮廓、灰度明暗与空间关系，16:9；人物、场景和道具仍严格跟随项目资产与设定。";
  return board.style_lock;
}

function labelRule() {
  const mode=(project.project_options||DEFAULT_PROJECT_OPTIONS).label_mode;
  if(mode==="ids_english")return "每格边缘仅保留宫格 ID、SHOT、REF 和极短英文制作注；不得生成剧情字幕、对白框或其他说明文字。";
  if(mode==="ids_project_language")return "每格边缘仅保留宫格 ID、SHOT、REF 和项目语言极短制作注；不得生成剧情字幕、对白框或其他说明文字。";
  return "每格画内仅在边缘保留宫格 ID、SHOT、REF；其他文字、字幕、对白与说明全部留给后期。";
}

function buildPanelPrompt(panel,board=currentBoard()) {
  const sources=(panel.source_ids||[]).join(",")||"未标注";
  const detail=panel.emotion_detail||analyzeEmotionDetail(panel);
  const emotionBlock=detail.detected?`\n情绪节拍：${detail.baseline} → ${detail.trigger} → ${detail.leak} → ${detail.mask} → ${detail.end_state}\n视觉焦点：${detail.visual_focus}；推荐景别：${detail.recommended_shot}；特写理由：${detail.focus_reason}\n情绪细节负面约束：${detail.negative_constraints}`:"";
  return `[STYLE LOCK]\n${resolvedStyle(board)}\n\n[VALIDATION MODE]\n${board.validation_mode}\n\n[${panel.id}｜${panel.shot_ref}｜REF:${panel.asset_refs}｜来源:${sources}｜${panel.start_state||"T?"}→${panel.end_state||"T?"}｜${panel.shot_purpose||"action"}｜${Number(panel.duration).toFixed(2)}s｜${panel.shot_size}｜${panel.angle||"平视"}｜${panel.camera_move}]\n本格观察状态：${panel.observation_state}；采样时刻约 ${Number(panel.sample_time||0).toFixed(2)} 秒；只呈现这一时刻，不重复其他格状态。\n画面动作与台词：${panel.action}\n人物锚定：${panel.character_anchor}\n场景锚定：${panel.scene_anchor}\n动作与表情表演：${panel.performance}${emotionBlock}\n表演来源：${panel.performance_provenance||"剧本确认"}\n表演链：${panel.performance_sequence||"保持起止状态连续"}\n台词/声音：${panel.dialogue_audio||"仅保持已确认环境声"}\n连续性：${panel.continuity}\n画内文字：${labelRule()}\n全局约束：${board.global_constraints}`;
}

function buildSegmentPrompt(board=currentBoard()) {
  const options=project.project_options||DEFAULT_PROJECT_OPTIONS;
  const mapping=board.panels.map(panel=>{const detail=panel.emotion_detail||analyzeEmotionDetail(panel);const focus=detail.detected?`；情绪焦点：${detail.visual_focus}；${detail.focus_reason}`:"";return `[${panel.id}｜${panel.shot_ref}｜REF:${panel.asset_refs}｜${panel.observation_state}｜${Number(panel.sample_time||0).toFixed(2)}s] ${panel.action}；${panel.shot_size}；${panel.angle||"平视"}；${panel.camera_move}；表演：${panel.performance}${focus}；声音：${panel.dialogue_audio||"仅保持已确认环境声"}`;}).join("\n");
  const gridRule=options.grid_mode==="black_optional"?"优先填满九格；确实无法从原事件推导的格可用黑底说明格，但不得复制状态或虚构剧情。":"必须填满九格；九格分别截取完整事件时间轴上的九个不重复观察状态，禁止重复动作终点或用相同画面凑格。";
  return `[STYLE LOCK]\n${resolvedStyle(board)}\n\n生成16:9、严格3×3九宫格，从左到右、从上到下。${board.validation_mode}。${gridRule}\n${labelRule()}\n线标仅用于制作信息：灰=动作/方向，蓝=镜头，青虚线=视线，黄=光源，紫=声音，绿=REF；未指定则不生成，禁止用长文字解释画面。\n\n${mapping}\n\n人物锚定：${board.panels[0].character_anchor}\n场景锚定：${board.panels[0].scene_anchor}\n全局约束：${board.global_constraints}`;
}

function buildFinalVideoPrompt(board=currentBoard()) {
  return board.video_master_prompt || "";
}
function renderVideoMaster(){
  el("videoMasterInput").value=currentBoard().video_master_prompt||"";
}
function saveVideoMaster(){
  const board=currentBoard(),next=el("videoMasterInput").value;
  if(next===(board.video_master_prompt||""))return;
  board.video_master_history=board.video_master_history||[];
  if(board.video_master_prompt)board.video_master_history.push({saved_at:new Date().toISOString(),prompt:board.video_master_prompt});
  board.video_master_prompt=next;board.completed=false;project.last_packaged_at="";
  board.panels.forEach(panel=>{panel.reverse_status="pending";panel.reverse_checked_at="";});
  renderSegmentSelect();renderPanelSelect();renderHitGrid();updateDerived();saveState();
}

function buildEditPrompt(panel,board=currentBoard()) {
  const index=board.panels.indexOf(panel), row=Math.floor(index/3)+1, col=index%3+1;
  const singlePanelStyle=resolvedStyle(board).replace(/16:9横构图[，；。]?/gi,"").replace(/严格3[×x]3网格[，；。]?/gi,"");
  return `Generate one standalone 16:9 replacement storyboard panel for ${panel.id}, originally row ${row}, column ${col}. Do not generate a 3x3 grid. The panel will be deterministically composited back into the existing storyboard.\n\n[STYLE LOCK - SINGLE PANEL]\n${singlePanelStyle}\n\n[${panel.id}｜${panel.shot_ref}｜REF:${panel.asset_refs}｜来源:${(panel.source_ids||[]).join(",")||"未标注"}｜${panel.start_state||"T?"}→${panel.end_state||"T?"}｜${panel.shot_purpose||"action"}｜${Number(panel.duration).toFixed(2)}s｜${panel.shot_size}｜${panel.angle||"平视"}｜${panel.camera_move}]\n画面动作与台词：${panel.action}\n人物锚定：${panel.character_anchor}\n场景锚定：${panel.scene_anchor}\n动作与表情表演：${panel.performance}\n表演来源：${panel.performance_provenance||"剧本确认"}\n表演链：${panel.performance_sequence||"保持起止状态连续"}\n台词/声音：${panel.dialogue_audio||"仅保持已确认环境声"}\n连续性：${panel.continuity}\n全局约束：${board.global_constraints}\n\n期望：${panel.expected||"匹配本格Prompt与REF"}\n实际偏差：${panel.actual||"未填写"}\n仅修改：${panel.change||"修正本格以匹配Prompt"}\n\n只输出这一格的完整16:9画面；保留同一画风、人物身份、空间轴线、光线、道具状态和连续性。左上保留${panel.id}，左下保留${panel.shot_ref}，右下保留绿色REF:${panel.asset_refs}。不得生成其他宫格、额外边框、字幕、对白框、Logo或水印。`;
}

function syncFields(){
  const board=currentBoard(),panel=currentPanel();
  const before=JSON.stringify(panel);
  panel.duration=Math.max(.1,Number(fields.duration.value)||.1);
  Object.entries(fields).forEach(([key,field])=>{if(key!=="duration")panel[key]=field.value.trim();});
  if(JSON.stringify(panel)!==before){panel.reverse_status="pending";panel.reverse_checked_at="";board.completed=false;project.last_packaged_at="";refreshEmotionMetadata(board,(project.project_options||DEFAULT_PROJECT_OPTIONS).emotion_closeup_mode,false);deriveEventTimeline(board);renderEventTimeline();saveState();}
  updateDerived();
}
function loadFields(){ const panel=currentPanel(); Object.entries(fields).forEach(([key,field])=>{field.value=panel[key]??"";}); el("panelSelect").value=panel.id; updateDerived(); drawCrop(); }

function updateDerived(){
  const board=currentBoard(), panel=currentPanel(), index=project.segments.indexOf(board);
  const reverseAccepted=board.panels.filter(item=>item.reverse_status==="accepted").length, reverseComplete=reverseAccepted===board.panels.length;
  el("scriptName").textContent=project.script_name||"未命名"; el("segmentId").textContent=board.segment_id; el("currentPanel").textContent=panel.id; el("totalDuration").textContent=`${totalDuration(board).toFixed(2)}s`; el("completionState").textContent=board.completed?"已完成":`成图反查 ${reverseAccepted}/${board.panels.length}`;
  el("segmentProgress").textContent=`${index+1} / ${project.segments.length}`; el("toggleComplete").textContent=board.completed?"撤销我的完成确认":(reverseComplete?"完成最后核查并进入结果输出":`成图反查 ${reverseAccepted}/${board.panels.length}`); el("panelPrompt").textContent=buildPanelPrompt(panel,board); el("segmentPrompt").textContent=buildSegmentPrompt(board); el("videoPrompt").textContent=board.video_master_prompt?buildFinalVideoPrompt(board):"本段仍在9宫调试；请逐格查看成图并反向核对对应 Prompt。九格全部由你标记为“对应通过”后，才开放确认主稿的最终导出。"; el("copyVideoPrompt").disabled=!board.video_master_prompt; el("editPrompt").textContent=panel.edit_prompt||"尚未生成"; el("generationState").textContent=board.image_data_url&&board.last_replaced_panel?`${board.last_replaced_panel} 已替换 · 需重新反查`:(board.image_data_url?"九宫格已回填 · 执行成图反查":"Prompt已准备，等待$imagegen");
  const hasEdit=Boolean(panel.expected||panel.actual||panel.change); el("editPanel").classList.toggle("ready",hasEdit); el("editStatus").textContent=hasEdit?`${panel.id} 已预填`:`${panel.id} 待填写`;
  el("reverseProgress").textContent=`${reverseAccepted} / ${board.panels.length} 已通过`;
  const evidence=(board.events||[]).find(event=>(panel.event_ids||[]).includes(event.id));
  el("currentEventEvidence").textContent=evidence?`${evidence.id}｜${evidence.start.toFixed(2)}–${evidence.end.toFixed(2)}s｜${evidence.shot_ref}｜${evidence.observation_state}：${evidence.body}`:"当前格尚无事件时间轴证据";
  const emotion=panel.emotion_detail||analyzeEmotionDetail(panel),mode=(project.project_options||DEFAULT_PROJECT_OPTIONS).emotion_closeup_mode;
  el("emotionFocusBadge").textContent=mode==="off"?"已关闭":panel.closeup_applied?`已应用 ${panel.shot_size}`:emotion.eligible?`建议 ${emotion.recommended_shot}`:emotion.detected?"保留空间景别":"保持原景别";
  el("emotionBeatText").textContent=emotion.detected?`情绪节拍：${emotion.baseline} → ${emotion.trigger} → ${emotion.leak} → ${emotion.mask} → ${emotion.end_state}`:"当前格没有足够的微表情或微动作证据，不强行增加特写。";
  el("emotionFocusReason").textContent=`视觉焦点：${emotion.visual_focus}。${emotion.focus_reason}`;
  el("reverseValidation").classList.toggle("accepted",panel.reverse_status==="accepted");el("reverseValidation").classList.toggle("revise",panel.reverse_status==="revise");
  document.querySelectorAll("[data-reverse-status]").forEach(button=>button.classList.toggle("active",button.dataset.reverseStatus===panel.reverse_status));
  el("reverseGateMessage").textContent=reverseComplete?"九格成图与提示词已全部对应通过；现在可由你完成 SEG 确认。":`还有 ${board.panels.length-reverseAccepted} 格未通过最终反查；换图、修图或改 Prompt 会使对应格回到待反查。`;
  renderPipeline();
}

function renderPipeline(){
  const anyImage=project.segments.some(item=>item.image_data_url), anyReverse=project.segments.some(item=>item.panels.some(panel=>panel.reverse_status!=="pending")), allDone=project.segments.length>0&&project.segments.every(item=>item.completed&&item.image_data_url&&item.panels.every(panel=>panel.reverse_status==="accepted")), stage=allDone?7:(anyReverse?6:(anyImage?5:project.pipeline_stage||1));
  el("exportReviewHtml").disabled=false;
  document.querySelectorAll("[data-stage]").forEach((item,index)=>{item.classList.toggle("done",index+1<stage);item.classList.toggle("active",index+1===stage);});
  const status=stage===1?"剧本已载入":stage===2?"正在自动拆段":stage===3?"九格Prompt已准备，等待$imagegen":stage===4?"九宫格已回填":stage===5?"逐格调整成图与提示词":stage===6?"最后核查：成图反向对应提示词":project.last_packaged_at?"最终成果已输出":"成图反查已完成，请选择最终交付格式";
  el("pipelineStatus").textContent=status;
  el("resultOutputStage").hidden=!allDone;
}

function renderSegmentSelect(){ el("segmentSelect").innerHTML=project.segments.map(item=>{const passed=item.panels.filter(panel=>panel.reverse_status==="accepted").length;return `<option value="${item.segment_id}">${item.segment_id} · ${escapeHtml(item.title||item.source_range||"段落")} · 反查${passed}/${item.panels.length}${item.completed?" · 已完成":""}</option>`;}).join(""); el("segmentSelect").value=activeSegmentId; }
function renderPanelSelect(){ const board=currentBoard(); el("panelSelect").innerHTML=board.panels.map(panel=>`<option value="${panel.id}">${panel.reverse_status==="accepted"?"✓":panel.reverse_status==="revise"?"!":"·"} ${panel.id} · ${escapeHtml(panel.shot_ref)} · ${escapeHtml(panel.asset_refs)}</option>`).join(""); }
function renderHitGrid(){ const board=currentBoard(); el("hitGrid").innerHTML=board.panels.map((panel,index)=>`<button type="button" data-index="${index}" class="${panel.id===activePanelId?"active ":""}reverse-${panel.reverse_status||"pending"}">${panel.id}${panel.reverse_status==="accepted"?" ✓":panel.reverse_status==="revise"?" !":""}</button>`).join(""); el("hitGrid").querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>selectPanel(board.panels[Number(button.dataset.index)].id))); }
function renderLookup(query=""){ const board=currentBoard(), normalized=query.trim().toLowerCase(); const matches=board.panels.filter(panel=>!normalized||[panel.id,panel.shot_ref,panel.asset_refs,panel.action,panel.performance,buildPanelPrompt(panel,board)].join(" ").toLowerCase().includes(normalized)); el("lookupResults").innerHTML=matches.map(panel=>`<button type="button" data-panel="${panel.id}"><b>${panel.id}</b><span>${escapeHtml(panel.shot_ref)} · ${escapeHtml(panel.asset_refs)}</span></button>`).join("")||`<span class="muted">没有匹配结果</span>`; el("lookupResults").querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>selectPanel(button.dataset.panel))); }
function renderVersions(){ const board=currentBoard(); el("versionList").innerHTML=board.versions.length?board.versions.slice().reverse().map(version=>`<button type="button" class="version-item" data-version="${version.id}"><b>${escapeHtml(version.id)}</b><span>${escapeHtml(version.panel_id)} · ${Number(version.duration).toFixed(2)}s · ${escapeHtml(version.shot_size)}</span></button>`).join(""):`<p class="muted">当前SEG尚未保存逐格版本。</p>`; el("versionList").querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>loadVersion(button.dataset.version))); }

function renderProjectOptions(){
  const options=project.project_options||DEFAULT_PROJECT_OPTIONS;
  Object.entries(optionFields).forEach(([key,field])=>{field.value=options[key]??DEFAULT_PROJECT_OPTIONS[key];});
  el("customStoryboardStyleInput").disabled=options.style_mode!=="custom";
  const labels={full_unique:"九格不重复",black_optional:"允许黑底说明格",project:"跟随项目",graphite:"灰阶铅笔",custom:"自定义",ids_only:"仅ID/SHOT/REF",ids_english:"附英文短注",ids_project_language:"附项目语言短注",ninegrid:"九宫核心",director:"导演调度",full:"全链路",continuous:"连续时间轴",platform:"平台专用",enhanced:"剧情驱动加强特写",suggest:"仅建议特写",off:"关闭情绪分析"};
  el("projectOptionSummary").textContent=`当前：${labels[options.grid_mode]} · ${labels[options.style_mode]} · ${labels[options.label_mode]} · ${labels[options.workflow_mode]} · ${labels[options.video_mode]} · ${labels[options.emotion_closeup_mode]}`;
}

function applyProjectOptions(){
  const next={};Object.entries(optionFields).forEach(([key,field])=>{next[key]=field.value.trim();});
  project.project_options={...DEFAULT_PROJECT_OPTIONS,...next};
  project.segments.forEach(board=>{refreshEmotionMetadata(board,project.project_options.emotion_closeup_mode,true);deriveEventTimeline(board);board.completed=false;board.panels.forEach(panel=>{panel.reverse_status="pending";panel.reverse_checked_at="";});});
  project.last_packaged_at="";renderAll();
}

function renderEventTimeline(){
  const board=currentBoard();deriveEventTimeline(board);
  el("eventTimelineList").innerHTML=(board.events||[]).map(event=>`<article class="timeline-item"><b>${escapeHtml(event.id)} · ${Number(event.start).toFixed(2)}–${Number(event.end).toFixed(2)}s · ${escapeHtml(event.shot_ref)}</b><span>${escapeHtml(event.observation_state)}｜${escapeHtml(event.body)}</span></article>`).join("");
}

function renderImage(){ const board=currentBoard(), hasImage=Boolean(board.image_data_url), image=el("storyboardImage"); el("imageStage").classList.toggle("has-image",hasImage); el("visualColumn").classList.toggle("has-image",hasImage); el("downloadCurrent").disabled=!hasImage; el("downloadAll").disabled=!hasImage; el("downloadBoard").disabled=!hasImage; el("panelReplaceInput").disabled=!hasImage; el("replacePanelLabel").classList.toggle("disabled",!hasImage); if(hasImage){if(image.getAttribute("src")!==board.image_data_url)image.src=board.image_data_url;if(image.complete&&image.naturalWidth)requestAnimationFrame(drawCrop);}else{image.removeAttribute("src");el("cropMeta").textContent=`${board.segment_id}尚未回填九宫格图片`; const canvas=el("cropCanvas");canvas.getContext("2d").clearRect(0,0,canvas.width,canvas.height);}}
function renderAll(){ renderVideoMaster(); renderProjectOptions(); renderSegmentSelect(); renderPanelSelect(); renderHitGrid(); renderLookup(el("lookupQuery").value||""); renderVersions(); renderEventTimeline(); renderImage(); loadFields(); saveState(); }

function selectPanel(panelId){ syncFields(); activePanelId=panelId; renderHitGrid(); loadFields(); }
function selectSegment(segmentId){ syncFields(); activeSegmentId=segmentId; activePanelId=currentBoard().panels[0].id; el("lookupQuery").value=""; renderAll(); }
function setReverseStatus(status){
  if(!currentBoard().image_data_url){alert("请先回填九宫格成图，再进行提示词反查。");return;}
  syncFields();const board=currentBoard(),panel=currentPanel();panel.reverse_status=status;panel.reverse_checked_at=status==="pending"?"":new Date().toISOString();board.completed=false;project.last_packaged_at="";renderSegmentSelect();renderPanelSelect();renderHitGrid();updateDerived();saveState();
}
function selectNextReversePending(){
  syncFields();const board=currentBoard(),start=board.panels.findIndex(panel=>panel.id===activePanelId);let target=null;
  for(let offset=1;offset<=board.panels.length;offset++){const candidate=board.panels[(start+offset)%board.panels.length];if(candidate.reverse_status!=="accepted"){target=candidate;break;}}
  if(target)selectPanel(target.id);else alert("本段九格已经全部通过成图反查，可以完成最后确认。");
}

function drawCrop(){ const board=currentBoard(),image=el("storyboardImage"),canvas=el("cropCanvas"); if(!board.image_data_url||!image.complete||!image.naturalWidth)return; const index=board.panels.findIndex(panel=>panel.id===activePanelId), width=image.naturalWidth/3,height=image.naturalHeight/3,col=index%3,row=Math.floor(index/3); canvas.width=Math.floor(width);canvas.height=Math.floor(height);const context=canvas.getContext("2d");context.clearRect(0,0,canvas.width,canvas.height);context.drawImage(image,col*width,row*height,width,height,0,0,canvas.width,canvas.height);el("cropMeta").textContent=`${activePanelId} · 第${row+1}行第${col+1}列 · ${canvas.width}×${canvas.height}px`;}

let saveTimer;
function saveState(){
  try{
    const lightweight=JSON.parse(JSON.stringify(project));
    lightweight.segments.forEach(item=>{item.image_data_url="";});
    localStorage.setItem(STORAGE_KEY,JSON.stringify(lightweight));
  }catch(error){console.warn("Could not persist lightweight project",error);}
  clearTimeout(saveTimer);
  saveTimer=setTimeout(()=>writeSavedProject(project).catch(error=>console.warn("Could not persist full project",error)),500);
}
function saveVersion(){syncFields();const board=currentBoard(),panel=currentPanel();panel.edit_prompt=buildEditPrompt(panel,board);const serial=board.versions.filter(item=>item.panel_id===panel.id).length+1;board.versions.push({...JSON.parse(JSON.stringify(panel)),id:`${panel.id}-R${String(serial).padStart(2,"0")}`,panel_id:panel.id,panel_prompt:buildPanelPrompt(panel,board),segment_duration:totalDuration(board),storyboard_image:board.image_name||"prompt-only",saved_at:new Date().toISOString()});saveState();renderVersions();updateDerived();}
function loadVersion(versionId){const board=currentBoard(),version=board.versions.find(item=>item.id===versionId);if(!version)return;const panel=board.panels.find(item=>item.id===version.panel_id);["shot_ref","asset_refs","duration","shot_size","camera_move","action","character_anchor","scene_anchor","performance","continuity","expected","actual","change","edit_prompt"].forEach(key=>{panel[key]=version[key];});panel.reverse_status="pending";panel.reverse_checked_at="";board.completed=false;refreshEmotionMetadata(board,(project.project_options||DEFAULT_PROJECT_OPTIONS).emotion_closeup_mode,false);activePanelId=panel.id;renderHitGrid();loadFields();}

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
  context.drawImage(replacement,sx,sy,sw,sh,col*cellWidth,row*cellHeight,cellWidth,cellHeight);context.strokeStyle="#111";context.lineWidth=Math.max(2,canvas.width/800);context.strokeRect(col*cellWidth,row*cellHeight,cellWidth,cellHeight);
  board.image_revision=Number(board.image_revision||1)+1;board.image_name=`${board.segment_id}-storyboard-v${String(board.image_revision).padStart(2,"0")}.png`;board.image_data_url=canvas.toDataURL("image/png");board.last_replaced_panel=activePanelId;board.generation_state="panel_replaced";currentPanel().reverse_status="pending";currentPanel().reverse_checked_at="";board.completed=false;project.last_packaged_at="";renderImage();renderPanelSelect();renderHitGrid();updateDerived();drawCrop();saveState();
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
function reviewPanelCrop(image,index){
  const canvas=document.createElement("canvas"),context=canvas.getContext("2d");
  const sourceWidth=image.naturalWidth/3,sourceHeight=image.naturalHeight/3;
  canvas.width=Math.round(sourceWidth);canvas.height=Math.round(sourceHeight);
  context.drawImage(image,(index%3)*sourceWidth,Math.floor(index/3)*sourceHeight,sourceWidth,sourceHeight,0,0,canvas.width,canvas.height);
  return canvas.toDataURL("image/png");
}
async function buildReviewHtml(snapshot){
  const segments=[];
  for(const board of snapshot.segments){
    const image=board.image_data_url?await loadImageSource(board.image_data_url):null;
    const panelCards=board.panels.map((panel,index)=>{
      const panelImage=image?`<img class="panel-image" src="${reviewPanelCrop(image,index)}" alt="${escapeHtml(panel.id)} 当前九宫格裁切图">`:`<div class="no-image">本段尚未回填图片</div>`;
      const note=[panel.actual&&`实际偏差：${panel.actual}`,panel.change&&`建议修改：${panel.change}`].filter(Boolean).join("\n");
      return `<article class="panel" data-panel="${escapeHtml(panel.id)}"><div class="panel-top"><b>${escapeHtml(panel.id)}</b><span>${escapeHtml(panel.shot_ref||"")} · ${Number(panel.duration||0).toFixed(2)}s</span></div>${panelImage}<div class="panel-content"><p><strong>资产 REF</strong> ${escapeHtml(panel.asset_refs||"未标注")}</p><p><strong>预期画面</strong> ${escapeHtml(panel.expected||panel.action||"未填写")}</p><details><summary>查看对应单格 Prompt</summary><pre>${escapeHtml(buildPanelPrompt(panel,board))}</pre></details><label>我的校验意见<textarea data-note="${escapeHtml(panel.id)}" placeholder="填写需修改的画面或提示词">${escapeHtml(note)}</textarea></label><div class="choices" data-choice="${escapeHtml(panel.id)}"><button type="button" data-value="pending" class="active">待校验</button><button type="button" data-value="accepted">通过</button><button type="button" data-value="revise">需修改</button></div></div></article>`;
    }).join("");
    segments.push(`<section class="segment"><div class="segment-title"><div><small>${escapeHtml(board.segment_id)}</small><h2>${escapeHtml(board.title||board.segment_id)}</h2></div><span>${totalDuration(board).toFixed(2)}s · ${board.completed?"工作台已确认":"等待用户校验"}</span></div><p class="source">${escapeHtml(board.source_range||"")}</p>${image?`<img class="board-image" src="${board.image_data_url}" alt="${escapeHtml(board.segment_id)} 九宫格总图">`:`<p class="no-image">本段尚未回填九宫格图片</p>`}<div class="panel-grid">${panelCards}</div></section>`);
  }
  const stem=snapshot.segments.length===1?cleanFileStem(snapshot.segments[0].segment_id):cleanFileStem(snapshot.script_name);
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escapeHtml(snapshot.script_name||"九宫项目")} · 九宫校验</title><style>
  :root{--bg:#f2efe8;--paper:#fffdf8;--ink:#20252a;--muted:#65707a;--line:#d8d0c0;--accent:#0f766e}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.6 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}main{width:min(1480px,calc(100% - 24px));margin:24px auto 64px}h1{font-size:28px;margin:0 0 8px}h2{font-size:20px;margin:3px 0}p{margin:8px 0}.hero,.segment{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:20px;margin-bottom:16px}.hero p,.source{color:var(--muted)}.notice{padding:10px 12px;border-radius:8px;background:#fff3d7;border:1px solid #d9bd7a}.export{margin-top:10px;padding:8px 12px;border:0;border-radius:7px;background:var(--accent);color:#fff;cursor:pointer}.segment-title{display:flex;justify-content:space-between;align-items:center;gap:12px}.segment-title small{color:var(--accent);font-weight:700}.segment-title span{color:var(--muted);white-space:nowrap}.board-image{display:block;width:100%;height:auto;border-radius:8px;margin:12px 0}.panel-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:16px}.panel{min-width:0;border:1px solid var(--line);border-radius:9px;overflow:hidden;background:#fff}.panel-top{display:flex;justify-content:space-between;gap:6px;padding:9px 11px}.panel-top b{color:var(--accent)}.panel-top span{font-size:12px;color:var(--muted);text-align:right}.panel-image{display:block;width:100%;aspect-ratio:16/9;object-fit:cover}.panel-content{padding:10px 11px}.panel-content p{font-size:12px}.panel-content strong{display:block;color:var(--accent)}details{margin:10px 0;padding:8px;border:1px solid var(--line);border-radius:6px}summary{cursor:pointer;font-weight:700}pre{white-space:pre-wrap;word-break:break-word;max-height:350px;overflow:auto;font:12px/1.6 ui-monospace,SFMono-Regular,monospace;color:#36434b}.panel-content label{display:grid;gap:5px;font-size:12px;font-weight:700}textarea{width:100%;min-height:80px;resize:vertical;padding:8px;border:1px solid var(--line);border-radius:6px;font:inherit}.choices{display:flex;gap:5px;flex-wrap:wrap;margin-top:8px}.choices button{padding:5px 8px;border:1px solid var(--line);border-radius:6px;background:#fff;cursor:pointer}.choices button.active{border-color:var(--accent);background:#e1f3ee;color:var(--accent);font-weight:700}.no-image{padding:20px;background:#f5f3ee;color:var(--muted);text-align:center}.footer{color:var(--muted);font-size:12px}@media(max-width:1050px){.panel-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:650px){.panel-grid{grid-template-columns:1fr}.segment-title{align-items:flex-start;flex-direction:column}}
  </style></head><body data-export-stem="${escapeHtml(stem)}"><main><section class="hero"><h1>${escapeHtml(snapshot.script_name||"九宫项目")} · 校验 HTML</h1><p class="notice">这是九宫格工作台的校验文件。每格由你自行核对；本页的选择不会把工作项目标记为已完成，也不代替正式结果输出。</p><p>共 ${snapshot.segments.length} 段；九宫图和逐格裁切图已内嵌，可离线浏览。请填写意见并导出校验记录。</p><button id="exportNotes" class="export" type="button">导出我的校验记录 JSON</button></section>${segments.join("")}<p class="footer">来源：九宫格工作台 · 导出时间：${escapeHtml(new Date().toLocaleString("zh-CN"))}</p></main><script>
  (function(){var key="nine-grid-review:"+document.title;var saved={};try{saved=JSON.parse(localStorage.getItem(key)||"{}")}catch(e){}function persist(){try{localStorage.setItem(key,JSON.stringify(saved))}catch(e){}}document.querySelectorAll("[data-panel]").forEach(function(card){var id=card.getAttribute("data-panel"),group=card.querySelector("[data-choice]"),note=card.querySelector("[data-note]");if(saved[id]){note.value=saved[id].note||note.value;group.querySelectorAll("button").forEach(function(btn){btn.classList.toggle("active",btn.dataset.value===(saved[id].status||"pending"))})}note.addEventListener("input",function(){saved[id]={status:saved[id]&&saved[id].status||"pending",note:note.value};persist()});group.querySelectorAll("button").forEach(function(btn){btn.addEventListener("click",function(){saved[id]={status:btn.dataset.value,note:note.value};group.querySelectorAll("button").forEach(function(item){item.classList.toggle("active",item===btn)});persist()})})});document.getElementById("exportNotes").addEventListener("click",function(){var panels=Array.from(document.querySelectorAll("[data-panel]")).map(function(card){var id=card.getAttribute("data-panel"),group=card.querySelector("[data-choice]"),active=group.querySelector("button.active");return{id:id,status:active?active.dataset.value:"pending",note:card.querySelector("[data-note]").value}});var blob=new Blob([JSON.stringify({format:"nine-grid-user-review",exported_at:new Date().toISOString(),panels:panels},null,2)],{type:"application/json;charset=utf-8"}),url=URL.createObjectURL(blob),link=document.createElement("a");link.href=url;link.download=document.body.dataset.exportStem+"-用户校验记录.json";link.click();setTimeout(function(){URL.revokeObjectURL(url)},1000)})})();
  </script></body></html>`;
}
async function exportReviewHtml(){
  syncFields();
  const button=el("exportReviewHtml");button.disabled=true;button.textContent="正在保存当前页面…";
  try{
    const snapshot=await portableProject();
    const cssNode=document.querySelector("style[data-nine-grid-inline-css]");
    const cssLink=document.querySelector('link[rel="stylesheet"][href*="nine-grid.css"]');
    const appNode=document.querySelector("script[data-nine-grid-app]");
    const cssText=cssNode?cssNode.textContent:await fetch(cssLink.href,{cache:"no-store"}).then(response=>{if(!response.ok)throw new Error(`样式读取失败：HTTP ${response.status}`);return response.text();});
    const appText=appNode?.src?await fetch(appNode.src,{cache:"no-store"}).then(response=>{if(!response.ok)throw new Error(`程序读取失败：HTTP ${response.status}`);return response.text();}):appNode?.textContent;
    if(!appText)throw new Error("未找到工作台程序");

    const workspace={
      format:"nine-grid-workspace-html-v1",
      saved_at:new Date().toISOString(),
      active_segment_id:activeSegmentId,
      active_panel_id:activePanelId,
      project:snapshot
    };
    const clone=document.documentElement.cloneNode(true);
    clone.querySelectorAll('link[rel="stylesheet"][href*="nine-grid.css"],style[data-nine-grid-inline-css],script[data-nine-grid-app],#embeddedWorkspace').forEach(node=>node.remove());
    clone.querySelectorAll("input[type=file]").forEach(input=>input.value="");
    const clonedSaveButton=clone.querySelector("#exportReviewHtml");
    if(clonedSaveButton){clonedSaveButton.textContent="保存当前页面 HTML";clonedSaveButton.disabled=false;}
    const clonedStoryboard=clone.querySelector("#storyboardImage"),activeSnapshotBoard=snapshot.segments.find(item=>item.segment_id===activeSegmentId)||snapshot.segments[0];
    if(clonedStoryboard){if(activeSnapshotBoard?.image_data_url)clonedStoryboard.src=activeSnapshotBoard.image_data_url;else clonedStoryboard.removeAttribute("src");}
    const style=document.createElement("style");style.dataset.nineGridInlineCss="";style.textContent=cssText;clone.querySelector("head").appendChild(style);
    const embedded=document.createElement("script");embedded.id="embeddedWorkspace";embedded.type="application/json";embedded.textContent=JSON.stringify(workspace).replace(/<\/script/gi,"<\\/script");clone.querySelector("body").appendChild(embedded);
    const app=document.createElement("script");app.dataset.nineGridApp="";app.textContent=appText.replace(/<\/script/gi,"<\\/script");clone.querySelector("body").appendChild(app);
    const html=`<!doctype html>\n${clone.outerHTML}`;
    const stem=snapshot.segments.length===1?cleanFileStem(snapshot.segments[0].segment_id):cleanFileStem(snapshot.script_name);
    downloadBlob(new Blob([html],{type:"text/html;charset=utf-8"}),`${stem}-九宫工作台页面.html`);
  }catch(error){alert(`保存当前页面失败：${error.message}`);}
  finally{button.textContent="保存当前页面 HTML";renderPipeline();}
}
function buildResultsHtml(payload){
  const segmentCards=payload.segments.map(segment=>{
    const rows=segment.storyboard_reference.panel_map.map(panel=>`<tr><td>${escapeHtml(panel.panel_id)}</td><td>${escapeHtml(panel.shot_ref)}</td><td>${escapeHtml(panel.asset_refs)}</td><td>${Number(panel.duration).toFixed(2)}s</td><td>${escapeHtml(panel.observation_state||"")}<br>${escapeHtml(panel.meaning)}</td><td>${escapeHtml(panel.performance)}</td><td>${panel.reverse_validation?.status==="accepted"?"双层反查通过":"未通过"}${panel.reverse_validation?.image_to_script?`<br>成图→剧本：${escapeHtml(panel.reverse_validation.image_to_script)}`:""}${panel.reverse_validation?.script_to_prompt?`<br>剧本→Prompt：${escapeHtml(panel.reverse_validation.script_to_prompt)}`:""}</td></tr>`).join("");
    const notes=segment.change_notes.length?`<details><summary>修改记录（${segment.change_notes.length}）</summary>${segment.change_notes.map(note=>`<article class="note"><b>${escapeHtml(note.panel_id)}</b><p><strong>期望：</strong>${escapeHtml(note.expected||"—")}</p><p><strong>偏差：</strong>${escapeHtml(note.actual||"—")}</p><p><strong>修改：</strong>${escapeHtml(note.change||"—")}</p></article>`).join("")}</details>`:"";
    return `<section class="segment"><header><div><span>${escapeHtml(segment.segment_id)}</span><h2>${escapeHtml(segment.title||segment.segment_id)}</h2></div><em>${Number(segment.segment_duration).toFixed(2)} 秒</em></header><p class="source">来源：${escapeHtml(segment.source_range||"未标注")}</p><img src="${escapeHtml(segment.storyboard_reference.image_data_url)}" alt="${escapeHtml(segment.segment_id)} 九宫格故事板"><h3>最终视频生成 Prompt</h3><pre>${escapeHtml(segment.final_video_prompt)}</pre><h3>逐格对照与最终反查</h3><div class="table-wrap"><table><thead><tr><th>宫格</th><th>SHOT</th><th>资产 REF</th><th>时长</th><th>画面含义</th><th>表演</th><th>成图↔提示词</th></tr></thead><tbody>${rows}</tbody></table></div>${notes}</section>`;
  }).join("");
  return `<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escapeHtml(payload.script_name)} · 九宫格成果</title><style>:root{--bg:#f2efe8;--paper:#fffdf8;--ink:#20252a;--muted:#65707a;--line:#d8d0c0;--accent:#0f766e}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.65 Inter,"PingFang SC","Microsoft YaHei",sans-serif}main{width:min(1180px,calc(100% - 32px));margin:36px auto 64px}.hero,.segment{background:var(--paper);border:1px solid var(--line);border-radius:14px;box-shadow:0 8px 26px #352b2010}.hero{padding:26px;margin-bottom:20px}.hero h1{margin:4px 0 8px;font-size:28px}.hero p,.source{color:var(--muted)}.meta{display:flex;gap:10px;flex-wrap:wrap}.meta span,.segment header span{padding:4px 9px;border-radius:999px;background:#dff3ef;color:var(--accent);font-size:12px;font-weight:700}.segment{padding:22px;margin-top:18px}.segment header{display:flex;align-items:center;justify-content:space-between;gap:16px}.segment header div{display:flex;align-items:center;gap:10px}.segment h2,.segment h3{margin:0}.segment h2{font-size:20px}.segment h3{margin-top:20px;font-size:15px}.segment header em{color:var(--accent);font-style:normal;font-weight:700}.segment img{display:block;width:100%;height:auto;margin-top:14px;border-radius:10px;background:#161616}pre{margin:8px 0 0;padding:14px;overflow:auto;border-radius:9px;background:#f4f7f5;color:#35423f;white-space:pre-wrap;word-break:break-word;font:12px/1.65 ui-monospace,SFMono-Regular,Menlo,monospace}.table-wrap{overflow:auto;margin-top:8px}table{width:100%;border-collapse:collapse;font-size:12px}th,td{padding:9px 10px;border:1px solid var(--line);text-align:left;vertical-align:top}th{background:#f4f1ea;white-space:nowrap}details{margin-top:16px;padding:10px;border:1px solid var(--line);border-radius:8px}.note{padding:8px 0;border-top:1px solid var(--line)}.note:first-of-type{margin-top:8px}.note p{margin:3px 0}@media(max-width:700px){main{width:min(100% - 20px,1180px);margin-top:10px}.hero,.segment{padding:15px}.segment header,.segment header div{align-items:flex-start;flex-direction:column;gap:6px}}</style></head><body><main><section class="hero"><div class="meta"><span>九宫格成果</span><span>${payload.completed_segment_count} 个已完成 SEG</span></div><h1>${escapeHtml(payload.script_name||"未命名项目")}</h1><p>导出时间：${escapeHtml(new Date(payload.exported_at).toLocaleString("zh-CN"))}。本网页为离线浏览包，九宫格图片、逐格对照和最终视频 Prompt 均已内嵌。</p></section>${segmentCards}</main></body></html>`;
}

async function exportProject(){
  syncFields();
  if(project.segments.some(board=>!String(board.video_master_prompt||" ").trim())){alert("缺少完整视频主稿。旧项目可继续编辑，但不能从九格重建最终正文；请逐段保存完整主稿。");return;}
  const reviewComplete=project.segments.length>0&&project.segments.every(board=>board.completed&&board.image_data_url&&board.panels.every(panel=>panel.reverse_status==="accepted"));
  if(!reviewComplete){alert("最终核查尚未完成；请逐格查看成图，反向核对对应 Prompt，并将九格全部标记为“对应通过”，再进入结果输出。");return;}
  let snapshot;
  try{snapshot=await portableProject();}catch(error){alert(`结果输出失败：${error.message}`);return;}
  const readyBoards=snapshot.segments.filter(board=>board.completed&&board.image_data_url);
  const segments=readyBoards.map((board)=>{
    const panelMap=board.panels.map(panel=>({panel_id:panel.id,shot_ref:panel.shot_ref,asset_refs:panel.asset_refs,duration:panel.duration,observation_state:panel.observation_state,sample_time:panel.sample_time,meaning:panel.action,performance:panel.performance,emotion_detail:panel.emotion_detail,reverse_validation:{status:panel.reverse_status,image_to_script:panel.reverse_note,script_to_prompt:panel.reverse_prompt_note,checked_at:panel.reverse_checked_at}}));
    const changeNotes=board.panels.filter(panel=>panel.expected||panel.actual||panel.change).map(panel=>({panel_id:panel.id,expected:panel.expected,actual:panel.actual,change:panel.change}));
    return {segment_id:board.segment_id,title:board.title,source_range:board.source_range,segment_duration:totalDuration(board),completed:board.completed,generation_state:board.generation_state,event_timeline:board.events,reverse_validation_gate:"9/9 panels passed image→script/timeline→prompt review by user",final_prompt_type:"video_generation",final_video_prompt:buildFinalVideoPrompt(board),video_master_history:board.video_master_history||[],storyboard_reference:{image_name:board.image_name,image_data_url:board.image_data_url,panel_map:panelMap},change_notes:changeNotes};
  });
  const payload={package_type:"open-cowart-user-approved-video-results-with-storyboards",trigger_command:"结果输出",script_name:project.script_name,project_options:project.project_options,segments,exported_at:new Date().toISOString(),completed_segment_count:segments.length,review_gate:"本轮全部SEG均已完成逐格成图→剧本/时间轴→Prompt双层反查，9/9格由用户明确标记对应通过并确认完成",package_rule:"只输出由用户完成成图反查并逐段确认的SEG；最终Prompt为视频生成Prompt；九宫格作为人工验证资料，不自动作为实际投喂参考图；不交付草稿、未经用户确认的内容、九宫格作图Prompt或工具文件。"};
  project.last_packaged_at=payload.exported_at;
  if(el("exportFormat").value==="html"){
    downloadBlob(new Blob([buildResultsHtml(payload)],{type:"text/html;charset=utf-8"}),`${cleanFileStem(project.script_name)}-九宫格成果浏览.html`);
    renderPipeline();saveState();return;
  }
  downloadBlob(new Blob([JSON.stringify(payload,null,2)],{type:"application/json"}),`${(project.script_name||"项目").replace(/\.[^.]+$/,"")}-已完成视频提示词+九宫格成果包.json`);
  renderPipeline();saveState();
}
async function copyText(value){try{await navigator.clipboard.writeText(value);}catch{const box=document.createElement("textarea");box.value=value;document.body.appendChild(box);box.select();document.execCommand("copy");box.remove();}}

async function importScriptText(text,name){ if(!text.trim()){alert("剧本内容为空");return;} project=normalizeReverseValidation(parseScriptToProject(text,name));project.segments.forEach(board=>refreshEmotionMetadata(board,project.project_options.emotion_closeup_mode,true));activeSegmentId=project.segments[0].segment_id;activePanelId=project.segments[0].panels[0].id;el("scriptTextInput").value=text;renderAll(); }

el("scriptFileInput").addEventListener("change",async()=>{const file=el("scriptFileInput").files?.[0];if(file)await importScriptText(await file.text(),file.name);});
el("parseScriptButton").addEventListener("click",()=>importScriptText(el("scriptTextInput").value,"粘贴剧本"));
el("applyProjectOptions").addEventListener("click",applyProjectOptions);
el("styleModeInput").addEventListener("change",()=>{el("customStoryboardStyleInput").disabled=el("styleModeInput").value!=="custom";});
el("segmentSelect").addEventListener("change",event=>selectSegment(event.target.value));
el("previousSegment").addEventListener("click",()=>{const index=project.segments.findIndex(item=>item.segment_id===activeSegmentId);if(index>0)selectSegment(project.segments[index-1].segment_id);});
el("videoMasterInput").addEventListener("change",saveVideoMaster);
el("saveVideoMaster").addEventListener("click",saveVideoMaster);
el("nextSegment").addEventListener("click",()=>{const index=project.segments.findIndex(item=>item.segment_id===activeSegmentId);if(index<project.segments.length-1)selectSegment(project.segments[index+1].segment_id);});
el("toggleComplete").addEventListener("click",()=>{const board=currentBoard();if(!board.completed&&!String(board.video_master_prompt||" ").trim()){alert("请先保存并核对完整视频主稿，包括未入格事件、对白/OS和转场。");return;}if(!board.completed&&!board.image_data_url){alert("请先回填并检视本段九宫格图片。");return;}if(!board.completed){const unresolved=board.panels.filter(panel=>panel.reverse_status!=="accepted");if(unresolved.length){activePanelId=unresolved[0].id;renderPanelSelect();renderHitGrid();loadFields();alert(`最后一道核查尚未完成：还有 ${unresolved.length} 格未标记“对应通过”。已定位到 ${activePanelId}。`);return;}}board.completed=!board.completed;renderSegmentSelect();updateDerived();saveState();});
el("panelSelect").addEventListener("change",event=>selectPanel(event.target.value));
Object.values(fields).forEach(field=>{field.addEventListener("input",()=>{syncFields();});field.addEventListener("change",()=>{syncFields();});});
document.querySelectorAll("[data-reverse-status]").forEach(button=>button.addEventListener("click",()=>setReverseStatus(button.dataset.reverseStatus)));
el("nextReversePending").addEventListener("click",selectNextReversePending);
el("lookupQuery").addEventListener("input",event=>renderLookup(event.target.value));
el("saveVersion").addEventListener("click",saveVersion);
el("buildEditPrompt").addEventListener("click",()=>{syncFields();const panel=currentPanel();panel.edit_prompt=buildEditPrompt(panel,currentBoard());el("editPrompt").textContent=panel.edit_prompt;});
el("copyPanelPrompt").addEventListener("click",()=>copyText(buildPanelPrompt(currentPanel(),currentBoard())));
el("copySegmentPrompt").addEventListener("click",async()=>{await copyText(buildSegmentPrompt(currentBoard()));el("copySegmentPrompt").textContent="已复制当前SEG Prompt";setTimeout(()=>{el("copySegmentPrompt").textContent="复制当前SEG生图Prompt";},1000);});
el("copyVideoPrompt").addEventListener("click",async()=>{const board=currentBoard();if(!board.completed)return;await copyText(buildFinalVideoPrompt(board));el("copyVideoPrompt").textContent="已复制";setTimeout(()=>{el("copyVideoPrompt").textContent="复制视频Prompt";},1000);});
el("saveProject").addEventListener("click",saveProjectFile);
el("exportReviewHtml").addEventListener("click",exportReviewHtml);
el("exportFormat").addEventListener("change",()=>{el("exportPackage").textContent=el("exportFormat").value==="html"?"输出网页成果":"输出 JSON 成果";});
el("exportPackage").addEventListener("click",exportProject);
el("imageInput").addEventListener("change",()=>{const file=el("imageInput").files?.[0];if(!file)return;const reader=new FileReader();reader.onload=()=>{const board=currentBoard();board.image_data_url=reader.result;board.image_name=file.name;board.image_revision=Number(file.name.match(/-v(\d+)/i)?.[1]||1);board.last_replaced_panel="";board.generation_state="image_ready";board.panels.forEach(panel=>{panel.reverse_status="pending";panel.reverse_checked_at="";});board.completed=false;project.last_packaged_at="";renderImage();renderPanelSelect();renderHitGrid();updateDerived();saveState();};reader.readAsDataURL(file);});
el("panelReplaceInput").addEventListener("change",async()=>{const file=el("panelReplaceInput").files?.[0];if(file)await replaceCurrentPanel(file);el("panelReplaceInput").value="";});
el("storyboardImage").addEventListener("load",drawCrop);
el("packageInput").addEventListener("change",async()=>{const file=el("packageInput").files?.[0];if(!file)return;try{const data=JSON.parse(await file.text());if(Array.isArray(data.segments)&&data.segments.length&&data.segments.every(item=>Array.isArray(item.panels)&&item.panels.length===9)){project=normalizeReverseValidation(data);}else if(Array.isArray(data.panels)&&data.panels.length===9){project=normalizeReverseValidation({package_type:"open-cowart-nine-grid-project",script_name:file.name,source_text:"",pipeline_stage:data.image_data_url?4:3,last_packaged_at:"",segments:[data]});}else{throw new Error("请导入工作项目JSON；最终成果包不含可编辑九格数据");}activeSegmentId=project.segments[0].segment_id;activePanelId=project.segments[0].panels[0].id;renderAll();}catch(error){alert(`导入失败：${error.message}`);}finally{el("packageInput").value="";}});
el("downloadCurrent").addEventListener("click",()=>{drawCrop();downloadCanvas(`${activePanelId}.png`);});
el("downloadBoard").addEventListener("click",downloadBoardImage);
el("downloadAll").addEventListener("click",async()=>{const board=currentBoard(),initial=activePanelId;for(const panel of board.panels){activePanelId=panel.id;drawCrop();downloadCanvas(`${panel.id}.png`);await new Promise(resolve=>setTimeout(resolve,120));}activePanelId=initial;renderHitGrid();drawCrop();});

async function bootstrapProject(){
  if(embeddedWorkspace){renderAll();return;}
  const autoload=new URLSearchParams(window.location.search).get("autoload");
  if(autoload){
    if(!autoload.startsWith("projects/")||autoload.includes("..")){
      alert("自动载入路径无效");
    }else{
      try{
        const response=await fetch(autoload,{cache:"no-store"});
        if(!response.ok)throw new Error(`HTTP ${response.status}`);
        const data=await response.json();
        if(!Array.isArray(data.segments)||!data.segments.length)throw new Error("项目中没有有效SEG");
        project=normalizeReverseValidation(data);
        activeSegmentId=project.segments[0].segment_id;
        activePanelId=project.segments[0].panels[0].id;
      }catch(error){
        alert(`自动载入失败：${error.message}`);
      }
    }
  }else{
    try{
      const saved=await readSavedProject();
      if(Array.isArray(saved?.segments)&&saved.segments.length){
        project=normalizeReverseValidation(saved);
        activeSegmentId=project.segments[0].segment_id;
        activePanelId=project.segments[0].panels[0].id;
      }
    }catch(error){console.warn("Could not restore full project",error);}
  }
  renderAll();
}

bootstrapProject();

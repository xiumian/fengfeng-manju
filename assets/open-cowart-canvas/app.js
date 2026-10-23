const nodeTypes = {
  script: {
    title: "文本解析",
    subtitle: "识别类型并结构化剧本",
    icon: "T",
    color: "#2563eb",
    purpose: "把原始文本拆成剧本类型、角色、场景、对白、情绪和目标成片规格。",
    input: "用户文本、小说、广告 brief、短剧对白、分镜草稿",
    output: "Script JSON、场景列表、角色表、镜头候选"
  },
  analysis: {
    title: "剧本分析",
    subtitle: "戏剧目标与镜头拆分",
    icon: "A",
    color: "#7c3aed",
    purpose: "分析人物关系、情绪转折、场景目标，并把长段剧情拆成可执行短镜头。",
    input: "Script JSON、类型规则、导演 Skill",
    output: "Scene Map、Shot Plan、节奏标记"
  },
  assetReq: {
    title: "资产需求",
    subtitle: "生成角色/场景/道具清单",
    icon: "R",
    color: "#b45309",
    purpose: "把剧本需求转成可生产、可审核、可复用的数字资产规格。",
    input: "角色、场景、道具、声音需求",
    output: "Asset Requirements、优先级、依赖关系"
  },
  assetGen: {
    title: "数字资产库",
    subtitle: "稳定 ID 与参考图",
    icon: "D",
    color: "#15803d",
    purpose: "为角色、场景、道具、声音创建稳定资产 ID，避免每个镜头重复文字描述造成漂移。",
    input: "资产规格、风格 Skill、用户参考图",
    output: "char_A、scene_03、prop_letter_01、voice_A"
  },
  director: {
    title: "导演调度",
    subtitle: "角色走位 / 对白节奏 / 镜头计划",
    icon: "B",
    color: "#4f46e5",
    purpose: "基于剧本与资产建立A/B/C角色映射、空间图、角色起止点、视线、道具状态、对白节奏和镜头计划。",
    input: "已确认剧本、数字资产、场景布局、对白台账",
    output: "Asset Grounding、Scene Map、Role Schedule、Camera Plan"
  },
  microexpression: {
    title: "微表演节拍",
    subtitle: "基线 / 触发 / 泄露 / 控制 / 终态",
    icon: "µ",
    color: "#a21caf",
    purpose: "把抽象情绪转成克制、可见、可按时间执行的眼神、呼吸、下颌和身体反应。",
    input: "角色调度、对白节拍、关键刺激、镜头覆盖",
    output: "Emotion Beat、Performance Prompt、Targeted Negatives"
  },
  storyboard: {
    title: "九宫格拆解",
    subtitle: "节拍 / SHOT / REF 双向绑定",
    icon: "9",
    color: "#6d28d9",
    purpose: "把一个10–15秒片段拆成九个可见节拍，并为每格生成唯一宫格ID、原镜号SHOT REF和资产REF。",
    input: "已确认片段、原镜号、数字资产ID、空间轴线",
    output: "3×3 Prompt、SEGxx-Pxx 对照表、生成前检查"
  },
  imagegen: {
    title: "$imagegen 生图",
    subtitle: "调用内置生成并保存版本",
    icon: "I",
    color: "#c2410c",
    purpose: "把九宫格Prompt交给Codex的$imagegen生成，导入成品并按片段ID和版本号保存。",
    input: "九宫格Prompt、画风参考、剧情资产参考",
    output: "Storyboard PNG、像素信息、版本记录"
  },
  gridEdit: {
    title: "九宫格修改",
    subtitle: "按唯一格号验收与修正",
    icon: "M",
    color: "#be123c",
    purpose: "用SEGxx-Pxx定位偏差，核对SHOT/REF并生成只修改指定格的受控编辑Prompt。",
    input: "确定版本的故事板、宫格ID、期望内容/REF、实际偏差",
    output: "逐格问题单、$imagegen编辑Prompt、新版本任务"
  },
  prompt: {
    title: "资产绑定提示词",
    subtitle: "用 ID 替代冗长描述",
    icon: "P",
    color: "#0f766e",
    purpose: "把资产引用、角色调度、镜头语言、负面约束合成平台可用的视频提示词。",
    input: "Shot Plan、Asset IDs、连续性规则",
    output: "Video Prompt、Keyframes、Negative Constraints"
  },
  video: {
    title: "生图/生视频",
    subtitle: "多候选生成与回滚",
    icon: "V",
    color: "#dc2626",
    purpose: "按镜头生成图像和视频候选，保留 seed、版本和失败原因。",
    input: "Video Prompt、参考资产、模型参数",
    output: "Shot Clips、候选版本、质量评分"
  },
  audio: {
    title: "生音频",
    subtitle: "对白/环境/BGM/SFX",
    icon: "S",
    color: "#0891b2",
    purpose: "让声音从剧本阶段就参与节奏设计，而不是最后机械贴合。",
    input: "对白、环境音、音乐情绪、静默点",
    output: "Voice、SFX、BGM、Audio Cues"
  },
  edit: {
    title: "时间线装配",
    subtitle: "自动剪辑并导出成片",
    icon: "E",
    color: "#111827",
    purpose: "把镜头、对白、音效、字幕和转场装配为可导出的完整视频。",
    input: "Shot Clips、Audio Cues、字幕、转场规则",
    output: "Timeline、Preview、Final Render"
  },
  check: {
    title: "连续性检查",
    subtitle: "身份/空间/光线/道具",
    icon: "C",
    color: "#be123c",
    purpose: "检查角色身份漂移、场景翻转、道具状态错误、光线不一致和多角色错位。",
    input: "镜头结果、资产库、剧本事实",
    output: "风险报告、修复建议、补镜任务"
  }
};

let nodes = [
  { id: "n1", type: "script", x: 520, y: 390, status: "ready" },
  { id: "n2", type: "analysis", x: 850, y: 310, status: "ready" },
  { id: "n3", type: "assetReq", x: 1180, y: 405, status: "ready" },
  { id: "n4", type: "assetGen", x: 1515, y: 300, status: "ready" },
  { id: "n4d", type: "director", x: 1860, y: 220, status: "ready" },
  { id: "n4m", type: "microexpression", x: 2210, y: 380, status: "ready" },
  { id: "n5", type: "storyboard", x: 2560, y: 300, status: "ready" },
  { id: "n6", type: "imagegen", x: 2910, y: 300, status: "ready" },
  { id: "n7", type: "gridEdit", x: 3260, y: 300, status: "ready" },
  { id: "n8", type: "prompt", x: 3610, y: 300, status: "ready" },
  { id: "n9", type: "video", x: 3960, y: 220, status: "ready" },
  { id: "n10", type: "audio", x: 3960, y: 480, status: "ready" },
  { id: "n11", type: "edit", x: 4310, y: 350, status: "ready" },
  { id: "n12", type: "check", x: 4660, y: 350, status: "ready" }
];

let edges = [
  ["n1", "n2"],
  ["n2", "n3"],
  ["n3", "n4"],
  ["n4", "n4d"],
  ["n4d", "n4m"],
  ["n4m", "n5"],
  ["n5", "n6"],
  ["n6", "n7"],
  ["n7", "n8"],
  ["n8", "n9"],
  ["n8", "n10"],
  ["n9", "n11"],
  ["n10", "n11"],
  ["n11", "n12"],
  ["n12", "n3"]
];

const stage = document.getElementById("stage");
const wrap = document.getElementById("canvasWrap");
const nodesLayer = document.getElementById("nodesLayer");
const edgesSvg = document.getElementById("edges");
const detail = document.getElementById("nodeDetail");
const zoomReadout = document.getElementById("zoomReadout");
const palette = document.getElementById("modulePalette");
const timelineTrack = document.getElementById("timelineTrack");
const miniTrack = document.getElementById("miniTrack");
const promptPreview = document.getElementById("promptPreview");
const workflowJson = document.getElementById("workflowJson");
const bindingCharacter = document.getElementById("bindingCharacter");
const bindingScene = document.getElementById("bindingScene");
const bindingProp = document.getElementById("bindingProp");
const bindingVoice = document.getElementById("bindingVoice");

let workflowData = buildWorkflowData(document.getElementById("scriptInput").value);

const requestedNodeId = new URLSearchParams(window.location.search).get("node");
let selectedId = nodes.some((node) => node.id === requestedNodeId) ? requestedNodeId : "n5";
document.body.classList.toggle("grid-editor-mode", selectedId === "n7" && requestedNodeId === "n7");
let mode = "select";
let scale = 0.82;
let offset = { x: -270, y: 35 };
let dragging = null;
let panning = null;
let connectStart = null;
let selectedPromptShotIndex = 0;
let suppressNodeClick = false;

function render() {
  stage.style.transform = `translate(${offset.x}px, ${offset.y}px) scale(${scale})`;
  zoomReadout.textContent = `${Math.round(scale * 100)}%`;
  renderNodes();
  renderEdges();
  renderDetail();
  renderMinimap();
  renderWorkflowJson();
}

function renderNodes() {
  nodesLayer.innerHTML = "";
  nodes.forEach((node) => {
    const type = nodeTypes[node.type];
    const el = document.createElement("article");
    el.className = `node ${node.id === selectedId ? "selected" : ""} ${node.status === "running" ? "running" : ""} ${node.status === "skipped" ? "skipped" : ""} ${isUnlocked(node.id) ? "unlocked" : ""}`;
    el.style.left = `${node.x}px`;
    el.style.top = `${node.y}px`;
    el.dataset.id = node.id;
    el.innerHTML = `
      <div class="node-header">
        <div class="node-icon" style="background:${type.color}">${type.icon}</div>
        <div class="node-title">
          <strong>${type.title}</strong>
          <span>${type.subtitle}</span>
        </div>
      </div>
      <div class="node-body">
        <p>${type.purpose}</p>
        <div class="ports">
          <span class="port"><i class="dot"></i>输入</span>
          <span class="status ${node.status}">${statusText(node.status)}</span>
          <span class="port">输出<i class="dot"></i></span>
        </div>
      </div>
    `;
    el.addEventListener("pointerdown", onNodePointerDown);
    el.addEventListener("click", onNodeClick);
    nodesLayer.appendChild(el);
  });
}

function renderEdges() {
  edgesSvg.innerHTML = "";
  edges.forEach(([from, to]) => {
    const a = nodes.find((node) => node.id === from);
    const b = nodes.find((node) => node.id === to);
    if (!a || !b) return;
    const ax = a.x + 246;
    const ay = a.y + 66;
    const bx = b.x;
    const by = b.y + 66;
    const mid = Math.max(80, Math.abs(bx - ax) * 0.45);
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", `M ${ax} ${ay} C ${ax + mid} ${ay}, ${bx - mid} ${by}, ${bx} ${by}`);
    path.setAttribute("class", `edge-path ${from === selectedId || to === selectedId ? "active" : ""}`);
    edgesSvg.appendChild(path);
  });
}

function renderDetail() {
  const node = nodes.find((item) => item.id === selectedId);
  if (!node) return;
  const type = nodeTypes[node.type];
  const upstream = getUpstream(selectedId).map(getNodeTitle).join("、") || "无";
  const downstream = getDownstream(selectedId).map(getNodeTitle).join("、") || "无";
  const baseDetail = `
    <div class="detail-head">
      <div>
        <h2>${type.title}</h2>
        <p>${type.subtitle}</p>
      </div>
      <span class="status ${node.status}">${statusText(node.status)}</span>
    </div>
    <div class="io-grid">
      <div class="io-item"><b>主旨</b><span>${type.purpose}</span></div>
      <div class="io-item"><b>输入</b><span>${type.input}</span></div>
      <div class="io-item"><b>输出</b><span>${type.output}</span></div>
      <div class="io-item"><b>连线逻辑</b><span>上游：${upstream}<br>下游：${downstream}</span></div>
    </div>
    <div class="node-run-controls">
      <button class="small-button primary" id="completeNode">完成当前节点</button>
      <button class="small-button" id="runFromNode">从此节点继续</button>
      <button class="small-button" id="skipNode">跳过节点</button>
      <button class="small-button danger" id="resetNode">重置节点</button>
    </div>
  `;
  const focusedGridEditor = document.body.classList.contains("grid-editor-mode") && node.type === "gridEdit";
  const focusedHeader = `<div class="detail-head"><div><h2>九宫格逐格编辑与 Prompt 速查</h2><p>点击宫格互查、调整参数、保存对应版本</p></div></div>`;
  detail.innerHTML = `${focusedGridEditor ? focusedHeader : baseDetail}${renderNodeWorkbench(node.type)}`;
  bindNodeRunControls();
  bindScriptImporter();
  bindNineGridWorkbench();
  bindDirectorWorkbench();
  bindMicroexpressionWorkbench();
  bindImagegenWorkbench();
  bindGridEditWorkbenchV2();
  bindPromptEditor();
  bindVideoGenerator();
  bindTimelineAssembler();
  promptPreview.textContent = buildPromptFor(node.type);
}

function renderNodeWorkbench(type) {
  if (type === "director") return renderDirectorWorkbench();
  if (type === "microexpression") return renderMicroexpressionWorkbench();
  if (type === "storyboard") return renderNineGridWorkbench();
  if (type === "imagegen") return renderImagegenWorkbench();
  if (type === "gridEdit") return renderGridEditWorkbench();
  if (type === "prompt") return renderPromptEditor();
  if (type === "script") return renderScriptImporter();
  if (type === "video") return renderVideoGenerator();
  if (type === "edit") return renderTimelineAssembler();
  return "";
}

function bindNodeRunControls() {
  const completeButton = document.getElementById("completeNode");
  const runFromButton = document.getElementById("runFromNode");
  const skipButton = document.getElementById("skipNode");
  const resetButton = document.getElementById("resetNode");
  if (!completeButton || !runFromButton || !skipButton || !resetButton) return;

  completeButton.addEventListener("click", () => {
    setNodeStatus(selectedId, "done");
    markDownstreamReady(selectedId);
    render();
  });

  runFromButton.addEventListener("click", () => {
    runGraphFrom(selectedId);
  });

  skipButton.addEventListener("click", () => {
    setNodeStatus(selectedId, "skipped");
    markDownstreamReady(selectedId);
    render();
  });

  resetButton.addEventListener("click", () => {
    setNodeStatus(selectedId, "ready");
    render();
  });
}

function renderScriptImporter() {
  const scriptValue = document.getElementById("scriptInput").value;
  return `
    <div class="node-workbench">
      <div class="workbench-row">
        <label class="field-label">导入文件</label>
        <input class="file-input" id="scriptFileInput" type="file" accept=".txt,.md,.json,.csv,text/plain,text/markdown,application/json" />
        <div class="helper-text" id="scriptFileMeta">支持 TXT、Markdown、JSON、CSV。JSON 会优先读取 source/script/content/text 字段。</div>
      </div>
      <div class="workbench-row">
        <label class="field-label" for="scriptNodeEditor">剧本文本预览</label>
        <textarea id="scriptNodeEditor" class="script-editor" spellcheck="false">${escapeHtml(scriptValue)}</textarea>
      </div>
      <div class="workbench-actions">
        <button class="small-button primary" id="applyScriptImport">应用并解析</button>
        <button class="small-button" id="syncScriptToLeft">同步到左侧</button>
        <button class="small-button" id="clearScriptEditor">清空文本</button>
      </div>
    </div>
  `;
}

function bindScriptImporter() {
  const fileInput = document.getElementById("scriptFileInput");
  const scriptEditor = document.getElementById("scriptNodeEditor");
  const fileMeta = document.getElementById("scriptFileMeta");
  const applyButton = document.getElementById("applyScriptImport");
  const syncButton = document.getElementById("syncScriptToLeft");
  const clearButton = document.getElementById("clearScriptEditor");
  if (!fileInput || !scriptEditor || !applyButton || !syncButton || !clearButton) return;

  fileInput.addEventListener("change", async () => {
    const file = fileInput.files && fileInput.files[0];
    if (!file) return;
    const rawText = await file.text();
    const extractedText = extractScriptText(rawText, file.name);
    scriptEditor.value = extractedText;
    fileMeta.textContent = `已导入：${file.name}，${Math.round(file.size / 1024)} KB`;
    promptPreview.textContent = `已导入文件 ${file.name}，可点击“应用并解析”生成结构化剧本。`;
  });

  applyButton.addEventListener("click", () => {
    applyScriptText(scriptEditor.value);
    setNodeStatus(selectedId, "done");
    markDownstreamReady(selectedId);
    selectedPromptShotIndex = 0;
    renderTimeline();
    renderBindings();
    render();
  });

  syncButton.addEventListener("click", () => {
    document.getElementById("scriptInput").value = scriptEditor.value;
    promptPreview.textContent = "已同步到左侧剧本输入框，尚未重新解析。";
  });

  clearButton.addEventListener("click", () => {
    scriptEditor.value = "";
    fileMeta.textContent = "已清空，可重新导入或粘贴文本。";
  });
}

function ensureDirectorBlocking() {
  if (!workflowData.director_blocking) {
    const assets = workflowData.assets;
    const defaults = workflowData.director_defaults || {};
    const characterMap = workflowData.characters?.length
      ? workflowData.characters.map((item) => `${item.role_alias}=${item.id}(${item.image_ref}/${item.name})`).join("；")
      : `A=${assets.character.id}`;
    const characterFacts = workflowData.characters?.length
      ? workflowData.characters.map((item) => `${item.id}: ${item.image_ref} ${item.name}，${item.requirement}`).join("\n")
      : `${assets.character.id}: ${assets.character.requirement}`;
    workflowData.director_blocking = {
      character_map: characterMap,
      confirmed_facts: workflowData.source,
      asset_facts: `${characterFacts}\n${assets.scene.id}: ${assets.scene.requirement}\n${assets.prop.id}: ${assets.prop.requirement}`,
      spatial_map: defaults.spatial_map || `A的位置按剧本锁定；${assets.prop.id}保持原位；${assets.scene.id}的布局、主光方向与180度轴线保持不变。`,
      role_schedule: defaults.role_schedule || workflowData.shots.map((shot) => `${shot.id}: A执行“${shot.action}”，写清起点、终点、路径、视线和道具状态。`).join("\n"),
      dialogue_rhythm: defaults.dialogue_rhythm || "按对白意义、情绪、权力变化、视线和走位拆节拍；无剧本对白时保留声音触发与静默反应。",
      camera_plan: defaults.camera_plan || workflowData.shots.map((shot) => `${shot.id}: 3–8秒，1–2个主要动作，单一主要运镜，明确首尾关键帧与禁止运镜。`).join("\n"),
      prompt: ""
    };
  }
  return workflowData.director_blocking;
}

function renderDirectorWorkbench() {
  const data = ensureDirectorBlocking();
  return `
    <div class="node-workbench">
      <div class="notice-box">保持资产ID不变；A/B/C只作为调度别名。事实、资产、假设和待确认项必须分层，镜头设计必须服从角色走位。</div>
      <div class="workbench-row"><label class="field-label">角色映射</label><input id="directorCharacterMap" value="${escapeHtml(data.character_map)}" /></div>
      <div class="workbench-row"><label class="field-label">剧本确认事实</label><textarea id="directorConfirmed" class="negative-editor">${escapeHtml(data.confirmed_facts)}</textarea></div>
      <div class="workbench-row"><label class="field-label">资产确认事实</label><textarea id="directorAssets" class="negative-editor">${escapeHtml(data.asset_facts)}</textarea></div>
      <div class="workbench-row"><label class="field-label">空间图 / 轴线 / 主光</label><textarea id="directorSpatial" class="negative-editor">${escapeHtml(data.spatial_map)}</textarea></div>
      <div class="workbench-row"><label class="field-label">角色调度表</label><textarea id="directorSchedule" class="prompt-editor">${escapeHtml(data.role_schedule)}</textarea></div>
      <div class="workbench-row"><label class="field-label">对白节奏</label><textarea id="directorDialogue" class="negative-editor">${escapeHtml(data.dialogue_rhythm)}</textarea></div>
      <div class="workbench-row"><label class="field-label">镜头计划</label><textarea id="directorCamera" class="prompt-editor">${escapeHtml(data.camera_plan)}</textarea></div>
      <div class="workbench-actions"><button class="small-button primary" id="buildDirectorPrompt">保存并生成导演摘要</button><button class="small-button" id="copyDirectorPrompt">复制摘要</button></div>
      <div class="io-item"><b>导演摘要</b><span class="mono-wrap">${escapeHtml(data.prompt || "尚未生成")}</span></div>
    </div>
  `;
}

function bindDirectorWorkbench() {
  const buildButton = document.getElementById("buildDirectorPrompt");
  const copyButton = document.getElementById("copyDirectorPrompt");
  if (!buildButton || !copyButton) return;
  const data = ensureDirectorBlocking();
  const sync = () => {
    data.character_map = document.getElementById("directorCharacterMap").value.trim();
    data.confirmed_facts = document.getElementById("directorConfirmed").value.trim();
    data.asset_facts = document.getElementById("directorAssets").value.trim();
    data.spatial_map = document.getElementById("directorSpatial").value.trim();
    data.role_schedule = document.getElementById("directorSchedule").value.trim();
    data.dialogue_rhythm = document.getElementById("directorDialogue").value.trim();
    data.camera_plan = document.getElementById("directorCamera").value.trim();
    data.prompt = buildDirectorSummary(data);
  };
  buildButton.addEventListener("click", () => {
    sync();
    promptPreview.textContent = data.prompt;
    renderWorkflowJson();
    renderDetail();
  });
  copyButton.addEventListener("click", async () => {
    sync();
    await copyText(data.prompt);
    copyButton.textContent = "已复制";
    setTimeout(() => { copyButton.textContent = "复制摘要"; }, 900);
    renderWorkflowJson();
  });
}

function buildDirectorSummary(data) {
  return `角色映射：${data.character_map}\n\n剧本确认事实：${data.confirmed_facts}\n\n资产确认事实：${data.asset_facts}\n\n空间与连续性：${data.spatial_map}\n\n角色调度：${data.role_schedule}\n\n对白节奏：${data.dialogue_rhythm}\n\n镜头计划：${data.camera_plan}\n\n约束：每镜1–2个主要动作、一个主要运镜；不越轴、不交换身份、不跳动道具、不迁移主光。`;
}

function ensureMicroexpressions() {
  if (!workflowData.microexpressions) {
    const beats = {};
    workflowData.shots.forEach((shot) => { beats[shot.id] = createMicroexpressionBeat(shot); });
    workflowData.microexpressions = { selected_shot_id: workflowData.shots[0].id, beats };
  }
  return workflowData.microexpressions;
}

function createMicroexpressionBeat(shot) {
  if (shot.microexpression) return { ...shot.microexpression, prompt: "" };
  const alerted = /身后|动静|脚步|竹林|声源|警醒|反应/.test(shot.action);
  const sleepy = /昏睡|微阖|打坐|睡意/.test(shot.action);
  if (sleepy) {
    return {
      baseline: "看似入定，实则昏睡：微阖双目、下颌放松、肩部松弛、呼吸缓慢",
      trigger: "尚未出现外部刺激，维持睡意基线",
      leak: "头部略低，眼睑保持近闭，身体重心稳定",
      mask: "维持打坐外观，不增加夸张睡态",
      end_state: "仍盘坐面对祭坛，桃木剑横放双腿且完全不动",
      cues: "微阖眼睑 + 放松下颌 + 缓慢呼吸",
      negative: "no exaggerated snoring, no body collapse, no standing, no sword movement, no identity drift, no prop deformation",
      prompt: ""
    };
  }
  return {
    baseline: alerted ? "盘坐昏睡，微阖双目，头部与躯干保持不动" : "克制、专注于当前动作",
    trigger: alerted ? "来自身后竹林的声音" : `完成“${shot.action}”的关键刺激`,
    leak: alerted ? "眼睑先轻颤一次，呼吸停半拍，双目只睁成窄缝" : "视线短暂停住，下眼睑轻微收紧",
    mask: alerted ? "眼睛先瞟向身后声源，头部随后只转几度，躯干仍保持盘坐" : "控制呼吸，保持动作幅度克制",
    end_state: alerted ? "睡意消退，安静但明确地警醒锁定声源" : "可读但不过度的情绪落点",
    cues: alerted ? "眼睑轻颤 + 呼吸停顿 + 眼神先行 + 下颌轻微收紧" : "视线停顿 + 浅吸气 + 下颌轻微用力",
    negative: "no frozen neutral face, no exaggerated eye widening, no mechanical blinking, no sudden head snap, no standing, no sword movement, no identity drift, no prop movement",
    prompt: ""
  };
}

function renderMicroexpressionWorkbench() {
  const data = ensureMicroexpressions();
  const beat = data.beats[data.selected_shot_id];
  const options = workflowData.shots.map((shot) => `<option value="${shot.id}" ${shot.id === data.selected_shot_id ? "selected" : ""}>${shot.id} · ${escapeHtml(shot.action)}</option>`).join("");
  return `
    <div class="node-workbench">
      <div class="notice-box">把抽象情绪改写为基线→触发→泄露→控制→终态。每个短节拍只使用2–4个可见通道，默认克制强度。</div>
      <div class="workbench-row"><label class="field-label">镜头</label><select id="microShotId">${options}</select></div>
      <div class="param-grid">
        <label><span>基线</span><textarea id="microBaseline">${escapeHtml(beat.baseline)}</textarea></label>
        <label><span>触发</span><textarea id="microTrigger">${escapeHtml(beat.trigger)}</textarea></label>
        <label><span>泄露</span><textarea id="microLeak">${escapeHtml(beat.leak)}</textarea></label>
        <label><span>控制/掩饰</span><textarea id="microMask">${escapeHtml(beat.mask)}</textarea></label>
        <label><span>结束状态</span><textarea id="microEnd">${escapeHtml(beat.end_state)}</textarea></label>
        <label><span>2–4个可见通道</span><textarea id="microCues">${escapeHtml(beat.cues)}</textarea></label>
      </div>
      <div class="workbench-row"><label class="field-label">针对性负面约束</label><textarea id="microNegative" class="negative-editor">${escapeHtml(beat.negative)}</textarea></div>
      <div class="workbench-actions"><button class="small-button primary" id="buildMicroPrompt">保存并生成表演Prompt</button><button class="small-button" id="copyMicroPrompt">复制Prompt</button></div>
      <div class="io-item"><b>表演Prompt</b><span class="mono-wrap">${escapeHtml(beat.prompt || "尚未生成")}</span></div>
    </div>
  `;
}

function bindMicroexpressionWorkbench() {
  const buildButton = document.getElementById("buildMicroPrompt");
  const copyButton = document.getElementById("copyMicroPrompt");
  const shotSelect = document.getElementById("microShotId");
  if (!buildButton || !copyButton || !shotSelect) return;
  const data = ensureMicroexpressions();
  const sync = () => {
    const beat = data.beats[data.selected_shot_id];
    beat.baseline = document.getElementById("microBaseline").value.trim();
    beat.trigger = document.getElementById("microTrigger").value.trim();
    beat.leak = document.getElementById("microLeak").value.trim();
    beat.mask = document.getElementById("microMask").value.trim();
    beat.end_state = document.getElementById("microEnd").value.trim();
    beat.cues = document.getElementById("microCues").value.trim();
    beat.negative = document.getElementById("microNegative").value.trim();
    beat.prompt = buildMicroexpressionPrompt(data.selected_shot_id, beat);
    return beat;
  };
  shotSelect.addEventListener("change", () => {
    sync();
    data.selected_shot_id = shotSelect.value;
    renderWorkflowJson();
    renderDetail();
  });
  buildButton.addEventListener("click", () => {
    const beat = sync();
    promptPreview.textContent = beat.prompt;
    renderWorkflowJson();
    renderDetail();
  });
  copyButton.addEventListener("click", async () => {
    const beat = sync();
    await copyText(beat.prompt);
    copyButton.textContent = "已复制";
    setTimeout(() => { copyButton.textContent = "复制Prompt"; }, 900);
    renderWorkflowJson();
  });
}

function buildMicroexpressionPrompt(shotId, beat) {
  return `${shotId} 微表演：基线“${beat.baseline}”。触发“${beat.trigger}”后，先出现“${beat.leak}”，随后“${beat.mask}”，结束于“${beat.end_state}”。可见通道仅限：${beat.cues}。表演克制、按因果顺序发生；眼睛先于头部，必要时呼吸先于说话。${beat.negative}.`;
}

function normalizeStoryboardPanel(panel, index, boardDefaults = {}) {
  const fallback = boardDefaults.panels?.[index] || {};
  const merged = { ...fallback, ...panel };
  return {
    id: merged.id || `SEG01-P${String(index + 1).padStart(2, "0")}`,
    shot_ref: merged.shot_ref || "SHOT 01",
    asset_refs: merged.asset_refs || boardDefaults.asset_refs || "SC01+CH01",
    beat: merged.beat || `第${index + 1}个可见动作节拍`,
    duration: Number(merged.duration) > 0 ? Number(merged.duration) : 1.5,
    shot_size: merged.shot_size || "中景",
    camera_move: merged.camera_move || "固定镜头",
    character_anchor: merged.character_anchor || "保持角色身份、面部、发型、服装和身体朝向一致",
    scene_anchor: merged.scene_anchor || "保持场景布局、轴线、声源方向和主光方向一致",
    continuity: merged.continuity || "继承上一格的人物位置、视线、道具状态与空间关系",
    action: merged.action || merged.beat || `第${index + 1}个动作节拍`,
    performance: merged.performance || "动作与表情按因果顺序发生，表演克制且可读"
  };
}

function calculateSegmentDuration(board) {
  return Number(board.panels.reduce((sum, panel) => sum + (Number(panel.duration) || 0), 0).toFixed(2));
}

function buildPanelLookupPrompt(panel) {
  return `[${panel.id}｜${panel.shot_ref}｜REF:${panel.asset_refs}｜${Number(panel.duration).toFixed(2)}s｜${panel.shot_size}｜${panel.camera_move}]\n画面与动作：${panel.action || panel.beat}\n人物锚定：${panel.character_anchor}\n场景锚定：${panel.scene_anchor}\n表情与表演：${panel.performance}\n连续性：${panel.continuity}`;
}

function ensureStoryboardWorkflow() {
  if (!workflowData.storyboard) {
    const boardDefaults = workflowData.storyboard_defaults || {};
    workflowData.storyboard = {
      segment_id: "SEG01",
      shot_ref: "SHOT 01",
      asset_refs: boardDefaults.asset_refs || "SC01+CH01",
      panels: Array.from({ length: 9 }, (_, index) => normalizeStoryboardPanel({}, index, boardDefaults)),
      prompt: "",
      versions: [],
      quick_lookup_versions: [],
      revision: {
        panel_id: "SEG01-P01",
        expected: "",
        actual: "",
        change: "",
        prompt: ""
      }
    };
  }
  workflowData.storyboard.quick_lookup_versions ||= [];
  workflowData.storyboard.panels = workflowData.storyboard.panels.map((panel, index) => normalizeStoryboardPanel(panel, index, workflowData.storyboard_defaults || {}));
  restorePromptLibrary(workflowData.storyboard);
  workflowData.storyboard.segment_duration = calculateSegmentDuration(workflowData.storyboard);
  return workflowData.storyboard;
}

function renderNineGridWorkbench() {
  const board = ensureStoryboardWorkflow();
  const panelRows = board.panels.map((panel, index) => `
    <div class="panel-row">
      <b>${panel.id}</b>
      <input data-panel-field="shot" data-panel-index="${index}" value="${escapeHtml(panel.shot_ref)}" aria-label="${panel.id} SHOT REF" />
      <input data-panel-field="refs" data-panel-index="${index}" value="${escapeHtml(panel.asset_refs)}" aria-label="${panel.id} 资产 REF" />
      <textarea data-panel-field="beat" data-panel-index="${index}" aria-label="${panel.id} 节拍">${escapeHtml(panel.beat)}</textarea>
    </div>
  `).join("");
  return `
    <div class="node-workbench">
      <div class="notice-box">本节点独立完成九宫格拆解。每格必须双向绑定：宫格ID ↔ SHOT REF ↔ 资产REF ↔ 提示词节拍。</div>
      <div class="param-grid">
        <label><span>片段ID</span><input id="gridSegmentId" value="${escapeHtml(board.segment_id)}" /></label>
        <label><span>默认SHOT REF</span><input id="gridShotRef" value="${escapeHtml(board.shot_ref)}" /></label>
        <label><span>默认资产REF</span><input id="gridAssetRefs" value="${escapeHtml(board.asset_refs)}" /></label>
      </div>
      <div class="panel-grid-head"><b>宫格ID</b><b>SHOT REF</b><b>资产REF</b><b>可见节拍</b></div>
      <div class="panel-grid-editor">${panelRows}</div>
      <div class="workbench-actions">
        <button class="small-button primary" id="buildNineGridPrompt">生成双向九宫格 Prompt</button>
        <button class="small-button" id="applyGridDefaults">应用默认标识</button>
        <button class="small-button" id="copyNineGridPrompt">复制给 $imagegen</button>
      </div>
      <div class="io-item"><b>Prompt快照</b><span class="mono-wrap">${escapeHtml(board.prompt || "尚未生成")}</span></div>
    </div>
  `;
}

function bindNineGridWorkbench() {
  const buildButton = document.getElementById("buildNineGridPrompt");
  const defaultsButton = document.getElementById("applyGridDefaults");
  const copyButton = document.getElementById("copyNineGridPrompt");
  if (!buildButton || !defaultsButton || !copyButton) return;
  const board = ensureStoryboardWorkflow();

  const syncPanelInputs = () => {
    const segmentInput = document.getElementById("gridSegmentId");
    const shotInput = document.getElementById("gridShotRef");
    const refsInput = document.getElementById("gridAssetRefs");
    board.segment_id = normalizeSegmentId(segmentInput.value);
    board.shot_ref = shotInput.value.trim() || "SHOT 01";
    board.asset_refs = refsInput.value.trim() || "REF:NONE";
    board.panels = board.panels.map((panel, index) => ({
      ...panel,
      id: `${board.segment_id}-P${String(index + 1).padStart(2, "0")}`,
      shot_ref: document.querySelector(`[data-panel-field="shot"][data-panel-index="${index}"]`).value.trim() || board.shot_ref,
      asset_refs: document.querySelector(`[data-panel-field="refs"][data-panel-index="${index}"]`).value.trim() || board.asset_refs,
      beat: document.querySelector(`[data-panel-field="beat"][data-panel-index="${index}"]`).value.trim(),
      action: document.querySelector(`[data-panel-field="beat"][data-panel-index="${index}"]`).value.trim()
    }));
    board.segment_duration = calculateSegmentDuration(board);
    if (!board.panels.some((panel) => panel.id === board.revision.panel_id)) {
      board.revision.panel_id = board.panels[0].id;
    }
  };

  defaultsButton.addEventListener("click", () => {
    const segmentId = normalizeSegmentId(document.getElementById("gridSegmentId").value);
    const shotRef = document.getElementById("gridShotRef").value.trim() || "SHOT 01";
    const assetRefs = document.getElementById("gridAssetRefs").value.trim() || "REF:NONE";
    board.segment_id = segmentId;
    board.shot_ref = shotRef;
    board.asset_refs = assetRefs;
    board.panels = board.panels.map((panel, index) => ({ ...panel, id: `${segmentId}-P${String(index + 1).padStart(2, "0")}`, shot_ref: shotRef, asset_refs: assetRefs }));
    board.revision.panel_id = board.panels[0].id;
    renderDetail();
    renderWorkflowJson();
  });

  buildButton.addEventListener("click", () => {
    syncPanelInputs();
    board.prompt = buildNineGridPrompt(board);
    promptPreview.textContent = board.prompt;
    renderWorkflowJson();
    renderDetail();
  });

  copyButton.addEventListener("click", async () => {
    syncPanelInputs();
    board.prompt = buildNineGridPrompt(board);
    await copyText(board.prompt);
    copyButton.textContent = "已复制";
    setTimeout(() => { copyButton.textContent = "复制给 $imagegen"; }, 900);
    renderWorkflowJson();
  });
}

function renderImagegenWorkbench() {
  const board = ensureStoryboardWorkflow();
  const versions = board.versions.length
    ? board.versions.map((version) => `<div class="candidate-item"><b>${escapeHtml(version.id)}</b><span>${escapeHtml(version.name)} · ${Math.round(version.size / 1024)} KB · ${escapeHtml(version.status)}</span></div>`).join("")
    : `<div class="empty-reference">尚未导入 $imagegen 成品。</div>`;
  return `
    <div class="node-workbench">
      <div class="notice-box">Open Cowart canvas 不伪装生成后端。点击复制后由 Codex 调用 $imagegen；成品再导入这里做版本、标识和验收管理。</div>
      <div class="workbench-row"><label class="field-label">当前九宫格 Prompt</label><textarea id="imagegenPrompt" class="prompt-editor" spellcheck="false">${escapeHtml(board.prompt || buildNineGridPrompt(board))}</textarea></div>
      <div class="workbench-row"><label class="field-label">导入 $imagegen 成品</label><input class="file-input" id="storyboardImageInput" type="file" accept="image/png,image/jpeg,image/webp" multiple /><div class="helper-text" id="storyboardImageMeta">使用片段ID+版本号保存，不覆盖旧版。</div></div>
      <div class="workbench-actions"><button class="small-button primary" id="copyForImagegen">复制 Prompt 给 $imagegen</button><button class="small-button" id="saveImagegenPrompt">保存 Prompt</button></div>
      <div class="candidate-list">${versions}</div>
    </div>
  `;
}

function bindImagegenWorkbench() {
  const promptInput = document.getElementById("imagegenPrompt");
  const imageInput = document.getElementById("storyboardImageInput");
  const copyButton = document.getElementById("copyForImagegen");
  const saveButton = document.getElementById("saveImagegenPrompt");
  if (!promptInput || !imageInput || !copyButton || !saveButton) return;
  const board = ensureStoryboardWorkflow();
  saveButton.addEventListener("click", () => {
    board.prompt = promptInput.value.trim();
    promptPreview.textContent = board.prompt;
    renderWorkflowJson();
  });
  copyButton.addEventListener("click", async () => {
    board.prompt = promptInput.value.trim();
    await copyText(board.prompt);
    copyButton.textContent = "已复制";
    setTimeout(() => { copyButton.textContent = "复制 Prompt 给 $imagegen"; }, 900);
  });
  imageInput.addEventListener("change", async () => {
    const files = [...(imageInput.files || [])];
    const imported = await Promise.all(files.map(readImageReference));
    const start = board.versions.length + 1;
    imported.forEach((image, index) => board.versions.push({ ...image, id: `${board.segment_id}-V${String(start + index).padStart(2, "0")}`, status: "awaiting_grid_review" }));
    document.getElementById("storyboardImageMeta").textContent = `已导入 ${imported.length} 张；当前 ${board.versions.length} 个版本。`;
    renderWorkflowJson();
    renderDetail();
  });
}

function renderGridEditWorkbench() {
  const board = ensureStoryboardWorkflow();
  const revision = board.revision;
  const selectedPanel = board.panels.find((panel) => panel.id === revision.panel_id) || board.panels[0];
  const options = board.panels.map((panel) => `<option value="${panel.id}" ${panel.id === revision.panel_id ? "selected" : ""}>${panel.id} · ${panel.shot_ref} · ${panel.asset_refs}</option>`).join("");
  const version = board.versions.length ? board.versions[board.versions.length - 1] : null;
  const versionText = version ? version.id : "尚未导入成品";
  const shotSizes = ["全景", "中景", "中近景", "近景", "特写"].map((value) => `<option ${selectedPanel.shot_size === value ? "selected" : ""}>${value}</option>`).join("");
  const cameraMoves = ["固定镜头", "缓慢推近", "缓慢拉远", "轻微横移", "跟随", "轻微摇镜"].map((value) => `<option ${selectedPanel.camera_move === value ? "selected" : ""}>${value}</option>`).join("");
  const lookupVersions = board.quick_lookup_versions.length
    ? board.quick_lookup_versions.slice().reverse().map((item) => `<button type="button" class="lookup-version" data-lookup-version="${escapeHtml(item.id)}"><b>${escapeHtml(item.id)}</b><span>${escapeHtml(item.panel_id)} · ${Number(item.duration).toFixed(2)}s · ${escapeHtml(item.shot_size)} · ${escapeHtml(item.camera_move)}</span></button>`).join("")
    : `<div class="empty-reference">保存当前格后，会在这里形成“宫格 ↔ Prompt”的速查版本。</div>`;
  const imagePreview = version?.data_url
    ? `<div class="storyboard-source"><img id="storyboardSourceImage" src="${escapeHtml(version.data_url)}" alt="${escapeHtml(version.id)} 九宫格成品" /><div class="storyboard-hit-grid">${board.panels.map((panel, index) => `<button type="button" data-crop-index="${index}" aria-label="选择 ${panel.id}">${panel.id}</button>`).join("")}</div></div>`
    : `<div class="empty-reference">请先导入九宫格图片；没有成品时也可先调整对应 Prompt。</div>`;
  return `
    <div class="node-workbench">
      <div class="review-summary"><span><b>成品</b>${escapeHtml(versionText)}</span><span><b>当前格</b>${escapeHtml(selectedPanel.id)}</span><span><b>段落时长</b><em id="segmentDurationReadout">${calculateSegmentDuration(board).toFixed(2)}s</em></span><span><b>速查版本</b>${board.quick_lookup_versions.length}</span></div>
      <div class="lookup-bar"><input id="panelLookupQuery" placeholder="输入宫格ID、SHOT、REF或提示词互查" /><div id="panelLookupResults" class="lookup-results"></div></div>
      <div class="grid-review-layout">
        <section class="grid-visual-column">${imagePreview}<div class="crop-preview-wrap"><canvas id="panelCropCanvas" width="480" height="270"></canvas><div id="panelCropMeta" class="helper-text">选择宫格后显示实际拆图。</div></div><div class="workbench-actions"><button class="small-button primary" id="downloadPanelCrop" ${version ? "" : "disabled"}>导出当前格 PNG</button><button class="small-button" id="downloadAllCrops" ${version ? "" : "disabled"}>导出全部九格</button></div></section>
        <section class="grid-editor-column">
          <div class="workbench-row"><label class="field-label">宫格 / SHOT / REF</label><select id="revisionPanelId">${options}</select></div>
          <div class="compact-fields three"><label><span>时长（秒）</span><input id="panelDuration" type="number" min="0.1" step="0.1" value="${selectedPanel.duration}" /></label><label><span>景别</span><select id="panelShotSize">${shotSizes}</select></label><label><span>运镜</span><select id="panelCameraMove">${cameraMoves}</select></label></div>
          <div class="compact-fields two"><label><span>SHOT REF</span><input id="panelShotRef" value="${escapeHtml(selectedPanel.shot_ref)}" /></label><label><span>资产 REF</span><input id="panelAssetRefs" value="${escapeHtml(selectedPanel.asset_refs)}" /></label></div>
          <div class="workbench-row"><label class="field-label">画面动作</label><textarea id="panelAction" class="negative-editor">${escapeHtml(selectedPanel.action)}</textarea></div>
          <div class="anchor-grid"><label><span>人物锚定</span><textarea id="panelCharacterAnchor">${escapeHtml(selectedPanel.character_anchor)}</textarea></label><label><span>场景锚定</span><textarea id="panelSceneAnchor">${escapeHtml(selectedPanel.scene_anchor)}</textarea></label><label><span>动作与表情表演</span><textarea id="panelPerformance">${escapeHtml(selectedPanel.performance)}</textarea></label><label><span>连续性</span><textarea id="panelContinuity">${escapeHtml(selectedPanel.continuity)}</textarea></label></div>
          <div class="io-item compact-output"><b>当前格对应 Prompt</b><span id="panelPromptReadout" class="mono-wrap">${escapeHtml(buildPanelLookupPrompt(selectedPanel))}</span></div>
          <details class="revision-details"><summary>需要修图时填写偏差</summary><div class="workbench-row"><label class="field-label">期望内容 / REF</label><textarea id="revisionExpected" class="negative-editor">${escapeHtml(revision.expected)}</textarea></div><div class="workbench-row"><label class="field-label">实际偏差</label><textarea id="revisionActual" class="negative-editor">${escapeHtml(revision.actual)}</textarea></div><div class="workbench-row"><label class="field-label">确认修改</label><textarea id="revisionChange" class="negative-editor">${escapeHtml(revision.change)}</textarea></div></details>
          <div class="workbench-actions"><button class="small-button primary" id="saveLookupVersion">保存速查版本</button><button class="small-button" id="buildRevisionPrompt">生成修图 Prompt</button><button class="small-button" id="copyRevisionPrompt">复制修图 Prompt</button><button class="small-button" id="exportLookupPackage">导出速查包</button></div>
          <div class="io-item"><b>修图 Prompt</b><span id="revisionPromptReadout" class="mono-wrap">${escapeHtml(revision.prompt || "尚未生成")}</span></div>
        </section>
      </div>
      <div class="lookup-library"><b>已保存的 Prompt 速查版本</b><div class="lookup-version-list">${lookupVersions}</div></div>
    </div>
  `;
}

function bindGridEditWorkbench() {
  const buildButton = document.getElementById("buildRevisionPrompt");
  const copyButton = document.getElementById("copyRevisionPrompt");
  if (!buildButton || !copyButton) return;
  const board = ensureStoryboardWorkflow();
  const panelSelect = document.getElementById("revisionPanelId");
  const sourceImage = document.getElementById("storyboardSourceImage");
  const cropCanvas = document.getElementById("panelCropCanvas");
  const cropMeta = document.getElementById("panelCropMeta");
  const drawCrop = () => {
    if (!sourceImage || !cropCanvas || !panelSelect || !sourceImage.complete || !sourceImage.naturalWidth) return;
    const panelIndex = Math.max(0, board.panels.findIndex((panel) => panel.id === panelSelect.value));
    const sourceWidth = sourceImage.naturalWidth / 3;
    const sourceHeight = sourceImage.naturalHeight / 3;
    const col = panelIndex % 3;
    const row = Math.floor(panelIndex / 3);
    cropCanvas.width = Math.floor(sourceWidth);
    cropCanvas.height = Math.floor(sourceHeight);
    const context = cropCanvas.getContext("2d");
    context.clearRect(0, 0, cropCanvas.width, cropCanvas.height);
    context.drawImage(sourceImage, col * sourceWidth, row * sourceHeight, sourceWidth, sourceHeight, 0, 0, cropCanvas.width, cropCanvas.height);
    if (cropMeta) cropMeta.textContent = `${panelSelect.value} · 第${row + 1}行第${col + 1}列 · ${cropCanvas.width}×${cropCanvas.height}px`;
    document.querySelectorAll("[data-crop-index]").forEach((button, index) => button.classList.toggle("active", index === panelIndex));
  };
  if (sourceImage) {
    sourceImage.addEventListener("load", drawCrop, { once: true });
    if (sourceImage.complete) drawCrop();
  }
  panelSelect?.addEventListener("change", () => {
    board.revision.panel_id = panelSelect.value;
    drawCrop();
  });
  document.querySelectorAll("[data-crop-index]").forEach((button) => {
    button.addEventListener("click", () => {
      panelSelect.value = board.panels[Number(button.dataset.cropIndex)].id;
      board.revision.panel_id = panelSelect.value;
      drawCrop();
    });
  });
  document.getElementById("downloadPanelCrop")?.addEventListener("click", () => {
    drawCrop();
    downloadCanvas(cropCanvas, `${board.revision.panel_id}.png`);
  });
  document.getElementById("downloadAllCrops")?.addEventListener("click", async () => {
    const initial = panelSelect.value;
    for (const panel of board.panels) {
      panelSelect.value = panel.id;
      board.revision.panel_id = panel.id;
      drawCrop();
      downloadCanvas(cropCanvas, `${panel.id}.png`);
      await delay(120);
    }
    panelSelect.value = initial;
    board.revision.panel_id = initial;
    drawCrop();
  });
  const syncRevision = () => {
    board.revision.panel_id = document.getElementById("revisionPanelId").value;
    board.revision.expected = document.getElementById("revisionExpected").value.trim();
    board.revision.actual = document.getElementById("revisionActual").value.trim();
    board.revision.change = document.getElementById("revisionChange").value.trim();
    board.revision.prompt = buildGridRevisionPrompt(board);
  };
  buildButton.addEventListener("click", () => {
    syncRevision();
    promptPreview.textContent = board.revision.prompt;
    renderWorkflowJson();
    renderDetail();
  });
  copyButton.addEventListener("click", async () => {
    syncRevision();
    await copyText(board.revision.prompt);
    copyButton.textContent = "已复制";
    setTimeout(() => { copyButton.textContent = "复制给 $imagegen"; }, 900);
    renderWorkflowJson();
  });
}

function bindGridEditWorkbenchV2() {
  const buildButton = document.getElementById("buildRevisionPrompt");
  const copyButton = document.getElementById("copyRevisionPrompt");
  const panelSelect = document.getElementById("revisionPanelId");
  if (!buildButton || !copyButton || !panelSelect) return;
  const board = ensureStoryboardWorkflow();
  const sourceImage = document.getElementById("storyboardSourceImage");
  const cropCanvas = document.getElementById("panelCropCanvas");
  const cropMeta = document.getElementById("panelCropMeta");
  let activePanelId = board.revision.panel_id;
  const panelFields = {
    duration: document.getElementById("panelDuration"),
    shot_size: document.getElementById("panelShotSize"),
    camera_move: document.getElementById("panelCameraMove"),
    shot_ref: document.getElementById("panelShotRef"),
    asset_refs: document.getElementById("panelAssetRefs"),
    action: document.getElementById("panelAction"),
    character_anchor: document.getElementById("panelCharacterAnchor"),
    scene_anchor: document.getElementById("panelSceneAnchor"),
    performance: document.getElementById("panelPerformance"),
    continuity: document.getElementById("panelContinuity")
  };
  const getPanel = (id = activePanelId) => board.panels.find((panel) => panel.id === id) || board.panels[0];
  const drawCrop = () => {
    if (!sourceImage || !cropCanvas || !sourceImage.complete || !sourceImage.naturalWidth) return;
    const panelIndex = Math.max(0, board.panels.findIndex((panel) => panel.id === activePanelId));
    const sourceWidth = sourceImage.naturalWidth / 3;
    const sourceHeight = sourceImage.naturalHeight / 3;
    const col = panelIndex % 3;
    const row = Math.floor(panelIndex / 3);
    cropCanvas.width = Math.floor(sourceWidth);
    cropCanvas.height = Math.floor(sourceHeight);
    const context = cropCanvas.getContext("2d");
    context.clearRect(0, 0, cropCanvas.width, cropCanvas.height);
    context.drawImage(sourceImage, col * sourceWidth, row * sourceHeight, sourceWidth, sourceHeight, 0, 0, cropCanvas.width, cropCanvas.height);
    if (cropMeta) cropMeta.textContent = `${activePanelId} · 第${row + 1}行第${col + 1}列 · ${cropCanvas.width}×${cropCanvas.height}px`;
    document.querySelectorAll("[data-crop-index]").forEach((button, index) => button.classList.toggle("active", index === panelIndex));
  };
  const refreshDerivedOutput = () => {
    board.segment_duration = calculateSegmentDuration(board);
    document.getElementById("segmentDurationReadout").textContent = `${board.segment_duration.toFixed(2)}s`;
    document.getElementById("panelPromptReadout").textContent = buildPanelLookupPrompt(getPanel());
  };
  const syncPanelFields = (panelId = activePanelId) => {
    const panel = getPanel(panelId);
    panel.duration = Math.max(0.1, Number(panelFields.duration.value) || 0.1);
    panel.shot_size = panelFields.shot_size.value;
    panel.camera_move = panelFields.camera_move.value;
    panel.shot_ref = panelFields.shot_ref.value.trim() || board.shot_ref;
    panel.asset_refs = panelFields.asset_refs.value.trim() || board.asset_refs;
    panel.action = panelFields.action.value.trim() || panel.beat;
    panel.beat = panel.action;
    panel.character_anchor = panelFields.character_anchor.value.trim();
    panel.scene_anchor = panelFields.scene_anchor.value.trim();
    panel.performance = panelFields.performance.value.trim();
    panel.continuity = panelFields.continuity.value.trim();
    board.segment_duration = calculateSegmentDuration(board);
    return panel;
  };
  const loadPanelFields = (panelId) => {
    const panel = getPanel(panelId);
    activePanelId = panel.id;
    board.revision.panel_id = panel.id;
    panelSelect.value = panel.id;
    Object.entries(panelFields).forEach(([key, field]) => { field.value = panel[key]; });
    refreshDerivedOutput();
    drawCrop();
  };
  const syncRevision = () => {
    const panel = syncPanelFields(activePanelId);
    board.revision.panel_id = panel.id;
    board.revision.expected = document.getElementById("revisionExpected").value.trim();
    board.revision.actual = document.getElementById("revisionActual").value.trim();
    board.revision.change = document.getElementById("revisionChange").value.trim();
    board.revision.prompt = buildGridRevisionPrompt(board);
    refreshDerivedOutput();
    return panel;
  };
  if (sourceImage) {
    sourceImage.addEventListener("load", drawCrop, { once: true });
    if (sourceImage.complete) drawCrop();
  }
  panelSelect.addEventListener("change", () => {
    syncPanelFields(activePanelId);
    loadPanelFields(panelSelect.value);
  });
  document.querySelectorAll("[data-crop-index]").forEach((button) => button.addEventListener("click", () => {
    syncPanelFields(activePanelId);
    loadPanelFields(board.panels[Number(button.dataset.cropIndex)].id);
  }));
  Object.values(panelFields).forEach((field) => {
    field.addEventListener("input", () => { syncPanelFields(activePanelId); refreshDerivedOutput(); });
    field.addEventListener("change", () => { syncPanelFields(activePanelId); refreshDerivedOutput(); });
  });
  document.getElementById("downloadPanelCrop")?.addEventListener("click", () => {
    drawCrop();
    downloadCanvas(cropCanvas, `${activePanelId}.png`);
  });
  document.getElementById("downloadAllCrops")?.addEventListener("click", async () => {
    const initial = activePanelId;
    for (const panel of board.panels) {
      activePanelId = panel.id;
      panelSelect.value = panel.id;
      drawCrop();
      downloadCanvas(cropCanvas, `${panel.id}.png`);
      await delay(120);
    }
    loadPanelFields(initial);
  });
  const renderLookupResults = (query = "") => {
    const normalized = query.trim().toLowerCase();
    const matches = board.panels.filter((panel) => !normalized || [panel.id, panel.shot_ref, panel.asset_refs, panel.action, panel.character_anchor, panel.scene_anchor, panel.performance, buildPanelLookupPrompt(panel)].join(" ").toLowerCase().includes(normalized));
    const container = document.getElementById("panelLookupResults");
    container.innerHTML = matches.map((panel) => `<button type="button" data-lookup-panel="${panel.id}"><b>${panel.id}</b><span>${escapeHtml(panel.shot_ref)} · ${escapeHtml(panel.asset_refs)}</span></button>`).join("") || `<span class="helper-text">没有匹配结果</span>`;
    container.querySelectorAll("[data-lookup-panel]").forEach((button) => button.addEventListener("click", () => {
      syncPanelFields(activePanelId);
      loadPanelFields(button.dataset.lookupPanel);
    }));
  };
  document.getElementById("panelLookupQuery")?.addEventListener("input", (event) => renderLookupResults(event.target.value));
  renderLookupResults();
  document.getElementById("saveLookupVersion")?.addEventListener("click", () => {
    const panel = syncRevision();
    const serial = board.quick_lookup_versions.filter((item) => item.panel_id === panel.id).length + 1;
    const snapshot = {
      id: `${panel.id}-R${String(serial).padStart(2, "0")}`,
      panel_id: panel.id,
      shot_ref: panel.shot_ref,
      asset_refs: panel.asset_refs,
      duration: panel.duration,
      shot_size: panel.shot_size,
      camera_move: panel.camera_move,
      action: panel.action,
      character_anchor: panel.character_anchor,
      scene_anchor: panel.scene_anchor,
      performance: panel.performance,
      continuity: panel.continuity,
      panel_prompt: buildPanelLookupPrompt(panel),
      revision_prompt: board.revision.prompt,
      storyboard_version: board.versions.at(-1)?.id || "prompt-only",
      segment_duration: calculateSegmentDuration(board),
      saved_at: new Date().toISOString()
    };
    board.quick_lookup_versions.push(snapshot);
    persistPromptLibrary(board);
    promptPreview.textContent = snapshot.panel_prompt;
    renderWorkflowJson();
    renderDetail();
  });
  buildButton.addEventListener("click", () => {
    syncRevision();
    promptPreview.textContent = board.revision.prompt;
    document.getElementById("revisionPromptReadout").textContent = board.revision.prompt;
    renderWorkflowJson();
  });
  copyButton.addEventListener("click", async () => {
    syncRevision();
    await copyText(board.revision.prompt);
    copyButton.textContent = "已复制";
    setTimeout(() => { copyButton.textContent = "复制修图 Prompt"; }, 900);
    renderWorkflowJson();
  });
  document.getElementById("exportLookupPackage")?.addEventListener("click", () => {
    syncRevision();
    downloadJson({
      package_type: "open-cowart-nine-grid-lookup",
      segment_id: board.segment_id,
      segment_duration: calculateSegmentDuration(board),
      storyboard_prompt: buildNineGridPrompt(board),
      panels: board.panels.map((panel) => ({ ...panel, panel_prompt: buildPanelLookupPrompt(panel) })),
      quick_lookup_versions: board.quick_lookup_versions,
      storyboard_versions: board.versions,
      exported_at: new Date().toISOString()
    }, `${board.segment_id}-九宫格提示词速查包.json`);
  });
  document.querySelectorAll("[data-lookup-version]").forEach((button) => button.addEventListener("click", () => {
    const snapshot = board.quick_lookup_versions.find((item) => item.id === button.dataset.lookupVersion);
    if (!snapshot) return;
    syncPanelFields(activePanelId);
    const panel = getPanel(snapshot.panel_id);
    ["shot_ref", "asset_refs", "duration", "shot_size", "camera_move", "action", "character_anchor", "scene_anchor", "performance", "continuity"].forEach((key) => { panel[key] = snapshot[key]; });
    loadPanelFields(snapshot.panel_id);
    promptPreview.textContent = snapshot.panel_prompt;
  }));
}

function renderVideoGenerator() {
  const videoData = ensureVideoGeneration();
  const referenceImages = videoData.reference_images.length
    ? videoData.reference_images.map((image) => `
        <figure class="reference-thumb">
          <img src="${image.data_url}" alt="${escapeHtml(image.name)}" />
          <figcaption>${escapeHtml(image.name)}</figcaption>
        </figure>
      `).join("")
    : `<div class="empty-reference">还没有导入示例图。</div>`;
  const candidates = videoData.candidates.length
    ? videoData.candidates.map((candidate) => `
        <div class="candidate-item">
          <b>${candidate.id}</b>
          <span>${candidate.status} · seed ${candidate.seed} · ${candidate.duration}s · ${candidate.references} 张参考图</span>
        </div>
      `).join("")
    : `<div class="empty-reference">尚未生成候选记录。</div>`;

  return `
    <div class="node-workbench">
      <div class="workbench-row">
        <label class="field-label">导入示例图</label>
        <input class="file-input" id="videoImageInput" type="file" accept="image/png,image/jpeg,image/webp" multiple />
        <div class="helper-text" id="videoImageMeta">支持 PNG、JPG、WEBP，可多选；图片会作为本地参考图写入导出 JSON。</div>
      </div>
      <div class="reference-grid" id="videoReferenceGrid">${referenceImages}</div>
      <div class="workbench-row">
        <label class="field-label" for="videoDescription">补充文字描述</label>
        <textarea id="videoDescription" class="script-editor" spellcheck="false">${escapeHtml(videoData.description)}</textarea>
      </div>
      <div class="param-grid">
        <label>
          <span>候选数量</span>
          <input id="videoCandidateCount" type="number" min="1" max="8" value="${videoData.candidate_count}" />
        </label>
        <label>
          <span>Seed</span>
          <input id="videoSeed" type="number" value="${videoData.seed}" />
        </label>
        <label>
          <span>时长秒</span>
          <input id="videoDuration" type="number" min="2" max="12" value="${videoData.duration}" />
        </label>
      </div>
      <div class="workbench-actions">
        <button class="small-button primary" id="saveVideoInput">保存输入</button>
        <button class="small-button" id="simulateVideoCandidates">生成候选记录</button>
        <button class="small-button" id="clearVideoRefs">清空参考图</button>
      </div>
      <div class="candidate-list">${candidates}</div>
    </div>
  `;
}

function bindVideoGenerator() {
  const imageInput = document.getElementById("videoImageInput");
  const descriptionInput = document.getElementById("videoDescription");
  const countInput = document.getElementById("videoCandidateCount");
  const seedInput = document.getElementById("videoSeed");
  const durationInput = document.getElementById("videoDuration");
  const saveButton = document.getElementById("saveVideoInput");
  const simulateButton = document.getElementById("simulateVideoCandidates");
  const clearButton = document.getElementById("clearVideoRefs");
  const imageMeta = document.getElementById("videoImageMeta");
  if (!imageInput || !descriptionInput || !saveButton || !simulateButton || !clearButton) return;

  imageInput.addEventListener("change", async () => {
    const files = [...(imageInput.files || [])];
    const imported = await Promise.all(files.map(readImageReference));
    workflowData.video_generation.reference_images.push(...imported);
    imageMeta.textContent = `已导入 ${imported.length} 张示例图，当前共 ${workflowData.video_generation.reference_images.length} 张。`;
    renderWorkflowJson();
    renderDetail();
  });

  saveButton.addEventListener("click", () => {
    updateVideoGenerationFromInputs(descriptionInput, countInput, seedInput, durationInput);
    promptPreview.textContent = buildVideoGenerationBrief();
    renderWorkflowJson();
  });

  simulateButton.addEventListener("click", () => {
    updateVideoGenerationFromInputs(descriptionInput, countInput, seedInput, durationInput);
    workflowData.video_generation.candidates = Array.from({ length: workflowData.video_generation.candidate_count }, (_, index) => ({
      id: `candidate_${String(index + 1).padStart(2, "0")}`,
      status: "ready_for_external_generation",
      seed: workflowData.video_generation.seed + index,
      duration: workflowData.video_generation.duration,
      references: workflowData.video_generation.reference_images.length,
      description: workflowData.video_generation.description
    }));
    setNodeStatus(selectedId, "done");
    markDownstreamReady(selectedId);
    renderWorkflowJson();
    renderDetail();
  });

  clearButton.addEventListener("click", () => {
    workflowData.video_generation.reference_images = [];
    workflowData.video_generation.candidates = [];
    renderWorkflowJson();
    renderDetail();
  });
}

function renderTimelineAssembler() {
  const timelineData = ensureTimelineAssembly();
  const cuts = timelineData.cuts.length
    ? timelineData.cuts.map((cut) => `
        <div class="candidate-item">
          <b>${cut.shot_id} · ${cut.start}s-${cut.end}s</b>
          <span>${cut.action} · ${cut.audio_cue} · ${cut.transition}</span>
        </div>
      `).join("")
    : `<div class="empty-reference">还没有生成时间线切点。</div>`;

  return `
    <div class="node-workbench">
      <div class="workbench-row">
        <label class="field-label">导入剪辑依据</label>
        <input class="file-input" id="timelineFileInput" type="file" accept=".txt,.md,.json,.csv,text/plain,text/markdown,application/json" />
        <div class="helper-text" id="timelineFileMeta">可导入剧本、导演说明、剪辑表或客户修改意见。</div>
      </div>
      <div class="workbench-row">
        <label class="field-label" for="timelineReferenceText">参照文本 / 剪辑规则</label>
        <textarea id="timelineReferenceText" class="script-editor" spellcheck="false">${escapeHtml(timelineData.reference_text)}</textarea>
      </div>
      <div class="param-grid">
        <label>
          <span>主比例</span>
          <input id="timelineAspect" type="text" value="${escapeHtml(timelineData.aspect_ratio)}" />
        </label>
        <label>
          <span>字幕</span>
          <input id="timelineSubtitles" type="text" value="${escapeHtml(timelineData.subtitles)}" />
        </label>
        <label>
          <span>转场</span>
          <input id="timelineTransition" type="text" value="${escapeHtml(timelineData.default_transition)}" />
        </label>
      </div>
      <div class="workbench-actions">
        <button class="small-button primary" id="buildTimeline">生成时间线</button>
        <button class="small-button" id="syncScriptToTimeline">同步当前剧本</button>
        <button class="small-button" id="clearTimelineReference">清空依据</button>
      </div>
      <div class="candidate-list">${cuts}</div>
    </div>
  `;
}

function bindTimelineAssembler() {
  const fileInput = document.getElementById("timelineFileInput");
  const referenceInput = document.getElementById("timelineReferenceText");
  const aspectInput = document.getElementById("timelineAspect");
  const subtitlesInput = document.getElementById("timelineSubtitles");
  const transitionInput = document.getElementById("timelineTransition");
  const buildButton = document.getElementById("buildTimeline");
  const syncButton = document.getElementById("syncScriptToTimeline");
  const clearButton = document.getElementById("clearTimelineReference");
  const fileMeta = document.getElementById("timelineFileMeta");
  if (!fileInput || !referenceInput || !buildButton || !syncButton || !clearButton) return;

  fileInput.addEventListener("change", async () => {
    const file = fileInput.files && fileInput.files[0];
    if (!file) return;
    const rawText = await file.text();
    referenceInput.value = extractScriptText(rawText, file.name);
    fileMeta.textContent = `已导入：${file.name}，${Math.round(file.size / 1024)} KB`;
    promptPreview.textContent = "已导入剪辑依据，可点击“生成时间线”。";
  });

  syncButton.addEventListener("click", () => {
    referenceInput.value = workflowData.source;
    promptPreview.textContent = "已同步当前剧本作为时间线装配依据。";
  });

  clearButton.addEventListener("click", () => {
    referenceInput.value = "";
    const timelineData = ensureTimelineAssembly();
    timelineData.reference_text = "";
    timelineData.cuts = [];
    renderTimeline();
    renderWorkflowJson();
    renderDetail();
  });

  buildButton.addEventListener("click", () => {
    updateTimelineAssemblyFromInputs(referenceInput, aspectInput, subtitlesInput, transitionInput);
    workflowData.timeline_assembly.cuts = buildTimelineCuts(workflowData.timeline_assembly);
    setNodeStatus(selectedId, "done");
    markDownstreamReady(selectedId);
    renderTimeline();
    renderWorkflowJson();
    promptPreview.textContent = buildTimelineBrief();
    renderDetail();
  });
}

function renderPromptEditor() {
  const shot = workflowData.shots[selectedPromptShotIndex] || workflowData.shots[0];
  const options = workflowData.shots
    .map((item, index) => `<option value="${index}" ${index === selectedPromptShotIndex ? "selected" : ""}>${item.id} - ${item.action}</option>`)
    .join("");
  return `
    <div class="node-workbench">
      <div class="workbench-row">
        <label class="field-label" for="promptShotSelect">镜头</label>
        <select id="promptShotSelect">${options}</select>
      </div>
      <div class="workbench-row">
        <label class="field-label" for="promptEditor">Prompt 编辑器</label>
        <textarea id="promptEditor" class="prompt-editor" spellcheck="false">${escapeHtml(shot.prompt)}</textarea>
      </div>
      <div class="workbench-row">
        <label class="field-label" for="negativeEditor">负面约束</label>
        <textarea id="negativeEditor" class="negative-editor" spellcheck="false">${escapeHtml(workflowData.negative_constraints.join(", "))}</textarea>
      </div>
      <div class="workbench-actions">
        <button class="small-button primary" id="savePrompt">保存到镜头</button>
        <button class="small-button" id="resetPrompt">按资产重建</button>
        <button class="small-button" id="copyPrompt">复制 Prompt</button>
      </div>
      <div class="io-item">
        <b>当前绑定</b>
        <span>${workflowData.assets.character.id} + ${workflowData.assets.scene.id} + ${workflowData.assets.prop.id}</span>
      </div>
    </div>
  `;
}

function bindPromptEditor() {
  const shotSelect = document.getElementById("promptShotSelect");
  const promptEditor = document.getElementById("promptEditor");
  const negativeEditor = document.getElementById("negativeEditor");
  const saveButton = document.getElementById("savePrompt");
  const resetButton = document.getElementById("resetPrompt");
  const copyButton = document.getElementById("copyPrompt");
  if (!shotSelect || !promptEditor || !negativeEditor) return;

  shotSelect.addEventListener("change", () => {
    selectedPromptShotIndex = Number(shotSelect.value);
    renderDetail();
  });

  promptEditor.addEventListener("input", () => {
    promptPreview.textContent = promptEditor.value;
  });

  negativeEditor.addEventListener("input", () => {
    workflowData.negative_constraints = splitConstraints(negativeEditor.value);
    renderWorkflowJson();
  });

  saveButton.addEventListener("click", () => {
    workflowData.shots[selectedPromptShotIndex].prompt = promptEditor.value.trim();
    workflowData.negative_constraints = splitConstraints(negativeEditor.value);
    promptPreview.textContent = workflowData.shots[selectedPromptShotIndex].prompt;
    renderWorkflowJson();
  });

  resetButton.addEventListener("click", () => {
    workflowData.shots[selectedPromptShotIndex].prompt = buildShotPrompt(workflowData.shots[selectedPromptShotIndex].action, workflowData.assets, workflowData.negative_constraints);
    renderDetail();
    renderWorkflowJson();
  });

  copyButton.addEventListener("click", async () => {
    const text = promptEditor.value.trim();
    try {
      await navigator.clipboard.writeText(text);
    } catch (error) {
      promptEditor.focus();
      promptEditor.select();
      document.execCommand("copy");
    }
    copyButton.textContent = "已复制";
    setTimeout(() => {
      copyButton.textContent = "复制 Prompt";
    }, 900);
  });
}

function renderPalette() {
  palette.innerHTML = "";
  Object.entries(nodeTypes).forEach(([key, type]) => {
    const item = document.createElement("button");
    item.className = "palette-item";
    item.innerHTML = `
      <span class="palette-icon" style="background:${type.color}">${type.icon}</span>
      <span><strong>${type.title}</strong><span>${type.subtitle}</span></span>
    `;
    item.addEventListener("click", () => addNode(key));
    palette.appendChild(item);
  });
}

function renderTimeline() {
  const assembly = ensureTimelineAssembly();
  const clips = assembly.cuts.length
    ? assembly.cuts.map((cut) => [cut.shot_id, `${cut.action} | ${cut.start}s-${cut.end}s`])
    : workflowData.shots.map((shot) => [shot.id, `${shot.action} | ${shot.duration}s`]);
  clips.push(["Audio", workflowData.audio.join(" + ")]);
  clips.push(["Render", assembly.aspect_ratio || workflowData.render_targets.join(" / ")]);
  timelineTrack.innerHTML = clips.map(([title, body]) => `<div class="clip"><b>${title}</b><span>${body}</span></div>`).join("");
}

function renderBindings() {
  bindingCharacter.textContent = workflowData.characters?.length ? workflowData.characters.map((item) => item.id).join("+") : workflowData.assets.character.id;
  bindingScene.textContent = workflowData.assets.scene.id;
  bindingProp.textContent = workflowData.assets.prop.id;
  bindingVoice.textContent = workflowData.assets.voice.id;
}

function renderWorkflowJson() {
  if (!workflowJson) return;
  const visibleData = JSON.parse(JSON.stringify(workflowData));
  (visibleData.storyboard?.versions || []).forEach((version) => {
    if (version.data_url) version.data_url = `[embedded image: ${version.name}]`;
  });
  workflowJson.textContent = JSON.stringify(visibleData, null, 2);
}

function renderMinimap() {
  miniTrack.innerHTML = "";
  nodes.forEach((node) => {
    const mini = document.createElement("span");
    mini.className = "mini-node";
    mini.style.left = `${Math.max(4, Math.min(152, node.x / 19))}px`;
    mini.style.top = `${Math.max(4, Math.min(80, node.y / 10))}px`;
    mini.style.background = nodeTypes[node.type].color;
    miniTrack.appendChild(mini);
  });
}

function statusText(status) {
  return { ready: "待运行", running: "运行中", done: "已完成", skipped: "已跳过" }[status] || status;
}

function buildPromptFor(type) {
  const activeShot = workflowData.shots[selectedPromptShotIndex] || workflowData.shots[0];
  const prompts = {
    script: `输出 Script JSON：${workflowData.script_type}/${workflowData.genre}/${workflowData.tone}；拆出 ${workflowData.assets.character.id}、${workflowData.assets.scene.id}、${workflowData.assets.prop.id}。`,
    analysis: `镜头拆分：${workflowData.shots.map((shot) => `${shot.id} ${shot.action}`).join("；")}。`,
    assetReq: `生成资产需求：${workflowData.assets.character.id} 角色一致性、${workflowData.assets.scene.id} 场景、${workflowData.assets.prop.id} 道具、${workflowData.assets.voice.id} 声音。`,
    assetGen: `创建资产 ID：${Object.values(workflowData.assets).map((asset) => asset.id).join(" + ")}。资产通过用户确认后锁定版本。`,
    director: ensureDirectorBlocking().prompt || buildDirectorSummary(ensureDirectorBlocking()),
    microexpression: ensureMicroexpressions().beats[ensureMicroexpressions().selected_shot_id].prompt || buildMicroexpressionPrompt(ensureMicroexpressions().selected_shot_id, ensureMicroexpressions().beats[ensureMicroexpressions().selected_shot_id]),
    storyboard: buildNineGridPrompt(ensureStoryboardWorkflow()),
    imagegen: `$imagegen 输入：${ensureStoryboardWorkflow().segment_id} 九宫格Prompt；生成后导入 Open Cowart canvas 并保存版本。`,
    gridEdit: ensureStoryboardWorkflow().revision.prompt || `选择 ${ensureStoryboardWorkflow().revision.panel_id}，填写期望、实际偏差和确认修改后生成受控编辑Prompt。`,
    prompt: activeShot.prompt,
    video: buildVideoGenerationBrief(),
    audio: `声音任务：${workflowData.audio.join("，")}；声音节奏跟随镜头停顿点。`,
    edit: buildTimelineBrief(),
    check: `检查：${workflowData.assets.character.id} 身份稳定、${workflowData.assets.prop.id} 位置连续、${workflowData.assets.scene.id} 空间不翻转、声音方向一致、无新增人物。`
  };
  return prompts[type];
}

function onNodeClick(event) {
  if (suppressNodeClick) {
    suppressNodeClick = false;
    event.stopPropagation();
    return;
  }
  const id = event.currentTarget.dataset.id;
  if (mode === "connect") {
    handleConnect(id);
    event.stopPropagation();
    return;
  }
  selectedId = id;
  render();
  event.stopPropagation();
}

function onNodePointerDown(event) {
  if (mode !== "select") return;
  const id = event.currentTarget.dataset.id;
  const node = nodes.find((item) => item.id === id);
  selectedId = id;
  dragging = {
    id,
    startX: event.clientX,
    startY: event.clientY,
    nodeX: node.x,
    nodeY: node.y,
    moved: false
  };
  event.currentTarget.setPointerCapture(event.pointerId);
}

window.addEventListener("pointermove", (event) => {
  if (dragging) {
    const dx = event.clientX - dragging.startX;
    const dy = event.clientY - dragging.startY;
    if (!dragging.moved && Math.hypot(dx, dy) < 7) return;
    dragging.moved = true;
    const node = nodes.find((item) => item.id === dragging.id);
    node.x = dragging.nodeX + dx / scale;
    node.y = dragging.nodeY + dy / scale;
    render();
  }
  if (panning) {
    offset.x = panning.offsetX + event.clientX - panning.startX;
    offset.y = panning.offsetY + event.clientY - panning.startY;
    render();
  }
});

window.addEventListener("pointerup", () => {
  suppressNodeClick = Boolean(dragging?.moved);
  dragging = null;
  panning = null;
});

wrap.addEventListener("pointerdown", (event) => {
  if (event.target.closest(".node") || event.target.closest(".canvas-toolbar")) return;
  if (mode !== "connect") {
    panning = {
      startX: event.clientX,
      startY: event.clientY,
      offsetX: offset.x,
      offsetY: offset.y
    };
  }
});

wrap.addEventListener("wheel", (event) => {
  event.preventDefault();
  const next = clamp(scale + (event.deltaY > 0 ? -0.06 : 0.06), 0.38, 1.45);
  const rect = wrap.getBoundingClientRect();
  const mx = event.clientX - rect.left;
  const my = event.clientY - rect.top;
  const worldX = (mx - offset.x) / scale;
  const worldY = (my - offset.y) / scale;
  scale = next;
  offset.x = mx - worldX * scale;
  offset.y = my - worldY * scale;
  render();
}, { passive: false });

document.querySelectorAll("[data-mode]").forEach((button) => {
  button.addEventListener("click", () => {
    mode = button.dataset.mode;
    connectStart = null;
    document.querySelectorAll("[data-mode]").forEach((item) => item.classList.toggle("active", item === button));
    wrap.classList.toggle("connecting", mode === "connect");
  });
});

document.getElementById("zoomIn").addEventListener("click", () => {
  scale = clamp(scale + 0.1, 0.38, 1.45);
  render();
});

document.getElementById("zoomOut").addEventListener("click", () => {
  scale = clamp(scale - 0.1, 0.38, 1.45);
  render();
});

document.getElementById("fitView").addEventListener("click", () => {
  fitToNodes();
  render();
});

document.getElementById("toggleMinimap").addEventListener("click", () => {
  document.getElementById("minimap").classList.toggle("hidden");
});

document.getElementById("analyzeScript").addEventListener("click", () => {
  applyScriptText(document.getElementById("scriptInput").value);
  selectedPromptShotIndex = 0;
  nodes = nodes.map((node) => node.type === "script" || node.type === "analysis" || node.type === "assetReq" ? { ...node, status: "done" } : node);
  selectedId = "n3";
  renderTimeline();
  renderBindings();
  render();
});

document.getElementById("exportWorkflow").addEventListener("click", () => {
  const payload = {
    canvas: { nodes, edges },
    workflow: workflowData,
    exported_at: new Date().toISOString()
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "open-cowart-canvas-workflow.json";
  link.click();
  URL.revokeObjectURL(url);
});

document.getElementById("runWorkflow").addEventListener("click", async () => {
  await runGraphFrom(selectedId);
});

document.querySelectorAll("[data-node-target]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".skill").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    selectWorkflowNode(button.dataset.nodeTarget);
  });
});

function selectWorkflowNode(id) {
  const node = nodes.find((item) => item.id === id);
  if (!node) return;
  selectedId = id;
  mode = "select";
  connectStart = null;
  document.querySelectorAll("[data-mode]").forEach((item) => item.classList.toggle("active", item.dataset.mode === "select"));
  wrap.classList.remove("connecting");
  const rect = wrap.getBoundingClientRect();
  scale = Math.max(scale, 0.72);
  offset.x = rect.width * 0.45 - (node.x + 123) * scale;
  offset.y = rect.height * 0.45 - (node.y + 66) * scale;
  render();
  detail.scrollIntoView({ block: "start", behavior: "smooth" });
}

function handleConnect(id) {
  if (!connectStart) {
    connectStart = id;
    selectedId = id;
    render();
    return;
  }
  if (connectStart !== id && !edges.some(([from, to]) => from === connectStart && to === id)) {
    edges.push([connectStart, id]);
    setNodeStatus(id, "ready");
  }
  connectStart = null;
  selectedId = id;
  render();
}

function addNode(type) {
  const id = `n${Date.now()}`;
  const rect = wrap.getBoundingClientRect();
  const x = (rect.width / 2 - offset.x) / scale;
  const y = (rect.height / 2 - offset.y) / scale;
  nodes.push({ id, type, x, y, status: "ready" });
  selectedId = id;
  render();
}

async function runGraphFrom(startId) {
  const order = getExecutablePath(startId);
  for (const id of order) {
    const node = nodes.find((item) => item.id === id);
    if (!node || node.status === "skipped") continue;
    setNodeStatus(id, "running");
    selectedId = id;
    render();
    await delay(280);
    setNodeStatus(id, "done");
    markDownstreamReady(id);
    render();
  }
}

function getExecutablePath(startId) {
  const visited = new Set();
  const order = [];
  const visit = (id) => {
    if (visited.has(id)) return;
    visited.add(id);
    order.push(id);
    getExecutableDownstream(id).forEach(visit);
  };
  visit(startId);
  return order;
}

function getExecutableDownstream(id) {
  const source = nodes.find((item) => item.id === id);
  if (!source) return [];
  return getDownstream(id).filter((targetId) => {
    const target = nodes.find((item) => item.id === targetId);
    return target && target.x >= source.x;
  });
}

function getDownstream(id) {
  return edges.filter(([from]) => from === id).map(([, to]) => to);
}

function getUpstream(id) {
  return edges.filter(([, to]) => to === id).map(([from]) => from);
}

function getNodeTitle(id) {
  const node = nodes.find((item) => item.id === id);
  return node ? nodeTypes[node.type].title : id;
}

function setNodeStatus(id, status) {
  nodes = nodes.map((node) => node.id === id ? { ...node, status } : node);
}

function markDownstreamReady(id) {
  const downstream = getDownstream(id);
  nodes = nodes.map((node) => {
    if (!downstream.includes(node.id) || node.status !== "ready") return node;
    return { ...node, status: "ready" };
  });
}

function isUnlocked(id) {
  const upstream = getUpstream(id);
  if (upstream.length === 0) return false;
  const node = nodes.find((item) => item.id === id);
  if (!node || node.status !== "ready") return false;
  return upstream.some((upstreamId) => {
    const upstreamNode = nodes.find((item) => item.id === upstreamId);
    return upstreamNode && ["done", "skipped"].includes(upstreamNode.status);
  });
}

function fitToNodes() {
  const rect = wrap.getBoundingClientRect();
  const padding = 96;
  const minX = Math.min(...nodes.map((node) => node.x));
  const minY = Math.min(...nodes.map((node) => node.y));
  const maxX = Math.max(...nodes.map((node) => node.x + 246));
  const maxY = Math.max(...nodes.map((node) => node.y + 132));
  const width = maxX - minX + padding * 2;
  const height = maxY - minY + padding * 2;
  scale = clamp(Math.min(rect.width / width, rect.height / height), 0.38, 1.05);
  offset.x = (rect.width - (maxX - minX) * scale) / 2 - minX * scale;
  offset.y = (rect.height - (maxY - minY) * scale) / 2 - minY * scale;
}

function extractNamedBlock(source, label) {
  const pattern = new RegExp(`【${label}】\\s*([\\s\\S]*?)(?=【|$)`);
  return (source.match(pattern)?.[1] || "").trim();
}

function parseCharacterAnchors(source) {
  return [...source.matchAll(/图片(\d+)\s*作为(.+?)的视觉锚定\+([^\n。]+)[。]?/g)].map((match, index) => ({
    id: `char_${String.fromCharCode(65 + index)}`,
    role_alias: String.fromCharCode(65 + index),
    image_ref: `图片${match[1]}`,
    name: match[2].trim(),
    requirement: match[3].replace(/严格按此图渲染/g, "").trim(),
    must_follow_reference: true
  }));
}

function parseShotCamera(camera) {
  const shotSize = camera.match(/桌面特写|手部特写|中近景|近景|中景|全景|特写/)?.[0] || "中景";
  const lens = camera.match(/\d+mm(?:\s+close focus)?/i)?.[0] || "50mm";
  const angle = /微低角度/.test(camera) ? "微低角度" : "视线高度";
  const movement = /handheld|手持|呼吸感/i.test(camera) ? "轻微手持微颤" : (/转/.test(camera) ? "受控焦点/构图转移" : "固定镜头");
  return { shot_size: shotSize, lens, angle, movement };
}

function buildExplicitMicroexpression(title, action) {
  if (/笑容僵|小心试探/.test(action)) return { baseline: "乖巧笑意尚在", trigger: "练习本被推到面前，规则重新生效", leak: "笑容停住，眼睛先落到练习本，再移向容嬷嬷", mask: "压低声量，小心试探，不做大幅动作", end_state: "紧张地等待裁定", cues: "笑容停顿 + 视线转移 + 浅吸气", negative: "no exaggerated grimace, no eye popping, no mechanical blinking, no identity drift" };
  if (/温柔缓慢收回|事故记录/.test(action)) return { baseline: "脸上仍留有温柔余韵", trigger: "取出事故记录并重申规矩", leak: "眼神的柔和先消失，嘴角逐渐归平", mask: "动作平稳、声线冷静，保持死板式威严", end_state: "严格而克制的规则执行者", cues: "目光降温 + 嘴角归平 + 手指轻点", negative: "no sudden angry face, no exaggerated scowl, no prop teleporting, no identity drift" };
  if (/端起温水|二十遍|讨价还价/.test(action)) return { baseline: "冷静掌控局面", trigger: "宫女一试图讨价还价", leak: "淡淡一瞥，几乎不可见地收紧下眼睑", mask: "端水动作不急不慢，语速平稳", end_state: "清楚落下二十遍的裁定", cues: "侧目一瞥 + 下眼睑轻收 + 平稳呼吸", negative: "no shouting, no exaggerated eyebrow raise, no cup movement error, no identity drift" };
  if (/垮下脸|捂住嘴|三十遍/.test(action)) return { baseline: "刚出现一丝希望", trigger: "二十遍与再撒娇三十遍的连续加罚", leak: "脸部瞬间垮下，嘴角下沉", mask: "委屈尾音刚拖出便立刻捂住嘴", end_state: "强行止住撒娇，认命服从", cues: "嘴角下沉 + 眼神失落 + 双手捂嘴", negative: "no cartoon crying, no exaggerated sobbing, no repeated hand motion, no identity drift" };
  if (/葡萄|极轻微笑意|切黑/.test(action)) return { baseline: "容嬷嬷闭眼维持威严，宫女一低头罚抄", trigger: "宫女一把葡萄偷偷放入容嬷嬷掌心", leak: "手指自然收紧，嘴角只抬起极轻微弧度", mask: "不睁眼、不改变靠坐姿势", end_state: "严格纪律下留下极轻的温暖余韵", cues: "手指收紧 + 单侧嘴角微抬 + 平稳呼吸", negative: "no broad smile, no eye opening, no sentimental embrace, no grape deformation, no identity drift" };
  return { baseline: "克制的中性状态", trigger: title, leak: "视线短暂停住", mask: "动作幅度保持克制", end_state: "可读但不过度的情绪落点", cues: "视线停顿 + 呼吸变化", negative: "no frozen neutral face, no exaggerated expression, no identity drift" };
}

function allocateShotDurations(sections, totalDuration) {
  const weights = sections.map((section) => {
    const spokenLength = section.dialogue.join("").replace(/[^\u4e00-\u9fffA-Za-z0-9]/g, "").length;
    return Math.max(1.2, spokenLength / 5.8 + section.action_parts.length * 0.35 + 0.5);
  });
  const totalWeight = weights.reduce((sum, value) => sum + value, 0);
  const durations = weights.map((weight) => Number((totalDuration * weight / totalWeight).toFixed(1)));
  durations[durations.length - 1] = Number((durations[durations.length - 1] + totalDuration - durations.reduce((sum, value) => sum + value, 0)).toFixed(1));
  return durations;
}

function buildExplicitStoryboardDefaults(shots, characters, sceneId, propId) {
  const refs = `${sceneId}+${characters.map((item) => item.id).join("+")}+${propId}`;
  const distribution = Array(shots.length).fill(1);
  while (distribution.reduce((sum, value) => sum + value, 0) < 9) {
    const candidates = shots.map((shot, index) => shot.duration / distribution[index]);
    const target = candidates.indexOf(Math.max(...candidates));
    distribution[target] += 1;
  }
  const panels = [];
  shots.forEach((shot, shotIndex) => {
    const count = distribution[shotIndex];
    for (let index = 0; index < count; index += 1) {
      const actionStart = Math.floor(shot.action_parts.length * index / count);
      const actionEnd = Math.max(actionStart + 1, Math.floor(shot.action_parts.length * (index + 1) / count));
      const dialogueStart = Math.floor(shot.dialogue.length * index / count);
      const dialogueEnd = Math.ceil(shot.dialogue.length * (index + 1) / count);
      const action = shot.action_parts.slice(actionStart, actionEnd).join("；") || shot.action;
      const dialogue = shot.dialogue.slice(dialogueStart, dialogueEnd).join("；");
      panels.push({
        shot_ref: shot.id.toUpperCase(),
        asset_refs: refs,
        duration: Number((shot.duration / count).toFixed(2)),
        shot_size: shot.camera_details.shot_size,
        camera_move: shot.camera_details.movement,
        action: `${action}${dialogue ? `；台词：${dialogue}` : ""}`,
        beat: `${action}${dialogue ? `；台词：${dialogue}` : ""}`,
        character_anchor: characters.map((item) => `${item.role_alias}=${item.id}/${item.image_ref}/${item.name}`).join("；"),
        scene_anchor: "员工休息包厢、暖黄台灯、深蓝灰绒面沙发、圆形茶几与全部桌面道具位置保持一致",
        performance: shot.microexpression.cues + "；" + shot.microexpression.end_state,
        continuity: "只出现A与B；练习本、事故记录、温水、葡萄、手帕位置和交接状态连续；无清晰可读文字"
      });
    }
  });
  return { asset_refs: refs, panels: panels.slice(0, 9) };
}

function parseExplicitShotWorkflow(source) {
  const shotMatches = [...source.matchAll(/【([^】]*镜头\s*([A-Z])[^】]*)】\s*([\s\S]*?)(?=【[^】]*镜头\s*[A-Z][^】]*】|【声音设计|【关键约束|$)/g)];
  if (shotMatches.length < 2) return null;
  const totalDuration = Number(source.match(/整段\s*(\d+(?:\.\d+)?)\s*秒/)?.[1] || 15);
  const characters = parseCharacterAnchors(source);
  const groundedCharacters = characters.length ? characters : [{ id: "char_A", role_alias: "A", image_ref: "未提供", name: "角色一", requirement: "视觉锚定待确认", must_follow_reference: false }];
  const sections = shotMatches.map((match) => {
    const body = match[3].trim();
    const camera = (body.match(/机位[:：]\s*([^\n]+)/)?.[1] || "固定中景").replace(/[。；]+$/, "");
    const actionLines = [...body.matchAll(/画面[:：]\s*([^\n]+)/g)].map((item) => item[1].replace(/[。；]+$/, ""));
    const actionParts = actionLines.flatMap((line) => line.split("+").map((item) => item.trim()).filter(Boolean));
    const dialogue = [...body.matchAll(/台词[:：]\s*([^\n]+)/g)].map((item) => item[1].trim());
    const sound = [...body.matchAll(/声音[:：]\s*([^\n]+)/g)].map((item) => item[1].trim());
    const action = actionLines.join("；") || match[1].trim();
    return { letter: match[2], title: match[1].trim(), body, camera, camera_details: parseShotCamera(camera), action, action_parts: actionParts.length ? actionParts : [action], dialogue, sound, microexpression: buildExplicitMicroexpression(match[1], action) };
  });
  const durations = allocateShotDurations(sections, totalDuration);
  const styleLock = (source.match(/\[STYLE LOCK\]\s*([\s\S]*?)(?=图片\d+\s*作为)/)?.[1] || "").trim();
  const sceneSetting = extractNamedBlock(source, "场景物理设置");
  const soundDesign = extractNamedBlock(source, "声音设计 全段统一");
  const keyConstraints = extractNamedBlock(source, "关键约束");
  const sceneId = "scene_ktv_staff_lounge_01";
  const propId = "prop_lounge_table_set_01";
  const characterMap = groundedCharacters.map((item) => `${item.role_alias}=${item.id}(${item.image_ref}/${item.name})`).join("；");
  const negativeConstraints = keyConstraints.split("+").map((item) => item.replace(/[。；]+$/, "").trim()).filter(Boolean);
  const shots = sections.map((section, index) => {
    const duration = durations[index];
    const dialogueText = section.dialogue.length ? `原台词按顺序：${section.dialogue.join("；")}` : "无台词";
    const prompt = `${duration.toFixed(1)}秒，${section.title}，硬切进入。STYLE LOCK：${styleLock}。角色锚定：${characterMap}。场景：${sceneSetting}。机位：${section.camera}；${section.camera_details.shot_size}，${section.camera_details.lens}，${section.camera_details.angle}，${section.camera_details.movement}。动作：${section.action}。${dialogueText}。微表演：${section.microexpression.baseline} → ${section.microexpression.trigger} → ${section.microexpression.leak} → ${section.microexpression.mask} → ${section.microexpression.end_state}。声音：${section.sound.join("；") || soundDesign}。连续性：只出现容嬷嬷和宫女一；暖黄台灯为唯一实际光源；沙发、圆桌和全部道具位置连续。约束：${negativeConstraints.join("；")}。`;
    return { id: `Shot ${String(index + 1).padStart(2, "0")}`, source_label: `镜头${section.letter}`, duration, action: section.action, action_parts: section.action_parts, camera: section.camera, camera_details: section.camera_details, dialogue: section.dialogue, sound: section.sound, microexpression: section.microexpression, prompt };
  });
  const assets = {
    character: { id: groundedCharacters[0].id, type: "character", requirement: `${groundedCharacters[0].image_ref} ${groundedCharacters[0].name}：${groundedCharacters[0].requirement}` },
    scene: { id: sceneId, type: "scene", requirement: sceneSetting },
    prop: { id: propId, type: "prop", requirement: "温水、剥好葡萄、干净手帕、黑色练习本、事故记录、签字笔的外观、位置与交接状态连续；纸面文字模糊不可读" },
    voice: { id: "voice_duo_01", type: "voice", requirement: "保留全部原台词、说话人、弱声/冷静/委屈/清楚落字和停顿节奏" }
  };
  const roleSchedule = shots.map((shot) => `${shot.id}/${shot.source_label}/${shot.duration.toFixed(1)}s：${shot.action}；${shot.dialogue.join("；") || "无台词"}`).join("\n");
  const cameraPlan = shots.map((shot) => `${shot.id}：${shot.camera}；${shot.camera_details.shot_size}；${shot.camera_details.lens}；${shot.camera_details.angle}；${shot.camera_details.movement}；硬切衔接。`).join("\n");
  return {
    source,
    script_type: "explicit_five_shot_video_prompt",
    genre: "TVB palace comedy rule-enforcement punchline",
    tone: "deadpan comedy with warm emotional residue",
    style_lock: styleLock,
    source_text_confirmation: { script_confirmed_facts: [sceneSetting, `${totalDuration}秒连续视频`, `${shots.length}个镜头硬切`, "只出现容嬷嬷和宫女一"], asset_confirmed_facts: [], assumptions: ["图片2与图片3的实际像素内容尚未附在本轮消息中，只验证文字锚定"], needs_user_confirmation: ["正式生成前需重新附上图片2和图片3"] },
    characters: groundedCharacters,
    assets,
    shots,
    negative_constraints: negativeConstraints,
    video_generation: { description: "Seedance单条连续视频，内部按A-E五镜头硬切；严格保持角色、场景、道具与台词连续。", reference_images: [], candidate_count: 4, seed: 240701, duration: totalDuration, candidates: [] },
    timeline_assembly: { reference_text: source, aspect_ratio: "16:9 anamorphic", subtitles: "none", default_transition: "hard_cut", cuts: [] },
    audio: soundDesign.split("+").map((item) => item.replace(/[。；]+$/, "").trim()).filter(Boolean),
    render_targets: ["16:9 anamorphic"],
    director_defaults: { spatial_map: `场景：${sceneSetting}\nA与B保持首帧建立的沙发左右关系，具体左右以参考图/首帧为准；圆形茶几固定在两人前方；暖黄色台灯是唯一实际光源；所有道具位置和持有状态按A-E连续。`, role_schedule: roleSchedule, dialogue_rhythm: shots.map((shot) => `${shot.id}：${shot.dialogue.join("；") || "静默表演"}`).join("\n"), camera_plan: cameraPlan },
    storyboard_defaults: buildExplicitStoryboardDefaults(shots, groundedCharacters, sceneId, propId)
  };
}

function buildWorkflowData(text) {
  const source = text.trim() || "一个角色进入空间，发现关键道具，情绪发生变化。";
  const explicitWorkflow = parseExplicitShotWorkflow(source);
  if (explicitWorkflow) return explicitWorkflow;
  const hasRain = /雨|下雨|雨声/.test(source);
  const hasLetter = /信|纸条|文件/.test(source);
  const hasFootstep = /脚步|身后|有人/.test(source);
  const hasDoor = /门|推门|进入/.test(source);
  const hasSeatedMeditation = /盘坐|打坐/.test(source);
  const hasAltar = /祭坛/.test(source);
  const hasPeachwoodSword = /桃木剑/.test(source);
  const hasBambooSound = /竹林/.test(source) && /声音|声响|动静/.test(source);
  const hasSleepToAlert = /昏睡|睡着|睡意/.test(source) && /警醒|警觉|微睁|睁眼|瞟向/.test(source);
  const isSeatedAlertScene = hasSeatedMeditation && (hasPeachwoodSword || hasSleepToAlert || hasBambooSound);
  const propName = hasPeachwoodSword ? "peachwood_sword" : (hasLetter ? "letter" : "key_object");
  const sceneTone = /昏暗|夜|冷|悬疑|恐惧/.test(source) ? "cold, tense, restrained" : "grounded, cinematic, controlled";
  const actions = isSeatedAlertScene ? [
    "面对祭坛盘坐，桃木剑横放双腿并保持不动",
    "微阖双目，看似打坐实则昏睡",
    "身后竹林声音触发眼睑轻颤与呼吸停顿",
    "眼神先于头部瞟向身后声源，结束于克制警醒"
  ] : [
    hasDoor ? "进入场景" : "建立场景",
    hasLetter ? "发现关键物" : "观察环境",
    hasLetter ? "拾起道具" : "靠近目标",
    hasFootstep ? "听见身后动静并反应" : "情绪停顿并收束"
  ];
  const assets = {
    character: { id: "char_A", type: "character", requirement: isSeatedAlertScene ? "秦剑师；稳定面部、发型、服装、盘坐轮廓与朝向" : "稳定面部、发型、服装和轮廓" },
    scene: { id: isSeatedAlertScene ? "scene_altar_bamboo_01" : "scene_03", type: "scene", requirement: isSeatedAlertScene ? `${sceneTone}；锁定祭坛、盘坐点、身后竹林声源方向与主光方向` : `${sceneTone}，保持空间布局和主光方向` },
    prop: { id: `prop_${propName}_01`, type: "prop", requirement: hasPeachwoodSword ? "桃木剑横向平放在盘坐的双腿上；全段不移动、不拔剑、不变形" : "道具位置和手部接触状态连续" },
    voice: { id: "voice_A", type: "voice", requirement: hasBambooSound ? "无对白；保留身后竹林声音触发与静默反应" : "克制、低声、贴合停顿" }
  };
  const negativeConstraints = ["no identity drift", "no extra people", "no face morphing", "no background warping", "no broken eyeline"];
  const shots = actions.map((action, index) => ({
    id: `Shot ${String(index + 1).padStart(2, "0")}`,
    duration: index === 3 ? 3 : 4,
    action,
    prompt: buildShotPrompt(action, assets, negativeConstraints)
  }));
  return {
    source,
    script_type: "short_drama",
    genre: hasFootstep || /悬疑|恐惧|危险/.test(source) ? "suspense" : "drama",
    tone: sceneTone,
    assets,
    shots,
    negative_constraints: negativeConstraints,
    video_generation: {
      description: "基于锁定资产与镜头 prompt 生成视频候选；保留角色身份、空间布局和道具状态。",
      reference_images: [],
      candidate_count: 4,
      seed: 240701,
      duration: 4,
      candidates: []
    },
    timeline_assembly: {
      reference_text: source,
      aspect_ratio: "9:16",
      subtitles: "auto",
      default_transition: "straight_cut",
      cuts: []
    },
    audio: hasBambooSound ? ["bamboo_grove_ambience", "offscreen_bamboo_sound", "held_silence_after_trigger"] : [hasRain ? "rain_near" : "room_tone", hasLetter ? "paper_rustle" : "soft_movement", hasFootstep ? "distant_footstep" : "low_music_bed"],
    render_targets: ["9:16", "16:9"],
    director_defaults: isSeatedAlertScene ? {
      spatial_map: `A始终盘坐在${hasAltar ? "祭坛前" : "固定盘坐点"}，面向祭坛；${assets.prop.id}横放双腿；竹林声源位于A身后，具体左/右方位待场景资产确认；身体不离开盘坐点，保持180度轴线与主光方向。`,
      role_schedule: `Shot 01: A盘坐面对祭坛，桃木剑横放双腿，起止位置不变。\nShot 02: A维持打坐外观，微阖双目，头略低、肩松、呼吸慢，剑不动。\nShot 03: 身后竹林声音触发；A眼睑轻颤、呼吸停半拍，头与躯干暂不动。\nShot 04: A双目微睁，眼神先瞟向身后声源；短暂停顿后头部只转几度，仍盘坐，桃木剑不动。`,
      camera_plan: `Shot 01: 4秒中景，35mm，固定镜头，建立祭坛—A—身后竹林空间关系。\nShot 02: 4秒中近景，50mm，缓慢推近，读出“似入定实昏睡”。\nShot 03: 3秒近景，85mm，固定镜头，呈现眼睑轻颤与呼吸停顿。\nShot 04: 4秒近景，85mm，固定镜头；眼先于头，禁止甩头、起身和拔剑。`
    } : null,
    storyboard_defaults: isSeatedAlertScene ? buildSeatedAlertStoryboardDefaults(assets) : null
  };
}

function buildSeatedAlertStoryboardDefaults(assets) {
  const refs = `${assets.scene.id}+${assets.character.id}+${assets.prop.id}`;
  const base = { asset_refs: refs, character_anchor: "秦剑师身份、面部、发型、服装、盘坐轮廓与朝向保持一致", scene_anchor: "祭坛、盘坐点、身后竹林声源方向、180度轴线与主光方向保持一致", continuity: "桃木剑始终横放双腿；人物不起身、不拔剑、不交换方向" };
  const rows = [
    ["SHOT 01", 1.5, "中景", "固定镜头", "建立A面对祭坛盘坐，桃木剑横放双腿", "安静、松弛，维持似入定的外观"],
    ["SHOT 01", 1.2, "中景", "固定镜头", "保持祭坛—A—身后竹林的空间关系", "双手放松，身体重心稳定"],
    ["SHOT 02", 1.4, "中近景", "缓慢推近", "A微阖双目、头略低、肩松，显出实则昏睡", "微阖眼睑、放松下颌、缓慢呼吸"],
    ["SHOT 02", 1.1, "中近景", "缓慢推近", "桃木剑仍横亘双腿，身体没有位移", "睡意持续，不增加夸张睡态"],
    ["SHOT 03", 0.8, "近景", "固定镜头", "身后竹林声音触发瞬间", "眼睑先轻颤一次，呼吸停半拍"],
    ["SHOT 03", 0.9, "特写", "固定镜头", "双目只睁成窄缝，头与躯干暂不动", "睡意尚未完全褪去，眼神开始聚焦"],
    ["SHOT 04", 0.8, "特写", "固定镜头", "眼神先向身后声源偏移", "下眼睑轻收，下颌开始收紧"],
    ["SHOT 04", 1.0, "近景", "固定镜头", "短暂停顿后头部只转几度，躯干仍面对祭坛", "动作克制，不甩头，桃木剑不动"],
    ["SHOT 04", 1.3, "近景", "固定镜头", "结束于安静但明确地警醒锁定身后声源", "睡意消退，警醒可读但不过度"]
  ];
  return {
    asset_refs: refs,
    panels: rows.map(([shot_ref, duration, shot_size, camera_move, action, performance]) => ({ ...base, shot_ref, duration, shot_size, camera_move, action, beat: action, performance }))
  };
}

function ensureTimelineAssembly() {
  if (!workflowData.timeline_assembly) {
    workflowData.timeline_assembly = {
      reference_text: workflowData.source || "",
      aspect_ratio: "9:16",
      subtitles: "auto",
      default_transition: "straight_cut",
      cuts: []
    };
  }
  return workflowData.timeline_assembly;
}

function updateTimelineAssemblyFromInputs(referenceInput, aspectInput, subtitlesInput, transitionInput) {
  const timelineData = ensureTimelineAssembly();
  timelineData.reference_text = referenceInput.value.trim();
  timelineData.aspect_ratio = aspectInput.value.trim() || "9:16";
  timelineData.subtitles = subtitlesInput.value.trim() || "auto";
  timelineData.default_transition = transitionInput.value.trim() || "straight_cut";
}

function buildTimelineCuts(timelineData) {
  let cursor = 0;
  const reference = timelineData.reference_text || workflowData.source;
  return workflowData.shots.map((shot, index) => {
    const start = cursor;
    cursor += shot.duration;
    return {
      shot_id: shot.id,
      start,
      end: cursor,
      action: shot.action,
      reference_basis: reference.slice(0, 180),
      audio_cue: workflowData.audio[index] || workflowData.audio[0],
      subtitle_mode: timelineData.subtitles,
      transition: index === 0 ? "start" : timelineData.default_transition
    };
  });
}

function buildTimelineBrief() {
  const timelineData = ensureTimelineAssembly();
  const cutText = timelineData.cuts.length ? `${timelineData.cuts.length} 个切点` : "尚未生成切点";
  return `时间线装配：依据参照文本生成 ${cutText}，主比例 ${timelineData.aspect_ratio}，字幕 ${timelineData.subtitles}，转场 ${timelineData.default_transition}。`;
}

function ensureVideoGeneration() {
  if (!workflowData.video_generation) {
    workflowData.video_generation = {
      description: "",
      reference_images: [],
      candidate_count: 4,
      seed: 240701,
      duration: 4,
      candidates: []
    };
  }
  return workflowData.video_generation;
}

function updateVideoGenerationFromInputs(descriptionInput, countInput, seedInput, durationInput) {
  const videoData = ensureVideoGeneration();
  videoData.description = descriptionInput.value.trim();
  videoData.candidate_count = clamp(Number(countInput.value) || 1, 1, 8);
  videoData.seed = Number(seedInput.value) || 240701;
  videoData.duration = clamp(Number(durationInput.value) || 4, 2, 12);
}

function readImageReference(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      resolve({
        id: `ref_${Date.now()}_${Math.random().toString(16).slice(2, 8)}`,
        name: file.name,
        type: file.type,
        size: file.size,
        data_url: reader.result
      });
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

function buildVideoGenerationBrief() {
  const videoData = ensureVideoGeneration();
  return `视频生成输入已保存：${videoData.reference_images.length} 张参考图，${videoData.candidate_count} 个候选，seed ${videoData.seed}，${videoData.duration}s。${videoData.description}`;
}

function applyScriptText(text) {
  const normalized = text.trim() || "一个角色进入空间，发现关键道具，情绪发生变化。";
  document.getElementById("scriptInput").value = normalized;
  workflowData = buildWorkflowData(normalized);
}

function extractScriptText(rawText, fileName) {
  const ext = fileName.split(".").pop().toLowerCase();
  if (ext !== "json") return rawText.trim();
  try {
    const data = JSON.parse(rawText);
    return findTextInJson(data) || JSON.stringify(data, null, 2);
  } catch (error) {
    return rawText.trim();
  }
}

function findTextInJson(value) {
  if (typeof value === "string") return value;
  if (!value || typeof value !== "object") return "";
  const preferredKeys = ["source", "script", "content", "text", "story", "screenplay", "prompt"];
  for (const key of preferredKeys) {
    if (typeof value[key] === "string" && value[key].trim()) return value[key].trim();
  }
  if (Array.isArray(value)) {
    return value.map(findTextInJson).filter(Boolean).join("\n\n");
  }
  return Object.values(value).map(findTextInJson).filter(Boolean).join("\n\n");
}

function buildShotPrompt(action, assets, negativeConstraints) {
  return `Use ${assets.character.id} + ${assets.scene.id} + ${assets.prop.id}. ${assets.character.id} ${action}。保持角色身份、服装、发型和脸部一致。Static medium shot, 35mm lens feel. ${negativeConstraints.join(", ")}.`;
}

function buildNineGridPrompt(board) {
  const panelLines = board.panels.map(buildPanelLookupPrompt).join("\n\n");
  return `Use $imagegen to create one exact 16:9, target 2048x1152, strict 3x3 storyboard for ${board.segment_id}. Read left-to-right, top-to-bottom. Segment duration: ${calculateSegmentDuration(board).toFixed(2)} seconds. Use black/white/neutral-gray rough pencil narrative art; color only for sparse production annotations.\n\nMandatory bidirectional labels: each panel shows its exact panel ID top-left, SHOT REF bottom-left, and green REF asset IDs bottom-right. These labels must match the prompt and actual panel content.\n\n${panelLines}\n\nPreserve character and scene anchors, spatial axis, identities, action order, performance, eyelines, prop state and lighting continuity. No prose, dialogue balloons, timeline, logo, watermark or other readable text.`;
}

function buildGridRevisionPrompt(board) {
  const revision = board.revision;
  const targetVersion = board.versions.length ? board.versions[board.versions.length - 1].id : `${board.segment_id}-VXX`;
  const panel = board.panels.find((item) => item.id === revision.panel_id);
  const panelIndex = Math.max(0, board.panels.findIndex((item) => item.id === revision.panel_id));
  const row = Math.floor(panelIndex / 3) + 1;
  const col = panelIndex % 3 + 1;
  return `Edit Image 1, the exact existing storyboard version ${targetVersion}. Target only row ${row}, column ${col}, panel ${revision.panel_id}. Preserve the 16:9 strict 3x3 grid, borders, rough pencil style, identities, continuity, and every other panel pixel-for-pixel where possible.\n\n${panel ? buildPanelLookupPrompt(panel) : `[${revision.panel_id}｜${board.shot_ref}｜REF:${board.asset_refs}]`}\n\nExpected: ${revision.expected || "use the confirmed panel beat and reference mapping"}\nActual deviation: ${revision.actual || "not specified"}\nChange only: ${revision.change || "correct the panel to match its prompt and REF"}\n\nDo not modify P01-P09 except ${revision.panel_id}. Keep all mandatory panel IDs, SHOT REF labels and green asset REF labels exact. Preserve the saved duration, shot size, camera movement, character anchor, scene anchor, action, expression performance and continuity mapping. Keep narrative art black/white/gray; color only for production annotations. No other text, logo or watermark.`;
}

function downloadCanvas(canvas, fileName) {
  if (!canvas || !canvas.width || !canvas.height) return;
  canvas.toBlob((blob) => {
    if (!blob) return;
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }, "image/png");
}

function downloadJson(payload, fileName) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function persistPromptLibrary(board) {
  const payload = {
    source: workflowData.source,
    segment_id: board.segment_id,
    panels: board.panels,
    quick_lookup_versions: board.quick_lookup_versions,
    segment_duration: calculateSegmentDuration(board),
    saved_at: new Date().toISOString()
  };
  try {
    localStorage.setItem("open-cowart-prompt-library-v1", JSON.stringify(payload));
  } catch (error) {
    console.warn("Prompt library could not be persisted", error);
  }
}

function restorePromptLibrary(board) {
  if (board.prompt_library_restored) return;
  board.prompt_library_restored = true;
  try {
    const saved = JSON.parse(localStorage.getItem("open-cowart-prompt-library-v1") || "null");
    if (!saved || saved.source !== workflowData.source || saved.segment_id !== board.segment_id) return;
    board.panels = board.panels.map((panel, index) => normalizeStoryboardPanel(saved.panels?.[index] || panel, index, saved));
    board.quick_lookup_versions = Array.isArray(saved.quick_lookup_versions) ? saved.quick_lookup_versions : [];
  } catch (error) {
    console.warn("Prompt library could not be restored", error);
  }
}

function normalizeSegmentId(value) {
  const match = String(value || "").toUpperCase().match(/(?:SEG|S)?\s*0*(\d+)/);
  const number = match ? Number(match[1]) : 1;
  return `SEG${String(number).padStart(2, "0")}`;
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch (error) {
    const fallback = document.createElement("textarea");
    fallback.value = text;
    document.body.appendChild(fallback);
    fallback.select();
    document.execCommand("copy");
    fallback.remove();
  }
}

function splitConstraints(value) {
  return value
    .split(/[,，\n]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

renderPalette();
renderTimeline();
renderBindings();
fitToNodes();
render();

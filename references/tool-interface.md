# 工具接口（8.2）

双轨交付在task.delivery中指定outputs为dual；copy_format默认full，只有用户明确要精简才填compact。full按完整模板复制，每镜独立六项音效；相对时序也用独立的“——【镜头标题】”行分镜。双轨的compile同时提交text（制片主稿）与model_ready_prompt（本段直投稿），显式时码使用同一组timing_nodes标题。分集装订：episode命令读取按剧情排序的运行文件路径JSON数组（相对清单所在目录），例如 python scripts/workflow.py episode manifest.json --out episode.json。首段含完整共用页；共用页重复时须一致，装订后只保留一份全集资产，model_ready_prompts按唯一片段编号取独立文本。局改后旧直投稿失效，重新编译完整片段，不拿单事件补丁直接生成。

Python 3，无第三方运行依赖。输入只读，--out写新版本，不能覆盖输入。语义识别、设计和复核由模型完成，程序不调用模型服务。

## 单段交稿

整段提示词只取一个片段，复用既有 `init/context/submit/repair/deliver`，不用开整集工程。总管准备 `segment.json`（来源和事件、原句、首尾及需求，按[项目合同](project-contract.md)）和 `task.json`（如 `{"mode":"prompt","handoff":"departments","delivery":{"duration":19,"timing":"explicit"}}`）。`reason` 短记本轮范围；默认一份完整稿，可以用 `delivery.outputs:"dual"` 同时产主稿和直投稿。片段已锁长时保留排期，用户明确要求不显示时码用 `relative`。每站的程序输入取自当前状态，不预写下一站稿。

```text
python scripts/workflow.py init segment.json task.json --out run-00.json
python scripts/workflow.py context task.json source --project run-00.json --out source-in.json
python scripts/workflow.py submit run-00.json source source-out.json --context source-in.json --out run-01.json
python scripts/workflow.py deliver checked-run.json --out checked-text.json
```

按 `workflow.plan.steps` 重复中间两步，每次用上一站的新运行文件；未通过时不能取下一站的上下文。各站读取 `upstream` 的实际成果，不仅是状态名。交接字段沿用下文工程命令及以下补充：

- 剧本部在常规源文映射之外交 `design`（事件 ID → 可拍因果与固定首尾）。资产、动作、表演、特效按同样的事件设计形状只交本专业的成果。
- 摄影站先从当前上下文取 `camera_source` 原样与 `view_plan` 运行下节 `storyboard-plan`，再排 `design` 镜头列表。提交常规事件 `design`，另带 `camera_plan:{view_plan,plan_receipt,design}`。该回执绑定摄影的实际前序输入。新镜头未定前不打开声音站。
- 声音站交常规事件 `design` 和 `shot_audio`：键是摄影已定的镜头标题，每镜值为六个单行字符串字段：动作层、特效层、环境层、同步节点、主次变化、跨镜承接。编译逐字承接已定的取景词组、运动与六项声音（仅授权精简直投有声音例外），不是再做一次设计。
- 复核阶段在常规覆盖外提交 `camera_review`。以 `continuity` 核最后事件末态，并对照每个 `beat:<id>`、`shot:1` 等逐镜及 `cut:1` 等切口；已排到六秒的镜另核 `hold:<镜号>`，不是时长上限。每项有 `status:"met"`、实际理由和各份正文的 `evidence`。证据键为 `master`／`direct`，逐镜和末态填短引句；beat 内填 `{"shot:2":"关联镜画面引句"}`；cut 内填 `{"out":"上一镜末画面","in":"下一镜起画面"}`；hold 内填依次出现且不同的 `{"first":"早处画面","last":"后处画面"}`。声音栏不能替代画面。缺口填 `status:"unmet"`、`return_to`、`reason`；或直接走 `repair`，不交虚假证据。

当前部门缺件时先补它；上游需改才 `repair`，保留之前已经通过的站和旧运行文件。只有 `deliver` 返回的指定正文可交，不附检查和接力记录。阻断时不生成交稿；不拿 `light-deliver` 的临时卡跳过接力。程序核结构、回执及真实引文，拍法收益仍由复核判断。历史旧档按原合同可读；本轮新完整提示词走部门接力。

### 分镜版轻量交稿

先建立只含 `source` 和 `view_plan` 的短交接。整段接力使用摄影上下文的 `camera_source` 作为 `source`。只交分镜时另建 `source`，包含 `scope`（授权范围）、`requirements`（已锁项ID到说明）、`outputs:["storyboard"]`、`dialogues`（按序原句）、`timing` 与已锁定的 `duration`。`view_plan` 按观众应看懂变化的顺序排列，每个关键看点只写 `id`（短英文或数字 ID）、`change`（变化）、`see`（必须看清）、`choice`（取景取舍和理由）。在逐镜起草前运行：

```text
python scripts/workflow.py storyboard-plan viewing-plan.json --out view-receipt.json
```

此步只核交接并返回看点 ID 和短回执，不输出镜头。带同一份 `view_plan` 和 `plan_receipt` 到摄影提交（独立分镜带原 `source` 到 `light-deliver`）。若稿没拍到，返工而不是悄改计划；回执不能代替导演的判断。

两路线共用下列摄影交接。只交分镜时只放 `drafts.storyboard`，不用主稿、直投稿和提示词栏目；正文布局按用户要求：

- `design` 每镜保留 `heading`（实际正文中唯一的镜头标题，显式秒数也写在这里）、`watch`（观看任务）、`beats`（此镜承担的计划 ID，可多项，非关键连接可空），以及引用本镜实际正文的 `focal`（焦段或视角）和 `framing`（机位与构图短句）。要检排期时，每镜加 `start`、`end`。已定总长即使用户不要可见时码，也保留内部排期。
- `motion` 在本镜选一组：`{"fixed":"固定机位"}`，或 `{"trigger":"起动触发","path":"运动方向与路径","stop":"具体停止点"}`；右侧值须是本镜正文的具体引句，不能用景别代替。
- 只交分镜的 `review`：先查每个 `beat:<id>`，证据用 `{"shot:2":"一处真实引句"}` 或多镜引句；须在关联镜头，后揭示的看点不能被提前拍明。再核锁点、逐镜和切口。锁点和镜头项证据键为 `storyboard`；切口用 `{"out":"上镜末的画面","in":"下镜起的画面"}`。漏拍、错序或不连贯用 `unmet` 加 `return_to` 和原因。不要求一看点一镜；单镜没有切口项。

独立分镜用 `python scripts/workflow.py light-deliver handoff.json --out checked-board.json`，只从 `outputs.storyboard` 取通过的原稿。结构通过不代替对焦段取舍、台词余量、动作连贯和切镜收益的语义复查。

## 工程命令

```text
python scripts/workflow.py plan task.json --project project.json
python scripts/workflow.py init project.json task.json --out run-01.json
python scripts/workflow.py context task.json source --project run-01.json --out source-context.json
python scripts/workflow.py submit run-01.json source source-result.json --context source-context.json --out run-02.json
python scripts/workflow.py discover run-02.json discovered.json --out run-03.json
python scripts/workflow.py repair run-05.json camera "反应看不清，改摄影" --out run-06.json
python scripts/workflow.py check run-06.json
python scripts/workflow.py refresh-rules run-06.json --out run-06-current-rules.json
python scripts/workflow.py workbench-json grid-checked.json --out workbench-project.json
```

source：checked_event_ids、source_coverage（源文行ID→event_ids/reason）；专业模块：design（事件ID→设计）。
action/vfx的context分别附action_candidates/vfx_candidates，按事件与负责需求匹配本地库，明确ACT-/VFX-ID优先、完整名其次、关键词加权最后。自动默认最多2类，明确ID涉及更多类时完整提供指定类；候选不是已批准的新能力。可在已有requirements.description指定ID，无需写进故事。
compile：text、event_ids、dialogue_ids、coverage；有台词还需utterances（id/speaker/start/end，最后两项是正文字符位置）。全稿prompt且delivery.timing=explicit时，必须提交timing_nodes；节点heading与正文章节同名，起止数字也必须一致，例如“——0—2秒：【开场】”不能登记为0—15秒。relative无时码稿可不交，revise不替换全段排期。
validate：content_checked、evidence、coverage、requirement_reviews、limitations。coverage对应完整需求表，值为正文确切引文或字符范围；不能用笼统引用掩盖未完成内容。
discover：reason、requirements数组，元素含id/kind/description/source_ids/event_ids/source_quote。只补处理环节，不改原文事实。
requirements单项可附specialties数组，见[专项登记](specialty-selection.md)：performance对应microexpression，vfx对应vfx-techniques。无需重复写features；discover同样支持。程序校验声明后按工序实际装入全文，旧context不能用于新专项提交；不接受任意文件路径或包外skill调用。

只扩写按[创作准备](creation-preparation.md)由模型交付剧本，不调用本CLI；没有新增expand命令。creation为可选的模型交接记录，不是脚本认证的扩写结果。

每次submit先取当前context，使用--context交接；规则、源文、计划或上游有变，旧回执将失效。五份共享方法由主责工序读全文，接力工序按职责读取原文所需章节；rules.path保留来源，rules.text是当次实际下发的全文或章节，回执校验实际内容。programmatic API submit的第四参数为context返回的receipt。哈希不是用户认证，也不证明模型已理解规则。maintain仍需明确授权记录，不能用补调路径扩权。

绑定项目的context按已登记能力加载适用的专项方法；无项目的context仅能预览候选。check和绑定context的rules_review分开报告历史记录状态和当前规则状态：checked_under_older_rules表示至少一处已交接工序的规则包指纹已变化或不可核验，不等于旧结果错误。changed_modules是直接变化的工序，rerun_modules是需要重做的已交接工序，remaining_modules另含原本未做的工序，keep_modules为可继续使用的前缀。结构检查通过不代表当前规则复核通过，更不代表成片通过。

同一合同且计划结构兼容时，refresh-rules要求另存到不存在的新文件；保留旧稿、已通过的前缀、旧结果和回执，工作流标成rule_refresh_required。重新取resume_from的context再提交；不占返修/补调预算。示例：只改编译规则时，保留上游设计和摄影，仅重做编译与复核。路径注册表、合同或源事实不兼容时仍走另存并init的迁移路径，不能以刷新替代。

局改需要master_sections，每任务一个事件；多事件另分任务或走全稿。九宫只写panels（id/event_ids/sample_time/prompt），grid九格，edit_grid目标一格。真实出图和用户接受另行进行。

旧8.0/8.1运行项目重新init，旧记录保存在workflow_archives；不要直接手改contract_version绕过迁移。
8.2.1保留8.2数据合同，但规则注册表有变；已有8.2.0的运行记录同样先另存，再init归档。重新init保留sources、events和已有主稿，不代表旧工序已通过新版规则。
回归：python -m unittest discover -s tests -p "test_*.py"；node --test tests/event-core.test.cjs；保存样例的CLI串跑：python tests/run_sample.py <独立输出目录>。这些不代表成片验证。

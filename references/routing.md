# 调度协议

## 语义识别与程序补调
先按[创作准备](creation-preparation.md)确定忠实改编、授权扩写或仅补拍法。只扩写不建立生产workflow；准备好完整底稿且要求继续提示词时，才进入以下程序化调度。
模型先读取完整来源，提取事件、对白、约束和逐事件能力需求。当前用户意图决定mode，不用关键词推断维护授权。用户不必列模块；features是提示，程序会结合底稿结构和需求清单补调。

任务JSON例：`{"mode":"prompt","features":[],"scope":[],"reason":"含对白和动作；请由底稿核对专业需求"}`。
mode：prompt主稿、revise单事件局改、grid已有主稿九宫、edit_grid单格修改、workbench保存恢复、discuss技能讨论、maintain明确授权的维护。
features：action/performance/vfx/assets/sound。程序从登记对白补表演和声音，从事件需求或保守声响信号补声音；从events.requires和requirements补能力；少量攻防/法术词只作保守补调信号，不代表自然语言理解，也不能以无命中判定无需模块。模型必须逐事件检查特殊需求。
专项按[专项登记](specialty-selection.md)写入对应需求的specialties；不依赖特定中文词也能明确装入白名单资料。专业决策与协作交接遵循[专业职责](design-boundaries.md)。

## 路线
prompt/revise：source → 按底稿与需求覆盖补齐assets/action/performance/vfx/sound → camera → compile → validate。
grid/edit_grid：source → 必要assets → sampling → validate。已有主稿的动作由主稿核对，不强制重新设计；无主稿先走prompt。
workbench：workbench → validate。discuss只讨论；maintain读取维护制度并登记明确授权，不由程序自行改代码。

## 执行中补调
当前模块发现遗漏需求，用discover提交需求ID、kind、description、source_ids、event_ids、source_quote及原因。引用必须存在于源文，不能借补调新增剧情或能力。多项同时发现就批量登记。
需要专项时在新需求附specialties数组；同样受真实引句、负责事件与专业一致性检查。改剧情回创作准备并保存旧底稿重新init，不借补调越过授权。
程序重建计划，保留共同且有效的上游结果；新增/受影响的工序起及其下游失效并存档。不能拿旧摄影/编译结果绕过刚补入的动作或声音工序。补调与返修共享最多两轮预算，耗尽则明确未解决内容，不能静默删需求。

## 读取与提交
context返回实际规则文件、专业分配的事件、必要前后状态、需求覆盖表及上游结果。已声明具体事件覆盖时，专业模块只提交这些事件，并附版本回执。submit必须携带当前context文件；上游、需求、规则或返修轮次变化后重新取context。回执只能证明与当前提供的规则包一致，不能证明模型真正理解或执行了文字。
需求引用通过不等于语义落实。全稿任务的 source 核对全部来源的每个非空段落，局部任务核对关联来源，compile与validate分别给出每项需求的实际正文位置，最终仍对照原文检查。详见coverage-contract.md。

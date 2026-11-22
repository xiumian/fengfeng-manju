# 专项需求登记与实际加载

先按事件意义判断所需方法，再登记专项；用户不必自己写ID。关键词是保守兜底，不代表自然语言理解，无命中不等于无需专项。不把全部专项默认塞入所有上下文。

本版显式专项白名单与 `scripts/workflow_rules.py:SPECIALTIES` 对应：

| specialties ID | requirement.kind | 实际装入 | 模型判断的适用场景 |
|---|---|---|---|
| microexpression | performance | microexpression-cues.md | 细微态度泄露、掩饰或言行反差需要具体可见线索，不能只写情绪名 |
| vfx-techniques | vfx | vfx-techniques.md | 需细化效果的分解、材质运动、残留或视觉强调方法，不只指定外观名称 |
| realistic-fight | action | [写实打斗导法](production-specialties/realistic-fight/guide.md)＋动作与受力附页 | 双方必须有可见的接挡／落空、受力与顺势变化；奇幻打斗可按需借这些影视方法，不取消已定设定 |
| vfx-fight | vfx | [特效打斗导法](production-specialties/vfx-fight/guide.md)＋效果特征附页 | 复合大招、主次效果、爆发边界、形态参考或多个效果需要区分；可按需查内置库 |
| impact-frame | vfx | [冲击帧导法](production-specialties/impact-frame/guide.md)＋冲击构图附页 | 关键接触、对撞、贯穿、压伏或碎裂需要一个可见的击点；VFX定画面和恢复，camera决定同镜重音或短切 |
| director-handoff | camera | [导演衔接](production-specialties/director-handoff/guide.md)；同一事件给 source、compile、validate 下发对应短页 | 多段续戏、采用尾帧、多人换位或关键决定要从拆戏一直保到直投稿。无外部运行要求，不增设工序 |
| scene-storyboard | camera | [跨风格分镜](production-specialties/scene-storyboard/guide.md)＋空间状态与预算 | 有拍法选择、线索揭示、多人或动作交接时，需要确定每镜拍什么、什么时候切或留，以及换角度后谁看得见 |
| emotion-expression | performance | [近景表情与情绪转折](production-specialties/emotion-expression/guide.md)＋可见线索选择 | 表情起落、听者改变决定、动作持续时的可见反应；关注变化，不必和一般 microexpression 同报 |

在现有 requirements 单项中增加可选 `specialties` 数组，例如原文为“她接过信，神色如常。”：

```json
{"id":"R:reaction","kind":"performance","description":"用短暂的可见变化承载人物收到信息后的反应，不改变剧情结果。","source_ids":["S1"],"event_ids":["E1"],"source_quote":"她接过信，神色如常。","specialties":["microexpression"]}
```

kind 决定所属工序，event_ids 决定负责事件，specialties 决定额外资料。不需要在 features 再抄一遍。未知ID、错专业、重复ID、字符串代替数组和任意路径被拒绝。多个需求选同一专项只装一次。九宫任务沿用主稿，不因专项声明重开专业创作工序。

执行中才发现需求，沿用 discover 的 reason/requirements 接口，在新需求中附 specialties 和真实源文引句；同一事实已登记也可补一项更细的方法需求，不能借此改事实。程序重新安排工序、存档失效下游并要求新context，旧回执不可沿用；共享现有两轮补调/返修预算。

检查实际 context.rules 的 path 与全文以及 receipt.rules_hash，不只查计划或日志里有没有文件名。覆盖证据仍须指出最终正文如何兑现该需求；装入文件、哈希一致均不证明模型理解或效果通过。

招式类别库仍按既有匹配最多装入两类；本版没有新增其显式ID接口，也没有自动调用包外独立skill。不在白名单但确需的方法先报告缺口，不编造ID或假装已读取。

极速直出／高燃重构不建工程时，按上表的事件含义直接打开专项导法与所需附页；没有使用的专项不读。工程档为真实来源登记对应ID；多种确实适用时可并用，同一职能优先最贴合的一套。导演衔接按本段涉及的来源、摄影、编译、复核分别装入短页，不让无关事件、九宫或工作台路线重开导演设计。见[专项总览](production-specialties/README.md)。发行版专项不依赖外部规则包或脚本。

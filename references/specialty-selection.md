# 专项需求登记与实际加载

先按事件意义判断所需方法，再登记专项；用户不必自己写ID。关键词是保守兜底，不代表自然语言理解，无命中不等于无需专项。不把全部专项默认塞入所有上下文。

本版显式专项白名单与 `scripts/workflow_rules.py:SPECIALTIES` 对应：

| specialties ID | requirement.kind | 实际装入 | 模型判断的适用场景 |
|---|---|---|---|
| microexpression | performance | microexpression-cues.md | 细微态度泄露、掩饰或言行反差需要具体可见线索，不能只写情绪名 |
| vfx-techniques | vfx | vfx-techniques.md | 需细化效果的分解、材质运动、残留或视觉强调方法，不只指定外观名称 |

在现有 requirements 单项中增加可选 `specialties` 数组，例如原文为“她接过信，神色如常。”：

```json
{"id":"R:reaction","kind":"performance","description":"用短暂的可见变化承载人物收到信息后的反应，不改变剧情结果。","source_ids":["S1"],"event_ids":["E1"],"source_quote":"她接过信，神色如常。","specialties":["microexpression"]}
```

kind 决定所属工序，event_ids 决定负责事件，specialties 决定额外资料。不需要在 features 再抄一遍。未知ID、错专业、重复ID、字符串代替数组和任意路径被拒绝。多个需求选同一专项只装一次。九宫任务沿用主稿，不因专项声明重开专业创作工序。

执行中才发现需求，沿用 discover 的 reason/requirements 接口，在新需求中附 specialties 和真实源文引句；同一事实已登记也可补一项更细的方法需求，不能借此改事实。程序重新安排工序、存档失效下游并要求新context，旧回执不可沿用；共享现有两轮补调/返修预算。

检查实际 context.rules 的 path 与全文以及 receipt.rules_hash，不只查计划或日志里有没有文件名。覆盖证据仍须指出最终正文如何兑现该需求；装入文件、哈希一致均不证明模型理解或效果通过。

招式类别库仍按既有匹配最多装入两类；本版没有新增其显式ID接口，也没有自动调用包外独立skill。不在白名单但确需的方法先报告缺口，不编造ID或假装已读取。

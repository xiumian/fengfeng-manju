# 文件分级与最小读取表 — fengfeng

## 加载纪律
先识别主人当前交付，不按文件数量决定上下文。只有进入下一阶段才补读该阶段契约；已在当前上下文读过且未修改的文件不反复读取。路径相对本文件。目录包含不等于需要加载，代码在需要运行/调试时读取，不全文灌入创作上下文。

|级别|用途|加载时机|
|---|---|---|
|L0|SKILL.md：边界与入口|调用skill时|
|L1|本表、当前任务契约／路由|选择当前阶段；视频/视听按prompt-execution.md必读集合，不受两份入口限制|
|L2|knowledge/、storyboard/专项知识、特效库|出现对应问题才选具体文件，不整目录加载|
|L3|工具命令、模板、assets/、scripts/|执行、交接或生成所需资源；代码仅调试时展开|
|L4|tests/、resource-map.json、source-verification-matrix.json、验收/迁移资料|明确测试、评分、源能力审计或旧工程迁移时；日常创作不加载|

## 当前任务最小集合
|任务|先读|仅在需要时追加|默认不读|
|---|---|---|---|
|只写故事／剧本|[创作路由](craft-routing.md)，按该路由选剧本专项|对白、表演、动作专项|九宫、工作台、资产流程、验收和溯源大表|
|只规划时间轴／九格|[统一契约](contracts.md)，视听规划加[通用核心](av-core.md)|打斗加action-visual-grammar.md；真的制图才读九宫契约|工具代码、资产全流程、平台适配|
|整板九宫图|[统一契约](contracts.md)、[九宫制作契约](storyboard-contract.md)|需要回填/编辑才读工作台；实际查看并附画风样板|全创作知识、评分、溯源大表|
|修改已有单格|[九宫制作契约](storyboard-contract.md)|实际合成/保存才读工作台；仅该格及依赖事件|其他无关SEG、整项目历史、全特效库|
|只写视频正文|[执行链](prompt-execution.md)、[通用核心](av-core.md)、[亡灵模板](video-template.md)、[投喂检查](prompt-feeding-checklist.md)|打斗必加action-visual-grammar.md；特效按需；时间/映射问题追加统一契约|九宫画内标注规则、工作台、资产出图|
|角色／场景／道具资产|[资产制作](asset-production.md)|仅对应资产知识；亲缘明确需要才追加|视频、全九宫及验收规则|
|启动／恢复／保存工作台|[工作台](workbench.md)、[工具命令](tool-commands.md)|编辑哪类内容再读对应契约|全剧作知识和审计大表|
|修复／交付|[质量流程](quality-workflow.md)|具体问题专项；正式投喂追加投喂检查；100分评分才读acceptance.md|无关阶段及源能力大表|
|全流程制作|[生产流程](production-pipeline.md)|逐阶段依次读取上表，不一次加载全套|尚未进入的阶段|

## 可选分支
- 高燃/玄幻/武学：[动作路由](action-routing.md)；具体技能才读[特效库](combat-vfx-library.md)。
- 模型/平台交接：明确需求才读[平台交接](platform-handoff.md)与[接口登记](model-interfaces.md)；历史参数不得冒充实时能力。
- 功能查询：[能力索引](capability-index.md)；它是入口表，不是日常必读。
- 源能力保留审计：明确审计才读source-verification-matrix.json、resource-map.json；禁止为了普通创作扫描全表。
- 旧工程迁移：主人明确选择后按工具命令执行；不是新项目必经步骤。

## 规则归属与冲突处理
入口仅保留核心边界。数据/映射规则归contracts.md；画风、英文显示字段与线标归storyboard-contract.md；生命周期归workbench.md；通用视听规则归av-core.md，视频执行归prompt-execution.md，栏目归video-template.md；实际工具指令归tool-commands.md。引用不代表递归加载。
旧knowledge/storyboard资料是专题参考，不覆盖当前契约：与当前亡灵正文、英文画内文字或非强制标注规则冲突时使用当前契约。若两个当前契约冲突，报告具体条款再处理，不自行加载全库找答案。
本分级是读取规程，不是自动上下文加载器；不同任务所需专项不同，不承诺固定token数。


## 当前视听运行边界
视听必读与旧资料排除范围以prompt-execution.md为准；maintenance/与BUGS.md仅明确归纳/审计时读取。此为读取纪律，不是自动加载器。

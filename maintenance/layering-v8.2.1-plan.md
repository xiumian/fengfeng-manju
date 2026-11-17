# v8.2.1 分层优化设计与实施计划

日期：2026-11-17。起点：7f90ed3e0ae614b785c9aab6f837a0f62048e7fb。
授权：主人提出“那就优化这些内容”，并确认“可以的”。仅维护本仓库 skill；不修改工作台、安装副本、模板正文，不上传。

## 已确认设计

采用补齐契约与定点修改调度，不重写生产流程。
- 创作准备：新增 `references/creation-preparation.md`，区分忠实改编、授权扩写、仅补拍法；交付完整剧本/事件、原始来源和补充记录。只扩写就停止，未确认设计不冒充原文。该阶段由模型执行，不伪称新增自动写剧本程序。
- 专业边界：新增 `references/design-boundaries.md`，明确动作/表演等模块提出观看需求，摄影作镜头决策，编译沿用。迁移表演中的具体拍法案例到摄影按需资料，保留细节。
- 专项加载：需求对象可显式声明 `specialties:["microexpression"]` 或 `["vfx-techniques"]`，使用固定注册表，不接受任意路径。需求 kind 必须匹配专业；仍用既有需求选工序、分事件、discover补调、覆盖与回执机制。关键词仅作兜底。来源工序实际收到准备与专项登记契约，专业上下文实际包含专项全文。
- 验证：反例测试无触发词的显式专项加载、无关事件隔离、非法声明、补调失效与旧回执、没有声明的旧项目兼容。文档测试检查扩写权限与交接位置，但不将文本存在当作创作能力验收。

## 顺序执行计划

### 1. 先写失败测试
- [x] 新建 `tests/test_layering.py`，调用真实 `workflow.init/context/discover/submit` 和 `workflow_rules.select_rules`。
- [x] 用无关键词事件与显式专项断言专业工序入选、规则全文入上下文、哈希一致；对未知/错专业/错类型/重复专项断言 ValueError。
- [x] 测试新准备契约和唯一职责归属文本。
- [x] `python -m unittest discover -s tests -p test_layering.py -v`，确认因缺少功能而失败。

### 2. 最小实现与规则修改
- [x] `scripts/workflow_rules.py` 加固定 `SPECIALTIES` 注册和 `validate_specialties(kind, specialties)`；`select_rules(..., specialties=())` 合并显式选择与关键词候选，去重并读取全文。
- [x] `scripts/workflow_coverage.py` 对每条 requirement 校验可选 specialties；不另建第二份需求清单。
- [x] `scripts/workflow.py:stage_rules` 仅收集当前 owner 的专项交给加载器，复用既有 rules_hash/coverage_hash 和 discover 下游失效。
- [x] 入口先识别讨论与维护，再引导创作准备；更新 routing/project-contract/coverage-contract/tool-interface 和专业模块。
- [x] 表演保留可见反应需求，具体镜头方法移到 `references/performance-camera-methods.md`；摄影工序装入，保持方法完整。
- [x] 同步本地开发版 8.2.1、变更说明；运行合同保持 8.2，字段为可选向后兼容；规则/需求变动仍使旧回执失效。

### 3. 验证与交付
- [x] 新测试通过后运行 Python 流程回归、包检查与保存样例 CLI 重放；不启动工作台或收费模型。
- [x] 自审差异，核对没有越权改剧情、任意路径加载、无关事件自动加载，以及模板正文没有变化。
- [x] 写 `maintenance/validation-v8.2.1.md`，分别记录结构测试、规则人工复核和未验证的创作/成片效果。
- [x] 保留本地修改等待主人审阅；不自动提交或推送。

## 边界与回退
专项识别仍由模型负责，程序只保证已登记项按所属专业装入；回执不证明理解。扩写契约是模型工作规程，不是新增模型调用器。可从当前分支查看完整 diff，基线提交保留；不执行 reset/clean。

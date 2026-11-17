# 工具接口（8.2）

Python 3，无第三方运行依赖。输入只读，--out写新版本，不能覆盖输入。语义识别、设计和复核由模型完成，程序不调用模型服务。

```text
python scripts/workflow.py plan task.json --project project.json
python scripts/workflow.py init project.json task.json --out run-01.json
python scripts/workflow.py context task.json source --project run-01.json --out source-context.json
python scripts/workflow.py submit run-01.json source source-result.json --context source-context.json --out run-02.json
python scripts/workflow.py discover run-02.json discovered.json --out run-03.json
python scripts/workflow.py repair run-05.json camera "反应看不清，改摄影" --out run-06.json
python scripts/workflow.py check run-06.json
python scripts/workflow.py workbench-json grid-checked.json --out workbench-project.json
```

source：checked_event_ids、source_coverage（源文行ID→event_ids/reason）；专业模块：design（事件ID→设计）。
action/vfx的context分别附action_candidates/vfx_candidates，按事件与负责需求匹配本地库，明确ACT-/VFX-ID优先、完整名其次、关键词加权最后。自动默认最多2类，明确ID涉及更多类时完整提供指定类；候选不是已批准的新能力。可在已有requirements.description指定ID，无需写进故事；旧运行若提示规则路径变化先另存并init，不绕过旧回执失效。
compile：text、event_ids、dialogue_ids、coverage；有台词还需utterances（id/speaker/start/end，最后两项是正文字符位置）。
validate：content_checked、evidence、coverage、requirement_reviews、limitations。coverage对应完整需求表，值为正文确切引文或字符范围；不能用笼统引用掩盖未完成内容。
discover：reason、requirements数组，元素含id/kind/description/source_ids/event_ids/source_quote。只补处理环节，不改原文事实。
requirements单项可附specialties数组，见[专项登记](specialty-selection.md)：performance对应microexpression，vfx对应vfx-techniques。无需重复写features；discover同样支持。程序校验声明后按工序实际装入全文，旧context不能用于新专项提交；不接受任意文件路径或包外skill调用。

只扩写按[创作准备](creation-preparation.md)由模型交付剧本，不调用本CLI；没有新增expand命令。creation为可选的模型交接记录，不是脚本认证的扩写结果。

每次submit先取当前context，使用--context交接；规则、源文、计划或上游有变，旧回执将失效。programmatic API submit的第四参数为context返回的receipt。哈希不是用户认证，也不证明模型已理解规则。maintain仍需明确授权记录，不能用补调路径扩权。

局改需要master_sections，每任务一个事件；多事件另分任务或走全稿。九宫只写panels（id/event_ids/sample_time/prompt），grid九格，edit_grid目标一格。真实出图和用户接受另行进行。

旧8.0/8.1运行项目重新init，旧记录保存在workflow_archives；不要直接手改contract_version绕过迁移。
8.2.1保留8.2数据合同，但规则注册表有变；已有8.2.0的运行记录同样先另存，再init归档。重新init保留sources、events和已有主稿，不代表旧工序已通过新版规则。
回归：python -m unittest discover -s tests -p "test_*.py"；node --test tests/event-core.test.cjs；保存样例的CLI串跑：python tests/run_sample.py <独立输出目录>。这些不代表成片验证。

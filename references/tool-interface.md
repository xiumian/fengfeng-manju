# 工具接口（8.2）

新做整段提示词在task.delivery中指定outputs为dual；copy_format默认full，只有用户明确要精简才填compact。full按完整模板复制，每镜独立六项音效；相对时序也用独立的“——【镜头标题】”行分镜。compile同时提交text（制片主稿）与model_ready_prompt（本段直投稿）。旧任务未指定时沿用单主稿。显式时码的两稿使用相同timing_nodes标题。分集装订：episode命令读取按剧情排序的运行文件路径JSON数组（相对清单所在目录），例如 python scripts/workflow.py episode manifest.json --out episode.json。首段含完整共用页，后段可从模板片段设定分隔头开始；重复共用页必须一致，否则先解决设定冲突。产物production_master只含一份全集资产，model_ready_prompts按唯一片段编号取独立文本。局改后旧直投稿失效，按修改后的完整片段重新编译，不拿单事件补丁直接生成。

Python 3，无第三方运行依赖。输入只读，--out写新版本，不能覆盖输入。语义识别、设计和复核由模型完成，程序不调用模型服务。

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

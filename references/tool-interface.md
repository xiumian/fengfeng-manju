# 工具接口

在技能根目录执行，Python 3，无第三方依赖。命令只读输入文件，`--out`写新版本，不覆盖输入。程序不调用模型；模型完成语义判断、创作和内容复核。

```text
python scripts/workflow.py plan task.json
python scripts/workflow.py init project.json task.json --out run-01.json
python scripts/workflow.py context task.json source --project run-01.json
python scripts/workflow.py submit run-01.json source source-result.json --out run-02.json
python scripts/workflow.py repair run-05.json camera "接触点被遮挡，退回摄影" --out run-06.json
python scripts/workflow.py check run-06.json
python scripts/workflow.py workbench-json grid-checked.json --out workbench-project.json
```

source提交`{"checked_event_ids":["E1"]}`；专业模块提交`{"design":{"E1":"具体执行设计"}}`；compile提交`{"text":"完整正文","event_ids":["E1"],"dialogue_ids":[]}`；validate提交`{"content_checked":true,"evidence":{"E1":"正文具体片段＋核对理由"},"limitations":["未生成视频"]}`。

模块结果只能按计划顺序submit；失败不会写出新项目。调用context取得当前工序规则和范围内事件，再使用上游结果创作。步骤列表和reason就是调度记录；workflow.results/history是实际交接与返修记录，不以计划代替执行。

局改必须已有按事件分开的master_sections与可选master_prefix。当前程序每个revise任务修改一个事件；多事件按任务拆开，必要时另建全稿任务。程序保留其他事件原文并重组正文，不猜测旧正文的段落边界。上游事实变化时存旧版本、重建任务；不偷偷覆盖。

九宫结果提交`panels`数组，元素含id/event_ids/sample_time/prompt；grid为9格，edit_grid仅目标1格。输出仅是采样提示词，状态为等待真实图片与用户接受，不自动生图、回填或标媒体通过。

完整grid规划通过后，workbench-json将完整事件、原文、主稿与9采样转换成网页可导入格式；不把未生成图像或用户接受状态伪造为完成。局部scope不能直接导出整板。

维护的authorization记录不是认证系统，不能靠脚本推断人类同意。maintain仅提供规则和记录接口，不执行文件改写。

检验：`python -m unittest discover -s tests -p "test_*.py"`；`node --test tests/event-core.test.cjs`。这些检查不证明生成质量。具体完整事件JSON及串跑脚本见examples/layered-12s-project.json和tests/run_sample.py。

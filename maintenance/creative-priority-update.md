# 创作决策顺序修订

authorization={explicit:true,user_request:"写吧"}，承接主人认可的六步优先级。

- 旧位置：SKILL.md缺少总推导顺序；design-boundaries.md只有职责；camera.md的“先试构图再决定动不动”容易执行成固定/少切优先。
- 本次：入口给总顺序并引用唯一正文；共用职责规则写六步、贯穿的约束与测试稿边界；摄影替换上述默认，并补局部同框不等于整段不切。
- 不改变source→validate调用顺序，不强制多方案/镜数/分析表。模板、雨巷测试稿、程序、安装副本不改。维持本地未发布8.2.1，不提交推送。
- 回退：outputs/creative-priority-update/before保存本轮前四份工作文件副本，保留此前未提交修改；新增测试为test_creative_priority_is_ordered_and_delivered_to_design_stages。
- 定向验证：python -m unittest discover -s tests -p test_professional_methods.py -v；检查顺序存在、摄影边界及8个实际工序context收到同一全文，不验证模型决策、导演审美或成片效果。结果见outputs/creative-priority-update/validation.txt。

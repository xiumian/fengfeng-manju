# 项目底稿与修改权限

项目含sources（id/text原始内容）、events（稳定id、source_ids、start/end数字秒、body事实、dialogues原句列表）、constraints（当前要求）、globals（已确认稳定设定）、segments（工作台可选）和workflow（计划、阶段结果、审查、返修记录）。有服装、伤损、持物、站位等状态改变时，记录该事件 start_state 与 end_state。创作模型可在底稿说明未定状态。完整来源落盘，摘要和九格不能替换它。

每个事件对白项含id、speaker、kind=dialogue/OS/VO、text。原文事实和台词不可由动作/摄影覆盖；自主创意也要先建立事件事实，再把新设计写到design。用户授权改事实时保存旧版并重建受影响计划，不假装是普通摄影修改。
底稿前的扩写及其权限、来源与补充记录唯一按[创作准备](creation-preparation.md)处理。可选creation记录不代替完整sources；专业模块的观看需求与决策归属按[专业职责](design-boundaries.md)交接，不把建议当作其他模块已生效方案。

模块输入输出见scripts/workflow.py的RULES注册表和各模块契约。设计输出统一为design映射：事件ID→设计文字；字段只属于模块命名空间。source提交checked_event_ids及source_coverage逐源文段落映射，程序检查已声明来源引用和时间，但不声称自动提取全部事实。compile提交text、event_ids、dialogue_ids、utterances及coverage，检查登记覆盖、完整发声单元和空占位；正文位置映射由模型确认，不以ID出现代替语义覆盖。

validate提交content_checked、evidence（事件ID→正文证据与理由）、coverage、requirement_reviews（按需求登记 status 与 reason）、limitations；新双轨任务另需direct_coverage（同一需求ID→直投稿引句或字符区间）。这些是执行者记录，程序核对引用和回执，不替代语义判断。grid/edit_grid另需用户接受的真实记录，程序不允许助手代为确认图像。

修改源文/事件、模块设计或主稿会使实际依赖结果失效。程序repair保留旧结果并退回工序；本轮采用按阶段保守失效，context按事件scope限制读取。运行文件中的编译中间产物不是已放行交稿；从当前已复核的流程提取正文并另存，不覆盖上一份确认稿。跨事件精确依赖优化留待验证，不声称完全自动推导。

旧工作台事件若没有完整来源、正文或明确确认，不从九格补成事实。仅有九格的旧工程保存为可编辑草稿，补齐完整事件及人工覆盖核对后才允许正式完成。结构合法、文字复核、图片接受和成片通过分开。

当前requirements、逐段来源映射、补调与正文证据以[覆盖契约](coverage-contract.md)为准。context回执约束版本一致，不是对模型理解的证明。

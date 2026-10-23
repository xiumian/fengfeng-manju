# 项目底稿与修改权限

项目含sources（id/text原始内容）、events（稳定id、source_ids、start/end数字秒、body事实、dialogues原句列表）、constraints（当前要求）、globals（已确认稳定设定）、segments（工作台可选）和workflow（计划、阶段结果、审查、返修记录）。完整来源落盘，摘要和九格不能替换它。

每个事件对白项含id、speaker、kind=dialogue/OS/VO、text。原文事实和台词不可由动作/摄影覆盖；自主创意也要先建立事件事实，再把新设计写到design。用户授权改事实时保存旧版并重建受影响计划，不假装是普通摄影修改。

模块输入输出见scripts/workflow.py的RULES注册表和各模块契约。设计输出统一为design映射：事件ID→设计文字；字段只属于模块命名空间。source提交checked_event_ids，程序检查已声明来源引用和时间，但不声称自动提取全部事实。compile提交text、event_ids与dialogue_ids，检查登记覆盖、原句出现次数和空占位；正文位置映射由模型确认，不以ID出现代替语义覆盖。

validate提交content_checked、evidence（事件ID→正文证据与理由）、limitations，记录实际复核；这些是执行者声明，不是脚本的语义识别。grid/edit_grid另需用户接受的真实记录，程序不允许助手代为确认图像。

修改源文/事件、模块设计或主稿会使实际依赖结果失效。程序repair保留旧结果并退回工序；本轮采用按阶段保守失效，context按事件scope限制读取。跨事件精确依赖优化留待验证，不声称完全自动推导。

旧工作台事件若没有完整来源、正文或明确确认，不从九格补成事实。仅有九格的旧工程保存为可编辑草稿，补齐完整事件及人工覆盖核对后才允许正式完成。结构合法、文字复核、图片接受和成片通过分开。

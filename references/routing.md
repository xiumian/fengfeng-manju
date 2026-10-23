# 调度协议

## 语义判定与程序分工
模型按当前用户意图选择mode与features，不用词语命中判定授权。不确定“讨论还是执行修改”时先保持讨论。程序验证结构并根据显式字段确定路线，无法判断字段是否忠实于用户；必须人工/模型核对。

任务JSON：`{"mode":"prompt","features":["action","performance"],"scope":[],"reason":"含实体攻防和对白；只交付文字"}`。
mode：prompt新主稿、revise局改、grid已有主稿九宫、edit_grid单格修图、workbench保存恢复、discuss技能讨论、maintain技能维护。
features：action实体接触、performance对白或关键反应、vfx法术/变身、assets已有资产库、sound复杂OS/VO/声画设计。无对应需求不选。
scope是事件ID列表；空列表表示全稿。局改必须给scope。全局身份/世界规则改变时按真实依赖扩大范围，不机械只读邻段。

## 路线与交接
prompt/revise：source底稿 → 按features选择assets/action/performance/vfx/sound → camera → compile → validate。
grid/edit_grid：source核对已有事件与主稿 → 按需assets → sampling → validate；没有主稿不能从图反推，先另行走prompt。
workbench：workbench → validate；内容修改另走相应路线。discuss仅返回讨论，不写入。maintain必须有明确授权记录，只进入maintenance。
程序将每步所需模块及原因写入计划；单步骤context返回当前规则、所选事件、相邻状态、必要全局约束和上游模块记录。简单任务一次创作内完成交接也可以，不要求每专业单独推理或重抄底稿。

实际输出用submit写入当前工序。结构不合格阻断该次写入；内容问题用repair退回当前或上游工序，保留失效记录。默认两轮定向返修，仍无法解决则报告具体阻碍，不无限循环或伪装完成。没有调用另一执行者不得称独立评审。

工序只取得该工序规则，不递归展开链接。链接是专项查询入口；例如vfx需要具体招式才查索引与命中类别，camera不自动加载表演和整库。旧文件若与当前归属冲突，按项目契约及当前模块处理，必要时报告冲突。

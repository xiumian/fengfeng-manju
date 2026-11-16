# 来源工序
先核对context的source_units，为每个非空源文段落填写source_coverage，再逐事件检查所需专业。发现requirements漏项用discover登记；不能只核对事件ID就声称源文完整。
输入：完整来源、当前要求、事件底稿。输出checked_event_ids和source_coverage，覆盖本次scope中的每个事件。
核对原事实、对白/OS/VO、关键反应、结果、换场与起终状态。所有source_ids真实可解析；完整源文到事件的漏项仍需逐条核对，程序不自动识别。新增设计不能冒充原文。
时间分配要容纳对白、反应、受力、慢放和摄影。复杂任务需要来源映射；简单任务不强迫长表。必要内容冲突先重排自选部分，再明确缺口。

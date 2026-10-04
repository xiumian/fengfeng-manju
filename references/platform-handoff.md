# Codex制作交接 — fengfeng

当前仅面向Codex。WorkBuddy、Coze、OpenClaw、Dify专用适配不属于当前实现或验收范围。H3停用。Codex负责读取本Skill、准备实际工具附件、执行生成、查看产物、维护项目并交付；网页与本地CLI不假装连接模型。

# 平台与工具交接 — fengfeng

当前提供Seedance 2.0、Seedance 2.5或未指定的交接选择，三者当前默认正文均为亡灵天灾架构，不因为版本选择引入旧七段式。H3停用。不从源资料推断当前API参数、图像数量或时长限制。

production_cli plan输出的是人工/工具交接数据，submission=manual-handoff-no-api-call：源剧情、事件/九格映射、必要资产请求、独立九宫提示词及视频正文。模型参数默认not-verified，不伪造模型ID或可提交API载荷。目标平台确定后，助手再核实当前官方参数，记录来源与日期，才能填入技术配置；默认不执行付费视频生成。

Codex按需使用Canvas/ComfyUI工具：以统一项目JSON和生产计划交接，原专项knowledge/comfyui-canvas-automation.md提供规划；不自动运行旧接口代码。平台执行器读取实际事件而非旧模板标题；生图节点使用grid_prompt与真实参考文件，视频节点使用video_prompt与已确认图，任务回执包含状态与真实产物位置。当前不是已连接的远端API服务。

制作阶段有明确需求时读script-template.md、shooting-checklist.md、publishing-calendar.md及storyboard/capcut-guide.md、douyin-best-practices.md。可选generate_script.py和analyze_video_data.py提供辅助草稿/算术建议，内置平台阈值仅是历史启发式，不是预测保证；其输出不替代亡灵视频正文。

未明确模型时plan保留unspecified并记录目标模型待选择；模板不替主人预选。entities须为数组，缺省空数组只是待提取，错误类型拒绝。

## 多模态附件清单
工作JSON可填写reference_bindings，每项asset_id、role、segment_id及可选event_ids。role为identity/space/prop/motion/camera/voice/sound/rhythm，真实资产kind须匹配用途。plan输出reference_attachments含路径、用途、审核及文件可读状态；未知绑定或错配拒绝。网页最终JSON保留附件元数据，但浏览器不验证本机任意路径实际存在；文件验证交付使用production_cli.cjs handoff PROJECT.json 空配置.json OUTPUT.json，逐一核验当前真实文件/审核并计算哈希。未审核或缺文件阻断，不自动复制外部素材、不提交API、不保证工具支持所有附件格式。技术测试审核模拟与主人确认必须分开。

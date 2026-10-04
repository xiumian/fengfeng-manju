# 完整能力入口索引 — fengfeng

这是实现入口索引，不是全部效果已经验收的声明。H3不属于当前启用范围。知识分支由助手读相关资料后实际创作；本地程序处理数据，不取代创作判断。

|能力|当前入口与交付|
|---|---|
|1 创意与剧本|production-pipeline.md；craft-routing.md；前提/结构/节拍/实体/剧本页|
|2 台词与表演|craft-routing.md；knowledge/dialogue-doctor-7d.md、dialogue-speed-check.md、wenxi-micro-expression.md、FACS专项；对白预算与可见表演|
|3 情绪曲线|knowledge/emotion-beat-curve.md；scripts/generate_emotion_curve.py；节拍数据与PNG|
|4 人物场景道具资产|asset-production.md；production_cli plan/register；四视、母版、道具出图请求、真实素材登记|
|5 空间机位与多人调度|knowledge/spatial-topview-camera.md、asset-spatial-ledger.md；storyboard/director-blocking-grammar.md；拓扑、观察位与人账|
|6 动作武学|action-routing.md；动作预演、攻防因果、兵器与身体反馈|
|7 玄幻与特效|references/combat-vfx-library.md与action-routing.md；条件选择、阶段与作用域|
|8 风格与画幅|craft-routing.md与knowledge/aspect-ratio-adaptation.md；按当前选择构图，不强制国漫或竖屏|
|9 时间轴与SEG|core.parseScript + 完整事件人工容量核对；knowledge/segment-splicing.md；不机械固定长度|
|10 九格规划与整板|workbench.md；core.gridPrompt；实际工具生成、查看、回填|
|11 单格替换与审核|core.editPrompt；工作台局部合成与版本、审核失效|
|12 连续视频正文|video-template.md；core.videoPrompt；唯一亡灵默认正文|
|13 模型/平台适配|platform-handoff.md；production_cli plan；Seedance2.0/2.5写作交接，参数未核实不填，不是自动API连接|
|14 质检与稿件检查|quality-workflow.md；validate_prompt.py、check_package.py、core.validate；数据/内容/图像分层|
|15 离线看板与曲线|build_board_lite.py、generate_emotion_curve.py；真实本地文件产物|
|16 工作台生命周期|nine-grid.html；编辑、回填、单格裁切、版本、保存/导入、确认后JSON/HTML|
|17 脚本与辅助制作|scripts/optional；script-template.md、shooting-checklist.md、publishing-calendar.md、storyboard/capcut-guide.md；按需辅助，不替代主稿|
|18 平台内容与样本边界|platform-handoff.md、knowledge/platform-safety-compliance-guide.md；历史样本不默认加载，不自动发布|

角色亲缘作为第4组子分支：仅明确需求启用，parent_ids登记依赖，实际参考图及生成工具由助手执行；请求输出不等于已出图或父子关系已确认。

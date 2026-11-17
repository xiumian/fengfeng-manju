# 全域情绪与表情维护验证｜2026-11-18

授权与回退见emotion-overhaul-plan.md；8.2.1未发布，构建日期已是2026-11-18，本轮不虚增版本。未改完整提示词模板、作品、工作台、安装副本，不提交推送、不收费生成。既有本地修改保留。

## 根因与改动
- performance已有策略/触发，保留；新增emotion-performance-design.md统一跨镜情绪轨迹、局部眉眼口颌/肌张力/注视对象、身体任务、掩饰与混合情绪、非对白声音与环境、摄影可见条件、编译保真与具体证据。
- microexpression-cues.md原英文内容按内在情绪配动作且含固定2—4通道、克制默认、强制近景/定机与先眼后头等配方。整页替换为中文可选构造、时序、题材强度与纠错，避免末尾追加矛盾。
- 共享全文实际进入performance/action/sound/camera/compile/validate的context并计入rules_hash；表情专项仍按原specialty/关键词有条件装入，不增新schema。
- source明确无对白不等于无表演；assets/vfx/sampling明确身份稳定、已有环境、遮挡、情绪不新增能力、静态图限度；不向不负责专业无差别装入全文。入口、专业职责、摄影方法和后台检查引用同一正文。
- 六组情境对照覆盖微笑的不同目标、静默失望、战斗恐惧与判断、欣喜戒备并存、闭眼呼气的不同依据、喜剧/空场。不把线索当心理诊断，保留原剧情与台词。

## 测试
- 新增4项测试：六模块真实context全文与指纹、具体方法/旧配方替换、各专业引用与模板无检查栏目、真实source/performance等submit后camera及compile获得原样具体表情文字。
- 全回归97项通过，outputs/emotion-overhaul/tests.log。第一次测试因正文没有“跨镜”字样但已有切镜继承规则失败，明确标题为跨镜情绪轨迹后重跑通过；不把词匹配当语义证明。
- python scripts/check_layered_package.py返回errors=[]。
- python tests/run_sample.py outputs/emotion-overhaul/cli-replay真实历史CLI回放通过：plan/init/7contexts/7handoffs，日志sample.log；这是旧保存样例非新模型创作。
- git diff --check退出0，既有CRLF归一化警告非错误。仅本轮与备份的差异见this-change.diff。

## 执行者文本语义自查与局限
对照案例均明确触发在先、变化与原任务并行、不同解释由剧情依据区分；无统一微表情数/镜长/哭笑模板。部门可提出需求不越权锁机位/改台词；取景不可读、缺设计和编译删细节分别返责任模块；理由和检查不进入投喂稿。
无成片生成/连续观看/核听，未验证观众感受、微表情准确性或任何成功率；程序测试仅证明注册、全文装入与交接。此次由子代理执行自查，根线程复核另行确认，不冒称独立审美验收。

## 根线程复核
根线程回读共享情绪方法、重写表情专项、表演模块与本轮定向diff，核对没有固定表情配方或越权锁镜。独立重跑test_emotion_design.py四项通过；另以15秒14镜三句对白测试稿完成九工序真实交接，六工序context均含共享方法，表演含microexpression专项，三句原文/说话者/字符位置通过现有提交校验。对白时码和姓名分行以兼容现有台词行识别；没有绕过重复发声检查。此为文字与交接复核，仍非独立美感或成片验收。测试稿位于outputs/ancient-battlefield-dialogue-15s/prompt.txt，旧无对白版本保留。

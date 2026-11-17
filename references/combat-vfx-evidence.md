# 打斗与特效方案的外部证据

本轮核查：2026-11-17。**没有找到足以把本库全部条目标成“当前视频模型已验证”的证据。**以下优先采用主创制作记录及官方示例工程，不把搜索到的热门提示词或作者自称成功当成稳定性证明。文件中的方案是本技能原创转译，全部标记adaptation_unverified；不是现实搏斗训练，也不是外部作品的逐镜复刻。

| ID | 一手来源 | 可确认的实现与本轮阅读范围 | 转译边界 |
|---|---|---|---|
| B1 | [ASC：John Wick 3主创访谈](https://theasc.com/article/john-wick-chapter-3-slayin-in-the-rain/) | 已读动作与摄影协作、预演及宽景选择的正文；该片已制作发行。 | 证明这类协作在成片制作中采用，不证明本库具体交锋来自影片，不强制长镜或宽景；本轮未逐帧播放影片。 |
| B2 | [ASC：Creed III](https://theasc.com/article/creed-iii-takes-big-swings/) | 已读Rolling With the Punches：多角度预演、动作故事与摄影随局势变化。 | 支持先比较观看条件再定镜；原创拳脚/反转案例不是片中拳法逐招转录，未本机复现。 |
| B3 | [SideFX：Fireball Explosion](https://www.sidefx.com/contentlibrary/fireball-explosion/) | 官方示例有HIP工程下载、效果演示及截图；已核对正文、作者、文件类型、示例用途。 | 已存在可获取的制作示例，未下载运行HIP、未完整观看演示；不能由此认证魔法火球的生成提示词。 |
| B4 | [SideFX：Creating explosions](https://www.sidefx.com/docs/houdini/pyro/explode.html) | 已读单次/连续爆发、源、轨迹和可下载爆炸示例说明。 | 支持区分爆发与持续源，不复制节点参数为视频模型控制值，不推定所有能量都爆炸。 |
| B5 | [SideFX：Labs Lightning](https://www.sidefx.com/docs/houdini/nodes/sop/labs--lightning.html) | 已读起终点、接触范围与线形控制说明。 | 技术实现文档；电系、路径和分支是借鉴范围，不能支持麻痹/导电等剧情设定。 |
| B6 | [Epic：Niagara Content Examples](https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-content-examples?application_version=4.27) | 已读官方示例表：静态/动态束、位置事件、碰撞事件及网格采样；示例工程入口可定位。 | 是UE4.27文档中的可复用实现，不是当前引擎兼容性保证；未安装运行，未把引擎实现视为Seedance复现。 |
| B7 | [SideFX：Destruction overview](https://www.sidefx.com/docs/houdini/destruction/overview.html) | 已读不同材料破碎、约束、代理和残片工作流。 | 只支持材料与后果分类，不替代真实物理计算，不替本项目授权毁墙伤人。 |
| B8 | [SideFX：Houdini Ice Solver](https://www.sidefx.com/tutorials/houdini-ice-solver/) | 作者发布在SideFX的冻结效果教程，有演示入口；本轮只核对简介与作者，没有观看完整教程。 | 作者公开实现线索，年代为Houdini15；不足以证明教程在新版本兼容，也不足以证明AI提示词已验证。 |
| B9 | [Seedance 2.5官方提示指南](https://docs.volcengine.com/docs/ark/seedance-2-5-prompt-guide?lang=zh) | 前轮核对过正文；本轮该地址超时，BytePlus镜像只有页面框架可读。 | 本轮不新增“官方已验证打斗模板”结论，不据旧快照确认当前入口规格。沿用本地具体描述原则，实际规格另查。 |
| P1 | [SideFX：POP Curve Force](https://www.sidefx.com/docs/houdini/nodes/dop/popcurveforce.html) | 扩库时已核对沿曲线、向曲线与绕曲线运动的说明。 | 仅支持轨迹组织手段，不代表万剑/灵流的神话能力已在生成模型上验证，也不把节点参数直接投喂。 |
| P2 | [SideFX：Shockwave](https://www.sidefx.com/docs/houdini/shelf/spyro_shockwave.html) | 已读爆发、后续火团及稍后贴地冲击环的组成和区别。 | 属于公开技术实现；本库允许纯能量/奇幻版本，但不冒称现实爆炸物理精确或提供装置制作。 |
| P3 | [SideFX：Following a leader](https://www.sidefx.com/docs/houdini/dopparticles/follow.html) | 已读领行者、追随群、不同目标分组与噪动的正文。 | 借鉴群体与层级运动，不说明任意规模剑群在视频模型中都能精确逐个控制；未本机复现示例。 |

2026-11-17粒子扩库另查Epic新版Niagara Examples Pack课程入口，但本轮直开无正文，未把新闻介绍或课程标题当已观看/运行的证据。法天象地、万剑归宗等为通用题材下的原创条件方案，不复制同名作品的专属画面，也不声明新增64条已出片。

## 条目如何标记
- `evidence_ids`：表示借鉴哪个已公开手段/实现，不表示来源出现了本条全部动作或能力；不同证据层级不能混成一个“已验证”标签。
- `validation_status: adaptation_unverified`：本库条件方案已编写，外部出处已登记；本条转译尚未以视频验证。原创空间、治疗、幻象等借B6的呈现组织，不声称官方实现了同名法术。
- 旧`source_ids`仍保留历史类别启发，见特效库来源记录；与本轮证据分开。
- 文字测试只证明条目、索引、实际交接与引用一致；语义走查由同一助手进行，不是独立盲测。

## 接下来怎样升级为实测方案
取得有使用权的参考视频，记录作者/链接、模型或制作工具、实际参考职责、可见起终态、接触与后果；没有播放就不写逐帧结论。实际生成时保存完整输入、模型版本、参数、产物路径与失败情况，先比较一个设计变量，再由主人看成片确认。一次成功只归属于该输入与入口，不把整类效果升级为普遍稳定。

本库只保存中文方法与原创短案例，不分发第三方工程、付费教程或成片素材；需要使用外部资产时另核许可。

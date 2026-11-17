# 专业方法补强验证记录

日期：2026-11-17。授权：主人“那你全面更新一下这些内容”。仅当前仓库、本地未发布8.2.1；未提交、推送、安装或调用生成服务。

## 本轮11份内容

|文件（相对仓库根）|本轮补强|
|---|---|
|references/creation-preparation.md|扩写从权限、当场目标、变化到因果桥；离别的不同目的对照，容量与授权纠错。|
|references/modules/action.md|目标、距离、支撑、应对与局势变化的交锋构造；护送/夺物/追退/群战的选择及代价。|
|references/modules/camera.md|观众与人物的知情关系、空间分层、构图/机位/运动选择、运镜代价及重新建立方位；去掉为变化而变速的旧要求。|
|references/modules/performance.md|当场意图、策略、触发、可见线索及听者参与；掩饰与相同台词不同目的对照，不默认克制或部位堆砌。|
|references/modules/vfx.md|先机制后外观，供能、附着/投射/持续/范围/变化的选择组合及反例。|
|references/modules/sound.md|听觉视点、主次、距离、遮挡、主观声与声桥选择；接触同步与声音过载纠错。|
|references/modules/sampling.md|以验证信息选真实状态、去冗余补盲区，再确定采样时间；九格不足或材料不足的诚实处理。|
|references/modules/compile.md|保留事实及专业方案的融合步骤，区分并行与先后，消除同义重复但不删不同关系；正文与后台分离。|
|references/performance-camera-methods.md|同一来袭事件的不同知情/观看方案，递物/隐瞒/空房的选择和代价。|
|references/visual-impact-design.md|以可见行为选择材质、利用既有参照建立尺度，硬壳/柔韧对照及越权边界。|
|references/vfx-techniques.md|按方向/接触/强调/后果选专项；连续供能与一次释放、烟/能量/碎屑区分及机制对照。|

保留已有具体方法和职责，不将所有段落改成统一套路。新增步骤、选择表、条件例和纠错是综合设计，不宣称每个场景都必须跑全表或逐栏输出。

## 专业依据

本地登记：references/method-evidence.md，13个来源ID。电影语言/主创采访、表演/叙事教学资料、VFX与模型官方指南分开适用。

来源阅读范围分清正文可读与仅官方检索摘录；国家剧院PDF、GDC讲义全文抓取失败，课程/讲座未完整观看，不据此声称完整学习了其训练体系。各模块已写入可执行内容，网页用于追溯，不是默认调用依赖。平台简洁建议不覆盖主人完整模板，模拟软件文档不等于视频模型数值控制能力。

## 实际检查与结果

修改前已运行原64项测试通过。新增定向测试后先见缺方法/来源及旧镜头要求导致失败，再补规则；既有全文交接测试在修改前即通过，不能将此描述成新增加载能力。

最终命令与完整stdout/stderr/退出码保存在outputs/professional-method-update-20261117/after-manifest.json：

1. `python -m unittest discover -s tests -p "test_*.py"`：68项通过（原64+新增4）。新增检查覆盖11份方法维度、真实context全文及指纹一致、镜头旧默认移除、来源范围声明。
2. `python scripts/check_layered_package.py`：errors=[]；检查活动链接、语法、模块注册及版本，不做语义/媒体验收。
3. `python tests/run_sample.py outputs/professional-method-update-20261117/cli-replay`：plan+init+7次context+7次校验提交通过。使用历史保存交接，不称新创作、独立模型或质量提升证据。
4. `python outputs/professional-method-update-20261117/run_cases.py`：3个新手写案例通过真实init/context/submit：雨站离别、窄门护送、护层破裂后撤离；另将护层完整主稿走source/sampling/validate，9个非均匀状态草稿通过，状态仍为awaiting_actual_image_and_user_acceptance。
5. `git diff --check`：通过。

案例工序输入、规则全文context、交接输出和最终工程保存在outputs/professional-method-update-20261117/cases/；汇总case-results.json。原创新案例是同一助手根据新规则手写并自查，不是独立执行者实验。覆盖引文使用同事件的局部见证，只说明接口接受；摄影、材质、声音、并行关系等细节另做文字走查，程序不认证这些语义。

## 范围保护

修改前副本与SHA256在outputs/professional-method-update-20261117/before/及before-manifest.json。逐项比对：11份目标文件均变更；10份保护文件SHA256完全一致：投喂模板、后台复核及8份特效类别文件（48条库条目）。本轮新增来源登记、定向测试、维护记录及CHANGELOG条目，不修改生产接口或工作台；先前已有未提交修改保留，不把其差异冒充本轮变更。

可复核命令：`python outputs/professional-method-update-20261117/verify.py`。输出目录为本机验证产物，不是发行包的新运行依赖。

## 尚未验收

未生成图片/视频/音频，未实际验证Seedance或其他模型理解、速度坡道、微表情、口型、视觉审美、跨场景泛化或生成成功率。规则更具体与交接无回归已检查；成片是否更好仍需主人试片反馈与实际素材比较。

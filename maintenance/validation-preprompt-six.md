# 六项前置创作验证｜2026-11-18

授权/范围/回退见preprompt-six-plan.md。版本仍8.2.1本地未发布，合同8.2不变。已有工作树修改保留。

## 实际方法与加载
- narrative-event-design.md：任务/摩擦/选择后果、信息差、日常与追逐两类对照；归属创作准备，source核对。source/compile/validate实际加载。
- dialogue-relationship-design.md：逐句目的、潜台词依据、听者选择、人物语言差异与容量；原句保护与授权新增分开。同句“给我”两种目的、静默回应等案例。source/performance/sound/compile/validate加载。
- character-prop-design.md：任务到轮廓、服装结构、道具功能、材质行为、识别与战损状态；不是只选图。assets/action/compile/validate加载。
- scene-space-design.md：区域/边界/地标、可见与可达、交互属性、路线/支撑与环境后果；追逐/室内/空场选择。assets/action/camera/compile/validate加载。
- art-style-material-design.md：风格化3D、二维、真人/混合媒介的形体/材料/运动区别、同钥匙跨媒介转译；不是堆渲染器名。assets/vfx/camera/compile/validate加载。
- lighting-color-design.md：源/向/遮挡/反射、明暗分离、主色面积、动态发光与跨镜世界位置；战斗和日常对照。assets/vfx/camera/compile/validate加载。

各有方法/授权/职责/返修/具体不足与方向。workflow_rules.PREPROMPT_METHODS显式注册，不依赖关键词。创作准备逐项判断已定/可补/不适用；决定进入sources/globals/requirements及实际负责模块，不能只留聊天/未交接备注。简单任务不强制六项都新增；没有新schema、工序、必填表格或前台分析栏目。

入口/相关模块/专业边界/后台复核衔接，新方法不替代既有动作、表情、音效、节奏和视觉保真。已有原句/事实不能借创作擅改；人物造型与已上传参考职责有别，字面设计不冒充锁定。

## 贯通示范与实际证据
outputs/preprompt-six-demo/prompt.txt为完整12秒五镜《关门前的钥匙》，全局/资产/片段/逐镜/两句台词/分层音效均填写。build.py执行source→assets→action→performance→sound→camera→compile→validate共八工序到text_checked。无超自然效果不强制vfx。

六项需求分别登记plot/performance/asset/camera，正文引句与具体关系逐项记录在输出结果及outputs/preprompt-six-update/six-feature-review.json。globals明确3D材质、空间与光源，真实上下文得到对应设计；原句、归属、时间段及覆盖经过现有submit校验。模板和旧作品未改，示范另存。

本次执行者复核：交物接稳后松手→右手收钥/左手顶门→让路→跨槛；钥匙最后在师父右侧衣袋，不与手持终态冲突；风格通过发束/衣折/漆木/铜边执行；门开扩大同一光源的光区、身体经过挡窄后恢复。逐镜无脑补新灯/拥抱/隐情，无超自然填充。

## 测试与命令
1. 新增test_preprompt_six.py三项：六份方法各负责工序及compile/validate全文与指纹、具体方法与创作准备入口、真实source/design/compile提交和六条独立正文证据。修改前失败/缺文件，red.log；不是先有程序自动编剧再补文档。
2. 真实夹具中camera收到assets具体设计；compile缺R:4美术证据会拒绝，补齐六条真实片段可提交。该拒绝利用已有coverage约束，不声称新增语义判别器。
3. python -m unittest discover -s tests -p 'test_*.py'：108项通过（原105+本轮3），tests.log。
4. python scripts/check_layered_package.py：errors=[]，package.log。
5. python tests/run_sample.py outputs/preprompt-six-update/cli-replay：历史保存样例plan/init/7contexts/7handoffs通过，cli.log。
6. git diff --check退出0，有既有CRLF归一化提示。定向差异this-change.diff，新六方法/测试/维护记录与示范另列。未修改提示词模板、旧作品、工作台、其他技能或安装副本，未提交推送、未生成媒体。

## 验收边界
“实际加载”由真实context全文/回执和交接验证；“写进正文”由本示范实际内容与同一执行者语义核对证明。自动测试不理解潜台词/美感，规则注册不能保证未来每次模型都会正确创作，不把本示范说成泛化成功率。无独立评审、出图、连续看片或核听，实际成片效果仍未验证。旧工程回执变更按已有机制重新context/必要时另存init。

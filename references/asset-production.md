# 资产制作与亲缘分支 — fengfeng

## 清单与工具
在生产配置的entities数组中逐项填写id、kind（character/scene/prop/audio）、name、description；可选parent_ids及lineage_notes仅用于剧情明确的亲缘角色。实体ID不是已存在素材REF。未提取完整时记录待补，不用把整段globals当作一个具体人物。

production_cli.cjs plan把实体清单转成可直接交给工具的资产制作请求；缺清单保留pending，未知依赖或循环依赖拒绝。character是四视资产请求，scene包含母版及独立布局图，prop是单件外观，audio是声音制作任务。它不会自动出图，也不把声音清单伪装为音频文件。

## 执行顺序
1. 核对外貌、服饰、材质、道具归属及场景拓扑；读knowledge/character-lineage-and-sheets.md、asset-spatial-ledger.md、production-ledger-handbook.md。这些是专项知识，旧硬门禁不覆盖文字起步模式。
2. 核心角色先生成四视并查看；存在明确亲缘需求时，先完成父/母代真实参考，再为依赖角色写继承及区别特征。parent_ids只提供顺序，不自动计算面部百分比，也不虚构亲属关系。
3. 亲缘生成时实际附件使用已查看的基准图；独立制作场景母版和布局图、关键道具图。生成器的提示词输出不是已完成资产。
4. 用production_cli.cjs register登记实际文件：配置包含id/path/kind/entity_id/purpose。工具核验非空文件并计算哈希；状态固定registered-unreviewed，取消旧审核。文件存在只证明可读，不证明图像/音频内容正确。
5. 助手检查文件类型、画面/声音、用途后请主人确认；资产登记ID才可写进panel.asset_refs。不绑定尚未生成的entity_id，不批量假定已审核。
6. 保存含实体清单/真实素材的项目，项目素材路径是本机引用，跨机交付须复制真实素材并更新路径；不能只交路径假装自包含素材包。九宫图仍内嵌保存。

示例配置见../templates/production-config.json。不需要资产图时entities可以为空并明确文字模式，任务清单不会因此宣称完整资产链通过。

角色face_traits/material_traits、场景topology等明确配置随definition完整交接并进入相关资产制作稿；不把额外细特征静默丢掉。final引用只接受confirmed/reviewed/locked素材，本段工作台明确确认身份和用途后才更新状态；文件可读检查与内容审核仍不同。

## 标准资产卡与普通四视的区别
原标准为面部近景＋无头正面/90°侧面/背面三个全身视区，另附材质细节、比例尺与HEX色表。四个带头全身视图只是普通转面参考，不自动算标准资产卡通过。未指定色值、身高等先登记待确认，实际图片逐区核对后才请求主人确认。

## 主人指定默认角色卡（优先于上文旧标准）
默认使用templates/character-card-display.txt：16:9展示板、左55%唯一大脸、右上正面/四分之三侧面/侧面/背面四个完整全身、右下动态姿势与细节、中文标注。保留主人模板，不混入旧版无头视图、HEX色表或比例尺要求。黑灰色半透明背景是画面描述，不自动开启透明PNG。追加真实角色设定；例举武器/配饰不是新增道具授权。
原标准存templates/character-card-legacy.txt。角色实体asset_card_template省略或display用新版；明确legacy用旧版，未知值报错。旧版尚未完成的出图验收不自动变成新版验收。此选择只改角色资产卡，不改场景资产、九宫铅笔样式、视频正文或无资产模式。

## 分支交接补齐（v0.3.6）
亲缘reference_files从同entity_id且kind=character的唯一已登记文件解析；零候选为missing、多候选为ambiguous；真实非空文件且已审核才execution_ready。不得把同门/师徒自动标遗传关系。场景asset_requests.tasks独立master/layout，各有任务ID、prompt与planned状态，登记时用途明确到母版或布局。两个planned任务不是两个已完成资产。

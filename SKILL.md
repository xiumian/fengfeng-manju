---
name: fengfeng-manju
description: 将小说、剧本或创意与资产转为完整中文视频提示词，设计动作、表演、特效与镜头；按需九宫验证、单格修图和工作台保存。
metadata:
  version: '8.2.0'
---

# fengfeng manju｜分层生产

先区分制作作品、修改作品、讨论技能、修改技能。讨论、提想法和要求方案不修改技能文件；明确授权后的维护读[维护制度](maintenance/change-control.md)。

## 开始当前任务
读[调度协议](references/routing.md)，将本次需求解析成任务JSON，运行 `python scripts/workflow.py plan task.json --project project.json`，再init建立运行版本。底稿必须包含完整来源、事件与必要约束；不要只靠features手填决定模块。随后用context读取当前模块，把上下文文件通过submit的`--context`交接；不递归读取全库。Python用环境中可用的Python 3。

生产由程序选路、检查交接与记录状态，由模型执行创作。程序不调用收费模型，不声称自动理解原文或验证画面。按交付停止，简单任务不强制全流程、九宫或多代理。

## 全程边界
- 原文与用户确认决定事实；设计补充单独记录。对白/OS、因果、结果与未入格事件不静默删除。
- 完整事件是数据源；主稿是视频正文来源。镜头、时间节点、九格互不等同；九格不能覆盖事件。
- 当前用户格式、时长、风格与授权优先。默认16:9真人电影写实；不继承模板案例人物、18秒、三图或白银力量。
- REF和候选图片不是已上传参考。实际生成须看图，用户接受后才标图像完成；静态图不证明速度或声音。
- 制作权限不包含修改技能、生成付费视频或发布。作品内已授权步骤自主推进，关键歧义才询问。

需求清单、自动补调与逐项回查见[覆盖协议](references/coverage-contract.md)。

交接结构见[项目契约](references/project-contract.md)，程序命令见[工具接口](references/tool-interface.md)，工作台任务才读[工作台](references/workbench-v8.md)。历史入口、旧分镜资料与案例只显式查阅，不覆盖现行规则。

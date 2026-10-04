# 工具命令 — fengfeng

仅启动工作台、操作项目数据、交接或开发检查时读取；写剧情、写提示词不必加载。以下路径均相对本skill根目录，执行前解析为绝对路径。缺依赖不自动安装，不自动启动服务或调用付费模型。

- `node scripts/migrate_legacy.cjs OLD.json NEW.json`：主人明确选择后迁移原九宫工作工程，保留旧快照/图/详细字段，时间与素材待核对，取消旧确认；不默认迁移历史样本。

- `node scripts/production_cli.cjs plan PROJECT.json CONFIG.json OUTPUT.json`：统一生产计划，导出资产请求、依赖、九宫与亡灵正文，不自动调用模型。
- `node scripts/production_cli.cjs register PROJECT.json ASSET.json OUTPUT.json`：核验真实素材文件并登记哈希，保持未审核并失效旧确认；不冒充完成资产。

在本机PowerShell运行 `python scripts/serve_workbench.py --no-open`；通常可双击 `启动工作台.cmd`。终端Ctrl+C停止服务，绑定127.0.0.1。macOS使用 `启动工作台.command`。Python启动不需要前端依赖；开发/数据CLI需现有Node，PNG曲线需Pillow。缺依赖不自动安装。
- `node scripts/project_cli.cjs parse INPUT.txt OUTPUT.json`：规则式分镜初稿，未确认估算不标定稿。
- `node scripts/project_cli.cjs validate PROJECT.json`：时间、映射、状态检查，不证明语义正确。
- `node scripts/project_cli.cjs prompt PROJECT.json OUTPUT.txt`：未审核时只能作为草稿；`results`命令必须通过审核门禁。
- `python scripts/validate_prompt.py INPUT.txt --duration 30`：亡灵格式和时间检查。
- `python scripts/build_board_lite.py PROJECT.json -o OUTPUT.html`：事件/九格/图像离线看板。
- `python scripts/generate_emotion_curve.py -i BEATS.json -o CURVE.png`：自定义情绪曲线。
- `python scripts/check_package.py`：资源、语法与核心回归检查。


# fengfeng manju v8.2.2｜新版

在 Codex 中调用 `$fengfeng-manju`，按任务调度工序。入口见 [SKILL.md](SKILL.md)，维护规则见 [维护制度](maintenance/change-control.md)，命令见 [工具接口](references/tool-interface.md)。

九宫格按需使用。Windows 双击 `启动九宫格.cmd`，macOS 运行 `9宫.command`。

## 当前分支

`新版` 是本次改后 skill 的分支预览；`release/v8.2.0` 保持不变。包含六项前置创作、动作与镜头节奏、情绪表情、128条特效与36条打斗方案、完整提示词模板及分层音效。本次增加可选段尾抽帧镜、主特效变化链、配乐主题线及关键因果逐项复核。规则/交接测试不等于生成成片验收，上传也不等于本机安装。

## 跨电脑维护

首次在另一台电脑克隆此版本。

```sh
git clone --branch 新版 https://github.com/xiumian/fengfeng-manju.git
```

在仓库内先执行 `git pull --ff-only`，修改并测试后提交，再执行 `git push`。仓库更新后，需将新版技能安装到要使用它的 Codex 环境。

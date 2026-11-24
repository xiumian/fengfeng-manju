# 全流程 v9.1.0｜部门接力

在 Codex 中调用 `$fengfeng-manju`，按任务调度工序。入口见 [SKILL.md](SKILL.md)，维护规则见 [维护制度](maintenance/change-control.md)，命令见 [工具接口](references/tool-interface.md)。

九宫格按需使用。Windows 双击 `启动九宫格.cmd`，macOS 运行 `9宫.command`。

## 当前分支

新模式在 `release/v9.1.0-handoff` 独立发布。原有分支和 v9.0 标签不被替换。

完整提示词按「剧本 → 场景资产 → 适用的动作／表演／特效 → 摄影 → 声音 → 编译 → 复核」逐站交接。每站用上一站已接收的成果；出问题退回对应工序，只重跑受影响的下游。只要剧本或分镜时在对应交付点停止。

完整投喂模板、每镜六项音效、六项专业导法和内置库保留。规则和文本检查不等于成片验收；拉取仓库也不等于更新本机安装。

## 跨电脑维护

首次在另一台电脑克隆此版本。

```sh
git clone --branch release/v9.1.0-handoff https://github.com/xiumian/fengfeng-manju.git
```

在仓库内先执行 `git pull --ff-only`，修改并测试后提交，再执行 `git push`。仓库更新后，需将新版技能安装到要使用它的 Codex 环境。

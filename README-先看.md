# fengfeng manju v8.2.0

在 Codex 中调用 `$fengfeng-manju`，按任务调度工序。入口见 [SKILL.md](SKILL.md)，维护规则见 [维护制度](maintenance/change-control.md)，命令见 [工具接口](references/tool-interface.md)。

九宫格按需使用。Windows 双击 `启动九宫格.cmd`，macOS 运行 `9宫.command`。

## 跨电脑维护

首次在另一台电脑克隆此版本。

```sh
git clone --branch release/v8.2.0 https://github.com/xiumian/fengfeng-manju.git
```

在仓库内先执行 `git pull --ff-only`，修改并测试后提交，再执行 `git push`。仓库更新后，需将新版技能安装到要使用它的 Codex 环境。

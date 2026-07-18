# GitHub CI Checks

状态：已批准

仓库：`zdjc445/EL26`

Workflow：`CI`

合并到 `main` 的必需检查名：

- `quality`
- `security`
- `containers (time-api)`
- `containers (time-web)`

工作流文件固定第三方 Action 到不可变 commit。更新 Action 时必须读取官方 release、替换 commit、检查 Diff，并重新运行工作流。

分支保护属于 GitHub 外部状态。首次工作流在远端成功运行后，Release Owner 使用具有 Administration(write) 权限的 GitHub CLI 身份执行：

```bash
gh api --method PUT -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2026-03-10" repos/zdjc445/EL26/branches/main/protection --input .github/branch-protection.json
gh api -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2026-03-10" repos/zdjc445/EL26/branches/main/protection
```

第二条命令必须返回四个 required contexts、一个批准、stale review dismissal、last-push approval、linear history、conversation resolution，并显示 force push 和 deletion 均关闭。保存输出到对应工作项；不得只凭 UI 操作口头宣称生效。

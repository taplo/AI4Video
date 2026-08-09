# Development Conventions

- 使用 `uv` 进行项目管理和环境管理（代替 pip/venv/poetry 等）

---

# Definition of Done

每次代码变更完成后，必须满足以下条件：

1. 代码通过 lint 检查
2. 代码通过 type check（如适用）
3. 相关测试通过
4. 新增或修改的函数/类有对应的测试覆盖

---

# Mandatory Workflows

## GSD 任务执行规范

- GSD wave 中 `type=implement` / `type=feature` / `type=fix` 的任务，**必须先通过 TDD skill** 再实现
- 每个 task 执行完毕后，运行 `scripts/verify.ps1`（或项目对应的验证脚本）
- 每个 phase 结束前，用 reviewer sub-agent 审查

## 代码审查规范

- 提交前用 `/receiving-code-review` skill 自审
- 复杂变更用 `/requesting-code-review` skill 请求审查

## 错误积累机制

- 每次发现 Agent 重复犯的规律性错误，记录到 `docs/agent-rules.md`
- `docs/agent-rules.md` 超过 30 条时，提炼高频规则到本文件

---

# Permissions

- 禁止直接运行 `git push --force`
- 禁止直接删除 `.git` 目录
- 禁止修改 `AGENTS.md` 中的 Definition of Done 节（除非用户明确要求）
- 大规模重构（>5 文件）前必须先用 `/brainstorming` skill

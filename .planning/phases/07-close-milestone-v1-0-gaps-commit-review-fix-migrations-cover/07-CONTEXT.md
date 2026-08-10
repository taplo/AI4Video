# Phase 7: Close milestone v1.0 gaps - Context

**Gathered:** 2026-08-10
**Status:** Ready for planning

<domain>
## Phase Boundary

里程碑 v1.0 关闭阶段（closure phase）——不新增功能，只关闭审计发现的阻止性缺口：

- 提交未提交的 Phase 06 review-fix（CR-01, CR-02, WR-01..WR-09）
- 将 Django migration chain 纳入版本控制（当前被 gitignore）
- 解决 Phase 05 coverage gate（D-05/D-08: 60% 目标 vs 实际 17%）
- 产出里程碑级验证证据（VERIFICATION.md）
- 清理残留工件（stale branch、recovery marker、dirty files）

缺口来源：`.planning/v1.0-MILESTONE-AUDIT.md`（status: gaps_found, 73/78 requirements）。

</domain>

<decisions>
## Implementation Decisions

### Review-fix 提交策略
- **D-01:** 采用**原子按问题组提交**（atomic per-concern commits），不合并为一个 consolidated commit
- **D-02:** 所有 dirty files 纳入关闭范围（含 GB28181SipServer.py），关闭后 working tree 必须干净
- **D-03:** stale branch `gsd-reviewfix/06-17660` 和 `.review-fix-recovery-pending.json` 在新提交**验证通过后删除**（先保留作备份，验证后删除）
- **D-04:** 为 Phase 04 和 Phase 06 **各写一份 REVIEW-FIX.md**（关闭 04 的 6 个 critical findings 和 06 的 CR-01/CR-02/WR-01..WR-09），引用对应 commit refs
- **D-05:** `tests/test_phase06_fixes.py`（untracked 测试）随 review-fix 一并提交

### Migration 版本控制
- **D-06:** **提交现有 migration chain 原样**（0001_initial + 0002_auditlog + 0003_alter_*），un-gitignore `app/migrations/`（保留 `__pycache__` ignored）
- **D-07:** migration 提交并入 **CR-02 原子提交**（0002/0003 是 CR-02 修复不可分割的一部分），不单独 chore commit
- **D-08:** CI 增加 `makemigrations --check` gate，确保 models 与已提交 migrations 无漂移（fresh clone 可复现 schema）

### Coverage gate 解
- **D-09:** **坚持达成 60%**（honor D-05），不降低门槛、不做模块白名单式 gate
- **D-10:** 新增测试**优先覆盖高价值模块**（auth/middleware、stream CRUD、analysis pipeline），再按 CONCERNS.md 优先级补齐至 app/ 整体 60%
- **D-11:** `--cov-fail-under=60` **在 CI 和本地 verify 脚本双重强制**（CI test.yml + scripts/verify.ps1 同步配置）
- **D-12:** 在关闭阶段 SUMMARY 中**记录 coverage 旅程**（baseline 17% → 60%，每模块 delta，以及故意未测模块 GB28181/engines 及理由）

### Validation 工件范围
- **D-13:** **仅产出里程碑级** `v1.0-VERIFICATION.md`，汇总 6 个 phase 证据（UAT+REVIEW+live verify），不逐 phase 写 Nyquist VALIDATION.md
- **D-14:** **回填** phase SUMMARY.md 的 `requirements-completed` frontmatter（04/05/06 summary 缺失，audit traceability gap 项）
- **D-15:** 本关闭阶段自身的验证证据走**标准 phase 生命周期**（07-SUMMARY.md），不额外规划 07-VALIDATION.md

### the agent's Discretion
- 原子提交的具体拆分粒度（每个 concern 一个 commit vs 按关键性分组）由 agent 决定，但必须以 CRITICALs 优先
- 具体新增测试用例的编写方式由 agent 决定
- VERIFICATION.md 的证据组织格式由 agent 决定

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 审计与缺口源头
- `.planning/v1.0-MILESTONE-AUDIT.md` — **MUST read first**。status=gaps_found 的完整证据、gap 清单、integration BLOCK 项

### Review-fix 证据
- `.planning/phases/06-other-upgrades/06-REVIEW.md` — CR-01, CR-02, WR-01..WR-09 的完整审查发现
- `.planning/phases/04-engineering-hardening/04-REVIEW.md` — 6 critical + 7 warning + 4 info finding
- `.planning/phases/06-other-upgrades/.review-fix-recovery-pending.json` — 待清理 recovery 标记
- `.planning/phases/06-other-upgrades/06-UAT.md` — UAT 断言证据
- `.planning/phases/05-test-infrastructure/05-01..06-SUMMARY.md` — 缺 requirements-completed frontmatter（需回填）
- `tests/test_phase06_fixes.py` — untracked review-fix 测试，需提交

### CI 与配置
- `.github/workflows/test.yml` — 现有 `--cov-fail-under=60` 配置（第 47 行附近），需同步本地 verify
- `.gitignore` (§32-33: `app/migrations/*`) — 需 un-gitignore migrations
- `scripts/verify.ps1` — 本地验证脚本，当前无 cov gate，需与 CI 同步

### Migration chain
- `app/migrations/0001_initial.py` — 初始 schema
- `app/migrations/0002_auditlog.py` — av_audit_log 表（CR-02 修复产物）
- `app/migrations/0003_alter_algorithmmodel_last_update_time_and_more.py` — 后续修改

### 覆盖目标模块（COVERAGE）
- `app/middleware.py` — 认证 + Safe header 逻辑（高价值）
- `app/views/UserView.py` — 登录/session（高价值）
- `app/views/StreamView.py` — stream CRUD（高价值）
- `app/analysis/pipeline.py`, `app/analysis/manager.py` — analysis 生命周期（高价值）
- `.planning/codebase/CONCERNS.md` §Test Coverage Gaps — 测试优先级矩阵

No external specs — requirements fully captured in decisions above (spec_loaded=false)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/test_phase06_fixes.py` — 已存在 review-fix 验证测试（156 测试套件中）
- `app/migrations/0002_auditlog.py` + `0003_*` — 已生成待提交的 migration 文件
- `app/fields.py` — EncryptedCharField（Phase 03 加密字段，review-fix 已改）
- `pytest.ini` / `tests/conftest.py` — Phase 05 建立的测试基础设施

### Established Patterns
- 每 phase 的 plan 单独提交（此前 06 以 3 个 plan SUMMARY 提交）——但本 phase 决策改为原子按 concern 提交
- 验证走 UAT.md + REVIEW.md（而非 VERIFICATION.md/Nyquist VALIDATION.md）——默认约定，本 phase 决策保持
- JSON 响应统一 `f_responseJson()`、视图 wildcard import（不影响本 phase）

### Integration Points
- `.github/workflows/test.yml` — 加 `makemigrations --check` 步骤 + 保持 60% 硬 gate
- `scripts/verify.ps1` — 加 `--cov-fail-under=60` 与 CI 对齐
- `.gitignore` — 移除 `app/migrations/*` 条目
- 所有 6 个 phase SUMMARY.md — 回填 requirements-completed frontmatter
- 新增 `v1.0-VERIFICATION.md`（里程碑级）替代逐 phase Nyquist

</code_context>

<specifics>
## Specific Ideas

本 phase 是**关闭型**而非功能型：核心约束是"不新增功能，把已有正确工作的证据固化并提交"。Coverage 哲学：宁可认真测高价值模块并为未测模块留文档化理由，也不要为凑百分比做低价值均匀覆盖。Git 历史哲学：修复要可追溯（atomic per-concern），migration 与触发它的修复同 commit。Git 历史哲学：修复要可追溯（atomic per-concern），migration 与触发它的修复同 commit。

</specifics>

<deferred>
## Deferred Ideas

- **逐 phase Nyquist VALIDATION.md** — 用户选择"Milestone-level only"；如需正式 Nyquist 逐 phase 合规，可在 v1.0 发布后作为独立 maintenance phase
- **降低 coverage 门槛方案**（lower gate / module-only gate）— 明确否决，D-05 保持 60%
- **Squash migrations 为单一 0001** — 明确否决（D-06），保持增量链保真实溯源

None of these were acted on — recorded for future phases.

</deferred>

---

*Phase: 7-Close milestone v1.0 gaps*
*Context gathered: 2026-08-10*
# Phase 07: Close milestone v1.0 gaps — Research

**Researched:** 2026-08-10
**Domain:** review-fix commit closure, Django migration version control, coverage gate (17% → 60%), milestone verification evidence
**Confidence:** HIGH (all critical claims verified by local execution against the actual repo)

## Summary

Phase 07 is a **closure phase** — it fixes no features, it fixes the milestone's blocking gap: Phase 06 review-fix
(CR-01, CR-02, WR-01..WR-09) applied but **uncommitted** in the working tree; the migration chain (0001/0002/0003)
**gitignored**; the Phase 05 coverage gate at **60% vs 17% actual**; and no milestone-level verification evidence.
Everything the phase needs already exists on disk — the work is committing, testing, and documenting, not building.

This research verified the live repo state:
- **Dirty files** map cleanly to review-fix concerns: `app/middleware.py` (CR-01 + WR-01/04/05/06), `app/utils/GB28181SipServer.py` (outbound CR-01 companion — attaches the Safe header to `/inner/` callbacks), `app/models.py` (WR-02 `auto_now`), `app/migrations/0002_auditlog.py` + `0003_alter_*` (CR-02/WR-02), `app/fields.py` (WR-03), `app/views/UserView.py` (WR-09), `manage.py` (WR-04), `requirements.txt` (WR-08), plus tracked-deployed `ai4video.sqlite3`.
- **`makemigrations --check --dry-run app` exits 0** — models and the on-disk migration chain are drift-free right now; the CI gate step will pass.
- **Coverage baseline: 12,706 statements, 2,159 covered (17%)**; 60% requires 7,624 covered → **+5,465 statements**.
- The stale branch `gsd-reviewfix/06-17660` is **checked out in a linked worktree** (`C:\Users\Administrator\AppData\Local\Temp\opencode\sv-06-reviewfix-17660`) — deletion requires `git worktree remove` FIRST, then `git branch -D`.

**Primary recommendation:** Sequence the closure as (1) atomic per-concern commits, CRITICALs first (CR-01 auth commit → CR-02 migration commit), (2) remaining WR fixes + regression tests, (3) coverage build-out over the high-value modules (auth/middleware, stream CRUD, analysis pipeline) with the full-suite gate run locally after each wave, (4) verification docs (04/06-REVIEW-FIX.md, frontmatter backfill, v1.0-VERIFICATION.md), (5) cleanup (delete recovery marker + stale worktree/branch) only after the new commits pass verification.

**Coverage verdict:** 60% is achievable **without any coverage exclusions** — the view layer alone (3,851 uncovered statements) plus analysis non-engine code (~2,000) exceeds the +5,465 target. `GB28181SipServer.py` and engine inference paths stay deliberately low and are documented in the SUMMARY (D-12); no `.coveragerc` omit needs to ship (honoring D-09).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Review-fix 提交策略**
- **D-01:** 采用**原子按问题组提交**（atomic per-concern commits），不合并为一个 consolidated commit
- **D-02:** 所有 dirty files 纳入关闭范围（含 GB28181SipServer.py），关闭后 working tree 必须干净
- **D-03:** stale branch `gsd-reviewfix/06-17660` 和 `.review-fix-recovery-pending.json` 在新提交**验证通过后删除**（先保留作备份，验证后删除）
- **D-04:** 为 Phase 04 和 Phase 06 **各写一份 REVIEW-FIX.md**（关闭 04 的 6 个 critical findings 和 06 的 CR-01/CR-02/WR-01..WR-09），引用对应 commit refs
- **D-05:** `tests/test_phase06_fixes.py`（untracked 测试）随 review-fix 一并提交

**Migration 版本控制**
- **D-06:** **提交现有 migration chain 原样**（0001_initial + 0002_auditlog + 0003_alter_*），un-gitignore `app/migrations/`（保留 `__pycache__` ignored）
- **D-07:** migration 提交并入 **CR-02 原子提交**（0002/0003 是 CR-02 修复不可分割的一部分），不单独 chore commit
- **D-08:** CI 增加 `makemigrations --check` gate，确保 models 与已提交 migrations 无漂移（fresh clone 可复现 schema）

**Coverage gate 解**
- **D-09:** **坚持达成 60%**（honor D-05），不降低门槛、不做模块白名单式 gate
- **D-10:** 新增测试**优先覆盖高价值模块**（auth/middleware、stream CRUD、analysis pipeline），再按 CONCERNS.md 优先级补齐至 app/ 整体 60%
- **D-11:** `--cov-fail-under=60` **在 CI 和本地 verify 脚本双重强制**（CI test.yml + scripts/verify.ps1 同步配置）
- **D-12:** 在关闭阶段 SUMMARY 中**记录 coverage 旅程**（baseline 17% → 60%，每模块 delta，以及故意未测模块 GB28181/engines 及理由）

**Validation 工件范围**
- **D-13:** **仅产出里程碑级** `v1.0-VERIFICATION.md`，汇总 6 个 phase 证据（UAT+REVIEW+live verify），不逐 phase 写 Nyquist VALIDATION.md
- **D-14:** **回填** phase SUMMARY.md 的 `requirements-completed` frontmatter（04/05/06 summary 缺失，audit traceability gap 项）
- **D-15:** 本关闭阶段自身的验证证据走**标准 phase 生命周期**（07-SUMMARY.md），不额外规划 07-VALIDATION.md

### the agent's Discretion
- 原子提交的具体拆分粒度（每个 concern 一个 commit vs 按关键性分组）由 agent 决定，但必须以 CRITICALs 优先
- 具体新增测试用例的编写方式由 agent 决定
- VERIFICATION.md 的证据组织格式由 agent 决定

### Deferred Ideas (OUT OF SCOPE)
- **逐 phase Nyquist VALIDATION.md** — 用户选择"Milestone-level only"；如需正式 Nyquist 逐 phase 合规，可在 v1.0 发布后作为独立 maintenance phase
- **降低 coverage 门槛方案**（lower gate / module-only gate）— 明确否决，D-05 保持 60%
- **Squash migrations 为单一 0001** — 明确否决（D-06），保持增量链保真实溯源
</user_constraints>

<phase_requirements>
## Phase Requirements

Requirements derive from the milestone audit gaps (`v1.0-MILESTONE-AUDIT.md`, `status: gaps_found`). There is no central REQUIREMENTS.md; requirements are phase-scoped D## codes.

| ID | Description | Research Support |
|----|-------------|------------------|
| phase05-D-05 | Coverage ≥ 60% (currently 16.99%, gate fails) | Section "Coverage gate" — baseline 12,706 stmts / 2,159 covered; +5,465 needed; realistic budget +5,600..6,400 across views + analysis + utils |
| phase05-D-08 | CI enforces coverage gate | `test.yml:47` already runs `--cov-fail-under=60` `[VERIFIED]`; pytest.ini addopts already include it `[VERIFIED]`; **verify.ps1 (line 128) is the only unenforced spot** — must add explicit cov flags |
| phase04-REVIEW | 04-REVIEW-FIX.md closing 6 criticals (all fixed in code, undocumented) | 04-REVIEW.md CR-01..CR-06 enumerated; phase 02 `02-REVIEW-FIX.md` is the format precedent `[VERIFIED: repo]`; commit refs provided by this phase's atomic commits |
| phase06-REVIEW | Commit CR-01/CR-02/WR-01..WR-09; write 06-REVIEW-FIX.md; remove recovery marker + stale branch | Dirty-file → concern mapping in "Commit Strategy" `[VERIFIED: git diff]`; worktree+marker cleanup sequence in "Runtime State Inventory" |
| phase06 integration BLOCK | Migration chain version-controlled (fresh clone reproducible) | `makemigrations --check --dry-run app` exits 0 `[VERIFIED: local execution]`; .gitignore lines 32-33 to remove; CI step snippet in "Code Examples" |
| audit traceability gap | requirements-completed frontmatter backfill (phase 01/03/04/05 summaries) | D-code lists per phase confirmed: 01→D-01..15, 03→D-01..16, 04→D-01..20, 05→D-01..16 `[VERIFIED: CONTEXT.md grep]`; 02/06 already have frontmatter |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Atomic per-concern commits | Git / VCS (local repo) | — | Commit ordering, grouping, and cleanup are pure git operations; no code tier involved |
| Migration version control | Git / VCS (repo) | CI (drift gate) | .gitignore change + committing 0001/0002/0003; CI `makemigrations --check` guarantees reproducibility |
| Coverage gate enforcement | CI / Local verify script | Test infra (pytest.ini) | `--cov-fail-under=60` enforced in CI, pytest.ini addopts, AND scripts/verify.ps1 (currently missing) |
| Coverage build-out (new tests) | Test tier (tests/) | CI (gate validation) | New tests live in `tests/`; they exercise API/backend behavior via Django test Client + mocked globals |
| Milestone verification evidence | Planning docs (.planning/) | — | v1.0-VERIFICATION.md aggregates UAT+REVIEW+live-verify evidence; no runtime component |
| Cleanup (marker, branch, worktree) | Git / VCS + OS filesystem | — | Recovery marker is a plain file (delete); branch requires linked-worktree removal first |

## Standard Stack

This phase installs **no new packages**. The entire toolchain is already present and version-pinned. All versions below were confirmed against the local environment (`uv pip show`, `pip index` equivalent for already-installed).

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Django | 5.2.17 | framework (pinned in requirements.txt) | `makemigrations --check` drift gate depends on it |
| pytest | 9.1.1 | test runner | installed via requirements-dev |
| pytest-django | 4.13.0 | Django test DB + fixtures | installed via requirements-dev |
| pytest-cov | 7.1.0 | coverage measurement + `--cov-fail-under` gate | installed via requirements-dev |
| coverage | 7.15.4 | data engine behind pytest-cov | installed transitively |
| git | (system) | atomic commits, worktree/branch cleanup | platform tool, no version constraint |
| uv | (system) | local command runner (`uv run python ...`) | AGENTS.md mandate: `uv` replaces pip/venv |

### Supporting
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `python manage.py makemigrations --check --dry-run app` | Django 5.2 | migration drift gate | CI step + locally after any models.py change |
| `git worktree remove` + `git branch -D` | git | stale branch cleanup | after verification passes (D-03) |
| `coverage report` | coverage 7.15.4 | per-module baseline/delta inspection | during coverage build-out to track module deltas |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `pytest-cov` `--cov-fail-under` | plain `coverage.py` + custom script | pytest-cov integrates with the existing pytest.ini addopts with zero new tooling — do not hand-roll a gate script |
| `.coveragerc [run] omit` for GB28181/engines | measure everything + document gaps | **Do NOT omit** — D-09 forbids module-whitelist gates; budget analysis shows 60% is reachable without it |

**Version verification:** performed 2026-08-10 (pytest 9.1.1, pytest-django 4.13.0, pytest-cov 7.1.0, coverage 7.15.4, Python 3.12.13 local; CI matrix 3.11/3.12 per test.yml). No package installs occur in this phase, so no registry verification is needed beyond the installed-state check above.

## Package Legitimacy Audit

> This phase installs **no external packages** (verified: the toolchain is already vendored in requirements.txt / requirements-dev.txt and present in `.venv`). The Package Legitimacy Gate found zero new installs, therefore no slopcheck run is required and no packages are tagged `[ASSUMED]`.

| Package | Registry | Disposition |
|---------|----------|-------------|
| (none added by this phase) | — | N/A — pytest-cov, pytest-django, coverage all already declared in requirements-dev.txt (committed, Phase 05) |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

Phase 07 is a state-transition closure, not a data-flow pipeline. The diagram shows artifact state transitions:

```
┌─ Current working tree (evidence verified 2026-08-10) ─────────────────────┐
│  dirty: middleware.py  GB28181SipServer.py  models.py  UserView.py        │
│         fields.py  manage.py  requirements.txt  ai4video.sqlite3          │
│  untracked: app/migrations/{0001,0002,0003}  tests/test_phase06_fixes.py  │
│             05-*SUMMARies  06-UAT.md  .review-fix-recovery-pending.json   │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   │
   [1] atomic commits (CRITICAL first, D-01/D-02)
                                   ▼
┌─ master history ─────────────────────────────────────────────────────────┐
│  C1 fix(06) CR-01 Secure-Header auth  (middleware + GB28181SipServer)    │
│  C2 fix(06) CR-02 migration chain + .gitignore + models + sqlite3 (D-07) │
│  C3 fix(06) WR-03/04/08/09  (fields, manage.py, requirements, UserView)  │
│  C4 test(06) test_phase06_fixes.py (D-05)                                │
│  C5.. docs(04/06) REVIEW-FIX.md + frontmatter backfill + UAT + audit     │
│  C6 chore      .gitignore runtime artifacts (clean tree, D-02)           │
│  C7 docs(07)   v1.0-VERIFICATION.md (D-13) + 07-SUMMARY (D-15)           │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   │
   [2] coverage build-out (D-09/D-10/D-11)  w/ gate run after each wave
                                   ▼
┌─ Test suite: 156 → ~400+ tests ──► ┌─ Gate: --cov-fail-under=60 ────────┐
│  auth/middleware (89%→)             │  CI test.yml (exists)             │
│  stream CRUD (4%→)                  │  pytest.ini addopts (exists)      │
│  analysis pipeline/manager (15-20%→)│  verify.ps1 (MUST ADD, D-11)      │
│  remaining views + utils            │  makemigrations --check (ADD, D-08)│
└──────────────────────────────────────┘                                    │
   [3] artifact cleanup (D-03, ONLY after verification passes)              │
   ▼                                                                        │
   git worktree remove sv-06-reviewfix-17660 → git branch -D                │
   gsd-reviewfix/06-17660 → delete .review-fix-recovery-pending.json        │
   ──────────────────────────────────────────────────────────────────────────┘
```

### Recommended workflow sequence (for the planner's task ordering)

1. **Commit review-fix** in CRITICAL-first order (exact file grouping below).
2. **Coverage build-out** in CONCERNS.md priority order (auth → stream CRUD → analysis pipeline → remaining views → utils). Run the full gate (`uv run pytest tests/`) after each wave; per-commit quick run `uv run pytest tests/ -q`.
3. **CI/config parity tasks**: makemigrations step in test.yml; cov flags in verify.ps1; .gitignore edits.
4. **Docs tasks**: 04-REVIEW-FIX.md → 06-REVIEW-FIX.md → frontmatter backfill → v1.0-VERIFICATION.md → 07-SUMMARY.
5. **Cleanup task (last)**: remove worktree + branch + recovery marker; final `git status` must be empty (D-02).

### Pattern 1: Atomic per-concern commits (dirty-file → concern mapping)

**What:** One commit per logical concern group, CRITICAL first. Granularity is per-file-group, not per-hunk: `app/middleware.py` bundles CR-01 + WR-01/04/05/06 in one file — hunk-level splitting (`git add -p`/`git apply --cached`) is impractical for an automated executor on a legacy multi-concern file, and D-01's discretion explicitly permits grouping by criticality.

**When to use:** Closure phases where review fixes exist in the working tree and must become auditable history.

| Commit | Message (type(scope)) | Files | Concerns |
|--------|----------------------|-------|----------|
| C1 | `fix(06): enforce Safe-header auth on /inner/ callbacks (CR-01)` | `app/middleware.py`, `app/utils/GB28181SipServer.py` | CR-01 + WR-01 (exact whitelist), WR-04 (has_key), WR-05 (denylist audit), WR-06 (XFF key) — same-file co-tenants, listed in message |
| C2 | `fix(06): version-control auditlog migration chain (CR-02)` | `.gitignore` (remove `app/migrations/*` lines 32-33), `app/migrations/0001_initial.py`, `0002_auditlog.py`, `0003_alter_*`, `app/models.py`, `ai4video.sqlite3` | CR-02 + WR-02 (`auto_now`, encoded by 0003 — models.py **must** ride with 0003 or `makemigrations --check` breaks). D-07: not a separate chore commit. |
| C3 | `fix(06): complete remaining review-fix warnings` | `app/fields.py`, `app/views/UserView.py`, `manage.py`, `requirements.txt` | WR-03 (Fernet sizing), WR-09 (cycle_key), WR-04 (propagate migrate errors), WR-08 (cryptography pin) |
| C4 | `test(06): add review-fix regression tests` | `tests/test_phase06_fixes.py` | D-05; one file, atomic |
| C5 | `docs(04): close phase 04 review findings` | `.planning/phases/04-engineering-hardening/04-REVIEW-FIX.md` | D-04 (6 criticals + warnings) |
| C6 | `docs(06): close phase 06 review findings` | `06-REVIEW-FIX.md`, `06-UAT.md`, `.planning/v1.0-MILESTONE-AUDIT.md`, `.planning/ROADMAP.md` | D-04 + audit evidence + roadmap updates |
| C7 | `docs(05): backfill requirements-completed frontmatter` | `05-01..06-SUMMARY.md` + any of 01/03/04 summaries missing it + `.planning/phases/01..04/0X-0Y-SUMMARY.md` | D-14 |
| C8 | `chore: ignore runtime artifacts` | `.gitignore` additions: `.coverage`, `htmlcov/`, `.pytest_cache/`, `backups/`, `db.sqlite3`, `.opencode/`; change `__pycache__/*` → `__pycache__/` (line 9) | D-02 clean tree (see Pitfall 3 for why line 9 is broken) |
| C9 | `docs(07): milestone v1.0 verification evidence` | `.planning/v1.0-VERIFICATION.md`, `07-SUMMARY.md` | D-13, D-15 |

**Executor note:** verify each commit with `git status --porcelain` after staging; never stage unrelated files (`git add <explicit paths>` only).

### Pattern 2: Migration version control + drift gate

**What:** Un-ignore the migration dir, commit the chain as-is (D-06, no squashing), and gate CI with `makemigrations --check`.

**When to use:** Any Django repo whose migrations were gitignored — fresh clones must reproduce the schema.

Verified facts:
- `.gitignore` lines 32-33 (`app/migrations/*`, `app/migrations/__pycache__/*`) are the only blockers; line 9 `__pycache__/*` keeps pycache ignored once line 33 is removed (but see Pitfall 3 — line 9 is root-anchored and should become `__pycache__/`).
- `python manage.py makemigrations --check --dry-run app` currently exits **0** ("No changes detected") with `DJANGO_SECRET_KEY` set — the CI gate will be green on first run. `[VERIFIED: local execution]`
- `--check` does not touch the DB — safe on a fresh clone with no sqlite file. `[CITED: https://docs.djangoproject.com/en/5.2/ref/django-admin/#cmdoption-makemigrations-check]`
- The CI step must carry the same env block as the test step (`DJANGO_SECRET_KEY` + `DEBUG=true`) because `framework/settings.py:36-52` raises `ValueError` when SECRET_KEY is absent in non-DEBUG. `[VERIFIED: settings.py]`

### Pattern 3: Coverage gate symmetry (CI + pytest.ini + verify.ps1)

**What:** The 60% gate enforced in exactly three places, all identical.

Verified current state:
- `pytest.ini:6` addopts ALREADY include `--cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=60` → every local `pytest tests/` run is gated today (it fails at 17%, which is the current pain).
- `.github/workflows/test.yml:47` ALREADY has `--cov-fail-under=60` → CI would fail on every push today.
- `scripts/verify.ps1:128` runs plain `pytest tests/ -v` — it inherits the pytest.ini gate, but D-11 wants the gate **explicit** in the script so a future pytest.ini edit cannot silently disable it. Make the invocation explicit: `uv run pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=60`.
- The audit notes Phase 06 UAT ran with `--no-cov` — **do not introduce or rely on `--no-cov` anywhere** in this phase; it is how the gate silently slipped.

### Pattern 4: Milestone verification evidence (v1.0-VERIFICATION.md)

**What:** A single milestone-level doc (D-13/D-15) aggregating per-phase evidence. Format is at the agent's discretion; recommended structure:

1. Frontmatter: `milestone: v1.0`, `verified: <date>`, `status: complete` (flips to complete when this phase's gate runs green), `requirements-ledger` pointer.
2. Executive summary: 73/78 gaps closed; the 5 unsatisfied were exactly the closure items this phase resolves.
3. Requirement ledger: per phase, the D-code list (now backed by backfilled frontmatter) → evidence pointer (UAT.md / REVIEW-FIX.md / live-verify line).
4. Test evidence: full suite pass count (156 + new), coverage 17% → 60% journey table (D-12), `makemigrations --check` green, `manage.py check` green.
5. Flow evidence: the audit's 4/4 E2E flows re-verified.
6. **Deliberately low-coverage modules** (D-12): `app/utils/GB28181SipServer.py` (needs live SIP signaling + ZLM binaries) and engine inference paths (need ONNX models / GPU) — documented rationale, not hidden.
7. Remaining roadmap items: per-phase Nyquist (deferred), tech debt (VersionView dead file, `ALLOWED_HOSTS` whitespace IN-03, etc.).

**REVIEW-FIX.md convention** (precedent: `02-REVIEW-FIX.md`): frontmatter `phase / fixed_at / review_path / iteration / findings_in_scope / fixed / skipped / status: all_fixed`, then per-finding sections with `**Files modified:**`, `**Applied fix:**`, `**Change details:**`, and `**Commit ref:**` (the C1/C2/C3 refs from this phase). 04-REVIEW-FIX.md must enumerate CR-01..CR-06; 06-REVIEW-FIX.md must enumerate CR-01/CR-02 + WR-01..WR-09.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Coverage gate | custom script computing % from coverage.py output | `pytest-cov --cov-fail-under=60` (already in pytest.ini/CI) | off-by-one thresholds, missing-module accounting, HTML/report plumbing already solved |
| Migration drift check | diffing models vs SQL scripts | `python manage.py makemigrations --check --dry-run` | Django already reconciles model state vs migration graph; hand-rolled checks drift |
| Coverage aggregation across runs | custom combine logic | pytest-cov `.coverage` data file + `coverage report` | coverage 7.x handles branch/context tracking; use its report for per-module deltas |
| Git atomic-commit scripting | shell loops / rebase surgery to split one file's hunks | Whole-file per-concern commits (grouped by criticality per D-01) | `git add -p` is interactive; automated hunk splitting via `git apply --cached` is the #1 source of wrong-file commits |
| "Progress toward 60%" tracking | manual spreadsheets | `coverage report --skip-covered` per wave | shows exact per-module miss counts to steer the next test batch |

**Key insight:** Everything this phase needs is a *declared capability of the tools already installed*. Hand-rolling any of these re-introduces exactly the class of gaps (aspirational gate, unverifiable evidence) that forced this closure phase into existence.

## Runtime State Inventory

> Included — this IS a closure/migration phase (git state, DB file, migration chain, branch/worktree artifacts).

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `ai4video.sqlite3` — tracked since initial commit (c4eeba9), currently **dirty** (migrations 0002/0003 applied on it per audit `showmigrations [X]`) | **Commit it inside the CR-02 commit** (canonicalizes the deployed schema state; keeps the PyInstaller run-time story intact). Alternative — untrack + gitignore — changes deployment assumptions; only if planner gets user sign-off |
| Stored data | `db.sqlite3` — stray untracked file (settings.py points at `ai4video.sqlite3`, so this is orphaned) | gitignore (`db.sqlite3`) in the chore commit |
| Live service config | None — no external service holds AI4Video state (no n8n/Datadog/etc.) | None — verified by absence in STATE/audit |
| OS-registered state | Linked worktree `C:\Users\Administrator\AppData\Local\Temp\opencode\sv-06-reviewfix-17660` (branch `gsd-reviewfix/06-17660` checked out there — `git worktree list` confirms) | `git worktree remove --force <path>` THEN `git branch -D gsd-reviewfix/06-17660` — **after** new commits pass verification (D-03). Deletion order matters: `git branch -D` fails while the branch is checked out in a worktree |
| OS-registered state | `.review-fix-recovery-pending.json` (untracked file at `.planning/phases/06-other-upgrades/`) | Plain file delete (no commit needed — it was never tracked) after verification (D-03) |
| Secrets/env vars | None — no key renames in this phase (DB file already named `ai4video.sqlite3`) | None |
| Build artifacts | `.coverage` (root), `htmlcov/`, `.pytest_cache/`, `tests/__pycache__/`, `backups/`, `.opencode/node_modules/` (zod vendored), `app/migrations/__pycache__/` | gitignore all in the chore commit (C8). **Do NOT commit `.opencode/node_modules`** — thousands of vendored files |

**The canonical question answered:** after every file is committed, the only runtime systems still holding stale state are (a) the linked worktree + branch (removed last), (b) the untracked recovery marker (file delete), and (c) regenerable artifacts (gitignored). A fresh clone then reproduces the schema via the committed migration chain + `manage.py migrate` (auto-migrate on runserver, WR-04 now propagates errors).

## Common Pitfalls

### Pitfall 1: Deleting a branch that is checked out in a linked worktree
**What goes wrong:** `git branch -D gsd-reviewfix/06-17660` errors with "cannot delete branch checked out at ...sv-06-reviewfix-17660" — the stale branch survives and D-03 fails.
**Why it happens:** The review-fix subagent ran in a temp worktree (`Temp\opencode\sv-06-reviewfix-17660`); worktrees keep the branch registered.
**How to avoid:** Always `git worktree list` first, then `git worktree remove --force <path>` (force for dirty worktree) before `git branch -D`.
**Warning signs:** `git branch -a` shows a `+` prefix on the branch name (= checked out elsewhere).

### Pitfall 2: `ai4video.sqlite3` binary churn across commits
**What goes wrong:** The tracked DB file is dirty now; committing it in the wrong commit (or leaving it out) leaves tree unclean at phase end (D-02) or buries the DB change in the wrong concern.
**Why it happens:** SQLite files are binary; every migrate/tests-without-test-DB run mutates them.
**How to avoid:** Stage it explicitly only in C2 (CR-02 migration commit). Do not touch it in C1/C3/C4.
**Warning signs:** `git diff --stat` shows `ai4video.sqlite3 | Bin` in unexpected commits.

### Pitfall 3: `.gitignore` `__pycache__/*` does not recurse
**What goes wrong:** `tests/__pycache__/` shows as untracked even though line 9 says `__pycache__/*` — D-02 clean-tree fails.
**Why it happens:** A gitignore pattern with a separator in the middle (`__pycache__/*`) is anchored to the .gitignore's directory — it only matches the repo-root `__pycache__`. The repo works around this with 10 explicit per-directory lines (30-40); `tests/` was missed. `[VERIFIED: git check-ignore returned no match]`
**How to avoid:** Change line 9 to `__pycache__/` (matches any level directory). Optionally delete the now-redundant explicit per-dir lines 30-31, 34-40 (keep it minimal: fixing line 9 + removing 32-33 is sufficient and lowest-risk).

### Pitfall 4: `makemigrations --check` env failure in CI
**What goes wrong:** The new CI step crashes with `ValueError: DJANGO_SECRET_KEY environment variable is required` because settings.py raises when SECRET_KEY is unset and DEBUG is false (default false).
**Why it happens:** The step inherits no env from the previous step.
**How to avoid:** Give the step the identical env block as the "Run tests" step: `DJANGO_SECRET_KEY: ci-test-secret-key` + `DEBUG: "true"`.

### Pitfall 5: Coverage gate drift via `--no-cov` / `-n`/xdist
**What goes wrong:** A "quick" local run with `--no-cov` hides coverage regressions (this exact slippage produced the audit's "UAT passed but gate fails" finding); `pytest -n auto` with xdist measures subprocesses incorrectly if `pytest-cov` collides with the test DB strategy.
**Why it happens:** pytest.ini addopts are overridable at the CLI; xdist + coverage needs per-worker DB handling.
**How to avoid:** Never pass `--no-cov`; keep the default single-process run for gate-bearing runs (both CI and verify.ps1); if xdist is ever used, run coverage as a separate non-parallel pass.

### Pitfall 6: Abstracting/squashing the migration chain
**What goes wrong:** Squashing 0002/0003 into 0001 or regenerating 0001 breaks the "applied markers" on the deployed `ai4video.sqlite3` (django_migrations already records `0001_initial` applied) → CR-02-style "empty migration plan" recurrence.
**Why it happens:** Django deduplicates applied migrations by (app, name).
**How to avoid:** D-06 is locked — commit the chain as-is, never regenerate 0001, never squash. `makemigrations --check` stays green only if models ↔ migrations stay in sync.

### Pitfall 7: Frontmatter backfill style mismatch
**What goes wrong:** Phase 06 summaries put `requirements-completed` in a *second* YAML-ish block inside the doc body (after `# Dependency graph`), while phase 05 summaries have a plain frontmatter block — backfill that copies the wrong style silently breaks any tooling expecting frontmatter.
**Why it happens:** No repo-wide SUMMARY template was enforced.
**How to avoid:** Add `requirements-completed: [...]` as the last key **inside the existing YAML frontmatter block** of each summary (phase 05 style: keys after `completed:`). For phase 06 summaries no change needed (already present). Per-plan subsets: use the audit's per-plan mapping where determinable, otherwise the full phase D-list (traceability requires presence, not per-plan precision).

## Code Examples

### 1. CI step: migration drift gate (add to `.github/workflows/test.yml` after "Install dependencies")

```yaml
      - name: Check for uncommitted migrations
        env:
          DJANGO_SECRET_KEY: ci-test-secret-key
          DEBUG: "true"
        run: |
          python manage.py makemigrations --check --dry-run app
```
Source: Django admin `--check` semantics [CITED: https://docs.djangoproject.com/en/5.2/ref/django-admin/#cmdoption-makemigrations-check]; env requirement [VERIFIED: framework/settings.py:36-52]; step passes on this repo right now [VERIFIED: local execution].

### 2. verify.ps1 pytest invocation (replace line 128)

```powershell
        Write-Host "  Running pytest (coverage gate >= 60%)..."
        & $uvPath run pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=60 2>&1
        if ($LASTEXITCODE -eq 0) { Write-Pass "pytest" } else { Write-Fail "pytest (exit $LASTEXITCODE)" }
```

### 3. .gitignore edits (chore commit C8)

```gitignore
# line 9: replace
__pycache__/*
# with
__pycache__/

# remove lines 32-33 entirely:
app/migrations/*
app/migrations/__pycache__/*

# add at the end (runtime/coverage artifacts):
.coverage
htmlcov/
.pytest_cache/
backups/
db.sqlite3
.opencode/
```

### 4. Stale branch/worktree cleanup (executed ONLY after verification passes — D-03)

```powershell
# from the repo root (master)
git worktree remove --force "C:\Users\Administrator\AppData\Local\Temp\opencode\sv-06-reviewfix-17660"
git branch -D gsd-reviewfix/06-17660
Remove-Item ".planning/phases/06-other-upgrades/.review-fix-recovery-pending.json"  # untracked -> no commit needed
git worktree list   # verify: only D:/projects/AI4Video remains
git status --porcelain   # verify: empty (D-02)
```

### 5. Per-wave coverage steering (during coverage build-out)

```bash
uv run python -m coverage report --skip-covered   # per-module miss counts drive next test batch
uv run pytest tests/                              # full gate run (pytest.ini addopts enforce 60%)
```

### 6. Test pattern for legacy views (extend `tests/test_stream.py` / new `test_analysis_manager.py`)

```python
# Source pattern: existing tests/test_auth.py + tests/conftest.py (mock_g_config, mock_g_zlm fixtures) [VERIFIED: repo]
import pytest
from django.test import Client

@pytest.mark.django_db
class TestStreamAPI:
    def test_stream_list_requires_login_then_succeeds(self, client, mock_g_zlm, mock_g_config):
        # unauthenticated -> middleware redirect (covers middleware auth branch)
        assert client.get("/stream/index").status_code == 302
        # authenticated session + mocked ZLM -> exercises full view body (covers StreamView CRUD/list)
        session = client.session
        session["user"] = {"id": 1, "name": "tester"}
        session.save()
        resp = client.get("/stream/index")
        assert resp.status_code == 200
```
(This mirrors the established `Client` + session + monkeypatch-global pattern already proven by the 156 green tests; URL paths must be taken from `app/urls.py` at implementation time.)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| SQLite DB blindly shipped/gitignored alongside apps | Migrations version-controlled; `makemigrations --check` in CI; auto-migrate on runserver | Django 3.1+ (`--check`) / best practice current | Fresh clones reproduce schema; drift caught in CI |
| Coverage reported ad-hoc, gate aspirational | `--cov-fail-under` hard gate in pytest.ini + CI + verify script | pytest-cov (current: 7.1.0) | CI cannot silently pass with low coverage |
| Per-phase Nyquist VALIDATION.md | **This project:** UAT.md + REVIEW-FIX.md + milestone-level v1.0-VERIFICATION.md | Project convention (deferred per D-13) | Milestone-level evidence aggregation, less per-phase ceremony |
| Regenerated 0001_initial (phase 06 mistake) | Incremental 0002/0003 preserving applied-marker history | CR-02 (this phase commits them) | Deployed DBs migrate forward instead of no-op'ing |

**Deprecated/outdated:**
- `django-fernet-fields` (WR-08): dropped from requirements.txt — project uses its own `EncryptedCharField` in `app/fields.py`; `cryptography` is now the declared dependency.
- `python manage.py migrate --run-syncdb` swallowing failures: now propagates (WR-04) so boot aborts on schema mismatch.
- `django-ratelimit` XFF dead code: resolved (WR-06) — IP source unified; `key=lambda r: ip` or REMOTE_ADDR consistent choice.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `backups/` and `db.sqlite3` are runtime artifacts safe to gitignore (no deployment contract requires them tracked) | Runtime State Inventory | If the PyInstaller build references `backups/` or `db.sqlite3` by path, ignoring them could break packaging — planner should grep `ai4video.spec`/build scripts before the chore commit |
| A2 | `.opencode/` (local harness skills + vendored node_modules) is safe to gitignore wholesale | Runtime State Inventory | Team members cloning fresh lose the `verify-and-record` skill until the harness is re-installed — acceptable for a local dev harness [ASSUMED] |
| A3 | Existing engine tests (test_onnx_engine, test_algorithm) already prove engines are partially testable with mocked runtimes; remaining engine coverage stays low deliberately (D-12) | Coverage | If the planner over-invests in engine tests (real ONNX/GPU deps), effort is wasted — engines are declared out of the meaningful 60% path |
| A4 | `coverage report` data file (`.coverage`) reflects the ~17% baseline; treat exact % as approximate until first full gate run of the phase | Coverage | Mid-phase numbers may differ slightly from published baseline; the gate (not the doc) is the source of truth |
| A5 | pytest-xdist (`-n`) is not used in gate-bearing runs (CI and verify.ps1 run serial) | Pitfall 5 | If someone adds `-n auto` to verify.ps1, coverage measurement may split across workers — keep serial for gate runs |

## Open Questions

1. **Tracked `ai4video.sqlite3` — commit the updated DB in CR-02, or untrack it?**
   - What we know: it is tracked since the initial commit and is currently dirty (0002/0003 applied on it, per audit). Committing it inside C2 keeps the deployed-DB story intact and satisfies D-02 with zero behavioral change.
   - What's unclear: whether untracking (gitignore + `git rm --cached`) is preferable going forward — a committed binary DB is an anti-pattern once migrations are version-controlled.
   - Recommendation: **commit in C2** (minimal change, preserves PyInstaller packaging behavior). Leave untracking to a future maintenance phase. Planner should verify `ai4video.spec`/build scripts don't expect a freshly-cloned DB elsewhere.
2. **Frontmatter backfill per-plan subset vs full phase D-list.**
   - What we know: audit only requires *presence* of `requirements-completed`; 06 summaries use per-plan subsets, 02 uses per-plan subsets.
   - What's unclear: per-plan precision for 01/03/04/05 requires mapping each plan to its D-codes (large grep effort, partial ambiguity).
   - Recommendation: backfill per-plan where the plan doc states its scope (audit's mapping suffices), else the full phase D-list. Traceability gap closes either way.
3. **Should the coverage build-out ship as one mega-wave or interleaved with commits?**
   - What we know: gate runs fail until tests land; D-10 dictates priority order (auth → stream CRUD → analysis).
   - What's unclear: whether the executor commits test files per module (cleaner history, more gate runs) or at wave granularity.
   - Recommendation: commit per module-group (e.g., `test(06): cover stream CRUD endpoints`) — each group leaves the suite passing-with-gate or only marginally short, and D-12's per-module delta table becomes trivially accurate.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| uv | local runs (verify.ps1, makemigrations, pytest) | ✓ | system-installed (`C:\Users\Administrator\.local\bin\uv.exe`) | plain `python` in `.venv` |
| Python | runtime + tests | ✓ | 3.12.13 (local); CI matrix 3.11/3.12 | — |
| git | atomic commits, worktree/branch cleanup | ✓ | repo at b37042e (master) | — |
| GitHub Actions | CI gate (coverage + migrations) | ✓ (config only) | test.yml present; runs on push/PR to master | local `uv run pytest tests/` mirrors it |
| ZLM binary (`ai4video_zlm.exe`) | live media streaming | ✗ | — | **Not required** — all tests mock `g_zlm` (conftest `mock_g_zlm`) |
| ONNX runtime/models, GPU | inference engines | ✗ | — | Engines deliberately low-coverage (D-12); engine tests mock runtimes |
| PowerShell 5.1 | verify.ps1 | ✓ | system | — |

**Missing dependencies with no fallback:** none — the phase's requireables are repo-local (git, uv, Python, installed pytest stack). The two external binaries absence (ZLM, ONNX/GPU) is *by design* and drives the D-12 documentation requirement, not a blocker.

## Validation Architecture

> `.planning/config.json` absent → `workflow.nyquist_validation` treated as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 + pytest-django 4.13.0 + pytest-cov 7.1.0 (coverage 7.15.4) |
| Config file | `pytest.ini` (DJANGO_SETTINGS_MODULE=framework.settings; addopts include `--cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=60`) |
| Quick run command | `uv run pytest tests/ -q` (per-commit sanity, no coverage interpretation) |
| Full suite command | `uv run pytest tests/` (addopts auto-enforce the 60% gate + html report) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| phase05-D-05 | Coverage ≥ 60% app-wide | unit/integration (new tests) | `uv run pytest tests/ --cov=app --cov-fail-under=60` | ❌ Wave 0 — existing 156 tests at 17%; new files to be created per module (extend test_stream.py, test_auth.py; new test_analysis_manager.py, test_utils_core.py recommended) |
| phase05-D-08 | CI enforces gate | CI config | `pytest tests/ ... --cov-fail-under=60` (test.yml:47 — exists ✓) + verify.ps1 explicit flags | ✅ `test.yml` exists; ❌ verify.ps1 edit |
| phase06-REVIEW | CR-01/02/WR-01..09 regression | unit (middleware) | `uv run pytest tests/test_phase06_fixes.py -v` | ✅ untracked file exists; committed in C4 |
| phase06-D-12 (audit BLOCK) | Migration chain reproducible | config drift check | `uv run python manage.py makemigrations --check --dry-run app` (exits 0 ✓) + CI step | ❌ CI step to add |
| phase04-REVIEW | 6 criticals closed + documented | documentation (REVIEW-FIX) + existing tests | existing suite green + `04-REVIEW-FIX.md` with commit refs | ❌ doc to write |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/ -q` (fast; keeps regressions out of commits)
- **Per wave merge:** `uv run pytest tests/` (full gate with coverage) + `uv run python manage.py makemigrations --check --dry-run app` + `uv run python manage.py check`
- **Phase gate:** full suite green with `--cov-fail-under=60`, migrations check green, `git status` clean, then `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_analysis_manager.py` — covers REQ phase05-D-05 (pipeline/manager/inference_pool: manager 589 stmts / 20%, pipeline 729 / 15%)
- [ ] `tests/test_stream_api.py` (or extend `test_stream.py`) — StreamView 755 stmts / 4% — largest single target
- [ ] `tests/test_views_remaining.py` (ControlView 457/6%, SmallModelView 614/6%, InnerlView 233/11%, NvrView 283/8%, LLMView 232/7%, IndexView 105/10%, SystemView 223/8%) — consolidation file recommended for volume
- [ ] `tests/test_utils_core.py` (GpuInfo 288/0%, ZLMediaKitApi 252/12%, OSSystem 221/9%, MediaServerManager 106/0%, GlobalUtils 175/45%)
- [ ] No framework install needed — pytest stack verified present (pytest 9.1.1, pytest-django 4.13.0, pytest-cov 7.1.0)

## Security Domain

> `security_enforcement` enabled (config.json absent = enabled). This phase is security-relevant: it *commits* security fixes (CR-01/CR-02, phase 04 criticals) and *tests* security behavior.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | `/inner/` Safe-header auth (CR-01, `hmac.compare_digest`), `/open` Safe-header check, login credential flow (UserView) — covered by test_phase06_fixes.py |
| V3 Session Management | yes | `request.session.cycle_key()` on login (WR-09) — regression test in test_phase06_fixes.py |
| V4 Access Control | yes | Whitelist exact-path matching (WR-01 — `/nvr/openSnapShot` no longer whitelisted); 403 JSON for unauthorized `/inner/` |
| V5 Input Validation | partial | Legacy code lacks systematic input validation; mitigation is parameterized ORM queries (04 CR-01) + `os.path.basename` (04 CR-08). New tests assert rejection paths but do not introduce a validation layer (out of scope) |
| V6 Cryptography | yes | Fernet via declared `cryptography==50.0.0` (WR-08); `EncryptedCharField` sizing (WR-03); timing-safe compares (`hmac.compare_digest`) |
| V9 Logging/Vulnerability detection (audit trail) | yes | AuditMiddleware denylist auditing (WR-05) writes to `av_audit_log` via committed 0002 migration (CR-02) — the audit chain is now reproducible from a fresh clone |
| V11 Business Logic (rate limiting) | yes | RateLimitMiddleware 200/min with consistent IP source (WR-06 — XFF dead code removed) |

### Known Threat Patterns for {Django 5.2 / AI4Video stack}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Unauthenticated machine-endpoint abuse (`/inner/*` ZLM/GB28181 callbacks: stream delete/overwrite, SIP INVITE flood) | Tampering / DoS | CR-01 Safe-header 403 gate — committed + regression-tested (test_inner_without_safe_header_redirects) |
| Session fixation on login | Elevation | `cycle_key()` (WR-09) — committed + tested |
| Timing side-channel on shared-secret compare | Information Disclosure | `hmac.compare_digest` (04 CR-02/CR-03; 06 `_check_safe`) |
| SQL injection via raw SQL utilities | Tampering | Parameterized queries (04 CR-01) — verified fixed, now under test (Database.py 17% → improving as utils tests land) |
| Audit-log integrity loss (`av_audit_log` never created) | Tampering / repudiation | 0002_auditlog migration committed; `makemigrations --check` prevents regression |
| Rate-limit bypass via XFF spoofing / dead code | DoS | WR-06 IP-source consistency; rate-limit tests green |
| Secret leakage in API responses (`api_key`) | Information Disclosure | 04 CR-04 masked (****last4) — regression coverage in auth/LLMView tests where feasible |

## Sources

### Primary (HIGH confidence — verified by local execution against this repo)
- `git status --porcelain`, `git branch -a`, `git worktree list`, `git diff <files>`, `git ls-files` — dirty/untracked/branch/worktree inventory and concern mapping (2026-08-10)
- `uv run python manage.py makemigrations --check --dry-run app` → exit 0 "No changes detected" — migration drift status
- `uv run python -m coverage report` → 12,706 stmts / 10,547 miss / 17% baseline; per-module table
- `uv pip show pytest pytest-django pytest-cov coverage` → 9.1.1 / 4.13.0 / 7.1.0 / 7.15.4
- `uv run pytest --collect-only -q` → 156 tests collected; addopts enforce the gate (run failed with "Required test coverage of 60% not reached" as expected at 17%)
- `framework/settings.py` (SECRET_KEY guard, DATABASES=ai4video.sqlite3), `pytest.ini`, `scripts/verify.ps1`, `.github/workflows/test.yml`, `.gitignore`, `manage.py`, `tests/conftest.py` reads
- `.planning/v1.0-MILESTONE-AUDIT.md`, `06-REVIEW.md`, `04-REVIEW.md`, `02-REVIEW-FIX.md`, `06-UAT.md`, `05-CONTEXT.md`, `04-CONTEXT.md`, `03-CONTEXT.md`, `01-CONTEXT.md`, `05-01-SUMMARY.md`, `06-01-SUMMARY.md`, `.review-fix-recovery-pending.json`, `CONCERNS.md §Test Coverage Gaps`

### Secondary (MEDIUM confidence — cited official docs)
- Django 5.2 admin `makemigrations --check` semantics — https://docs.djangoproject.com/en/5.2/ref/django-admin/#cmdoption-makemigrations-check `[CITED]`

### Tertiary (LOW confidence — training data, flagged)
- None asserted as findings. Assumption-graded items are confined to the Assumptions Log (A1-A5).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every tool version verified installed; no new packages introduced
- Architecture: HIGH — commit grouping, worktree cleanup, CI/cov parity, and migration gate all verified against the live repo (`git diff`, `git worktree list`, exit-code checks)
- Pitfalls: HIGH — the four operative pitfalls (worktree-bound branch, DB churn, `__pycache__/*` anchoring, CI env) each confirmed by direct observation; coverage-math pitfalls (A3-A5) MEDIUM

**Research date:** 2026-08-10
**Valid until:** 2026-08-17 (10 days — closure phase over a fast-moving git state; re-verify `git status` and coverage baseline if planning slips)
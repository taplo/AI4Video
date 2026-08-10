---
phase: 07
slug: close-milestone-v1-0-gaps-commit-review-fix-migrations-cover
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-10
---

# Phase 07 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 + pytest-django 4.13.0 + pytest-cov 7.1.0 |
| **Config file** | `pytest.ini` (DJANGO_SETTINGS_MODULE=framework.settings; addopts: `--cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=60`) |
| **Quick run command** | `uv run pytest tests/ -q` |
| **Full suite command** | `uv run pytest tests/` (addopts enforce 60% gate + html report) |
| **Estimated runtime** | ~60 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/ -q` (per-commit sanity — no coverage interpretation)

- **After every plan wave:** Run full gate: `uv run pytest tests/` + `uv run python manage.py makemigrations --check --dry-run app` + `uv run python manage.py check`

- **Before `/gsd-verify-work`:** Full suite green with `--cov-fail-under=60`, migrations check green, `git status` clean.

- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | phase06-REVIEW | T-07-01 | CR-01 `/inner/` Safe-header auth regression | integration | `uv run pytest tests/test_phase06_fixes.py -v` | ✅ | ⬜ pending |
| 07-01-02 | 01 | 1 | phase06-REVIEW | T-07-02 | CR-02 audit log via committed migrations | migration | `uv run python manage.py makemigrations --check --dry-run app` | ✅ | ⬜ pending |
| 07-02-01 | 02 | 2 | phase05-D-05 | — | Coverage ≥ 60% app-wide | unit/integration | `uv run pytest tests/ --cov=app --cov-fail-under=60` | ❌ W0 | ⬜ pending |
| 07-02-02 | 02 | 2 | phase05-D-08 | — | CI enforces gate symmetrically | CI config | `pytest ... --cov-fail-under=60` in test.yml + verify.ps1 | ✅ test.yml | ⬜ pending |
| 07-03-01 | 03 | 2 | phase05-D-12 | — | Coverage journey documented | docs | `07-SUMMARY.md` contains baseline→60% delta table | — | ⬜ pending |
| 07-04-01 | 04 | 3 | phase04-REVIEW | — | 04-REVIEW-FIX.md closes 6 criticals w/ commit refs | docs | `04-REVIEW-FIX.md` exists w/ commit hashes | ❌ | ⬜ pending |
| 07-04-02 | 04 | 3 | phase06-REVIEW | — | 06-REVIEW-FIX.md closes CR/WR w/ commit refs | docs | `06-REVIEW-FIX.md` exists w/ commit hashes | ❌ | ⬜ pending |
| 07-05-01 | 05 | 3 | phase06-REVIEW | — | v1.0-VERIFICATION.md aggregates all phase evidence | docs | `v1.0-VERIFICATION.md` exists, status passed | ❌ | ⬜ pending |
| 07-05-02 | 05 | 3 | (D-14) | — | SUMMARY frontmatter backfilled | docs | grep `requirements-completed:` in 01..06 SUMMARYs | ❌ | ⬜ pending |
| 07-06-01 | 06 | 3 | phase06-REVIEW | — | Stale branch + marker removed post-verify | git | `git branch -D gsd-reviewfix/06-17660`; marker deleted; `git worktree list` clean | — | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_analysis_manager.py` — covers phase05-D-05 (manager 589 stmts/20%, pipeline 729/15%)
- [ ] `tests/test_stream_api.py` (or extend `test_stream.py`) — StreamView 755 stmts/4%, largest single target
- [ ] `tests/test_views_remaining.py` — ControlView 457/6%, SmallModelView 614/6%, InnerlView 233/11%, NvrView 283/8%, LLMView 232/7%, IndexView 105/10%, SystemView 223/8%
- [ ] `tests/test_utils_core.py` — GpuInfo 288/0%, ZLMediaKitApi 252/12%, OSSystem 221/9%, MediaServerManager 106/0%, GlobalUtils 175/45%
- [ ] No framework install needed — pytest stack verified present (pytest 9.1.1, pytest-django 4.13.0, pytest-cov 7.1.0)

*Existing infrastructure covers the remainder of phase requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Stale branch cleanup | phase06-REVIEW | Requires git worktree state inspection | `git worktree remove --force <temp>` then `git branch -D gsd-reviewfix/06-17660`, confirm `git worktree list` clean |
| D-12 coverage-journey narrative | phase05-D-12 | Requires judgment on why GB28181/engines stay low | Write baseline 17% → 60% per-module delta table in SUMMARY with justifications |

*All other phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
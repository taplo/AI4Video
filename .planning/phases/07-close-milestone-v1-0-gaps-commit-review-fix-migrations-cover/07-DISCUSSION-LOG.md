# Phase 7: Close milestone v1.0 gaps - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-10
**Phase:** 7-close-milestone-v1-0-gaps-commit-review-fix-migrations-cover
**Areas discussed:** Review-fix commit strategy, Migration version-control, Coverage gate resolution, Validation artifact scope

---

## Review-fix Commit Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| One consolidated commit | Single commit grouping all CR/WR/test file | |
| Atomic per-concern commits | Separate commits: CRITICALs first, then warnings, then tests | ✓ |
| Two commits: code+tests, docs | Code+tests together, then docs | |

**User's choice:** Atomic per-concern commits
**Notes:** Cleaner blame/revert; commit granularity per-concern with CRITICALs prioritized.

| Option | Description | Selected |
|--------|-------------|----------|
| Delete both | Delete stale branch + recovery marker immediately | |
| Delete after verification | Keep as backup until new commits verified, then delete | ✓ |
| Keep both for now | Retain marker + branch | |

**User's choice:** Delete after verification
**Notes:** Branch and marker retained as backup until new commits are verified, then removed.

| Option | Description | Selected |
|--------|-------------|----------|
| Include all dirty files | Commit pre-existing dirty files so working tree is clean | ✓ |
| Review-fix scope only | Only commit files in review-fix scope | |

**User's choice:** Include all dirty files
**Notes:** Working tree must be clean after closure; GB28181SipServer.py included.

| Option | Description | Selected |
|--------|-------------|----------|
| Document both 04+06 | Write 06-REVIEW-FIX.md and 04-REVIEW-FIX.md with commit refs | ✓ |
| 06 only, 04 brief | Only 06 doc, 04 as brief note | |

**User's choice:** Document both 04+06
**Notes:** Satisfies audit closure gap for both phases (04's 6 criticals + 06's CR/WR findings).

---

## Migration Version-Control

| Option | Description | Selected |
|--------|-------------|----------|
| Commit chain as-is | Un-gitignore app/migrations/, commit 0001/0002/0003 | ✓ |
| Squash to single 0001 | Rebuild to one clean migration | |
| Keep gitignored + bootstrap | Regenerate via cold-start script | |

**User's choice:** Commit chain as-is
**Notes:** Preserves applied schema; matches Django default best practice.

| Option | Description | Selected |
|--------|-------------|----------|
| With CR-02 commit | Migrations committed in same atomic CR-02 commit | ✓ |
| Separate migration commit | Independent chore commit | |

**User's choice:** With CR-02 commit
**Notes:** 0002/0003 are inseparable from the CR-02 fix.

| Option | Description | Selected |
|--------|-------------|----------|
| CI reproduces schema | Add makemigrations --check gate; CI verifies fresh-clone reproduction | ✓ |
| No extra verification | Trust committed chain | |

**User's choice:** CI reproduces schema
**Notes:** makemigrations --check gate ensures no drift between models and committed migrations.

---

## Coverage Gate Resolution

| Option | Description | Selected |
|--------|-------------|----------|
| Reach 60% (honor D-05) | Add tests to genuinely reach 60% across app/ | ✓ |
| Lower gate, keep 60% aspirational | Retarget gate to realistic floor | |
| Coverage on tested modules only | Gate only on tested modules | |

**User's choice:** Reach 60% (honor D-05)
**Notes:** Honoring locked Phase 05 decision; risks longer closure phase but committed.

| Option | Description | Selected |
|--------|-------------|----------|
| Target high-value modules first | Auth/middleware, stream CRUD, analysis pipeline | ✓ |
| Even spread to hit number | Dilute across all modules | |

**User's choice:** Target high-value modules first
**Notes:** Follows CONCERNS.md priority matrix.

| Option | Description | Selected |
|--------|-------------|----------|
| Hard gate in CI + local | --cov-fail-under=60 in both CI and local verify | ✓ |
| CI-only gate | Enforcement only in CI | |

**User's choice:** Hard gate in CI + local
**Notes:** Dev and CI enforce identically.

| Option | Description | Selected |
|--------|-------------|----------|
| Document journey + leftover | Baseline 17%→60%, per-module delta, justified untested modules | ✓ |
| Assert final number only | Just report final 60% | |

**User's choice:** Document journey + leftover
**Notes:** Journeys recorded in closure SUMMARY for future phases.

---

## Validation Artifact Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Milestone-level only | One v1.0-VERIFICATION.md summarizing all 6 phases | ✓ |
| Per-phase VALIDATION (Nyquist) | Formal per-phase VALIDATION.md for all phases | |
| Milestone now, per-phase deferred | Milestone doc now, per-phase later | |

**User's choice:** Milestone-level only
**Notes:** Consistent with project's UAT-centric convention; avoids 6x retro work.

| Option | Description | Selected |
|--------|-------------|----------|
| Only milestone doc | Leave SUMMARY frontmatter as-is | |
| Backfill SUMMARY frontmatter | Add requirements-completed frontmatter to 04/05/06 | ✓ |

**User's choice:** Backfill SUMMARY frontmatter
**Notes:** Addresses audit traceability gap.

| Option | Description | Selected |
|--------|-------------|----------|
| Standard phase lifecycle | 07-SUMMARY.md via normal executor flow | ✓ |
| Plan a 07-VALIDATION.md | Validation as plan artifact | |

**User's choice:** Standard phase lifecycle
**Notes:** Closure evidence produced through standard phase lifecycle.

---

## the agent's Discretion

- Atomic commit splitting granularity (per-concern vs by-criticality grouping) — must prioritize CRITICALs
- Specific new test case writing approach
- VERIFICATION.md evidence organization format

## Deferred Ideas

- Per-phase Nyquist VALIDATION.md — deferred to post-v1.0 maintenance phase
- Coverage gate lowering / module-only gate — explicitly rejected (D-05 stays 60%)
- Squashing migrations to single 0001 — explicitly rejected (D-06 keeps incremental chain)
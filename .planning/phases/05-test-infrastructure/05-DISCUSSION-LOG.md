# Phase 5: test-infrastructure - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-09
**Phase:** 05-test-infrastructure
**Areas discussed:** Test framework choice, Coverage targets, Test organization, CI/CD integration

---

## Test framework choice

| Option | Description | Selected |
|--------|-------------|----------|
| pytest + pytest-django | Modern, fast, great fixtures, pytest-django plugin (RECOMMENDED) | ✓ |
| Django TestCase | Built-in, no extra dependencies, simpler setup | |
| You decide | You decide based on codebase patterns | |

**User's choice:** pytest + pytest-django
**Notes:** User chose the modern testing framework with good fixture support

---

## Coverage targets

| Option | Description | Selected |
|--------|-------------|----------|
| 60% core utilities | Start with core utilities, models, and security fixes (RECOMMENDED) | ✓ |
| 80% all modules | Comprehensive coverage including views and services | |
| You decide | You decide based on testing gaps analysis | |

**User's choice:** 60% core utilities
**Notes:** User chose to start with high-priority modules and achieve 60% coverage

---

## Test organization

| Option | Description | Selected |
|--------|-------------|----------|
| tests/ directory | tests/ at project root (RECOMMENDED) | ✓ |
| app/tests.py | app/tests.py (Django default) | |
| You decide | You decide based on project structure | |

**User's choice:** tests/ directory
**Notes:** User chose project root tests/ directory for better organization

---

## CI/CD integration

| Option | Description | Selected |
|--------|-------------|----------|
| Push + PR triggers | Run tests on every push and PR (RECOMMENDED) | ✓ |
| PR only | Run tests only on PRs | |
| You decide | You decide based on team workflow | |

**User's choice:** Push + PR triggers
**Notes:** User chose to run tests on both push and PR for comprehensive coverage

---

## the agent's Discretion

- Test case implementation details
- Fixture design
- Mock strategy (based on TESTING.md recommendations)

---

## Deferred Ideas

None — discussion stayed within phase scope

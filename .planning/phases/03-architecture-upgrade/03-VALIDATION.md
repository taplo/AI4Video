# Phase 3: 架构升级 - Validation

**Created:** 2026-08-08
**Phase:** 03-architecture-upgrade

## Validation Strategy

Phase 3 validation covers database modernization, model refactoring, configuration security, and process management. Tests are deferred to Phase 5 (testing infrastructure), so Phase 3 uses **manual verification gates** and **automated grep/CLI checks** for commit-time validation.

### Test Framework Status
| Property | Value |
|----------|-------|
| Framework | pytest (installed in Phase 5) |
| Config file | None — deferred |
| Phase 3 test command | Manual verification + grep checks |
| Full suite command | `pytest tests/ -v` (Phase 5) |

## Requirement → Verification Map

| Req ID | Behavior | Verification Method | Automated Command | Plan |
|--------|----------|--------------------|--------------------|------|
| D-01 | SQLite WAL mode active | Integration | `python -c "from django.db import connection; cursor=connection.cursor(); cursor.execute(\"PRAGMA journal_mode\"); print(cursor.fetchone())"` | 03-01 |
| D-02 | All views use ORM | Unit | `grep -r "g_database\." app/views/ \| wc -l` returns 0 | 03-04 |
| D-03 | Django default connection | Unit | Verify no custom connection management in settings | 03-01 |
| D-04 | g_dbLock removed | Unit | `grep -r "g_dbLock" app/ \| wc -l` returns 0 | 03-01 |
| D-05/D-08 | BaseModel used by all models | Unit | `grep -c "class.*BaseModel" app/models.py` returns 1+ | 03-02 |
| D-06 | Database rebuilt (no migration scripts) | Manual | Database file recreated, all models created | 03-02 |
| D-07 | Encrypted fields work | Integration | EncryptedCharField in models, verify DB stores encrypted bytes | 03-02 |
| D-09/D-12 | .env loaded correctly | Unit | `python -c "from dotenv import load_dotenv; load_dotenv(); import os; assert os.environ.get('TEST_KEY')"` | 03-03 |
| D-10 | Thread-safe config (RLock) | Unit | Verify threading.RLock in Config class | 03-03 |
| D-11 | Only sensitive values migrated | Manual | Verify .env contains only: SECRET_KEY, safe key, media secret, SIP password | 03-03 |
| D-13/D-14 | ThreadPoolExecutor manages pipelines | Unit | Start/stop analysis, verify thread pool lifecycle | 03-03 |
| D-15 | Signal handlers registered | Unit | `python -c "import signal; assert signal.getsignal(signal.SIGTERM) != signal.SIG_DFL"` | 03-03 |
| D-16 | Worker health checks | Unit | Verify heartbeat mechanism in AnalysisManager | 03-03 |

## Commit-Time Verification Gates

Each plan includes grep-based verification at commit time:

### Plan 01 — Database & Lock Removal
```bash
# WAL mode enabled (signal receiver exists)
grep -c "connection_created" framework/apps.py  # Should return 1+
# g_dbLock removed
grep -r "g_dbLock" app/ | wc -l  # Should return 0
```

### Plan 02 — BaseModel Mixin
```bash
# BaseModel defined
grep -c "class BaseModel" app/models.py  # Should return 1
# Models inherit BaseModel
grep -c "BaseModel" app/models.py  # Should return 9+ (1 def + 8 models)
```

### Plan 03 — Config Security & AnalysisManager
```bash
# .env file exists
test -f .env && echo "exists"
# load_dotenv called in settings
grep -c "load_dotenv" framework/settings.py  # Should return 1+
# ThreadPoolExecutor used
grep -c "ThreadPoolExecutor" app/analysis/manager.py  # Should return 1+
```

### Plan 04 — Raw SQL → ORM Migration
```bash
# No g_database calls in views
grep -r "g_database\." app/views/ | wc -l  # Should return 0
# No g_database calls in GlobalUtils
grep -r "g_database\." app/utils/GlobalUtils.py | wc -l  # Should return 0
# ORM used in views
grep -r "StreamModel\.objects" app/views/ | wc -l  # Should return 1+
grep -r "LLMModel\.objects" app/views/ | wc -l  # Should return 1+
grep -r "User\.objects" app/views/ | wc -l  # Should return 1+
grep -r "LogModel\.objects" app/views/ | wc -l  # Should return 1+
```

## Sampling Rate

| Gate | Command | Frequency |
|------|---------|-----------|
| Per task commit | Manual verification + grep checks | Every commit |
| Per wave merge | Full grep sweep across all modified files | End of wave |
| Phase gate | All grep checks pass + manual functional test | Before /gsd-verify-work |

## Wave 0 Gaps

Tests deferred to Phase 5:
- [ ] `tests/test_database.py` — covers D-01, D-04 (WAL mode, lock removal)
- [ ] `tests/test_models.py` — covers D-05, D-07, D-08 (BaseModel, encryption)
- [ ] `tests/test_views_orm.py` — covers D-02 (raw SQL → ORM)
- [ ] `tests/test_config.py` — covers D-09, D-10, D-12 (env vars, RLock)
- [ ] `tests/test_analysis_manager.py` — covers D-13, D-14, D-15, D-16 (ThreadPoolExecutor, signals, health)
- [ ] `tests/conftest.py` — shared fixtures (Django test client, mock streams)

## Phase Completion Criteria

Phase 3 is complete when:
- [ ] All 16 decisions (D-01 through D-16) verified via grep/manual checks
- [ ] No `g_database.` calls remain in views or GlobalUtils
- [ ] No `g_dbLock` references remain in codebase
- [ ] All models inherit BaseModel
- [ ] .env file created with sensitive values
- [ ] ThreadPoolExecutor replaces multiprocessing in AnalysisManager
- [ ] All plans produce SUMMARY.md files

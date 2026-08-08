---
phase: 02-onnx-fix
plan: 02
subsystem: api
tags: [onnx, logging, label-discovery, yolo]

# Dependency graph
requires:
  - phase: 02-onnx-fix
    provides: "Research on ONNX model detection pipeline failures"
provides:
  - "Warning logging on model path resolution failure"
  - "Extended label file discovery (labels.txt, {stem}.txt, static/labels/)"
affects: [02-onnx-fix]

# Tech tracking
tech-stack:
  added: []
  patterns: [warning-logging, multi-path-label-search]

key-files:
  created: []
  modified:
    - app/analysis/worker_pool.py
    - app/analysis/engines/base.py

key-decisions:
  - "Used logger.warning() with Chinese messages matching existing codebase convention"
  - "Static labels directory search wrapped in try/except to avoid Django import failures"
  - "Final return [] preserved per D-09 (never fail)"

patterns-established:
  - "Label search order: .labels → .names → .yaml → labels.txt → {stem}.txt → static/labels/"

requirements-completed: [D-06, D-08, D-09]

# Metrics
duration: 5min
completed: 2026-08-07
---

# Phase 2 Plan 2: ONNX Model Detection Fix Summary

**Warning logging on model path failure and multi-path label file discovery covering labels.txt, {stem}.txt, and static/labels/ directory**

## Performance

- **Duration:** 5 min
- **Started:** 2026-08-07T00:00:00Z
- **Completed:** 2026-08-07T00:05:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishes
- Added diagnostic warning logs to `resolve_model_path()` for two failure modes: missing weight directory and missing model file
- Extended `BaseEngine._resolve_labels()` with three new search paths per D-08: `labels.txt`, `{model_stem}.txt`, and `static/labels/` directory fallback
- All file reads wrapped in try/except; missing labels never crash (D-09)

## Task Commits

Each task was committed atomically:

1. **Task 01: Add warning log in resolve_model_path()** - N/A (non-git project)
2. **Task 02: Extend _resolve_labels() with additional search paths** - N/A (non-git project)

## Files Created/Modified
- `app/analysis/worker_pool.py` - Added two warning logs before `return ""` in `resolve_model_path()`
- `app/analysis/engines/base.py` - Added three new label search steps after existing `.yaml` search

## Decisions Made
- Used `logger.warning()` with Chinese messages matching existing codebase convention (e.g., `"weight目录未配置"`)
- Static labels directory search wrapped in `try/except` around Django `settings` import to avoid import failures in non-Django contexts
- Final `return []` preserved per D-09 (never fail on missing labels)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Known Stubs

None - all implemented code is functional.

## Threat Flags

None - no new security-relevant surface introduced.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Warning logging in place for model path resolution failures
- Label discovery expanded to cover common YOLO export patterns (labels.txt, {stem}.txt)
- Both changes are additive; existing behavior unchanged for models with .labels/.names/.yaml sidecar files

## Self-Check: PASSED

- `resolve_model_path.*模型文件不存在` in worker_pool.py: 1 match ✓
- `weight目录未配置` in worker_pool.py: 1 match ✓
- `labels.txt` in base.py: 2 matches ✓
- `stem_txt` in base.py: 4 matches ✓
- `static.*labels` in base.py: 5 matches ✓
- Original `.labels`/`.names`/`.yaml` search code unchanged ✓
- `return []` final fallback preserved ✓

---
*Phase: 02-onnx-fix*
*Completed: 2026-08-07*

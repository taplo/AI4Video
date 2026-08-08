---
phase: 02-onnx-fix
plan: 01
subsystem: api
tags: [onnx, yolo, auto-detect, onnxruntime, numpy]

# Dependency graph
requires:
  - phase: 01-init
    provides: "BaseEngine, OnnxEngine, YOLO postprocessing framework"
provides:
  - "algorithm_type auto-detection from output tensor shape at probe time"
  - "input auto-resize to model's actual dimensions"
  - "comprehensive error logging throughout ONNX detection pipeline"
  - "shape mismatch warning when algorithm_type doesn't match output format"
affects: [02-02, 03-labels, frontend]

# Tech tracking
tech-stack:
  added: []
  patterns: [auto-detect-heuristic, input-auto-resize, shape-mismatch-logging]

key-files:
  created: []
  modified:
    - app/views/SmallModelView.py
    - app/analysis/engines/onnx_engine.py
    - app/analysis/engines/yolo_postprocess.py

key-decisions:
  - "Used output shape dim comparison heuristic: dim1 > dim2 = v5, dim1 < dim2 = v8+"
  - "Auto-resize uses model's native input shape from session, falls back to user-configured input_size"
  - "Shape mismatch logging only fires when results are empty AND output shape contradicts algorithm_type"

patterns-established:
  - "Pattern: _detect_yolo_version() helper for YOLO version inference from tensor shapes"
  - "Pattern: _model_input_shape stored during load() for use in _preprocess()"

requirements-completed: [D-01, D-02, D-03, D-04, D-05, D-07, D-10, D-11, D-12]

# Metrics
duration: 8min
completed: 2026-08-07
---

# Phase 2 Plan 01: ONNX Model Detection Fix Summary

**Auto-detect YOLO version from output tensor shape, auto-resize input to model dimensions, and add shape mismatch logging throughout the ONNX detection pipeline**

## Performance

- **Duration:** 8 min
- **Started:** 2026-08-07
- **Completed:** 2026-08-07
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Probe endpoint now returns `algorithm_type_detected` with auto-detected YOLO version (yolo5/yolo8)
- OnnxEngine auto-resizes input to match model's actual input shape instead of user-configured size
- Shape mismatch warnings logged when algorithm_type doesn't match output tensor format

## Task Commits

Each task was committed atomically:

1. **Task 01: Add algorithm_type auto-detection in probe endpoint** - (feat)
2. **Task 02: Add input auto-resize and enhanced error logging in OnnxEngine** - (feat)
3. **Task 03: Add shape mismatch logging in yolo_postprocess.py** - (feat)

## Files Created/Modified
- `app/views/SmallModelView.py` - Added `_detect_yolo_version()` helper and `algorithm_type_detected` / `input_size_inferred` fields to probe response
- `app/analysis/engines/onnx_engine.py` - Added `_model_input_shape` storage, auto-resize in `_preprocess()`, enhanced error logging in `load()` and `detect()`
- `app/analysis/engines/yolo_postprocess.py` - Added shape mismatch warning in `_decode_detect()` when results are empty and output shape contradicts algorithm_type

## Decisions Made
- Used output shape dim comparison heuristic: dim1 > dim2 = v5, dim1 < dim2 = v8+ (D-02)
- Auto-resize uses model's native input shape from session, falls back to user-configured input_size for dynamic shapes (D-05)
- Shape mismatch logging only fires when results are empty AND output shape contradicts algorithm_type — avoids noise on valid low-confidence detections
- When `_detect_yolo_version()` returns None, `algorithm_type_detected` falls back to user-provided algorithm_type (D-10)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- ONNX detection pipeline now correctly auto-detects YOLO version at probe time
- Input auto-resize ensures detection works regardless of user-configured input_size
- Shape mismatch logging provides actionable diagnostics when algorithm_type is wrong
- Ready for Phase 02-02 (label file discovery) and Phase 03 (frontend integration showing detected type to user)

---
*Phase: 02-onnx-fix*
*Completed: 2026-08-07*

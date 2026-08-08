# Phase 2: ONNX 模型检测修复 — Plan Outline

**Phase:** 02-onnx-fix
**Plans:** 2
**Waves:** 2

## Wave Structure

| Wave | Plan | Autonomous | Description |
|------|------|------------|-------------|
| 1 | 02-01 | yes | Probe auto-detection + input auto-resize + error logging |
| 2 | 02-02 | yes | Path resolution warning + label file discovery |

## Plan Details

### Plan 02-01: Core Detection Fix (Wave 1)
**Requirements:** D-01, D-02, D-03, D-04, D-05, D-07, D-10, D-11, D-12
**Files:** SmallModelView.py, onnx_engine.py, yolo_postprocess.py
**Tasks:**
1. Add algorithm_type auto-detection in smallmodel_openProbe() — output shape heuristic, return algorithm_type_detected + input_size_inferred fields
2. Add input auto-resize in OnnxEngine — store model input shape during load(), use it in _preprocess()
3. Add enhanced error logging — load() failure details, detect() shape mismatch, _decode_detect() fallback logging

### Plan 02-02: Path & Label Improvements (Wave 2, depends on 02-01)
**Requirements:** D-06, D-08, D-09
**Files:** worker_pool.py, base.py
**Tasks:**
1. Add warning log in resolve_model_path() when model file not found
2. Extend BaseEngine._resolve_labels() with labels.txt, {stem}.txt, static/labels/ search paths

## Coverage Audit

| Requirement | Plan | Task |
|-------------|------|------|
| D-01 | 02-01 | T01 |
| D-02 | 02-01 | T01 |
| D-03 | 02-01 | T01 |
| D-04 | 02-01 | T01 |
| D-05 | 02-01 | T02 |
| D-06 | 02-02 | T01 |
| D-07 | 02-01 | T02, T03 |
| D-08 | 02-02 | T02 |
| D-09 | 02-02 | T02 |
| D-10 | 02-01 | T01 |
| D-11 | 02-01 | T01 |
| D-12 | 02-01 | T01 |

All 12 requirements covered. No deferred items.

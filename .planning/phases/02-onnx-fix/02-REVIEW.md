---
phase: 02-onnx-fix
reviewed: 2026-08-07T12:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - app/views/SmallModelView.py
  - app/analysis/engines/onnx_engine.py
  - app/analysis/engines/yolo_postprocess.py
  - app/analysis/worker_pool.py
  - app/analysis/engines/base.py
findings:
  critical: 2
  warning: 3
  info: 2
  total: 7
status: issues_found
---

# Phase 2: Code Review Report (ONNX Model Detection Fix)

**Reviewed:** 2026-08-07T12:00:00Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Reviewed 5 files changed in Phase 2 (ONNX Model Detection Fix). The changes add YOLO version auto-detection from output tensor shapes, auto-resize preprocessing based on model input shape, enhanced label resolution with multiple fallback paths, and improved diagnostic logging. Two critical security/correctness issues were found: a path traversal vulnerability in `resolve_model_path` and a missing `algorithm_type` in the engine cache key. Three warning-level issues involve logic edge cases in YOLO postprocessing transpose heuristics, negative `nc` computation in segment decode, and a non-deterministic label search. Two info items cover minor code quality issues.

## Critical Issues

### CR-01: Path Traversal in resolve_model_path — Arbitrary File Access

**File:** `app/analysis/worker_pool.py:125-126`
**Issue:** `resolve_model_path()` returns any user-supplied absolute path verbatim without validating it resides within the weight directory. The function is called from `smallmodel_openProbe()` (line 645) where `model_file` originates from user POST parameters. An attacker can supply `model_file=/etc/passwd` or `C:\Windows\System32\config\SAM` and the function returns the path directly, which is then passed to `EngineFactory.create()` and loaded by ONNX Runtime. This enables reading arbitrary files from the filesystem and potentially loading malicious model files.

**Call chain:** `smallmodel_openProbe(request)` → `params.get("model_file")` → `resolve_model_path(model_file)` → returns any absolute path → `EngineFactory.create(model_file=abs_path)` → `OnnxEngine.load()` reads file.

**Fix:**
```python
def resolve_model_path(model_file):
    if not model_file:
        return ""
    mf = str(model_file).strip()
    # SECURITY: Only resolve relative paths within weight_dir; reject absolute paths
    if os.path.isabs(mf):
        logger.warning("resolve_model_path: 拒绝绝对路径: %s", model_file)
        return ""
    weight_dir = get_weight_dir()
    if not weight_dir:
        logger.warning("resolve_model_path: weight目录未配置, 无法解析: %s", model_file)
        return ""
    for name in (mf, os.path.basename(mf)):
        cand = os.path.join(weight_dir, name)
        if os.path.isfile(cand):
            return cand
    logger.warning("resolve_model_path: 模型文件不存在: %s (weight_dir=%s)", model_file, weight_dir)
    return ""
```

### CR-02: Cache Key Missing algorithm_type — Stale Engine Reuse After Algorithm Update

**File:** `app/analysis/worker_pool.py:65`
**Issue:** The cache key in `get_detector()` is `(algo_id, engine_name, model_file, conf, iou, input_size, task_type, device)` but omits `algorithm_type`. Since `algorithm_type` controls postprocessing behavior (yolo5 vs yolo8 branch selection via `_is_v5()`), updating an algorithm's `algorithm_type` without changing its `model_file` will cause the stale cached engine to be returned with the wrong postprocessing logic. For example: algorithm A is loaded as yolo5, then updated to yolo8 in the database — subsequent inference still uses the yolo5 decode path, producing incorrect detection results.

**Fix:**
```python
key = (algo_id, engine_name, model_file, conf, iou, input_size, task_type, device, algo_type)
```
(Add `algo_type` to the tuple at line 65.)

## Warnings

### WR-01: Redundant No-Op Assignment in smallmodel_openProbe

**File:** `app/views/SmallModelView.py:665`
**Issue:** Line 665 reads `data.get("input_size_inferred")` and assigns it back to `data["input_size_inferred"]` — a no-op. The value is already set by `eng.probe()` at onnx_engine.py line 171. This is dead code that obscures the intent (possibly a copy-paste error from a planned fallback that was never implemented).

**Fix:** Remove line 665 entirely:
```python
# Line 665: DELETE this line
# data["input_size_inferred"] = data.get("input_size_inferred")
```

### WR-02: Transpose Heuristic in _decode_detect Fails When nc+4 >= N

**File:** `app/analysis/engines/yolo_postprocess.py:169`
**Issue:** The yolo8+ branch uses `arr.shape[0] < arr.shape[1]` as a heuristic to decide whether to transpose from `[nc+4, N]` to `[N, nc+4]`. For typical models (nc=80, N=8400) this works. However, when `nc+4 >= N` (e.g., nc=200 with N=100 predictions), the condition is false and the array is NOT transposed. The subsequent `nc = arr.shape[1] - 4` then computes `nc = N - 4` instead of the correct `nc`, producing wrong class scores and potentially incorrect detections. The yolo8 output format is ALWAYS `[nc+4, N]` after batch removal, so the transpose should be unconditional.

**Fix:**
```python
# yolo8/11/26: [1, nc+4, N]  需转置
if arr.ndim == 3 and arr.shape[0] == 1:
    arr = arr[0]
if arr.ndim != 2:
    return []
# yolo8+ output is always [nc+4, N] — always transpose to [N, nc+4]
if arr.shape[0] >= 4:
    arr = arr.T
if arr.ndim != 2 or arr.shape[1] < 5:
    return []
```

### WR-03: _decode_segment Computes Negative nc When nc Is None

**File:** `app/analysis/engines/yolo_postprocess.py:218-227`
**Issue:** In the yolo5 segment branch, when `nc` is None and `arr.shape[1]` is small (e.g., 20), the computation `nc = arr.shape[1] - 5 - 32 = -17` produces a negative value. The subsequent slice `cls_scores = arr[:, 5:5+(-17)]` produces `arr[:, 5:-12]` — a valid but wrong slice that skips the last 12 columns. The guard `if nm < 1: nm = 32` only checks `nm`, not `nc`. The yolo8+ branch (lines 250-258) has a similar issue.

**Fix:**
```python
if nc is None:
    nm = 32
    nc = arr.shape[1] - 5 - nm
    if nc < 1:
        # Not enough columns for segment; fall back to detect-only
        nc = arr.shape[1] - 5
        nm = 0
else:
    nm = arr.shape[1] - 5 - nc
if nm < 1:
    nm = 0
```

## Info

### IN-01: Redundant import json Shadows Top-Level Import

**File:** `app/analysis/worker_pool.py:189`
**Issue:** `import json` inside `_get_upload_weight_dir()` shadows the top-level `import json` at line 6. The function-level import is unnecessary since json is already imported at module scope.

**Fix:** Remove `import json` at line 189; the top-level import is sufficient.

### IN-02: Wildcard Import from ViewsBase

**File:** `app/views/SmallModelView.py:20`
**Issue:** `from app.views.ViewsBase import *` is a wildcard import. While this is an existing pattern in the codebase (not introduced by Phase 2), it makes the namespace unclear and risks name collisions. For new code, explicit imports are preferred.

**Fix:** Replace with explicit imports of needed symbols (e.g., `from app.views.ViewsBase import f_checkRequestSafe, f_parseGetParams, f_parsePostParams, f_responseJson, f_parseRequestLang, LANG_VIEWS_T`).

---

_Reviewed: 2026-08-07T12:00:00Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_

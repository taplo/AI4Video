# Phase 2: ONNX 模型检测修复 - Research

**Researched:** 2026-08-07
**Domain:** ONNX Runtime inference engine, YOLO postprocessing, model file management
**Confidence:** HIGH

## Summary

This phase fixes the ONNX model upload → detection pipeline. The root cause is a chain of four failures:

1. **algorithm_type mismatch**: The frontend defaults to `"yolo8"`, but users may upload YOLOv5/11/26 models. The `_decode_detect()` function in `yolo_postprocess.py` uses `_is_v5()` to branch — if the wrong branch is chosen, the entire output tensor is misinterpreted, producing garbage or empty results.

2. **Input size mismatch**: The user-configured `input_width`/`input_height` (default 640×640) may not match the model's actual input shape. `_preprocess()` blindly resizes to `(iw, ih)`, causing shape mismatch errors in ONNX inference.

3. **Path resolution failure**: `resolve_model_path()` returns `""` silently when a file doesn't exist, then the engine's `load()` logs a generic warning but the error is swallowed — the probe returns empty `input_shape`/`output_shape` with no explanation.

4. **Label file discovery gap**: `BaseEngine._resolve_labels()` only checks `model.labels`, `model.names`, `model.yaml` — not `labels.txt` or `{model_name}.txt` in the same directory.

**Primary recommendation:** Add an `algorithm_type` auto-detection step in `smallmodel_openProbe()` that opens the ONNX model, inspects the output tensor shape, and returns the detected version. Add auto-resize in `OnnxEngine._preprocess()` to silently adapt to model input shape. Expand `_resolve_labels()` search order per D-08.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| algorithm_type auto-detection | API / Backend (View layer) | — | `smallmodel_openProbe()` is the integration point; detection logic calls OnnxEngine.probe() |
| Input size auto-resize | API / Backend (Engine layer) | — | `OnnxEngine._preprocess()` owns input preparation |
| Path resolution | API / Backend (Worker pool) | — | `resolve_model_path()` is the single entry point |
| Label file discovery | API / Backend (Base engine) | — | `BaseEngine._resolve_labels()` is the shared method |
| Error logging | API / Backend (All layers) | — | Cross-cutting concern at each failure point |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| onnxruntime | 1.19.2 | ONNX model inference | Official Microsoft runtime, GPU support |
| numpy | 1.26.4 | Tensor manipulation | Required by ONNX and YOLO postprocessing |
| opencv-python | 4.10.0.84 | Image preprocessing, NMS | Standard computer vision library |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pyyaml | (implicit) | YAML label file parsing | When `.yaml` label files are present |

**Note:** All core libraries are already in `requirements-windows.txt`. No new packages need to be installed.

## Package Legitimacy Audit

> All packages in this phase are pre-existing dependencies. No new packages to audit.

| Package | Registry | Status | Disposition |
|---------|----------|--------|-------------|
| onnxruntime | PyPI | Pre-existing | Approved |
| numpy | PyPI | Pre-existing | Approved |
| opencv-python | PyPI | Pre-existing | Approved |

## Code Analysis

### File-by-File Breakdown

#### 1. `app/views/SmallModelView.py` — Probe Interface (D-04, D-10, D-11, D-12)

**Current behavior** (lines 609-652):
- `smallmodel_openProbe()` receives `engine`, `model_file`, `task_type`, `algorithm_type` from POST params
- Calls `resolve_model_path()` → creates engine via `EngineFactory.create()` → calls `eng.probe()`
- Returns probe result directly — no auto-detection of algorithm_type
- Default `algorithm_type` is `"yolo8"` (line 632)

**What needs to change:**
- After probe, if `task_type == "detect"`, inspect `output_shape` to auto-detect YOLO version
- Add `algorithm_type_detected` field (D-10) and `input_size_inferred` field (D-11) to response
- Keep existing fields unchanged (D-12)

**Detection logic** (per D-02):
```python
# Output shape heuristic:
# YOLOv5 detect: [1, N, 5+nc] — rows > columns (N >> 5+nc for typical images)
# YOLOv8/11/26 detect: [1, nc+4, N] — columns > rows (nc+4 is small, N is large)
# YOLOv5 segment: [1, N, 5+nc+nm] + proto [1, nm, mh, mw]
# YOLOv8/11/26 segment: [1, nc+4+nm, N] + proto [1, nm, mh, mw]
```

#### 2. `app/analysis/engines/onnx_engine.py` — ONNX Engine (D-05, D-07)

**Current behavior** (lines 70-93, 95-101, 103-124):
- `load()`: Opens ONNX session, logs input/output names. Error is logged but `_loaded` stays False.
- `_preprocess()`: Resizes to `self.input_size` (iw, ih) — no check if model expects different size.
- `detect()`: Calls `_preprocess()` → `_session.run()` → `decode_outputs()`. If shape mismatch, exception is caught and empty list returned.

**What needs to change:**
- In `_preprocess()` (D-05): Read model's actual input shape from session, resize accordingly, then pad/crop to expected input_size if needed. Or more simply: always resize to model's actual input shape.
- In `load()` (D-07): Log model file path, provider list, input/output shapes on failure.
- Store `self._model_input_shape` during `load()` for use in `_preprocess()`.

**Key insight for D-05:** The cleanest approach is to store the model's actual input shape during `load()`, then in `_preprocess()`, resize to that shape instead of the user-configured `input_size`. This makes the user-configured `input_size` a fallback/display value, while the model's own shape is authoritative.

#### 3. `app/analysis/engines/yolo_postprocess.py` — YOLO Postprocessing (D-02, D-07)

**Current behavior** (lines 60-61, 135-193):
- `_is_v5()` checks `algorithm_type in ("yolo5", "yolov5", "v5")` — binary v5 vs non-v5
- `_decode_detect()` branches on `_is_v5()`:
  - v5: Expects `[1, N, 5+nc]`, extracts obj×cls scores
  - v8+: Expects `[1, nc+4, N]`, transposes if needed, uses cls scores only

**What needs to change:**
- Add auto-detect fallback (D-07): If the expected decode path returns empty results, try the other path
- Add logging when output shape doesn't match expected pattern for the given algorithm_type
- The heuristic in D-02 (columns < rows → v5, columns > rows → v8+) can be applied here as a fallback

**Important:** The existing `_decode_detect()` already handles both v5 and v8+ paths correctly when given the right `algorithm_type`. The fix is about getting the right `algorithm_type` to this function, not changing its logic.

#### 4. `app/analysis/worker_pool.py` — Path Resolution (D-06)

**Current behavior** (lines 121-134):
- `resolve_model_path()` checks absolute path → weight dir → basename fallback
- Returns `""` if not found — no warning log

**What needs to change** (D-06):
- Add `logger.warning("resolve_model_path: 模型文件不存在: %s", model_file)` when returning empty string
- This is the single change point — all callers go through this function

#### 5. `app/analysis/engines/base.py` — Label Resolution (D-08, D-09)

**Current behavior** (lines 80-108):
- Searches: `model.labels` → `model.names` → `model.yaml`
- Returns `[]` if nothing found

**What needs to change** (D-08):
- New search order:
  1. `model.labels` (existing)
  2. `model.names` (existing)
  3. `model.yaml` (existing)
  4. `{model_dir}/labels.txt` (NEW)
  5. `{model_dir}/{model_name}.txt` (NEW, where model_name is the file stem)
  6. `static/labels/` directory (NEW)
  7. Empty list (D-09: never fail)

## Integration Points

### Data Flow for Probe

```
Frontend POST → smallmodel_openProbe()
  → resolve_model_path(model_file)           [worker_pool.py]
  → EngineFactory.create(engine_name, ...)   [factory.py]
    → OnnxEngine.probe()                     [onnx_engine.py:135-157]
      → ort.InferenceSession(model_file)
      → Get input_shape, output_shape
      → _resolve_labels(model_file)          [base.py:80-108]
  → (NEW) Auto-detect algorithm_type from output_shape
  → Return { ..., algorithm_type_detected, input_size_inferred }
```

### Data Flow for Detection

```
CameraPipeline → DetectorWorkerPool.get_detector(algorithm)
  → resolve_model_path(model_file)           [worker_pool.py]
  → OnnxEngine.__init__(algorithm_type=...)  [from AlgorithmModel]
  → OnnxEngine.load()
    → _resolve_labels(model_file)            [base.py]
  → OnnxEngine.detect(frame)
    → _preprocess(frame)                     [onnx_engine.py:95-101]
    → _session.run(inputs)                   [onnx_engine.py:109]
    → decode_outputs(...)                    [yolo_postprocess.py:32-57]
      → _decode_detect(outputs, algorithm_type, ...)
```

### Key Integration: algorithm_type Flow

1. **At probe time:** Frontend sends `algorithm_type` (default "yolo8") → probe auto-detects → returns `algorithm_type_detected` → user confirms/adjusts
2. **At add/edit time:** `smallmodel_openAdd/Edit` saves `algorithm_type` to `AlgorithmModel`
3. **At detection time:** `DetectorWorkerPool.get_detector()` reads `algorithm.algorithm_type` → passes to `OnnxEngine(algorithm_type=...)` → flows to `decode_outputs()`

The fix must ensure the **correct** `algorithm_type` is saved at step 2, so step 3 works. The auto-detection at step 1 is the key enabler.

## Risk Assessment

### What Could Break

| Risk | Impact | Mitigation |
|------|--------|------------|
| Auto-detect heuristic wrong for edge-case models | Wrong decode path, empty results | Log warning; keep user override ability (D-03) |
| Input resize changes detection quality | Slight accuracy change if model expects different preprocessing | Use model's native input shape, not user config |
| Label file search order finds wrong file | Wrong labels displayed | Search order is deterministic; `labels.txt` in model dir is most specific |
| ONNX session creation during probe is slow | UI delay during probe | Probe creates temporary session, discards after — acceptable for probe |

### Backward Compatibility

- D-12 requires keeping existing fields unchanged — only adding new fields
- Existing `algorithm_type` values in database are unaffected
- `_is_v5()` logic is unchanged — only the input to it changes (auto-detected value vs default)

## Validation Architecture

### Test Framework

No test infrastructure exists (`app/tests.py` is empty, no pytest.ini, no conftest.py). Phase 5 addresses this. For this phase:

**Manual verification only** — the fix is small enough to verify through:
1. Upload a YOLOv8 ONNX model → probe → verify `algorithm_type_detected: "yolo8"`, `input_size_inferred` matches model
2. Upload a YOLOv5 ONNX model → probe → verify `algorithm_type_detected: "yolo5"`
3. Upload a model with 320×320 input → set algorithm input_width=640 → detect → verify auto-resize works
4. Upload model with labels.txt in same directory → verify labels found
5. Upload model with no label files → verify empty labels, no crash

### Acceptance Criteria (from CONTEXT.md)

| ID | Requirement | Verification |
|----|-------------|--------------|
| D-01 | Auto-detect algorithm_type on upload | Probe returns `algorithm_type_detected` matching model version |
| D-02 | Output shape heuristic: columns < rows → v5, columns > rows → v8+ | Unit test with mock tensors |
| D-03 | Result shown to user, user can override | Frontend shows detected type, editable dropdown |
| D-04 | Implementation in `smallmodel_openProbe()` | Code location verified |
| D-05 | Auto-resize input to model shape | Detect with mismatched input_size succeeds |
| D-06 | Warning log on path not found | Log output verified |
| D-07 | Detailed error logging | Error logs show model path, providers, shapes |
| D-08 | Label search order: labels.txt → {name}.txt → static/labels/ | Test each path |
| D-09 | Empty labels on failure, no crash | No label file → empty list |
| D-10 | `algorithm_type_detected` field in probe response | JSON response verified |
| D-11 | `input_size_inferred` field in probe response | JSON response verified |
| D-12 | Existing fields unchanged | Regression check on existing response format |

## Implementation Recommendations

### Approach 1: Minimal Invasive (Recommended)

**Phase 2a — Probe auto-detection (D-01, D-02, D-03, D-10, D-11, D-12):**
- In `smallmodel_openProbe()`, after `eng.probe()` returns, inspect `info["output_shape"]`
- Apply heuristic: if output_shape[0] has 3 dims and shape[1] > shape[2], it's v5 format
- Set `info["algorithm_type_detected"]` and `info["input_size_inferred"]`
- User sees detected type and can override

**Phase 2b — Input auto-resize (D-05):**
- In `OnnxEngine.load()`, store `self._model_input_shape = session.get_inputs()[0].shape`
- In `OnnxEngine._preprocess()`, resize to `(self._model_input_shape[-1], self._model_input_shape[-2])` instead of `self.input_size`
- This makes the model's own shape authoritative

**Phase 2c — Error handling (D-06, D-07):**
- Add warning log in `resolve_model_path()` when returning empty
- Enhance `OnnxEngine.load()` error logging with model path, providers, input/output shapes
- Add shape mismatch logging in `_decode_detect()`

**Phase 2d — Label discovery (D-08, D-09):**
- Extend `BaseEngine._resolve_labels()` with new search paths
- Add `labels.txt` → `{stem}.txt` → `static/labels/` fallback

### Approach 2: Defensive Runtime Detection (Alternative)

Add auto-detection at detection time (not just probe time) — if `_decode_detect()` returns empty results, retry with the other v5/non-v5 branch. This is more defensive but adds latency to every detection frame.

**Recommendation:** Approach 1 is better because:
- Detection happens at 5 FPS — adding retry latency is unacceptable
- Probe happens once per model upload — one-time cost is acceptable
- Correct algorithm_type at probe → correct save → correct detection

### File Change Summary

| File | Changes | LOC Est. |
|------|---------|----------|
| `app/views/SmallModelView.py` | Add auto-detect logic in `smallmodel_openProbe()` | ~30 |
| `app/analysis/engines/onnx_engine.py` | Store model input shape, auto-resize, enhanced logging | ~25 |
| `app/analysis/worker_pool.py` | Add warning log in `resolve_model_path()` | ~3 |
| `app/analysis/engines/base.py` | Extend `_resolve_labels()` search order | ~20 |
| `app/analysis/engines/yolo_postprocess.py` | Add shape mismatch logging | ~10 |

**Total estimated:** ~88 lines of changes across 5 files.

## Common Pitfalls

### Pitfall 1: Dynamic ONNX Input Shapes
**What goes wrong:** YOLOv8n models can have dynamic input dims like `[1, 3, -1, -1]` or `[1, 3, 'dynamic', 'dynamic']`
**Why it happens:** Export with dynamic axes enabled
**How to avoid:** Handle `dynamic` or `-1` dimensions — use user-configured size as fallback when shape is dynamic
**Warning signs:** `input_shape` contains string values or -1 in ONNX probe output

### Pitfall 2: Segment Models Have Multiple Outputs
**What goes wrong:** Auto-detect heuristic on segment models sees 2 outputs, may confuse detection
**Why it happens:** Segment models output `[detections, protos]`
**How to avoid:** Only inspect `outputs[0]` for auto-detect heuristic; ignore proto shape

### Pitfall 3: Classify Models Have No Spatial Output
**What goes wrong:** Classify models output `[1, nc]` — no columns/rows to compare
**Why it happens:** Different task type
**How to avoid:** Only apply v5/v8 heuristic for `task_type == "detect"` and `task_type == "segment"`

## Code Examples

### Auto-detect Algorithm Type from Output Shape
```python
# In smallmodel_openProbe() — after eng.probe()
def _detect_yolo_version(output_shape, task_type):
    """Detect YOLO version from output tensor shape.
    
    Returns: 'yolo5' or 'yolo8' (default if uncertain)
    
    Logic:
    - YOLOv5 detect: [1, N, 5+nc]  → shape[1] > shape[2] (N >> 5+nc)
    - YOLOv8/11/26 detect: [1, nc+4, N]  → shape[1] < shape[2] (nc+4 << N)
    - YOLOv5 segment: [1, N, 5+nc+nm] + proto
    - YOLOv8/11/26 segment: [1, nc+4+nm, N] + proto
    """
    if not output_shape or task_type not in ("detect", "segment"):
        return None  # Can't determine
    
    primary = output_shape[0]  # First output tensor
    if len(primary) != 3:
        return None  # Unexpected rank
    
    # primary[0] is batch (1), compare primary[1] vs primary[2]
    dim1, dim2 = primary[1], primary[2]
    
    # Handle dynamic dims (strings or -1)
    if isinstance(dim1, str) or isinstance(dim2, str) or dim1 == -1 or dim2 == -1:
        return None  # Can't determine from dynamic shape
    
    if dim1 > dim2:
        return "yolo5"  # [1, N, 5+nc] format
    elif dim1 < dim2:
        return "yolo8"  # [1, nc+4, N] format
    else:
        return None  # Ambiguous
```

### Auto-resize in Preprocess
```python
# In OnnxEngine._preprocess()
def _preprocess(self, frame_bgr):
    # Use model's actual input shape if available
    if hasattr(self, '_model_input_shape') and self._model_input_shape:
        shape = self._model_input_shape
        if len(shape) >= 4 and not isinstance(shape[-1], str) and shape[-1] > 0:
            iw, ih = int(shape[-1]), int(shape[-2])
        else:
            iw, ih = self.input_size
    else:
        iw, ih = self.input_size
    
    resized = cv2.resize(frame_bgr, (iw, ih))
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    blob = rgb.astype(np.float32) / 255.0
    blob = np.transpose(blob, (2, 0, 1))[None, ...]
    return blob
```

### Extended Label Resolution
```python
# In BaseEngine._resolve_labels() — add after existing .yaml check
# Search: {model_dir}/labels.txt
model_dir = os.path.dirname(model_file)
labels_txt = os.path.join(model_dir, "labels.txt")
if os.path.isfile(labels_txt):
    try:
        with open(labels_txt, "r", encoding="utf-8") as f:
            return [ln.strip() for ln in f if ln.strip()]
    except Exception as e:
        logger.warning("%s: 读取 %s 失败: %s", self.ENGINE_NAME, labels_txt, e)

# Search: {model_dir}/{model_stem}.txt
stem = os.path.splitext(os.path.basename(model_file))[0]
stem_txt = os.path.join(model_dir, stem + ".txt")
if os.path.isfile(stem_txt):
    try:
        with open(stem_txt, "r", encoding="utf-8") as f:
            return [ln.strip() for ln in f if ln.strip()]
    except Exception as e:
        logger.warning("%s: 读取 %s 失败: %s", self.ENGINE_NAME, stem_txt, e)

# Search: static/labels/ directory
try:
    from django.conf import settings
    static_labels_dir = os.path.join(str(settings.BASE_DIR), "static", "labels")
    if os.path.isdir(static_labels_dir):
        for fn in os.listdir(static_labels_dir):
            fp = os.path.join(static_labels_dir, fn)
            if os.path.isfile(fp) and fn.endswith((".txt", ".names", ".labels")):
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        lines = [ln.strip() for ln in f if ln.strip()]
                    if lines:
                        return lines
                except Exception:
                    pass
except Exception:
    pass

return []  # D-09: never fail
```

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | ONNX models store static input shapes as integers (not strings) | Auto-detect | Low — dynamic shapes handled with fallback |
| A2 | YOLOv5 output shape always has dim1 > dim2 for detect task | Auto-detect | Medium — edge cases possible with very few classes |
| A3 | The probe endpoint is called once per model upload, not per detection frame | Architecture | Low — confirmed by code flow |
| A4 | `static/labels/` directory exists or can be created | Label discovery | Low — graceful fallback if not |
| A5 | Existing algorithm_type values in database are not changed by this fix | Backward compat | Low — code only reads, never writes algorithm_type in detect path |

## Open Questions (RESOLVED)

1. **[RESOLVED] Frontend auto-fill of algorithm_type**
   - What we know: Backend will return `algorithm_type_detected` in probe response
   - Resolution: Backend returns the value; frontend shows it as pre-filled suggestion in the algorithm_type dropdown. User must click "confirm" to save. This aligns with D-03 (推断结果回显给用户确认，用户可手动修改 algorithm_type).

2. **[RESOLVED] YOLOv11 vs YOLOv26 distinction**
   - What we know: Both v11 and v26 use the same `[1, nc+4, N]` output format as v8
   - Resolution: Report "yolo8" for all v8/v11/v26 since the postprocessing is identical. The `algorithm_type` field in the model can be manually set to v11/v26 if the user wants to track it. The probe endpoint returns `algorithm_type_detected: "yolo8"` for all v8+ variants.

## Sources

### Primary (HIGH confidence)
- Source code analysis of all 6 canonical files — direct reading
- Architecture documented in `.planning/codebase/ARCHITECTURE.md`
- Phase decisions locked in `02-CONTEXT.md`

### Secondary (MEDIUM confidence)
- YOLOv5/v8 output format differences confirmed by `yolo_postprocess.py` comments (lines 7-13)
- ONNX Runtime API usage patterns confirmed by existing `onnx_engine.py` and `reid_onnx_engine.py`

### Tertiary (LOW confidence)
- None — all findings based on direct source code analysis

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries already in requirements.txt, versions confirmed
- Architecture: HIGH — all integration points traced through source code
- Pitfalls: MEDIUM — dynamic shape edge cases need runtime testing
- Validation: LOW — no test suite exists; manual verification only

**Research date:** 2026-08-07
**Valid until:** 2026-09-07 (30 days — stable codebase)

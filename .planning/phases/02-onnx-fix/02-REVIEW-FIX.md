---
phase: 02-onnx-fix
fixed_at: 2026-08-07T13:00:00Z
review_path: .planning/phases/02-onnx-fix/02-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 2: Code Review Fix Report (ONNX Model Detection Fix)

**Fixed at:** 2026-08-07T13:00:00Z
**Source review:** .planning/phases/02-onnx-fix/02-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 5 (2 Critical, 3 Warning)
- Fixed: 5
- Skipped: 0

## Fixed Issues

### CR-01: Path Traversal in resolve_model_path — Arbitrary File Access

**Files modified:** `app/analysis/worker_pool.py`
**Applied fix:** Replaced absolute path acceptance with unconditional rejection. The function now rejects all absolute paths via `os.path.isabs(mf)` and logs a warning, preventing arbitrary file access through user-supplied model_file parameters.

**Change details:**
- Lines 121-138: Removed the condition `if os.path.isabs(mf) and os.path.isfile(mf): return mf` which previously returned absolute paths directly
- Added unconditional `if os.path.isabs(mf):` check that logs a warning and returns empty string
- This prevents path traversal attacks where an attacker could supply `/etc/passwd` or `C:\Windows\System32\config\SAM` as model_file

### CR-02: Cache Key Missing algorithm_type — Stale Engine Reuse After Algorithm Update

**Files modified:** `app/analysis/worker_pool.py`
**Applied fix:** Added `algo_type` to the cache key tuple in `get_detector()`.

**Change details:**
- Line 65: Changed key from `(algo_id, engine_name, model_file, conf, iou, input_size, task_type, device)` to `(algo_id, engine_name, model_file, conf, iou, input_size, task_type, device, algo_type)`
- This ensures that when an algorithm's `algorithm_type` is updated in the database (e.g., from yolo5 to yolo8), the engine cache will not return a stale instance with the wrong postprocessing logic

### WR-01: Redundant No-Op Assignment in smallmodel_openProbe

**Files modified:** `app/views/SmallModelView.py`
**Applied fix:** Removed line 665: `data["input_size_inferred"] = data.get("input_size_inferred")`

**Change details:**
- Removed the no-op assignment that read `data.get("input_size_inferred")` and wrote it back to the same key
- The value was already set by `eng.probe()` at onnx_engine.py line 171
- This dead code obscured intent and appeared to be a copy-paste artifact

### WR-02: Transpose Heuristic in _decode_detect Fails When nc+4 >= N

**Files modified:** `app/analysis/engines/yolo_postprocess.py`
**Applied fix:** Made transpose unconditional for yolo8+ output format.

**Change details:**
- Lines 168-170: Changed condition from `if arr.shape[0] < arr.shape[1] and arr.shape[0] >= 4:` to `if arr.shape[0] >= 4:`
- Updated comment from "行格式可能是 [4+nc, N] —— 转成 [N, 4+nc]" to "yolo8+ output is always [nc+4, N] — always transpose to [N, nc+4]"
- The yolo8+ output format is ALWAYS `[nc+4, N]` after batch removal, so the heuristic check `shape[0] < shape[1]` was incorrect when nc+4 >= N (e.g., nc=200 with N=100 predictions)

### WR-03: _decode_segment Computes Negative nc When nc Is None

**Files modified:** `app/analysis/engines/yolo_postprocess.py`
**Applied fix:** Added guard for negative nc in both yolo5 and yolo8+ segment decode branches.

**Change details (yolo5 branch, lines 220-230):**
- Added `if nc < 1:` check after computing `nc = arr.shape[1] - 5 - nm`
- When nc is negative (insufficient columns for segment), falls back to detect-only mode: `nc = arr.shape[1] - 5` and `nm = 0`
- Changed `nm < 1` handler from `nm = 32` to `nm = 0` to avoid cascading negative nc

**Change details (yolo8+ branch, lines 253-264):**
- Added same `if nc < 1:` guard for the yolo8+ branch
- When nc is negative, falls back to detect-only: `nc = arr.shape[1] - 4` and `nm = 0`
- Changed `nm < 1` handler from `nm = 32` (plus recalculation) to `nm = 0`

## Skipped Issues

None — all in-scope findings were successfully fixed.

---

_Fixed: 2026-08-07T13:00:00Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_

# Coding Conventions

**Analysis Date:** 2026-08-05

## Naming Patterns

**Files:**
- Views: PascalCase suffixed with `View` (e.g., `StreamView.py`, `AlgorithmView.py`)
- Models: PascalCase suffixed with `Model` (e.g., `StreamModel` in `app/models.py`)
- Services: snake_case suffixed with `_service` (e.g., `alarm_service.py`, `algorithm_test_service.py`)
- Utilities: PascalCase suffixed with `Utils` or `utils` (e.g., `LogUtils.py`, `UploadUtils.py`)
- Analysis engines: snake_case suffixed with `_engine` (e.g., `yolo_pytorch_engine.py`, `onnx_engine.py`)
- Private modules: prefixed with `_` (e.g., `_run_test`, `_build_engine`)

**Functions:**
- Module-level helpers in ViewsBase: `f_` prefix (e.g., `f_parseGetParams`, `f_checkRequestSafe`, `f_responseJson`)
- View API methods: `api_open` prefix (e.g., `api_openAdd`, `api_openIndex`)
- Private module functions: `_` prefix (e.g., `_algo_to_dict`, `_resolve_model_abs`)
- Service functions: plain snake_case (e.g., `write_alarm`, `start_test`)
- Model methods: snake_case (e.g., `buildPageLabels`, `group_by_field`)

**Variables:**
- Global singletons: `g_` prefix (e.g., `g_config`, `g_logger`, `g_database`, `g_zlm`)
- Module-level constants: UPPER_SNAKE_CASE (e.g., `AUTH_WHITELIST_PREFIXES`, `LOG_FORMAT`)
- Local variables in views: sometimes `__` prefix (e.g., `__ret`, `__msg`, `__check_ret`)
- Private instance vars: `_` prefix (e.g., `self._loaded`, `self._instance`)

**Types/Classes:**
- Models: PascalCase + `Model` suffix (e.g., `StreamModel`, `AlgorithmModel`, `AlarmModel`)
- Engines: PascalCase + `Engine` suffix (e.g., `BaseEngine`, `OnnxEngine`, `OpenVinoEngine`)
- Utilities: PascalCase + `Utils` suffix (e.g., `LogUtils`, `UploadUtils`)
- Exceptions: PascalCase + `Error` suffix (e.g., `EngineNotAvailableError`)

## Code Style

**Formatting:**
- No formatter configured (no `.prettierrc`, `biome.json`, `pyproject.toml`)
- Indentation: 4 spaces (consistent across all files)
- Line length: No enforced limit; lines up to ~120 chars observed
- Trailing whitespace: Not consistently trimmed
- Blank lines: Single blank lines between functions; occasional double blanks

**Linting:**
- No linter configured (no `.flake8`, `.pylintrc`, `mypy.ini`)
- No type annotations used anywhere
- No pre-commit hooks

## Import Organization

**Order:**
1. Standard library (`os`, `sys`, `time`, `json`, `threading`, `logging`)
2. Third-party packages (`cv2`, `numpy`, `requests`, `xlrd`)
3. Django framework (`django.db.models`, `django.http`, `django.shortcuts`)
4. Local app imports (`app.models`, `app.views.ViewsBase`, `app.utils.*`)

**Path Aliases:**
- None configured; all imports use absolute paths from project root

**Wildcard Imports:**
- Views use `from app.views.ViewsBase import *` and `from app.models import *` — this is the established pattern, even though it's generally discouraged. ViewsBase exports: `f_parseGetParams`, `f_parsePostParams`, `f_checkRequestSafe`, `f_responseJson`, `g_config`, `g_logger`, `g_database`, `g_zlm`, `LANG_VIEWS_T`, and more.

## Error Handling

**Patterns:**
- Broad `except Exception` with logging (most common):
  ```python
  try:
      # operation
  except Exception as e:
      g_logger.error("function_name() error: %s" % str(e))
  ```
- Return tuple pattern for view APIs: `(ret: bool, msg: str, data?: dict)`
- View response pattern: `{"code": 1000 if ret else 0, "msg": msg, ...}`
- Task status pattern: `{"status": "error", "message": str(e)}`

**Key files:**
- `app/views/ViewsBase.py`: `f_checkRequestSafe`, `f_responseJson`
- `app/views/StreamView.py`: `api_openAdd` (typical view API pattern)
- `app/services/algorithm_test_service.py`: `_run_test` (task error handling)

**Never raise in views; always return error JSON.** Example from `StreamView.py`:
```python
__ret = False
__msg = LANG_VIEWS_T(request, "msg_unknown_error")
try:
    # business logic
    __ret = True
    __msg = LANG_VIEWS_T(request, "msg_success")
except Exception as e:
    __msg = LANG_VIEWS_T(request, "msg_unknown_error")
    g_logger.error("StreamView.api_openXxx() error: %s" % str(e))
return f_responseJson({"code": 1000 if __ret else 0, "msg": __msg, ...})
```

## Logging

**Framework:** Python standard `logging` module with `TimedRotatingFileHandler`

**Setup:** `app/utils/Logger.py` → `CreateLogger()` function, used by `app/utils/GlobalUtils.py`

**Log format:**
```
%(asctime)s %(name)s:%(lineno)d [%(levelname)s] %(message)s
```

**Module loggers:**
- Global: `g_logger` (from `GlobalUtils.py`)
- Per-module: `logging.getLogger("module.name")` (e.g., `analysis.pipeline`, `services.alarm`, `analysis.engines.factory`)

**Patterns:**
- `g_logger.info(...)` for request logging
- `g_logger.error(...)` for error capture
- `logger.warning(...)` for non-critical failures
- `logger.exception(...)` for full stack traces in task failures

**Log location:** `log/ai4video<timestamp>.log` (daily rotation, 3 backups)

## Comments

**When to Comment:**
- Every file starts with author/contact block (6-line Chinese comment block)
- Module-level docstrings for complex modules (e.g., `pipeline.py`, `manager.py`)
- Chinese inline comments for business logic explanations

**Docstrings:**
- Used on: module-level, complex classes (`BaseEngine`, `CameraPipeline`, `Config`)
- Format: Triple-quoted strings, usually Chinese
- Not used on: most view functions, utility helpers, private functions

**Language:** Comments are predominantly Chinese; code identifiers are English

## Function Design

**Size:**
- View functions: 30-80 lines typical, some up to 200+ lines (e.g., `api_openAdd` in `StreamView.py`)
- Service functions: 50-200 lines
- Helper functions: 5-30 lines

**Parameters:**
- View functions receive `request` as first param
- Helper functions use plain positional/keyword args
- No type hints anywhere

**Return Values:**
- Views: `HttpResponse` via `f_responseJson()`
- Services: tuples `(bool, str)` or `(bool, str, list)`
- Helpers: plain Python types

## Module Design

**Exports:**
- Views: Individual functions, imported in `app/urls.py` as `StreamView.api_openAdd`
- Models: All models in single `app/models.py`, imported via wildcard
- Utils: Classes with `@staticmethod` methods (e.g., `LogUtils`, `UploadUtils`)

**Barrel Files:**
- `app/views/__init__.py`: Empty
- `app/utils/__init__.py`: Empty
- `app/analysis/__init__.py`: Empty

**Singleton Pattern:**
- Used extensively: `AnalysisManager`, `Config`, `Database`, `GB28181SipServer`
- Global instances created in `app/utils/GlobalUtils.py`: `g_config`, `g_logger`, `g_database`, `g_zlm`

## Django-Specific Patterns

**URL Routing:** `app/urls.py` maps paths to view module functions (not class-based views)

**Model Pattern:**
- All models inherit `ThreadSafetyManager` for SQLite thread safety
- Override `save()` and `delete()` with `g_dbLock` context manager
- Custom `Meta.db_table` for all models (e.g., `av_stream`, `av_algorithm`)

**Middleware:** Custom `SimpleMiddleware` in `app/middleware.py` for session-based auth

**CSRF:** Exempted for internal callbacks via `@csrf_exempt` decorator in `app/urls.py`

**Session:** Custom session key `AI4VideoSessionID`, user stored in `request.session["user"]`

---

*Convention analysis: 2026-08-05*

---
status: complete
phase: 04-engineering-hardening
files_reviewed: 12
findings:
  critical: 6
  warning: 7
  info: 4
  total: 17
---

## Findings

### CR-01: SQL Injection via Raw SQL in Database Utility
- file: app/utils/Database.py
- line: 27, 50
- description: `Database.select()` and `Database.execute()` accept raw SQL strings with no parameterization or sanitization. Any caller passing user-controlled input enables SQL injection.
- impact: Full database compromise — attacker can read, modify, or delete all data.
- fix: Replace raw string SQL with parameterized queries using `cursor.execute(sql, params)` and pass parameters as a tuple.

### CR-02: Timing-Attack-Vulnerable Secret Comparison
- file: app/views/ViewsBase.py
- line: 116
- description: `f_checkRequestSafe` compares the `Safe` header against `g_config.safe` using `==` operator, which is vulnerable to timing side-channel attacks.
- impact: Attacker can brute-force the safe token character-by-character by measuring response times.
- fix: Use `hmac.compare_digest(safe, g_config.safe)` for constant-time comparison.

### CR-03: Timing-Attack-Vulnerable Secret Comparison in Middleware
- file: app/middleware.py
- line: 44
- description: Same timing-vulnerable `==` comparison for the `Safe` header in `SimpleMiddleware`.
- impact: Same as CR-02 — safe token brute-force via timing side-channel.
- fix: Use `hmac.compare_digest(safe, g_config.safe)`.

### CR-04: API Key Leaked in API Responses
- file: app/views/LLMView.py
- line: 71, 214
- description: `api_openIndex` and `api_openInfo` return `d.api_key` / `llm.api_key` in JSON responses. The LLM API key is a secret credential.
- impact: Anyone who can call these endpoints (even with limited access) obtains the LLM API key, enabling unauthorized use of the LLM service and potential cost abuse.
- fix: Exclude `api_key` from list/detail responses. If the frontend needs to display a masked version, return only the last 4 characters (e.g., `****-abcd`).

### CR-05: Unsafe Default Django SECRET_KEY
- file: framework/settings.py
- line: 32
- description: `SECRET_KEY` falls back to `'ai4video-dev-insecure-key-change-in-production'` if the environment variable is not set. This is a well-known insecure default.
- impact: If deployed without `.env` configuration, session cookies, CSRF tokens, and signed data are all trivially forgeable.
- fix: Raise an error or exit at startup if `DJANGO_SECRET_KEY` is not set in production (i.e., when `DEBUG=False`). Never ship a fallback key.

### CR-06: Wildcard CORS on File Download Endpoint
- file: app/views/StorageView.py
- line: 59
- description: `api_openDownload` sets `Access-Control-Allow-Origin: *` on the response, allowing any website to trigger file downloads from this endpoint.
- impact: A malicious website can exfiltrate downloaded files (logs, configs) from a user's browser session via cross-origin requests.
- fix: Remove the wildcard CORS header. If cross-origin access is needed, use a specific allowlist of trusted origins. For internal-only download endpoints, CORS headers should not be set.

### WR-01: Missing `import base64` Causes Crash in LLM Test Endpoint
- file: app/views/LLMView.py
- line: 290
- description: `api_openTest` calls `base64.b64decode()` but `base64` is never imported in the file. This will raise `NameError` at runtime when `file_content_base64` is provided.
- impact: The LLM test endpoint is broken for base64-encoded image uploads.
- fix: Add `import base64` at the top of the file.

### WR-02: Missing `time` Import in StorageView
- file: app/views/StorageView.py
- line: 70
- description: The `__delayed_delete` function calls `time.sleep(5)` but `time` is not imported in this file. This will raise `NameError` when a file is downloaded.
- impact: File download works but the delayed delete thread crashes — downloaded temp files are never cleaned up.
- fix: Add `import time` at the top of the file.

### WR-03: IP Spoofing via User-Controlled `request_ip` Parameter
- file: app/views/ViewsBase.py
- line: 62, 66
- description: `f_parseRequestIp` reads `request_ip` from GET/POST parameters and returns it as the client IP. Any user can supply an arbitrary IP address.
- impact: Audit logs and rate-limiting based on IP are trivially bypassed. Logs become unreliable for forensics.
- fix: Remove the user-controlled `request_ip` parameter lookup. Always derive the IP from `request.META['REMOTE_ADDR']` or `X-Forwarded-For` (with trusted proxy validation).

### WR-04: Deprecated `dict.has_key()` Usage
- file: app/middleware.py
- line: 33
- description: `request.session.has_key("user")` uses `dict.has_key()` which has been deprecated since Python 3.
- impact: Will emit `DeprecationWarning` and may be removed in future Python versions.
- fix: Replace with `"user" in request.session`.

### WR-05: Undefined Attributes in `_start_process`
- file: app/analysis/manager.py
- line: 417-440
- description: `_start_process` references `self._mp_ctx`, `self._status_dict`, `self._infer_req_q`, `self._infer_resp_q`, and the unimported `pipeline_process_main` — none of which are defined in `__init__`.
- impact: Calling `_start_process` would raise `AttributeError`. The process-based pipeline mode is broken and cannot be used.
- fix: Either define these attributes in `__init__` or remove `_start_process` entirely (the codebase appears to only use `_start_thread`).

### WR-06: `StorageView.api_openDownload` Uses Unimported `g_config`
- file: app/views/StorageView.py
- line: 52
- description: `g_config.storageTempDir` is referenced but `g_config` is only available via `from app.views.ViewsBase import *`. While this works at runtime due to the wildcard import, it creates a fragile implicit dependency.
- impact: If the wildcard import in ViewsBase changes, StorageView will break with `NameError`.
- fix: Add an explicit `from app.utils.GlobalUtils import g_config` import.

### WR-07: LLM Test Endpoint Exempt from CSRF
- file: app/urls.py
- line: 169
- description: `csrf_exempt(LLMView.api_openTest)` disables CSRF protection on the LLM test endpoint. This endpoint performs state-changing operations (sends requests to external LLM APIs).
- impact: A cross-site request forgery attack could cause a victim's browser to make arbitrary LLM API calls, potentially incurring costs or leaking data.
- fix: Remove `csrf_exempt` and ensure the frontend sends the CSRF token. If the endpoint is called via AJAX, set `X-CSRFToken` header from the cookie.

### INFO-01: Broad Exception Catching Suppresses Errors
- file: app/views/ViewsBase.py
- line: 27, 101
- description: Bare `except:` and `except Exception` blocks in `f_parsePostParams` and `f_sessionReadUserId` silently swallow all errors.
- impact: Bugs and unexpected errors are hidden, making debugging difficult.
- fix: Catch specific exceptions (e.g., `json.JSONDecodeError`, `AttributeError`) and log unexpected ones.

### INFO-02: Excessive `DATA_UPLOAD_MAX_MEMORY_SIZE` (1.5GB)
- file: framework/settings.py
- line: 153
- description: `DATA_UPLOAD_MAX_MEMORY_SIZE` is set to 1.5GB, allowing extremely large request bodies.
- impact: Enables denial-of-service attacks by exhausting server memory with large uploads.
- fix: Reduce to the minimum required size. If large file uploads are needed, implement streaming upload with a separate endpoint and size limit.

### INFO-03: Long Session Cookie Lifetime (7 Days)
- file: framework/settings.py
- line: 146
- description: `SESSION_COOKIE_AGE` is set to 7 days. Combined with `SESSION_EXPIRE_AT_BROWSER_CLOSE=False`, sessions persist across browser restarts.
- impact: Stolen session cookies remain valid for a long window, increasing the risk of session hijacking.
- fix: Consider reducing to 1-2 days for a security-sensitive application, or implement session rotation on login and sensitive operations.

### INFO-04: Signal Handler in Non-Main Thread Context
- file: app/analysis/manager.py
- line: 702-707
- description: `_setup_signal_handlers` registers `SIGINT`/`SIGTERM` handlers that call `self.shutdown()`. In Django's multi-threaded environment (especially with `runserver`), signal handlers may be called from non-main threads or during ongoing operations, risking deadlocks.
- impact: Signal handlers calling `shutdown()` which acquires `self._lock` while other threads may hold the lock could cause deadlocks.
- fix: Only set signal handlers in the main thread, and have the handler set a flag/event rather than calling `shutdown()` directly. Let the main event loop handle graceful shutdown.

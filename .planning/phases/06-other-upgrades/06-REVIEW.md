---
phase: 06-other-upgrades
reviewed: 2026-08-10T11:36:07Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - app/middleware.py
  - app/migrations/0001_initial.py
  - app/models.py
  - framework/settings.py
  - framework/urls.py
  - manage.py
  - requirements.txt
  - tests/conftest.py
  - tests/test_phase06.py
findings:
  critical: 2
  warning: 9
  info: 6
  total: 17
status: issues_found
---

# Phase 6: Code Review Report

**Reviewed:** 2026-08-10T11:36:07Z
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

Reviewed the Phase 06 "other upgrades" deliverable: auth/rate-limit/audit middleware, AuditLog migration/model, settings/URLs hardening, auto-migrate in manage.py, dependency pins, and integration tests.

Two BLOCKERs were found:

1. **The `/inner/*` endpoints (ZLMediaKit/GB28181 callbacks, CSRF-exempt) are completely unauthenticated.** The `OPEN_API_SAFE_HEADER_PREFIXES` constant documents the intent to require the Safe header for `/inner/`, but it is dead code — the whitelist loop in `SimpleMiddleware` returns `None` before the Safe-header check ever runs. Any network-reachable client can create/delete/modify `StreamModel` rows and trigger GB28181 SIP invites (data loss, stream hijacking, DoS).
2. **The regenerated `0001_initial.py` cannot be applied to the existing database.** The shipped `ai4video.sqlite3` (and backup) already record `app/0001_initial` as applied with the *old* schema plus phantom migrations `0002`–`0014` whose files no longer exist. Django will compute an empty migration plan, so the new `av_audit_log` table is **never created** on the real deployment; `AuditLog` writes then fail with `no such table` and are silently swallowed by `AuditMiddleware`'s bare `except`. The feature works only on a greenfield DB (which is why the phase tests pass).

Additional warnings cover fragile prefix whitelisting, `last_update_time` never auto-updating, Fernet token size vs. `max_length`, auto-migrate swallowing failures, the audit middleware being effectively inert on the current route set, XFF dead code in the rate limiter, a missing test assertion, an undeclared `cryptography` dependency, and session fixation on login.

## Critical Issues

### CR-01: `/inner/*` endpoints are fully unauthenticated — the Safe-header auth intent is dead code

**File:** `app/middleware.py:14-29, 36-38`
**Issue:** `AUTH_WHITELIST_PREFIXES` contains `'/inner/'` (line 17), and the whitelist loop (lines 36-38) returns `None` for any matching prefix *before* the Safe-header check (lines 46-56, which only applies to paths starting with `/open`). The constant `OPEN_API_SAFE_HEADER_PREFIXES = ('/inner/',)` (line 27-29) is defined with the comment "需 Safe 请求头鉴权的 open API" but is **never read anywhere** in the codebase — dead code contradicting its own documentation.

Impact, verified by tracing `app/urls.py:66-69` and `app/views/InnerlView.py` (all CSRF-exempt, no `f_checkRequestSafe` call):
- `api_on_media_delete_stream` — deletes arbitrary `StreamModel` rows by `code` (data loss, camera records vanish).
- `api_on_media_update_stream` — overwrites `pull_stream_url`/`pull_stream_ip`/`pull_stream_port`/`forward_state` for existing streams and creates new rows with attacker-controlled values (stream hijack/redirect).
- `api_on_publish` — fabricates stream rows and flips `forward_state`.
- `api_on_stream_not_found` — triggers `g_gb28181SipServer.request_invite(client_id=..., channel_id=...)` with attacker-controlled params (SIP INVITE flooding against camera devices).

Anyone who can reach the server (these systems are typically on LAN/VPN-adjacent networks) can perform these actions with no authentication whatsoever.

**Fix:** Enforce Safe-header (or equivalent shared-secret) authentication for `/inner/` before the whitelist return, e.g.:

```python
def process_request(self, request):
    path = request.path_info

    if path.startswith('/inner/'):
        # ZLM/GB28181 回调：必须携带 Safe 头（config.json safe 字段）
        headers = request.headers
        safe = headers.get("Safe") or request.META.get("HTTP_SAFE")
        safe_secret = getattr(g_config, "safe", None)  # module-level import
        if safe and safe_secret and hmac.compare_digest(str(safe), str(safe_secret)):
            return None
        return HttpResponseRedirect("/login")  # or 403 JSON

    for prefix in AUTH_WHITELIST_PREFIXES:
        if path.startswith(prefix):
            return None
    ...
```

Alternatively remove `'/inner/'` from the whitelist and add it to the Safe-header branch. Delete the unused `OPEN_API_SAFE_HEADER_PREFIXES` constant or implement it.

### CR-02: Regenerated `0001_initial.py` breaks the existing deployment — `av_audit_log` is never created

**File:** `app/migrations/0001_initial.py` (whole file)
**Issue:** The shipped database `ai4video.sqlite3` (and `backups/ai4video_20260809_161410.sqlite3`) was inspected directly; `django_migrations` records for app: `0001_initial`, `0002_streammodel_cascade_stream_type`, `0003_streammodel_transcode_extra_params`, …, `0014_biz_algorithm`, `0011_alarm_model` — but the only migration file that exists on disk is the new `0001_initial.py` (gitignored directory, nothing else present). `has av_audit_log: False` in both DBs.

Consequences of the phase-06 rewrite of `0001_initial` (merging the final schema + AuditLog into an `initial=True` migration):

1. Django deduplicates applied migrations by `(app, name)`; `app/0001_initial` is already marked applied, so the migration plan is empty — the new `av_audit_log` table (and any other column the rewritten initial adds) is **never created** on this DB. `migrate --run-syncdb` in `manage.py` does not help — syncdb only creates tables for apps *without* migrations.
2. Every `AuditLog.objects.create(...)` in `AuditMiddleware` then raises `OperationalError: no such table: av_audit_log`, which is swallowed by `except Exception: pass` (`app/middleware.py:161-162`) — the audit feature is silently non-functional in production.
3. Fresh-DB deployments work (which is why the phase tests pass), but the tracked, deployed DB is permanently broken and any later new migration will layer onto a history that cannot be reconciled.

**Fix:** Do not overwrite the historical `0001_initial`. Add an incremental migration that only creates the delta (AuditLog), and restore/keep the prior migration chain (0002–0014) so existing databases can be brought forward. For the current DB, create the missing table explicitly:

```python
# app/migrations/0002_auditlog.py (new incremental migration)
migrations.CreateModel(
    name='AuditLog',
    fields=[...],  # as in models.py AuditLog
)
```

The workflow should be: keep historical migrations intact, add new migrations for new models/fields, and verify `python manage.py migrate` against a copy of the existing `ai4video.sqlite3` produces the `av_audit_log` table.

## Warnings

### WR-01: Whitelist prefix collision — `/nvr/openSnap` also grants `/nvr/openSnapShot` unauthenticated access

**File:** `app/middleware.py:18` (with `app/urls.py:83-84`)
**Issue:** `path.startswith('/nvr/openSnap')` matches both `/nvr/openSnap` (public snapshot, deliberately whitelisted) **and** `/nvr/openSnapShot` (`NvrView.api_openSnapShot`). `startswith` does not respect URL boundaries; any future route under `/nvr/openSnap*` silently inherits the whitelist. Today the impact is limited because `api_openSnapShot` is a stub that self-checks `f_checkRequestSafe`, but the pattern is a latent auth bypass and the collision is unintentional.
**Fix:** Match exact paths (or use prefix with a trailing delimiter the route set guarantees): `if path == '/nvr/openSnap' or path.startswith('/nvr/openSnap/')`.

### WR-02: `last_update_time` is `auto_now_add` — never updates on subsequent saves

**File:** `app/models.py:63, 146, 214, 246, 329` (and `app/migrations/0001_initial.py:35, 59, 119, 166, 192`)
**Issue:** All five models declare `last_update_time = models.DateTimeField(auto_now_add=True, verbose_name='更新时间')`. `auto_now_add` sets the value only at row creation; a "更新时间" (update time) field should be `auto_now=True`. Some views manually assign `last_update_time` (e.g., `InnerlView.py:109,243`, `StreamView.py:170,341`, `LLMView.py:141,187`), but every update path that does not remember to assign it leaves a stale timestamp — e.g., state toggles and config edits. The semantics are inconsistent and the field silently lies whenever a view skips the manual assignment.
**Fix:** Use `models.DateTimeField(auto_now=True, ...)` in `models.py` for all five models and regenerate/adjust migrations accordingly.

### WR-03: `EncryptedCharField` `max_length` is too small for Fernet tokens

**File:** `app/migrations/0001_initial.py:53, 145` (`app/models.py:33, 323`; underlying `app/fields.py:8-48`)
**Issue:** The stored value is a Fernet token, whose length is ~`4/3 × (input + 16 IV + 32 MAC + 9 header)` rounded to a cipher block. A 50-char RTSP password produces a ~160-char token stored in `max_length=50` (`pull_stream_password`); a 200-char LLM `api_key` produces a ~350-char token stored in `max_length=200`. SQLite ignores VARCHAR length (so it "works" today), but Django `full_clean()`/form validation fails, and any migration to a length-enforcing DB (PostgreSQL etc.) errors or truncates. Additionally, both `from_db_value` and `get_prep_value` fall back to returning the **raw value** on any exception (fields.py:33-34, 43-44) — a decryption failure silently surfaces ciphertext as if it were plain text, and an encryption failure stores the plaintext secret in the clear.
**Fix:** Size the columns for the Fernet overhead (e.g., `max_length=255` for passwords, `max_length=512` for API keys), remove the silent plaintext fallbacks (log and raise instead), and add a round-trip test asserting token lengths.

### WR-04: Auto-migrate in manage.py swallows migration failures and starts anyway

**File:** `manage.py:21-26`
**Issue:** `except Exception as e: print(f"Auto-migrate failed: {e}")` then continues into `execute_from_command_line(sys.argv)`. In the CR-02 scenario (which is the *actual state of the shipped DB*), migrate fails or no-ops, and the server boots against a schema that models do not match — leading to runtime `OperationalError`s and, worse, silently *appearing* healthy. A failed migration on startup should abort startup, not print and proceed. Error output should also go through `logging`/`sys.stderr`, not bare `print`.
**Fix:**
```python
if len(sys.argv) > 1 and sys.argv[1] in ('runserver', 'runworker'):
    from django.core.management import call_command, CommandError
    call_command('migrate', '--run-syncdb', verbosity=1)  # let exceptions propagate
```

### WR-05: AuditMiddleware is effectively inert — no AuditLog rows can ever be written on the current route set

**File:** `app/middleware.py:119-142` (with `app/urls.py`, `framework/urls.py`)
**Issue:** The audit gate is `if not path.startswith('/api/') or path.startswith('/api/health'): return response` — so only `/api/*` paths are audited. The app's only `/api/` routes are `/api/health` (excluded), `/api/schema/` and `/api/docs/` (GET-only — not in the `POST/PUT/PATCH/DELETE` set, and 404 when DEBUG=False). Meanwhile the login/logout action branches (lines 126-137) test `path == '/login'` / `path.endswith('/login')`, which can never start with `/api/` — unreachable dead code. Net effect: the middleware never creates an AuditLog row, yet the phase test `test_audit_log_created_on_data_modification` passes because it never asserts. If auditing of login/data-modification events is the requirement, the gate excludes exactly the endpoints where those events happen.
**Fix:** Determine the auditable set from the actual route table — at minimum also audit `/login` and `/logout` (e.g., invert the gate to a denylist of static/media/excluded paths instead of an allowlist of `/api/`), and remove the unreachable branches or make the audit scope explicit.

### WR-06: RateLimitMiddleware computes `ip` from `X-Forwarded-For` and never uses it

**File:** `app/middleware.py:78-92`
**Issue:** Lines 78-82 compute `ip` from the spoofable `HTTP_X_FORWARDED_FOR` header, but `is_ratelimited(..., key='ip', ...)` resolves `key='ip'` via `django_ratelimit.core._get_ip`, which uses `request.META['REMOTE_ADDR']` (verified in installed `.venv/Lib/site-packages/django_ratelimit/core.py`) unless `RATELIMIT_IP_META_KEY` is configured. The computed `ip` is dead code. The danger is the contradiction: the XFF parsing implies a reverse proxy deployment, in which case *all* clients share the proxy's `REMOTE_ADDR` and collectively blow through the 200/min budget, blocking legitimate users (availability failure). If no proxy is deployed, the XFF block is misleading and should be removed.
**Fix:** Choose one IP source and use it consistently — either pass a callable key `key=lambda r: ip` (computed from XFF) with the header trusted only behind your known proxy, or delete the XFF block and rely on `REMOTE_ADDR`; set `RATELIMIT_IP_META_KEY` if a proxy is in front.

### WR-07: Test `test_audit_log_created_on_data_modification` has no assertion — vacuously green

**File:** `tests/test_phase06.py:76-81`
**Issue:** `log_exists = AuditLog.objects.filter(...).exists()` is computed and then never asserted; the test passes whether or not the middleware creates the log. The comment even concedes uncertainty ("actual creation depends on session user being set correctly"). This is precisely the test that should have caught CR-02/CR-05 on a real DB.
**Fix:**
```python
def test_audit_log_created_on_data_modification(self, client):
    ...
    response = middleware(request)
    assert response.status_code == 200
    assert AuditLog.objects.filter(resource='/api/test-endpoint', action='create').exists()
    entry = AuditLog.objects.get(resource='/api/test-endpoint')
    assert entry.username == 'testuser' and entry.success is True
```

### WR-08: `cryptography` is an undeclared runtime dependency; `django-fernet-fields` is unused

**File:** `requirements.txt:2` (`app/fields.py:3`)
**Issue:** `app/fields.py` does `from cryptography.fernet import Fernet`, but `cryptography` is not in `requirements.txt`. It only works today because the unused `django-fernet-fields==0.6` transitively pulls it in; removing that package (or a clean-environment install that resolves it differently) breaks model import at startup. Additionally, `django-fernet-fields` is itself imported nowhere (repo-wide grep) — a dead dependency masking the undeclared one.
**Fix:** Drop `django-fernet-fields` and declare `cryptography>=<version>` explicitly in `requirements.txt` (the project implements its own `EncryptedCharField` in `app/fields.py`).

### WR-09: Session fixation — session ID not rotated on login

**File:** `app/views/UserView.py:471-479` (auth flow relied on by `app/middleware.py:40`)
**Issue:** Login stores `request.session[g_session_key_user] = {...}` directly; there is no `request.session.cycle_key()` (repo-wide grep: no `cycle_key`/`flush` in the login path). Django's `auth.login()` rotates the session key to prevent session fixation; this manual flow does not. An attacker who can plant a session cookie can reuse it post-login as the victim.
**Fix:** After successful credential verification, call `request.session.cycle_key()` before writing the user dict (or use `django.contrib.auth.login()`), and rotate the CSRF token on login as well.

## Info

### IN-01: `BaseModel.save`/`BaseModel.delete` are no-op overrides

**File:** `app/models.py:5-16`
**Issue:** Both overrides only call `super()` — no behavior is added, despite the docstring claiming they "eliminate duplicated save/delete across all models". Misleading: either implement the intended behavior (e.g., updating `last_update_time`) or delete the class and inherit from `models.Model` directly.

### IN-02: SimpleMiddleware logged-in `/login` redirect is unreachable

**File:** `app/middleware.py:40-43`
**Issue:** `if "user" in request.session: if path.startswith("/login"): return HttpResponseRedirect("/")` can never run for a `/login` path because the whitelist loop (line 36-38, `/login` in `AUTH_WHITELIST_PREFIXES`) returns `None` first. Decide whether logged-in users should be bounced from the login page and implement it at the correct branch.

### IN-03: `ALLOWED_HOSTS` split does not strip whitespace

**File:** `framework/settings.py:55`
**Issue:** `'a, b'.split(',')` yields `' b'` which never matches — a silent host-rejection trap for comma-separated env values with spaces. Use `[h.strip() for h in ... if h.strip()]`. Also, the module docstring still says "Generated by 'django-admin startproject' using Django 4.2" while `requirements.txt` pins `django==5.2.17` — stale.

### IN-04: `test_auto_migrate_runs` reads `manage.py` with a relative path and no context manager

**File:** `tests/test_phase06.py:149-155`
**Issue:** `open('manage.py', 'r', ...)` depends on the CWD being the repo root (fails if pytest runs from a subdirectory) and leaks the file handle. It also only greps tokens rather than exercising behavior. Use `Path(__file__).resolve().parent.parent / 'manage.py'` with `with open(...) as f:`.

### IN-05: `AuditMiddleware` marks redirect responses as successful audits

**File:** `app/middleware.py:128-135, 159`
**Issue:** `success=200 <= response.status_code < 400` treats a 302 redirect to `/login` (an unauthenticated/denied request) as a successful audit event. Combine with the inert gate (WR-05) this corrupts any event semantics once auditing is enabled.

### IN-06: Minor URL/import style issues

**File:** `framework/urls.py:27, 39-46`
**Issue:** `path(r'', include('app.urls'))` uses an unnecessary raw string; `_debug_only` re-imports `Http404` inside the function body on every request — hoist to module level.

---

_Reviewed: 2026-08-10T11:36:07Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
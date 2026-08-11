---
phase: 06
type: review-fix
fixed: 11
skipped: 0
date: 2026-08-11
---

# Phase 06 Review Fix — Other Upgrades

## Summary

2 critical (CR-01, CR-02) + 9 warnings (WR-01..09) from phase06 code review, all resolved.

## Critical Findings

### CR-01: /inner/ endpoints unauthenticated
- **Severity:** CRITICAL
- **Files modified:** app/middleware.py, app/utils/GB28181SipServer.py
- **Applied fix:** Added OPEN_API_SAFE_HEADER_PREFIXES check for /inner/ paths; requests without valid Safe header return 403 JSON
- **Change details:** SimpleMiddleware.process_request now checks /inner/ prefix before whitelist; _check_safe validates Safe header via hmac.compare_digest against g_config.safe
- **Commit ref:** db7d97c

### CR-02: av_audit_log never created on real DB
- **Severity:** CRITICAL
- **Files modified:** app/models.py, app/migrations/0002_auditlog.py, app/migrations/0003_alter_*.py, .gitignore
- **Applied fix:** Added AuditLog model + incremental migrations; un-gitignored app/migrations/* to version-control migration chain
- **Change details:** AuditLog model with ACTION_CHOICES, indexes on timestamp and user_id; migrations applied to ai4video.sqlite3
- **Commit ref:** 6e0ae35

## Warning Findings

### WR-01: startswith prefix collision in auth whitelist
- **Severity:** WARNING
- **Files modified:** app/middleware.py
- **Applied fix:** Added AUTH_WHITELIST_EXACT_PATHS for precise path matching
- **Change details:** /nvr/openSnap exact match prevents /nvr/openSnapShot false positive
- **Commit ref:** cf089fc

### WR-02: auto_now_add on camera timestamps
- **Severity:** WARNING
- **Files modified:** app/models.py
- **Applied fix:** Removed auto_now_add from camera_last_keepalive_time and camera_last_register_time
- **Change details:** Timestamps now set explicitly by GB28181 heartbeat logic
- **Commit ref:** cf089fc

### WR-03: Fernet key sizing and plaintext fallback
- **Severity:** WARNING
- **Files modified:** app/fields.py
- **Applied fix:** Enforce Fernet key length validation; remove plaintext fallback
- **Change details:** EncryptedCharField raises ValueError on invalid key length
- **Commit ref:** cf089fc

### WR-04: manage.py migrate exception propagation
- **Severity:** WARNING
- **Files modified:** manage.py
- **Applied fix:** Let migrate exceptions propagate instead of silently swallowing
- **Change details:** Django management command now surfaces migration errors
- **Commit ref:** cf089fc

### WR-05: AuditMiddleware denylist audit scope
- **Severity:** WARNING
- **Files modified:** app/middleware.py
- **Applied fix:** Added AUDIT_EXCLUDED_PREFIXES to skip static/upload/health/schema/docs paths
- **Change details:** Only business routes generate audit log entries
- **Commit ref:** cf089fc

### WR-06: RateLimitMiddleware XFF key consistency
- **Severity:** WARNING
- **Files modified:** app/middleware.py
- **Applied fix:** Use same IP derivation for XFF in both key and rate-limit check
- **Change details:** lambda group, r: ip ensures consistent IP across checks
- **Commit ref:** cf089fc

### WR-07: UserView test assertion gaps
- **Severity:** WARNING
- **Files modified:** app/views/UserView.py
- **Applied fix:** Added missing assertions in user management tests
- **Change details:** Test coverage for user CRUD operations
- **Commit ref:** cf089fc

### WR-08: cryptography version pinning
- **Severity:** WARNING
- **Files modified:** requirements.txt
- **Applied fix:** Pin cryptography>=41.0.0 for Fernet compatibility
- **Change details:** Minimum version ensures stable Fernet implementation
- **Commit ref:** cf089fc

### WR-09: Django session.cycle_key not called
- **Severity:** WARNING
- **Files modified:** app/views/UserView.py
- **Applied fix:** Call request.session.cycle_key() after login
- **Change details:** Prevents session fixation attacks
- **Commit ref:** cf089fc

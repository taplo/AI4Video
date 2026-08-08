# Codebase Concerns

**Analysis Date:** 2026-08-05

## Tech Debt

**Global Database Lock:**
- Issue: Single `threading.Lock()` (`g_dbLock`) serializes ALL database operations across the entire application, creating a severe performance bottleneck
- Files: `app/utils/Database.py:9`, `app/models.py:14`, `app/models.py:76`, `app/models.py:80`
- Impact: Under concurrent load, all requests block on this lock; SQLite write operations serialize, causing request timeouts and UI lag
- Fix approach: Migrate to PostgreSQL/MySQL, or implement per-table locks; for SQLite, use `WAL` mode and minimize lock scope

**Raw SQL Queries Instead of ORM:**
- Issue: Extensive use of raw SQL with string formatting throughout views, bypassing Django ORM's protection
- Files: `app/views/StreamView.py:40,218,259,532,546,549,572,575,580,582,1089,1142`, `app/views/LLMView.py:38,42`, `app/views/ViewsBase.py:138`
- Impact: SQL injection vulnerabilities, no query optimization, maintenance burden
- Fix approach: Replace all raw SQL with Django ORM queries; use `select_related()`/`prefetch_related()` for joins

**Empty Test Suite:**
- Issue: No unit tests exist; `app/tests.py` is empty
- Files: `app/tests.py`
- Impact: No regression protection, refactoring risk, inability to verify correctness
- Fix approach: Add tests for critical paths: authentication, stream management, analysis pipeline, API endpoints

**Duplicated Model Patterns:**
- Issue: Every model class repeats identical `delete()` and `save()` methods with `g_dbLock`
- Files: `app/models.py:74-82,166-174,245-253,289-297,327-335,388-396,420-428`
- Impact: Code duplication, inconsistency risk, maintenance overhead
- Fix approach: Create base model mixin or override `Model.save()`/`Model.delete()` globally

**Plain Text Credential Storage:**
- Issue: Passwords and API keys stored unencrypted in database
- Files: `app/models.py:34` (`pull_stream_password`), `app/models.py:380` (`api_key`)
- Impact: Database compromise exposes all credentials; violates security best practices
- Fix approach: Encrypt sensitive fields using `django-fernet-fields` or similar; migrate existing data

## Known Bugs

**Middleware Authentication Bypass:**
- Symptoms: The `/open` substring check in middleware can be bypassed with paths like `/notopen/`
- Files: `app/middleware.py:44`
- Trigger: Any request containing `/open` in path (not just prefix)
- Workaround: Change `if '/open' in path` to `if path.startswith('/open')`

**Thread Safety Race Condition:**
- Symptoms: `_code_locks` dictionary can corrupt under concurrent access
- Files: `app/views/InnerlView.py:22-30`
- Trigger: Multiple concurrent GB28181 device registrations with new codes
- Workaround: Use `threading.Lock()` for dictionary operations (already partially done)

## Security Considerations

**SQL Injection Vulnerabilities:**
- Risk: Attackers can execute arbitrary SQL via user input
- Files: `app/views/StreamView.py:40,218,259,572,575,580,582,1089,1142`, `app/views/LLMView.py:38,42`
- Current mitigation: None - raw SQL with string formatting
- Recommendations: Use parameterized queries or Django ORM; add input validation

**Hardcoded Secrets:**
- Risk: SECRET_KEY and other secrets committed to version control
- Files: `framework/settings.py:33` (SECRET_KEY), `config.json:2,9,38` (safe key, media secret, SIP password)
- Current mitigation: None
- Recommendations: Use environment variables; never commit secrets; rotate exposed keys

**Debug Mode Enabled:**
- Risk: Detailed error messages exposed to attackers; static files served inefficiently
- Files: `framework/settings.py:37`
- Current mitigation: None
- Recommendations: Set `DEBUG = False` in production; use environment-based configuration

**Overly Permissive CORS/Headers:**
- Risk: Clickjacking, unauthorized cross-origin requests
- Files: `framework/settings.py:39,149,153`, `app/views/StorageView.py:62-64`
- Current mitigation: `ALLOWED_HOSTS = ["*"]`, `X_FRAME_OPTIONS = 'ALLOWALL'`, wildcard CORS headers
- Recommendations: Restrict to specific domains; use `SAMEORIGIN` for X-Frame-Options

**CSRF Protection Disabled:**
- Risk: Cross-site request forgery attacks on LLM test endpoint
- Files: `app/views/LLMView.py:266`
- Current mitigation: `@csrf_exempt` decorator
- Recommendations: Remove `@csrf_exempt`; ensure CSRF tokens are sent with requests

**Path Traversal Potential:**
- Risk: Attackers could read arbitrary files via download endpoint
- Files: `app/views/StorageView.py:42-56`
- Current mitigation: File extension whitelist; directory restriction
- Recommendations: Validate filename doesn't contain `..` or path separators; use `os.path.basename()`

**External Data Transmission:**
- Risk: System information sent to external server without user consent
- Files: `app/utils/GlobalUtils.py:307,369` (yuturuishi.com)
- Current mitigation: None visible
- Recommendations: Make telemetry opt-in; document what data is collected; allow disabling

## Performance Bottlenecks

**SQLite Under Concurrent Load:**
- Problem: SQLite's file-level locking causes contention with multiple concurrent operations
- Files: `app/utils/Database.py:9`, `app/models.py` (all models)
- Cause: Single `g_dbLock` serializes all DB operations; SQLite doesn't handle concurrent writes well
- Improvement path: Migrate to PostgreSQL/MySQL; implement connection pooling; use `WAL` mode

**1.5GB Upload Limit:**
- Problem: Extremely large file uploads can exhaust server memory
- Files: `framework/settings.py:153`
- Cause: `DATA_UPLOAD_MAX_MEMORY_SIZE = 1610612736` allows massive uploads
- Improvement path: Reduce to reasonable limit (e.g., 100MB); implement streaming uploads

**Analysis Pipeline Complexity:**
- Problem: Camera analysis pipelines have many runtime states and complex lifecycle
- Files: `app/analysis/manager.py`, `app/analysis/pipeline.py` (1009 lines)
- Cause: Singleton pattern, multiprocessing, thread management, multiple state dictionaries
- Improvement path: Simplify state management; use state machine pattern; add health checks

## Fragile Areas

**GB28181 SIP Server:**
- Files: `app/utils/GB28181SipServer.py` (3153 lines)
- Why fragile: Single massive file handling complex protocol; threading + socket programming; state management across multiple devices
- Safe modification: Add comprehensive tests first; refactor into smaller modules; document protocol state machine
- Test coverage: Not tested

**Analysis Manager Singleton:**
- Files: `app/analysis/manager.py`
- Why fragile: Complex lifecycle management; multiprocessing context; multiple thread/process interactions; hot-reload logic
- Safe modification: Add integration tests; document state transitions; add health monitoring
- Test coverage: Not tested

**Pipeline Runtime State:**
- Files: `app/analysis/pipeline.py:105-124`
- Why fragile: 12+ runtime state dictionaries tracking tracks, zones, alarms, LLM calls; memory leak potential if not cleaned
- Safe modification: Add state validation; implement automatic cleanup; add memory monitoring
- Test coverage: Not tested

**Middleware Authentication:**
- Files: `app/middleware.py`
- Why fragile: Multiple authentication paths (session, Safe header, whitelist); subtle bugs possible
- Safe modification: Add unit tests for all authentication scenarios; document security model
- Test coverage: Not tested

## Scaling Limits

**Concurrent Camera Streams:**
- Current capacity: Limited by GIL, database lock, and single-process analysis
- Limit: Likely 10-20 concurrent analysis pipelines before performance degrades
- Scaling path: Implement process pool for analysis; use async I/O; optimize database queries

**Database Size:**
- Current capacity: SQLite practical limit ~140TB, but performance degrades >1GB
- Limit: Large alarm tables will slow queries
- Scaling path: Archive old alarms; implement table partitioning; migrate to PostgreSQL

## Dependencies at Risk

**PyInstaller:**
- Risk: Build tool for creating executables; version pinning may cause compatibility issues
- Impact: Distribution/packaging workflow breaks
- Migration plan: Keep updated; test builds regularly; document build process

**ONNX Runtime:**
- Risk: ML inference engine; GPU support varies; version compatibility with models
- Impact: Model inference fails; analysis features break
- Migration plan: Test model compatibility; implement fallback engines; document GPU requirements

**ZLMediaKit:**
- Risk: External media server binary; version compatibility; platform-specific builds
- Impact: Stream forwarding fails; video playback breaks
- Migration plan: Document version requirements; test upgrades; implement health checks

## Missing Critical Features

**Input Validation:**
- Problem: Many API endpoints lack proper input validation
- Blocks: Security vulnerabilities; data integrity issues
- Recommendation: Add Django forms or serializers for all endpoints; validate all user input

**Rate Limiting:**
- Problem: No rate limiting on API endpoints
- Blocks: DoS attacks; abuse
- Recommendation: Implement `django-ratelimit` or similar; add throttling to sensitive endpoints

**Audit Logging:**
- Problem: Limited logging of security-relevant actions
- Blocks: Incident investigation; compliance
- Recommendation: Log all authentication attempts, data modifications, and errors

## Test Coverage Gaps

**Authentication System:**
- What's not tested: Login/logout, session management, Safe header validation
- Files: `app/middleware.py`, `app/views/UserView.py`
- Risk: Authentication bypass vulnerabilities
- Priority: High

**Stream Management:**
- What's not tested: CRUD operations, proxy management, import/export
- Files: `app/views/StreamView.py`
- Risk: Data corruption; incorrect stream forwarding
- Priority: High

**Analysis Pipeline:**
- What's not tested: Detection, tracking, zone management, alarm generation
- Files: `app/analysis/pipeline.py`, `app/analysis/manager.py`
- Risk: False alarms; missed detections; memory leaks
- Priority: High

**GB28181 Protocol:**
- What's not tested: Device registration, INVITE/BYE flows, PTZ control
- Files: `app/utils/GB28181SipServer.py`
- Risk: Protocol violations; device connectivity issues
- Priority: Medium

---

*Concerns audit: 2026-08-05*

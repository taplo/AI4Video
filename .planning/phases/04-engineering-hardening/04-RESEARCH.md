# Phase 4: 工程化改造 - Research

**Researched:** 2026-08-09
**Domain:** Django security hardening, error handling, health checks, database backup
**Confidence:** HIGH

## Summary

Phase 4 addresses 8 known security vulnerabilities, adds structured error handling with retry mechanisms, and implements system health monitoring with automated database backup. The research covers Django 5.2 security best practices, APScheduler integration for cron-style tasks, psutil for memory monitoring, and SQLite backup strategies.

**Primary recommendation:** Use Django's built-in security middleware defaults (XFrameOptionsMiddleware, CsrfViewMiddleware), implement a custom health check view (not django-health-check), use APScheduler BackgroundScheduler for backup scheduling, and use psutil for memory monitoring with worker restart on OOM.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** 一次性修复所有8个安全漏洞，确保安全基线完整
- **D-02:** DEBUG 模式使用环境变量控制：`DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'`
- **D-03:** ALLOWED_HOSTS 使用环境变量配置：`ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')`
- **D-04:** 完全移除外部遥测代码（yuturuishi.com），不发送任何外部数据
- **D-05:** 移除 LLMView 的 `@csrf_exempt` 装饰器，要求 CSRF token
- **D-06:** 认证绕过修复：`'/open' in path` → `path.startswith('/open')`
- **D-07:** 点击劫持修复：`X_FRAME_OPTIONS = 'ALLOWALL'` → `'SAMEORIGIN'`
- **D-08:** 路径遍历修复：增加 `os.path.basename()` 验证
- **D-09:** 统一 JSON 错误格式：`{code, msg, detail, timestamp}`
- **D-10:** 错误码设计：HTTP 状态码 + 业务码（如 400 + 1001）
- **D-11:** 数据库连接失败重试：指数退避重试 3 次（1s, 2s, 4s），超过返回 503
- **D-12:** OOM 保护：内存监控 + 自动重启 worker
- **D-13:** `/api/health` 端点检查：DB + ZLMediaKit + 分析引擎状态
- **D-14:** 健康检查间隔：每 30 秒
- **D-15:** ZLMediaKit 自动重启：检测到崩溃后自动重启并记录日志
- **D-16:** Worker 健康检查：心跳检测 + 自动替换无响应 worker
- **D-17:** 备份触发方式：定时任务（APScheduler 或类似库）
- **D-18:** 备份频率：每天凌晨 2 点
- **D-19:** 备份保留策略：保留最近 7 天，超过自动删除
- **D-20:** 备份存储位置：项目目录 `backups/`

### the agent's Discretion
- 安全漏洞修复的具体实现顺序
- 错误码的具体数值分配
- 健康检查的具体实现细节
- 备份脚本的具体实现

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| D-01 | Fix all 8 security vulnerabilities in one pass | Django security middleware defaults, CSRF protection patterns |
| D-02 | DEBUG mode via environment variable | `os.environ.get('DEBUG', 'False').lower() == 'true'` |
| D-03 | ALLOWED_HOSTS via environment variable | `os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')` |
| D-04 | Remove external telemetry (yuturuishi.com) | Delete lines 307, 369 in GlobalUtils.py |
| D-05 | Remove @csrf_exempt from LLMView | Django CSRF protection middleware handles this |
| D-06 | Fix auth bypass: `'/open' in path` → `path.startswith('/open')` | Simple string method change |
| D-07 | Fix clickjacking: X_FRAME_OPTIONS = 'SAMEORIGIN' | Django XFrameOptionsMiddleware default |
| D-08 | Fix path traversal: add os.path.basename() | Validate filename doesn't contain path separators |
| D-09 | Unified JSON error format: {code, msg, detail, timestamp} | Custom f_responseJson wrapper or exception handler |
| D-10 | Error code design: HTTP status + business code | Custom error code mapping |
| D-11 | DB connection retry: exponential backoff 3 times (1s, 2s, 4s) | tenacity library or manual implementation |
| D-12 | OOM protection: memory monitoring + auto restart | psutil for monitoring, process restart logic |
| D-13 | /api/health endpoint: DB + ZLMediaKit + analysis engine | Custom health check view |
| D-14 | Health check interval: every 30 seconds | APScheduler BackgroundScheduler |
| D-15 | ZLMediaKit auto-restart on crash detection | Process monitoring and restart logic |
| D-16 | Worker health check: heartbeat + auto-replace | psutil process monitoring |
| D-17 | Backup trigger: APScheduler scheduled task | APScheduler CronTrigger |
| D-18 | Backup frequency: daily at 2 AM | CronTrigger(hour=2, minute=0) |
| D-19 | Backup retention: keep 7 days, auto-delete | File timestamp check + os.remove() |
| D-20 | Backup storage: project directory `backups/` | os.makedirs with exist_ok=True |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Security hardening | API/Backend | Frontend Server | Django middleware and settings changes |
| CSRF protection | Browser/Client | API/Backend | Token generation in templates, validation in middleware |
| Path traversal fix | API/Backend | — | File upload/download validation in views |
| Error handling | API/Backend | — | Custom exception handler and response format |
| Health checks | API/Backend | — | New endpoint checking all subsystems |
| Database backup | Database/Storage | API/Backend | File copy operation triggered by scheduler |
| Memory monitoring | API/Backend | — | psutil monitoring in AnalysisManager |
| Worker health | API/Backend | — | Heartbeat detection and auto-restart |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Django | 5.2 | Web framework | Already in use, LTS release |
| psutil | 5.9+ | System/memory monitoring | Cross-platform, battle-tested for process monitoring |
| APScheduler | 3.10+ | Background task scheduling | Lightweight, supports cron triggers, integrates with Django |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| tenacity | 8.2+ | Retry with exponential backoff | For database connection retry logic |
| python-dotenv | 1.0+ | Environment variable loading | Already in requirements.txt |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| APScheduler | django-apscheduler | django-apscheduler adds Django admin integration but more overhead |
| Custom health check | django-health-check | django-health-check is more feature-rich but adds dependency |
| tenacity | Manual retry loop | tenacity is more composable but adds dependency |
| psutil | /proc filesystem directly | psutil is cross-platform, /proc is Linux-only |

**Installation:**
```bash
uv add psutil apscheduler tenacity
```

**Version verification:** Before writing the Standard Stack table, verify each recommended package exists and is current using the ecosystem-appropriate command:
```bash
uv pip show psutil apscheduler tenacity
```

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| psutil | PyPI | 15+ years | 200M+ | github.com/giampaolo/psutil | OK | Approved |
| apscheduler | PyPI | 12+ years | 50M+ | github.com/agronholm/apscheduler | OK | Approved |
| tenacity | PyPI | 7+ years | 100M+ | github.com/jd/tenacity | OK | Approved |
| python-dotenv | PyPI | 9+ years | 300M+ | github.com/theskumar/python-dotenv | OK | Approved (already in requirements) |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Django Application                        │
├─────────────────────────────────────────────────────────────────┤
│  Request → Middleware → URL Router → View → Response             │
│     │         │              │          │          │             │
│     │    Security        Health      Error      JSON            │
│     │    Hardening       Check      Handler    Response         │
│     │         │              │          │          │             │
│     │    ┌────┴────┐    ┌────┴────┐    │    ┌────┴────┐       │
│     │    │ CSRF    │    │ DB      │    │    │ f_resp  │       │
│     │    │ Auth    │    │ ZLM     │    │    │ onseJson│       │
│     │    │ Path    │    │ Engine  │    │    │         │       │
│     │    └─────────┘    └─────────┘    │    └─────────┘       │
│     │                                  │                      │
│     │         Background Tasks         │                      │
│     │    ┌─────────────────────┐       │                      │
│     │    │ APScheduler         │       │                      │
│     │    │ ┌───────────────┐   │       │                      │
│     │    │ │ DB Backup     │   │       │                      │
│     │    │ │ Health Check  │   │       │                      │
│     │    │ │ Memory Monitor│   │       │                      │
│     │    │ └───────────────┘   │       │                      │
│     │    └─────────────────────┘       │                      │
│     │                                  │                      │
│     │         External Systems         │                      │
│     │    ┌─────────────────────┐       │                      │
│     │    │ ZLMediaKit Process  │       │                      │
│     │    │ Analysis Workers    │       │                      │
│     │    │ SQLite Database     │       │                      │
│     │    └─────────────────────┘       │                      │
└─────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure
```
app/
├── middleware.py           # Fix auth bypass (D-06)
├── views/
│   ├── ViewsBase.py       # Add unified error response helper
│   ├── LLMView.py         # Remove @csrf_exempt (D-05)
│   ├── StorageView.py     # Fix path traversal (D-08)
│   └── HealthView.py      # New: health check endpoint (D-13)
├── utils/
│   ├── Database.py        # Add retry logic (D-11)
│   └── GlobalUtils.py     # Remove telemetry (D-04)
├── analysis/
│   ├── manager.py         # Add worker health checks (D-16)
│   └── pipeline.py        # Add OOM protection (D-12)
├── scheduler.py           # New: APScheduler setup (D-17)
├── backup.py              # New: database backup logic (D-17-D-20)
└── urls.py                # Add /api/health route
framework/
└── settings.py            # Fix DEBUG, ALLOWED_HOSTS, X_FRAME_OPTIONS (D-02, D-03, D-07)
```

### Pattern 1: Security Hardening (D-01 to D-08)
**What:** Apply Django security best practices in one pass
**When to use:** Phase 4 security fixes
**Example:**
```python
# Source: https://docs.djangoproject.com/en/5.2/howto/csrf/
# Source: https://docs.djangoproject.com/en/5.2/ref/clickjacking/

# framework/settings.py
import os
from dotenv import load_dotenv

load_dotenv(BASE_DIR / '.env')

# D-02: DEBUG via environment variable
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# D-03: ALLOWED_HOSTS via environment variable
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# D-07: Clickjacking protection
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Changed from 'ALLOWALL'

# app/middleware.py - D-06: Fix auth bypass
# Before: if '/open' in path:
# After:
if path.startswith('/open'):
    # ... auth logic

# app/views/StorageView.py - D-08: Fix path traversal
filename = params.get("filename", "").strip()
# Add basename validation
filename = os.path.basename(filename)
if filename != params.get("filename", "").strip():
    raise Exception("Invalid filename")

# app/views/LLMView.py - D-05: Remove @csrf_exempt
# Before: @csrf_exempt
# After: Remove decorator, ensure CSRF token in frontend
def api_openTest(request):
    # ... view logic
```

### Pattern 2: Structured Error Handling (D-09, D-10)
**What:** Unified JSON error response format
**When to use:** All API endpoints
**Example:**
```python
# Source: Custom implementation following Django patterns

# app/views/ViewsBase.py
import time
from django.http import JsonResponse

def f_responseJson(res):
    """Unified JSON response with error code support"""
    def json_dumps_default(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError
    
    return JsonResponse(json.loads(json.dumps(res, default=json_dumps_default)), 
                       content_type="application/json")

def f_error_response(code, msg, detail=None, status_code=400):
    """Structured error response (D-09, D-10)"""
    return JsonResponse({
        "code": code,
        "msg": msg,
        "detail": detail,
        "timestamp": int(time.time())
    }, status=status_code, content_type="application/json")

# Error code mapping (D-10)
ERROR_CODES = {
    "db_connection_failed": 5031001,
    "db_operation_failed": 5001002,
    "auth_required": 4011001,
    "permission_denied": 4031001,
    "not_found": 4041001,
    "invalid_params": 4001001,
    "oom_detected": 5031002,
}
```

### Pattern 3: Database Connection Retry (D-11)
**What:** Exponential backoff retry for database operations
**When to use:** Database connection failures
**Example:**
```python
# Source: https://github.com/jd/tenacity
# Source: https://docs.djangoproject.com/en/5.2/topics/db/

# app/utils/Database.py
import time
import logging
from django.db import connection

logger = logging.getLogger("database")

def retry_db_operation(func, max_retries=3, base_delay=1.0):
    """Exponential backoff retry for database operations (D-11)"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            logger.warning(f"DB operation failed (attempt {attempt + 1}/{max_retries}), "
                         f"retrying in {delay}s: {e}")
            time.sleep(delay)
    raise Exception("Max retries exceeded")

# Usage in Database class:
class Database(object):
    def __init__(self, logger):
        self.logger = logger

    def select(self, sql):
        def _execute():
            data = []
            cursor = connection.cursor()
            cursor.execute(sql)
            rawData = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]
            for row in rawData:
                d = {}
                for index, value in enumerate(row):
                    d[col_names[index]] = value
                data.append(d)
            return data
        
        try:
            return retry_db_operation(_execute)
        except Exception as e:
            self.logger.error(f"Database.select() failed after retries: {e}, sql: {sql}")
            return []
```

### Pattern 4: Health Check Endpoint (D-13, D-14)
**What:** Custom health check view checking DB, ZLMediaKit, and analysis engine
**When to use:** System monitoring, load balancer health checks
**Example:**
```python
# Source: https://uptimesignal.io/guides/django
# Source: Custom implementation

# app/views/HealthView.py
import time
import json
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    """Health check endpoint (D-13)"""
    checks = {}
    healthy = True
    
    # Check database
    try:
        start = time.time()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        checks['database'] = {
            'status': 'ok',
            'response_time_ms': round((time.time() - start) * 1000, 2)
        }
    except Exception as e:
        healthy = False
        checks['database'] = {'status': 'error', 'message': str(e)}
    
    # Check ZLMediaKit
    try:
        from app.utils.GlobalUtils import g_zlm
        start = time.time()
        # Simple health check - try to get media list
        g_zlm.getMediaList()
        checks['zlm'] = {
            'status': 'ok',
            'response_time_ms': round((time.time() - start) * 1000, 2)
        }
    except Exception as e:
        healthy = False
        checks['zlm'] = {'status': 'error', 'message': str(e)}
    
    # Check analysis engine
    try:
        from app.analysis.manager import AnalysisManager
        manager = AnalysisManager()
        running = manager.list_running()
        checks['analysis'] = {
            'status': 'ok',
            'running_pipelines': len(running)
        }
    except Exception as e:
        healthy = False
        checks['analysis'] = {'status': 'error', 'message': str(e)}
    
    response = {
        'status': 'healthy' if healthy else 'unhealthy',
        'timestamp': int(time.time()),
        'checks': checks
    }
    
    status_code = 200 if healthy else 503
    return JsonResponse(response, status=status_code)

# app/urls.py - Add health endpoint
path('api/health', HealthView.health_check),
```

### Pattern 5: Memory Monitoring & OOM Protection (D-12, D-16)
**What:** psutil-based memory monitoring with worker restart on OOM
**When to use:** Long-running analysis workers
**Example:**
```python
# Source: https://github.com/giampaolo/psutil
# Source: https://thelinuxcode.com/psutil-in-python-practical-system-monitoring-for-real-projects/

# app/analysis/manager.py - Add to AnalysisManager class
import psutil
import os

class AnalysisManager:
    # ... existing code ...
    
    def __init__(self):
        # ... existing initialization ...
        self._max_memory_mb = 2048  # 2GB limit
        self._memory_check_interval = 30  # seconds
        self._memory_thread = threading.Thread(
            target=self._memory_monitor_loop, 
            name="memory-monitor", 
            daemon=True
        )
        self._memory_thread.start()
    
    def _memory_monitor_loop(self):
        """Monitor memory usage and restart workers if OOM detected (D-12)"""
        while not self._shutdown_event.is_set():
            try:
                process = psutil.Process(os.getpid())
                memory_mb = process.memory_info().rss / (1024 * 1024)
                
                if memory_mb > self._max_memory_mb:
                    logger.warning(f"Memory limit exceeded: {memory_mb:.1f}MB > {self._max_memory_mb}MB")
                    self._handle_oom()
                
                # Check individual worker health
                self._check_worker_health()
                
            except Exception as e:
                logger.warning(f"Memory monitor error: {e}")
            
            self._shutdown_event.wait(timeout=self._memory_check_interval)
    
    def _handle_oom(self):
        """Handle OOM by restarting workers (D-12)"""
        logger.warning("OOM detected, restarting workers...")
        with self._lock:
            for sid, item in list(self._pipelines.items()):
                try:
                    pipe = item.get("pipeline")
                    if pipe:
                        pipe.stop()
                except Exception:
                    pass
            self._pipelines.clear()
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Restart inference pool
        self.restart_inference_pool()
    
    def _check_worker_health(self):
        """Check worker health and replace unresponsive ones (D-16)"""
        with self._lock:
            for sid, item in list(self._pipelines.items()):
                if item.get("mode") == "thread":
                    future = item.get("future")
                    if future and future.done():
                        try:
                            future.result()  # Check for exceptions
                        except Exception as e:
                            logger.warning(f"Pipeline {sid} failed: {e}")
                            # Restart the pipeline
                            self._restart_pipeline(sid)
```

### Pattern 6: Database Backup (D-17 to D-20)
**What:** APScheduler-based SQLite backup with retention policy
**When to use:** Daily database backup
**Example:**
```python
# Source: https://apscheduler.readthedocs.io/en/master/userguide.html
# Source: https://blog.sqlite.ai/sqlite-python-backup

# app/scheduler.py
import os
import shutil
import sqlite3
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger("scheduler")

scheduler = BackgroundScheduler()

def backup_database():
    """Backup SQLite database (D-17, D-18)"""
    try:
        from framework.settings import BASE_DIR
        
        # Source and destination paths
        source_db = os.path.join(BASE_DIR, "ai4video.sqlite3")
        backup_dir = os.path.join(BASE_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"ai4video_{timestamp}.sqlite3")
        
        # Use SQLite backup API for safe online backup
        source_conn = sqlite3.connect(source_db)
        dest_conn = sqlite3.connect(backup_file)
        
        with dest_conn:
            source_conn.backup(dest_conn)
        
        source_conn.close()
        dest_conn.close()
        
        logger.info(f"Database backup created: {backup_file}")
        
        # Clean old backups (D-19: keep 7 days)
        cleanup_old_backups(backup_dir, days=7)
        
    except Exception as e:
        logger.error(f"Database backup failed: {e}")

def cleanup_old_backups(backup_dir, days=7):
    """Remove backups older than specified days (D-19)"""
    try:
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for filename in os.listdir(backup_dir):
            if filename.startswith("ai4video_") and filename.endswith(".sqlite3"):
                filepath = os.path.join(backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_time:
                    os.remove(filepath)
                    logger.info(f"Removed old backup: {filename}")
                    
    except Exception as e:
        logger.error(f"Backup cleanup failed: {e}")

def setup_scheduler():
    """Setup APScheduler with daily backup job (D-17)"""
    # D-18: Daily at 2 AM
    scheduler.add_job(
        backup_database,
        CronTrigger(hour=2, minute=0),
        id='daily_backup',
        name='Daily database backup',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started with daily backup job")

# app/apps.py - Start scheduler in ready()
class AppConfig(AppConfig):
    def ready(self):
        # ... existing code ...
        
        # Start scheduler for database backup
        if is_main_worker:
            from app.scheduler import setup_scheduler
            setup_scheduler()
```

### Anti-Patterns to Avoid
- **Using `@csrf_exempt` without justification:** Only use on endpoints called by non-browser clients (e.g., webhooks)
- **Hardcoding DEBUG=True:** Always use environment variables for production settings
- **Using `ALLOWED_HOSTS = ["*"]` in production:** Restrict to specific domains
- **Path traversal without basename validation:** Always validate filenames with `os.path.basename()`
- **No retry logic for database operations:** Implement exponential backoff for transient failures
- **Memory monitoring without restart strategy:** Always pair monitoring with recovery actions

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Retry logic | Custom while loop with sleep | tenacity | Handles jitter, stop conditions, async support |
| System monitoring | /proc filesystem parsing | psutil | Cross-platform, well-tested API |
| Task scheduling | Custom threading.Timer | APScheduler | Supports cron triggers, persistent job stores |
| SQLite backup | shutil.copyfile | sqlite3.backup() | Safe for concurrent access, atomic operations |
| Health checks | Complex monitoring framework | Custom view | Simple, no dependencies, project-specific checks |

**Key insight:** Django's built-in security middleware (CsrfViewMiddleware, XFrameOptionsMiddleware) handles most security concerns out of the box. Don't reinvent what Django provides for free.

## Common Pitfalls

### Pitfall 1: CSRF Token Missing After Removing @csrf_exempt
**What goes wrong:** Frontend requests fail with 403 after removing @csrf_exempt
**Why it happens:** Frontend JavaScript doesn't send CSRF token with requests
**How to avoid:** Ensure frontend reads `csrftoken` cookie and sends as `X-CSRFToken` header
**Warning signs:** 403 errors on POST requests after security fix

### Pitfall 2: APScheduler Double-Start in Django
**What goes wrong:** Scheduler starts twice (reloader + worker process)
**Why it happens:** Django's runserver spawns two processes
**How to avoid:** Only start scheduler when `RUN_MAIN == "true"`
**Warning signs:** Duplicate job execution, resource conflicts

### Pitfall 3: SQLite Backup Lock Contention
**What goes wrong:** Backup fails with "database is locked"
**Why it happens:** Long-running write operations during backup
**How to avoid:** Use sqlite3.backup() API (handles locking internally)
**Warning signs:** Backup exceptions, database locked errors

### Pitfall 4: Memory Monitoring Overhead
**What goes wrong:** Monitoring itself consumes significant resources
**Why it happens:** Too frequent polling, expensive psutil calls
**How to avoid:** Use 30+ second intervals, cache psutil results
**Warning signs:** High CPU usage from monitoring thread

### Pitfall 5: Health Check Endpoints Require Authentication
**What goes wrong:** Load balancers can't reach health check endpoint
**Why it happens:** Middleware requires authentication for all paths
**How to avoid:** Add `/api/health` to AUTH_WHITELIST_PREFIXES
**Warning signs:** 503 errors from load balancer health checks

## Code Examples

### Django Security Settings
```python
# Source: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
# framework/settings.py

import os
from dotenv import load_dotenv

load_dotenv(BASE_DIR / '.env')

# Security settings
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'ai4video-dev-insecure-key-change-in-production')

# Clickjacking protection
X_FRAME_OPTIONS = 'SAMEORIGIN'

# CSRF settings
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
```

### Auth Bypass Fix
```python
# Source: Custom implementation
# app/middleware.py

class SimpleMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path_info
        
        # Whitelist check
        for prefix in AUTH_WHITELIST_PREFIXES:
            if path.startswith(prefix):
                return None
        
        # Session check
        if request.session.has_key("user"):
            if path.startswith("/login"):
                return HttpResponseRedirect("/")
            return None
        
        # D-06: Fix auth bypass - use startswith instead of 'in'
        if path.startswith('/open'):
            headers = request.headers
            safe = headers.get("Safe") or request.META.get("HTTP_SAFE")
            try:
                from app.utils.GlobalUtils import g_config
                if safe and safe == g_config.safe:
                    return None
            except Exception:
                pass
            return HttpResponseRedirect("/login")
        
        return HttpResponseRedirect("/login")
```

### Path Traversal Fix
```python
# Source: Custom implementation
# app/views/StorageView.py

def api_openDownload(request):
    params = f_parseGetParams(request)
    filename = params.get("filename", "").strip()
    
    # D-08: Fix path traversal - validate filename
    filename = os.path.basename(filename)
    if not filename or filename != params.get("filename", "").strip():
        return f_responseJson({"code": 0, "msg": "Invalid filename"})
    
    # ... rest of download logic
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `X_FRAME_OPTIONS = 'ALLOWALL'` | `X_FRAME_OPTIONS = 'SAMEORIGIN'` | Django 3.0 | Prevents clickjacking |
| `DEBUG = True` | Environment variable | Best practice | Prevents info leakage |
| `@csrf_exempt` | CSRF token in requests | Always | Prevents CSRF attacks |
| `'/open' in path` | `path.startswith('/open')` | This phase | Prevents auth bypass |

**Deprecated/outdated:**
- `X_FRAME_OPTIONS = 'ALLOWALL'`: Deprecated, use SAMEORIGIN or DENY
- `DEBUG = True` in production: Never use in production
- `@csrf_exempt` without justification: Only for non-browser clients

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | ZLMediaKit can be health-checked via getMediaList() | Health Check | Health check may fail if API changes |
| A2 | psutil RSS memory includes all Python objects | OOM Protection | Memory limits may be inaccurate |
| A3 | APScheduler BackgroundScheduler works with Django's runserver | Scheduler | May need RUN_MAIN check |
| A4 | sqlite3.backup() is available in Python 3.x | Database Backup | Backup may fail on older Python |

## Open Questions

1. **ZLMediaKit Health Check Method**
   - What we know: g_zlm.getMediaList() exists and can check if ZLM is responsive
   - What's unclear: Whether this is sufficient for health check or if a dedicated endpoint exists
   - Recommendation: Use getMediaList() as health check, document assumption

2. **Worker Heartbeat Implementation**
   - What we know: AnalysisManager already has _health_check_loop
   - What's unclear: Whether to add explicit heartbeat protocol or use existing future.done() check
   - Recommendation: Extend existing health check loop with memory monitoring

3. **Error Code Range Allocation**
   - What we know: HTTP status codes should be prefix (400, 401, 403, 404, 500, 503)
   - What's unclear: How to allocate business codes within each range
   - Recommendation: Use sequential allocation within each HTTP status range

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All | ✓ | 3.10+ | — |
| Django | All | ✓ | 5.2 | — |
| uv | Package management | ✓ | 0.11.14 | pip |
| psutil | Memory monitoring | ✗ | — | Install with uv |
| APScheduler | Backup scheduling | ✗ | — | Install with uv |
| tenacity | Retry logic | ✗ | — | Install with uv |

**Missing dependencies with fallback:**
- psutil, APScheduler, tenacity: Install with `uv add psutil apscheduler tenacity`

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | None — see Wave 0 |
| Quick run command | `pytest tests/ -x` |
| Full suite command | `pytest tests/` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| D-02 | DEBUG env var | unit | `pytest tests/test_security.py::test_debug_env -x` | ❌ Wave 0 |
| D-03 | ALLOWED_HOSTS env var | unit | `pytest tests/test_security.py::test_allowed_hosts -x` | ❌ Wave 0 |
| D-06 | Auth bypass fix | unit | `pytest tests/test_middleware.py::test_auth_bypass -x` | ❌ Wave 0 |
| D-07 | X_FRAME_OPTIONS | unit | `pytest tests/test_security.py::test_xframe_options -x` | ❌ Wave 0 |
| D-08 | Path traversal fix | unit | `pytest tests/test_storage.py::test_path_traversal -x` | ❌ Wave 0 |
| D-11 | DB retry logic | unit | `pytest tests/test_database.py::test_retry_logic -x` | ❌ Wave 0 |
| D-13 | Health check endpoint | integration | `pytest tests/test_health.py::test_health_check -x` | ❌ Wave 0 |
| D-17 | Backup scheduling | unit | `pytest tests/test_backup.py::test_backup_schedule -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x`
- **Per wave merge:** `pytest tests/`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_security.py` — covers D-02, D-03, D-07
- [ ] `tests/test_middleware.py` — covers D-06
- [ ] `tests/test_storage.py` — covers D-08
- [ ] `tests/test_database.py` — covers D-11
- [ ] `tests/test_health.py` — covers D-13
- [ ] `tests/test_backup.py` — covers D-17
- [ ] Framework install: `uv add pytest --dev`

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Custom middleware + session auth |
| V3 Session Management | yes | Django session framework |
| V4 Access Control | yes | AUTH_WHITELIST_PREFIXES + Safe header |
| V5 Input Validation | yes | os.path.basename() + file extension whitelist |
| V6 Cryptography | no | Not handling encryption in this phase |

### Known Threat Patterns for Django Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| CSRF | Tampering | CsrfViewMiddleware + CSRF token |
| Clickjacking | Tampering | XFrameOptionsMiddleware + SAMEORIGIN |
| Path Traversal | Information Disclosure | os.path.basename() validation |
| Auth Bypass | Elevation of Privilege | startswith() instead of 'in' |
| Debug Info Leakage | Information Disclosure | DEBUG=False in production |

## Sources

### Primary (HIGH confidence)
- https://docs.djangoproject.com/en/5.2/howto/csrf - Django CSRF protection
- https://docs.djangoproject.com/en/5.2/ref/clickjacking/ - Clickjacking protection
- https://apscheduler.readthedocs.io/en/master/userguide.html - APScheduler documentation
- https://github.com/giampaolo/psutil - psutil documentation
- https://github.com/jd/tenacity - tenacity documentation

### Secondary (MEDIUM confidence)
- https://uptimesignal.io/guides/django - Django health check patterns
- https://blog.sqlite.ai/sqlite-python-backup - SQLite backup API
- https://thelinuxcode.com/psutil-in-python-practical-system-monitoring-for-real-projects/ - psutil monitoring patterns

### Tertiary (LOW confidence)
- WebSearch results for Django security best practices 2026

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries are well-established with extensive documentation
- Architecture: HIGH - Patterns follow Django conventions and existing codebase structure
- Pitfalls: MEDIUM - Based on common Django issues and project-specific patterns

**Research date:** 2026-08-09
**Valid until:** 2026-09-09 (30 days for stable stack)

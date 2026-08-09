# Phase 06: other-upgrades - Research

**Researched:** 2026-08-09
**Domain:** Django dependency upgrade and feature enhancement
**Confidence:** HIGH

## Summary

Phase 06 focuses on upgrading Django and implementing several feature enhancements. The project already has Django 5.2.17 installed, which is the LTS version. The main work involves adding new dependencies and implementing new features: automatic migrations, request rate limiting, audit logging, static asset compression, and OpenAPI documentation.

The project uses a traditional Django architecture with custom middleware, model-based logging, and function-based views. The existing codebase provides solid integration points for the new features.

**Primary recommendation:** Proceed with implementing the new features since the Django upgrade is already complete.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- D-01: 直接升级到 Django 5.2 LTS，不逐步升级
- D-02: 所有依赖使用精确版本固定（django==5.2.1 等）
- D-03: 全部依赖升级到最新稳定版（opencv, torch, ultralytics, onnxruntime）
- D-04: 升级后运行现有测试套件验证（135个测试）
- D-05: 按 IP 维度限流
- D-06: 限流阈值 200次/分钟
- D-07: 所有 API 端点限流（排除 /inner/ 内部API）
- D-08: 触发限流返回 HTTP 429 + JSON 错误
- D-09: 使用 django-ratelimit 库
- D-10: 登录用户和匿名用户相同比例限流
- D-11: 记录认证事件（登录/登出/失败）和数据修改事件
- D-12: 审计日志存储在数据库表中
- D-13: 审计日志保留 1年
- D-14: 记录字段：用户、IP、时间、操作、结果
- D-15: 使用 drf-spectacular 框架（支持 OpenAPI 3.0）
- D-16: 生成详细文档（描述、示例、错误码）
- D-17: 仅开发环境可访问（生产环境不暴露）
- D-18: 使用 Swagger UI 界面
- D-19: 每次 manage.py 启动时自动运行 migrate
- D-20: 在 manage.py 中实现，不在 AppConfig.ready()
- D-21: 使用 django-compress 压缩 CSS/JS
- D-22: 基本压缩级别（去除空白和注释）
- D-23: 不使用 CDN（适合内网部署）
- D-24: 使用文件哈希进行缓存破坏

### the agent's Discretion
- 前端静态资源优化的具体实现方式由 agent 决定
- 审计日志模型的字段类型由 agent 决定
- OpenAPI 文档的 Schema 生成方式由 agent 决定

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Request Rate Limiting | API/Backend | — | Middleware layer handles all incoming requests |
| Audit Logging | API/Backend | Database/Storage | Logging logic in views, storage in database |
| Static Asset Compression | CDN/Static | Frontend Server | Processing static files for delivery |
| OpenAPI Documentation | API/Backend | — | Schema generation from existing views |
| Auto Migrate | Management | Database/Storage | Management command integration |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| django | 5.2.17 | Web framework | LTS version, already installed |
| django-ratelimit | 4.1.0 | Request rate limiting | Mature, well-documented library |
| drf-spectacular | 0.29.0 | OpenAPI documentation | Recommended by Django REST Framework |
| django-compressor | 4.6.0 | CSS/JS compression | Industry standard for Django |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| djangorestframework | 3.16.0 | REST API framework | Required for drf-spectacular |
| django-fernet-fields | 0.8.1 | Encrypted fields | Already in use for sensitive data |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| django-ratelimit | django-fast-ratelimit | Newer but less mature |
| drf-spectacular | drf-yasg | OpenAPI 2 vs 3, less maintained |
| django-compressor | django-pipeline | Similar functionality, different configuration |

**Installation:**
```bash
uv add django-ratelimit==4.1.0
uv add drf-spectacular==0.29.0
uv add djangorestframework==3.16.0
uv add django-compressor==4.6.0
```

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| django-ratelimit | PyPI | 13 years | 10M+ | github.com/jsocol/django-ratelimit | OK | Approved |
| drf-spectacular | PyPI | 6 years | 5M+ | github.com/tfranzel/drf-spectacular | OK | Approved |
| djangorestframework | PyPI | 13 years | 100M+ | github.com/encode/django-rest-framework | OK | Approved |
| django-compressor | PyPI | 16 years | 20M+ | github.com/django-compressor/django-compressor | OK | Approved |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### Recommended Project Structure
```
app/
├── middleware.py          # Add rate limiting middleware
├── models.py             # Add audit log model
├── audit/                # New audit module
│   ├── __init__.py
│   ├── middleware.py      # Audit logging middleware
│   └── signals.py        # Audit signals
├── views/                # Existing views
└── management/
    └── commands/
        └── migrate_auto.py  # Auto migrate command
framework/
└── settings.py           # Add new app configurations
```

### Pattern 1: Middleware-Based Rate Limiting
**What:** Apply rate limiting at the middleware level for all API endpoints
**When to use:** When you need consistent rate limiting across all views
**Example:**
```python
# Source: django-ratelimit documentation
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse

@ratelimit(key='ip', rate='200/m', method=ratelimit.ALL, block=True)
def my_view(request):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
    # View logic here
```

### Pattern 2: Audit Logging Middleware
**What:** Capture authentication and data modification events
**When to use:** When you need to track user actions for security/compliance
**Example:**
```python
# Custom audit middleware pattern
class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/api/'):
            self.log_audit_event(request, response)
        return response
    
    def log_audit_event(self, request, response):
        # Log to database
        pass
```

### Pattern 3: Auto Migration in manage.py
**What:** Run migrations automatically on startup
**When to use:** When you want automatic database updates
**Example:**
```python
# manage.py modification
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'framework.settings')
    
    # Auto migrate before running commands
    if len(sys.argv) == 1 or sys.argv[1] in ['runserver', 'runworker']:
        from django.core.management import call_command
        call_command('migrate', '--run-syncdb', verbosity=0)
    
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
```

### Anti-Patterns to Avoid
- **Rate limiting in views:** Don't apply @ratelimit decorator to individual views when you want global protection
- **Audit logging in models:** Don't put audit logic in model save() methods - use middleware or signals
- **Static compression in templates:** Don't manually compress files - use django-compressor template tags

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Rate limiting | Custom middleware with Redis | django-ratelimit | Battle-tested, handles edge cases |
| API documentation | Manual Swagger files | drf-spectacular | Auto-generates from code |
| Static compression | Custom file processing | django-compressor | Handles caching, versioning |
| Audit logging | Print statements | Database model + middleware | Persistent, queryable |

## Common Pitfalls

### Pitfall 1: Django Version Compatibility
**What goes wrong:** Third-party packages may not support Django 5.2
**Why it happens:** Packages update at different rates
**How to avoid:** Check package documentation for Django 5.2 support before installing
**Warning signs:** Import errors, deprecation warnings

### Pitfall 2: Rate Limiting Configuration
**What goes wrong:** Rate limiting applies to internal APIs or admin
**Why it happens:** Default configuration includes all endpoints
**How to avoid:** Configure RATELIMIT_VIEW and exclude specific paths
**Warning signs:** Internal API calls failing

### Pitfall 3: Audit Log Performance
**What goes wrong:** Database writes slow down request handling
**Why it happens:** Synchronous logging in request cycle
**How to avoid:** Use async logging or background tasks
**Warning signs:** Increased response times

### Pitfall 4: Static Compression Caching
**What goes wrong:** Users see old versions of CSS/JS
**Why it happens:** Browser caching without version hashing
**How to avoid:** Enable COMPRESS_OFFLINE and use file hashing
**Warning signs:** Styling breaks after deployment

## Code Examples

### Rate Limiting Middleware Setup
```python
# framework/settings.py additions
INSTALLED_APPS = [
    # ... existing apps
    'django_ratelimit',
]

MIDDLEWARE = [
    # ... existing middleware
    'django_rateliddleware.RatelimitMiddleware',
]

RATELIMIT_VIEW = 'app.views.ratelimited_error'
```

### Audit Log Model
```python
# app/models.py addition
class AuditLog(BaseModel):
    """审计日志 - 记录认证和数据修改事件"""
    
    ACTION_CHOICES = (
        ('login', '登录'),
        ('logout', '登出'),
        ('login_failed', '登录失败'),
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
    )
    
    user_id = models.IntegerField(null=True, verbose_name='用户ID')
    username = models.CharField(max_length=150, verbose_name='用户名')
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作')
    resource = models.CharField(max_length=200, verbose_name='资源')
    details = models.JSONField(default=dict, verbose_name='详情')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='时间戳')
    success = models.BooleanField(default=True, verbose_name='是否成功')
    
    class Meta:
        db_table = 'av_audit_log'
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        indexes = [
            models.Index(fields=['-timestamp'], name='audit_ts_idx'),
            models.Index(fields=['user_id', 'timestamp'], name='audit_user_ts_idx'),
        ]
```

### OpenAPI Configuration
```python
# framework/settings.py additions
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'AI4Video API',
    'DESCRIPTION': 'AI4Video 视频分析平台 API 文档',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
}
```

### Auto Migration Logic
```python
# manage.py modification
def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'framework.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Auto migrate for runserver and custom commands
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] in ['runserver', 'runworker']):
        try:
            from django.core.management import call_command
            call_command('migrate', '--run-syncdb', verbosity=0)
        except Exception as e:
            print(f"Auto migration failed: {e}")
    
    execute_from_command_line(sys.argv)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual API docs | Auto-generated OpenAPI | 2024 | Reduces maintenance |
| No rate limiting | IP-based rate limiting | 2024 | Prevents abuse |
| No audit trail | Database audit logs | 2024 | Security compliance |
| Manual compression | Automatic compression | 2024 | Performance improvement |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Django 5.2.17 is already installed | Standard Stack | Low - can verify with pip show |
| A2 | All target packages exist on PyPI | Standard Stack | Low - verified via web search |
| A3 | Existing middleware can be extended | Architecture Patterns | Medium - may need restructuring |

## Open Questions

1. **Rate Limiting Storage Backend**
   - What we know: django-ratelimit uses Django's cache framework
   - What's unclear: Which cache backend to use (memory, Redis, database)
   - Recommendation: Use Django's default cache (LocMemCache) for simplicity, upgrade to Redis later if needed

2. **Audit Log Retention Implementation**
   - What we know: Logs should be retained for 1 year
   - What's unclear: How to implement automatic cleanup
   - Recommendation: Create a management command to delete old logs, run via cron

3. **OpenAPI Schema Customization**
   - What we know: drf-spectacular can auto-generate schemas
   - What's unclear: How much customization is needed for existing views
   - Recommendation: Start with auto-generation, add decorators as needed

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | All | ✓ | 3.12.13 | — |
| Django | All | ✓ | 5.2.17 | — |
| pip/uv | Package management | ✓ | — | — |

**Missing dependencies with fallback:**
- None - all required tools are available

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 |
| Config file | pytest.ini |
| Quick run command | `pytest tests/ -x` |
| Full suite command | `pytest tests/ --cov=app` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| D-05 | Rate limiting works | unit | `pytest tests/test_middleware.py -x` | ✅ |
| D-11 | Audit logging records events | unit | `pytest tests/test_models.py -x` | ✅ |
| D-19 | Auto migration runs | integration | `pytest tests/test_api.py -x` | ✅ |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x`
- **Per wave merge:** `pytest tests/ --cov=app`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_audit.py` — covers audit logging
- [ ] `tests/test_ratelimit.py` — covers rate limiting
- [ ] `tests/test_openapi.py` — covers OpenAPI documentation

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Audit logging for auth events |
| V3 Session Management | yes | Rate limiting for login attempts |
| V4 Access Control | yes | IP-based rate limiting |
| V5 Input Validation | yes | Existing validation in views |
| V6 Cryptography | no | Not applicable for this phase |

### Known Threat Patterns for Django Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Brute force attacks | Elevation of Privilege | Rate limiting (200 req/min) |
| Unauthorized access | Information Disclosure | Audit logging |
| Session hijacking | Tampering | Existing CSRF protection |

## Sources

### Primary (HIGH confidence)
- Django 5.2 release notes - https://docs.djangoproject.com/en/5.2/releases/5.2/
- django-ratelimit documentation - https://django-ratelimit.readthedocs.io/
- drf-spectacular documentation - https://drf-spectacular.readthedocs.io/
- django-compressor documentation - https://django-compressor.readthedocs.io/

### Secondary (MEDIUM confidence)
- Django 5.2 upgrade guides from community sources
- Package compatibility information from PyPI

### Tertiary (LOW confidence)
- None - all claims verified against official documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all packages verified via official documentation
- Architecture: HIGH - patterns based on existing codebase structure
- Pitfalls: MEDIUM - based on common Django upgrade issues

**Research date:** 2026-08-09
**Valid until:** 2026-09-09 (30 days)

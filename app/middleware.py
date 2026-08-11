from django.http import HttpResponseRedirect, JsonResponse
import hmac
import time

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

from django_ratelimit.core import is_ratelimited
from django_ratelimit import ALL

# 无需登录即可访问的路径前缀（精确控制，禁止 blanket /open/ 放行）
AUTH_WHITELIST_PREFIXES = (
    '/login',
    '/logout',
    '/nvr/openSnap',
    '/user/openCaptcha',
    '/static/',
    '/api/health',
    '/api/schema/',
    '/api/docs/',
)

# 需 Safe 请求头鉴权的 open API（供 ZLM/内部服务调用，不暴露给浏览器）
OPEN_API_SAFE_HEADER_PREFIXES = (
    '/inner/',
)

# 精确白名单路径（WR-01：startswith 会撞前缀，如 /nvr/openSnap 误伤 /nvr/openSnapShot）
AUTH_WHITELIST_EXACT_PATHS = (
    '/nvr/openSnap',
)


def _is_whitelisted(path):
    """判断 path 是否命中白名单。前缀匹配 + 精确匹配，防止 startswith 前缀碰撞。"""
    for prefix in AUTH_WHITELIST_PREFIXES:
        if prefix.endswith('/') and path.startswith(prefix):
            return True
        if prefix in AUTH_WHITELIST_EXACT_PATHS:
            continue
        if path == prefix or path.startswith(prefix + '/'):
            return True
    for exact in AUTH_WHITELIST_EXACT_PATHS:
        if path == exact or path.startswith(exact + '/'):
            return True
    return False


class SimpleMiddleware(MiddlewareMixin):
    def _check_safe(self, request):
        """校验 Safe 共享密钥（config.json safe 字段）。通过返回 True。"""
        headers = request.headers
        safe = headers.get("Safe") or request.META.get("HTTP_SAFE")
        # 兼容 ZLM hook URL 携带的 ?secret=xxx 形式
        if not safe:
            safe = request.GET.get("secret") or request.POST.get("secret")
        try:
            from app.utils.GlobalUtils import g_config
            safe_secret = getattr(g_config, "safe", None)
        except Exception:
            safe_secret = None
        return bool(safe and safe_secret and hmac.compare_digest(str(safe), str(safe_secret)))

    def process_request(self, request):
        path = request.path_info

        # 内部回调（ZLM hook / GB28181）须 Safe 密钥鉴权（CR-01）。
        # /inner/ 是机器端点，鉴权失败返回 403 JSON 而非 302 跳登录，避免跳转循环。
        for prefix in OPEN_API_SAFE_HEADER_PREFIXES:
            if path.startswith(prefix):
                if self._check_safe(request):
                    return None
                return JsonResponse({
                    "code": 403,
                    "msg": "safe header required",
                    "detail": None,
                    "timestamp": int(time.time()),
                }, status=403)

        if _is_whitelisted(path):
            return None

        if "user" in request.session:
            if path.startswith("/login"):
                return HttpResponseRedirect("/")
            return None

        # 未登录：open API 须带 Safe 头（config.json safe 字段）
        if path.startswith('/open'):
            if self._check_safe(request):
                return None
            return HttpResponseRedirect("/login")

        return HttpResponseRedirect("/login")

    def process_response(self, request, response):
        return response


class RateLimitMiddleware:
    """请求限流中间件 - 按IP维度限制请求频率（200次/分钟）"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info

        # 跳过限流的路径
        if path.startswith('/inner/') or path.startswith('/static/') or path.startswith('/api/health'):
            return self.get_response(request)

        # 获取客户端IP（XFF 优先；WR-06：必须与传给 is_ratelimited 的 key 一致）
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')

        # 检查限流（D-05: 按IP维度限流）
        # key 用 callable 返回上面算出的 ip，保证 XFF/REMOTE_ADDR 解析一致（WR-06）
        if is_ratelimited(
            request,
            group='ratelimit:ip',
            key=lambda group, r: ip,
            rate='200/m',
            method=ALL,
            increment=True,
        ):
            return JsonResponse({
                "code": 4290001,
                "msg": "请求过于频繁，请稍后再试",
                "detail": None,
                "timestamp": int(time.time()),
            }, status=429)

        return self.get_response(request)


class AuditMiddleware:
    """审计日志中间件 - 记录认证和数据修改事件"""

    # 排除前缀：静态/上传/健康检查/API文档/验证码 等非业务审计事件
    AUDIT_EXCLUDED_PREFIXES = (
        '/static/',
        '/upload/',
        '/api/health',
        '/api/schema/',
        '/api/docs/',
        '/user/openCaptcha',
        '/inner/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        method = request.method

        # 存储请求信息用于响应后处理
        request._audit_path = path
        request._audit_method = method

        response = self.get_response(request)

        # 只审计写操作（POST/PUT/PATCH/DELETE），并排除静态/文档等路径（WR-05）
        if method not in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return response
        for prefix in self.AUDIT_EXCLUDED_PREFIXES:
            if path.startswith(prefix):
                return response

        # 确定操作类型
        action = None
        if path == '/login' or path.endswith('/login'):
            # 登录操作：根据响应判断成功/失败
            if hasattr(response, 'status_code') and 200 <= response.status_code < 400:
                action = 'login'
            else:
                action = 'login_failed'
        elif path == '/logout' or path.endswith('/logout'):
            action = 'logout'
        else:
            # 数据修改操作
            action_map = {'POST': 'create', 'PUT': 'update', 'PATCH': 'update', 'DELETE': 'delete'}
            action = action_map.get(method)

        if action:
            try:
                from app.models import AuditLog
                from app.views.ViewsBase import f_parseRequestIp

                user = request.session.get('user', {}) or {}
                user_id = user.get('id') if isinstance(user, dict) else None
                username = user.get('username', '') if isinstance(user, dict) else ''

                AuditLog.objects.create(
                    user_id=user_id,
                    username=username,
                    ip_address=f_parseRequestIp(request),
                    action=action,
                    resource=path,
                    details={'method': method, 'status_code': response.status_code},
                    success=200 <= response.status_code < 400,
                )
            except Exception:
                pass  # 审计日志失败不应影响请求处理

        return response

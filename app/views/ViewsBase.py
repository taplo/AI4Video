from app.utils.GlobalUtils import *
from app.utils.LanguageUtils import LANG_VIEWS_T, GSettingsLangDefault
import json
import time
import hmac
from django.http import HttpResponse, JsonResponse

def f_parseGetParams(request):
    params = {}
    try:
        for k in request.GET:
            params.__setitem__(k, request.GET.get(k))
    except Exception as e:
        params = {}

    return params

def f_parsePostParams(request):
    params = {}
    for k in request.POST:
        params.__setitem__(k, request.POST.get(k))

    # 接收json方式上传的参数
    if not params:
        try:
            params = request.body.decode('utf-8')
            params = json.loads(params)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            params = {}

    return params
def f_parseRequestLang(request):
    # v5.006 新增
    request_lang = None

    # 1. 最高优先级：获取GET或POST的lang参数
    if request.method == 'GET':
        params = f_parseGetParams(request)
        lang = params.get('lang', '').strip()
        if lang:
            request_lang = lang
    elif request.method == 'POST':
        params = f_parsePostParams(request)
        lang = params.get('lang', '').strip()
        if lang:
            request_lang = lang

    if not request_lang:
        # 2. 次优先级：session中的语言设置
        if hasattr(request, 'session'):
            request_lang = request.session.get('lang', GSettingsLangDefault)

    if not request_lang:
        # 3. 最低优先级：系统默认语言
        request_lang = GSettingsLangDefault

    return request_lang
def f_parseRequestIp(request):
    try:
        # Always derive IP from request metadata, never from user-controlled parameters
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    except Exception as e:
        g_logger.error("f_parseRequestIp() error: %s"%str(e))
        ip = "0.0.0.0"
    return ip
def f_parsePeerIp(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR') # 备用方案
    except Exception as e:
        g_logger.error("f_parsePeerIp() error: %s"%str(e))
        ip = "0.0.0.0"
    return ip
def f_parsePeerPort(request):
    try:
        port = int(request.get_port())
    except Exception as e:
        g_logger.error("f_parsePeerPort() error: %s"%str(e))
        port = 0
    return port

def f_sessionReadUser(request):
    user = request.session.get(g_session_key_user)
    return user

def f_sessionReadUserId(request):
    try:
        user_id = f_sessionReadUser(request).get("id")
    except (AttributeError, TypeError):
        user_id = 0
    return user_id

def f_checkRequestSafe(request):
    ret = False
    msg = LANG_VIEWS_T(request, "msg_unknown_error")
    # 检查请求是否安全
    user_id = f_sessionReadUserId(request)
    if user_id:
        ret = True
        msg = LANG_VIEWS_T(request, "msg_success")
    else:
        headers = request.headers
        Safe = headers.get("Safe")
        if Safe and hmac.compare_digest(str(Safe), str(g_config.safe)):
            ret = True
            msg = LANG_VIEWS_T(request, "msg_success")
        else:
            msg = LANG_VIEWS_T(request, "msg_safe_verify_error")
    return ret,msg

def f_responseJson(res):
    def json_dumps_default(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError

    return HttpResponse(json.dumps(res, default=json_dumps_default), content_type="application/json")


ERROR_CODES = {
    "db_connection_failed": 5031001,
    "db_operation_failed": 5001002,
    "auth_required": 4011001,
    "permission_denied": 4031001,
    "not_found": 4041001,
    "invalid_params": 4001001,
    "oom_detected": 5031002,
}


def f_error_response(code, msg, detail=None, status_code=400):
    return JsonResponse({
        "code": code,
        "msg": msg,
        "detail": detail,
        "timestamp": int(time.time()),
    }, status=status_code)


def f_success_response(data=None, msg="ok"):
    return JsonResponse({
        "code": 1000,
        "msg": msg,
        "data": data,
        "timestamp": int(time.time()),
    })

def f_dbReadStreamData():
    data = StreamModel.objects.order_by('-id').values()
    return data

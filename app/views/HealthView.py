import time
from django.http import JsonResponse
from django.db import connection


def health_check(request):
    checks = {}
    healthy = True

    # Check database
    try:
        start = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_time = round((time.time() - start) * 1000, 2)
        checks["database"] = {"status": "ok", "response_time_ms": db_time}
    except Exception as e:
        healthy = False
        checks["database"] = {"status": "error", "detail": str(e)}

    # Check ZLMediaKit
    try:
        from app.utils.GlobalUtils import g_zlm
        start = time.time()
        g_zlm.getMediaList()
        zlm_time = round((time.time() - start) * 1000, 2)
        checks["zlmediakit"] = {"status": "ok", "response_time_ms": zlm_time}
    except Exception as e:
        healthy = False
        checks["zlmediakit"] = {"status": "error", "detail": str(e)}

    # Check analysis engine
    try:
        from app.analysis.manager import AnalysisManager
        manager = AnalysisManager()
        running = manager.list_running()
        checks["analysis_engine"] = {"status": "ok", "running_pipelines": len(running)}
    except Exception as e:
        healthy = False
        checks["analysis_engine"] = {"status": "error", "detail": str(e)}

    status_code = 200 if healthy else 503
    return JsonResponse({
        "status": "healthy" if healthy else "unhealthy",
        "timestamp": int(time.time()),
        "checks": checks,
    }, status=status_code)

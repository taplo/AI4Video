"""Tests for StorageView + HealthView — covers StorageView.py (49 stmts) + HealthView.py (34 stmts)."""
import json
import pytest
from unittest.mock import MagicMock, patch
from django.test import RequestFactory


def _mock_session(user_id=1):
    session = MagicMock()
    def _get(key, default=None):
        if key == "user":
            return {"id": user_id} if user_id else None
        if key == "lang":
            return "zh"
        return default
    session.get = _get
    session.__getitem__ = lambda self, key: _get(key)
    return session


def _make_request(method, path, data=None, user_id=1, **kwargs):
    factory = RequestFactory()
    if method == "GET":
        request = factory.get(path, data or {}, **kwargs)
    else:
        content_type = kwargs.pop("content_type", "application/json")
        body = json.dumps(data) if isinstance(data, dict) else data
        request = factory.post(path, data=body, content_type=content_type, **kwargs)
    request.session = _mock_session(user_id)
    return request


# ─── StorageView ─────────────────────────────────────────
class TestStorageView:
    def test_api_openInfo_get(self):
        from app.views.StorageView import api_openInfo
        request = _make_request("GET", "/storage/openInfo")
        response = api_openInfo(request)
        data = json.loads(response.content)
        assert data["code"] == 1000

    def test_api_openInfo_post_not_supported(self):
        from app.views.StorageView import api_openInfo
        request = _make_request("POST", "/storage/openInfo", data={})
        response = api_openInfo(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_api_openInfo_no_auth(self):
        from app.views.StorageView import api_openInfo
        request = _make_request("GET", "/storage/openInfo", user_id=None)
        response = api_openInfo(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_api_openDownload_invalid_filename(self):
        from app.views.StorageView import api_openDownload
        request = _make_request("GET", "/storage/openDownload", {"filename": "../etc/passwd"})
        response = api_openDownload(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_api_openDownload_unsupported_extension(self):
        from app.views.StorageView import api_openDownload
        request = _make_request("GET", "/storage/openDownload", {"filename": "test.exe"})
        response = api_openDownload(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_api_openDownload_missing_file(self):
        from app.views.StorageView import api_openDownload
        request = _make_request("GET", "/storage/openDownload", {"filename": "nonexistent.mp4"})
        response = api_openDownload(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_api_openDownload_empty_filename(self):
        from app.views.StorageView import api_openDownload
        request = _make_request("GET", "/storage/openDownload", {"filename": ""})
        response = api_openDownload(request)
        data = json.loads(response.content)
        assert data["code"] == 0


# ─── HealthView ──────────────────────────────────────────
class TestHealthView:
    def test_health_check_healthy(self):
        from app.views.HealthView import health_check
        request = _make_request("GET", "/health", user_id=None)
        with patch("app.views.HealthView.connection") as mock_conn, \
             patch("app.utils.GlobalUtils.g_zlm") as mock_zlm, \
             patch("app.analysis.manager.AnalysisManager") as mock_am:
            mock_conn.cursor.return_value.__enter__ = MagicMock()
            mock_conn.cursor.return_value.__exit__ = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_zlm.getMediaList.return_value = []
            mock_am.return_value.list_running.return_value = []
            response = health_check(request)
            data = json.loads(response.content)
            assert data["status"] == "healthy"
            assert response.status_code == 200

    def test_health_check_db_error(self):
        from app.views.HealthView import health_check
        request = _make_request("GET", "/health", user_id=None)
        with patch("app.views.HealthView.connection") as mock_conn, \
             patch("app.utils.GlobalUtils.g_zlm") as mock_zlm, \
             patch("app.analysis.manager.AnalysisManager") as mock_am:
            mock_conn.cursor.side_effect = Exception("DB error")
            mock_zlm.getMediaList.side_effect = Exception("ZLM error")
            mock_am.side_effect = Exception("AM error")
            response = health_check(request)
            data = json.loads(response.content)
            assert data["status"] == "unhealthy"
            assert response.status_code == 503

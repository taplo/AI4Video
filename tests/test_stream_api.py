"""Tests for StreamView — covers StreamView.py (755 stmts)."""
import json
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from django.test import RequestFactory


def _mock_session(user_id=1):
    """Create a mock session that f_sessionReadUserId can read."""
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
    """Create a request with mock session (no DB needed)."""
    factory = RequestFactory()
    if method == "GET":
        request = factory.get(path, data or {}, **kwargs)
    else:
        content_type = kwargs.pop("content_type", "application/json")
        body = json.dumps(data) if isinstance(data, dict) else data
        request = factory.post(path, data=body, content_type=content_type, **kwargs)
    request.session = _mock_session(user_id)
    return request


class TestStreamIndexPages:
    def test_online_page(self):
        from app.views.StreamView import online
        request = _make_request("GET", "/stream/online", user_id=None)
        request.session = MagicMock()
        request.session.get = MagicMock(return_value=None)
        response = online(request)
        assert response.status_code == 200

    def test_index_page(self):
        from app.views.StreamView import index
        request = _make_request("GET", "/stream/index", user_id=None)
        request.session = MagicMock()
        request.session.get = MagicMock(return_value=None)
        response = index(request)
        assert response.status_code == 200


class TestStreamOpenAddContext:
    def test_get_with_session_auth(self):
        from app.views.StreamView import api_openAddContext
        request = _make_request("GET", "/stream/openAddContext")
        with patch("app.views.StreamView.g_zlm") as mock_zlm:
            mock_zlm.default_stream_app = "live"
            mock_zlm.get_rtspUrl.return_value = "rtsp://test"
            mock_zlm.get_hlsUrl.return_value = "http://test.m3u8"
            mock_zlm.get_httpMp4Url.return_value = "http://test.mp4"
            mock_zlm.get_wsMp4Url.return_value = "ws://test.mp4"
            with patch("app.views.StreamView.StreamModel") as mock_sm:
                mock_sm.objects.filter.return_value.order_by.return_value.values.return_value = []
                response = api_openAddContext(request)
                data = json.loads(response.content)
                assert data["code"] == 1000
                assert "stream" in data

    def test_get_without_auth(self):
        from app.views.StreamView import api_openAddContext
        request = _make_request("GET", "/stream/openAddContext", user_id=None)
        request.session.get = MagicMock(return_value=None)
        response = api_openAddContext(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_post_method_not_supported(self):
        from app.views.StreamView import api_openAddContext
        request = _make_request("POST", "/stream/openAddContext", data={})
        response = api_openAddContext(request)
        data = json.loads(response.content)
        assert data["code"] == 0


class TestStreamOpenAdd:
    def test_post_missing_code(self):
        from app.views.StreamView import api_openAdd
        request = _make_request("POST", "/stream/openAdd", data={
            "nickname": "test", "pull_stream_type": "1",
            "pull_stream_url": "rtsp://test", "pull_stream_port": "554",
        })
        response = api_openAdd(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_post_invalid_type(self):
        from app.views.StreamView import api_openAdd
        request = _make_request("POST", "/stream/openAdd", data={
            "code": "c1", "nickname": "test", "pull_stream_type": "99",
            "pull_stream_url": "rtsp://test", "pull_stream_port": "554",
        })
        response = api_openAdd(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_post_gb28181_type(self):
        from app.views.StreamView import api_openAdd
        request = _make_request("POST", "/stream/openAdd", data={
            "code": "c1", "nickname": "test", "pull_stream_type": "21",
            "pull_stream_url": "", "pull_stream_port": "554",
        })
        response = api_openAdd(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_post_empty_nickname(self):
        from app.views.StreamView import api_openAdd
        request = _make_request("POST", "/stream/openAdd", data={
            "code": "c1", "nickname": "", "pull_stream_type": "1",
            "pull_stream_url": "rtsp://test", "pull_stream_port": "554",
        })
        response = api_openAdd(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_post_missing_url(self):
        from app.views.StreamView import api_openAdd
        request = _make_request("POST", "/stream/openAdd", data={
            "code": "c1", "nickname": "test", "pull_stream_type": "1",
            "pull_stream_url": "", "pull_stream_port": "554",
        })
        response = api_openAdd(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_post_long_nickname(self):
        from app.views.StreamView import api_openAdd
        request = _make_request("POST", "/stream/openAdd", data={
            "code": "c1", "nickname": "x" * 51, "pull_stream_type": "1",
            "pull_stream_url": "rtsp://test", "pull_stream_port": "554",
        })
        response = api_openAdd(request)
        data = json.loads(response.content)
        assert data["code"] == 0


class TestStreamOpenDel:
    def test_post_without_id(self):
        from app.views.StreamView import api_openDel
        request = _make_request("POST", "/stream/openDel", data={})
        response = api_openDel(request)
        data = json.loads(response.content)
        assert data["code"] == 0


class TestStreamOpenIndex:
    def test_get_returns_stream_list(self):
        from app.views.StreamView import api_openIndex
        request = _make_request("GET", "/stream/openIndex", {"p": "1", "ps": "10"})
        with patch("app.views.StreamView.StreamModel") as mock_sm, \
             patch("app.views.StreamView.g_zlm") as mock_zlm, \
             patch("app.views.StreamView.f_dbReadStreamData") as mock_db:
            mock_zlm.getMediaList.return_value = []
            mock_db.return_value = []
            mock_sm.objects.all.return_value.order_by.return_value.values.return_value = []
            response = api_openIndex(request)
            data = json.loads(response.content)
            assert "code" in data
            assert "data" in data

    def test_get_with_search(self):
        from app.views.StreamView import api_openIndex
        request = _make_request("GET", "/stream/openIndex", {"p": "1", "ps": "10", "code": "test"})
        with patch("app.views.StreamView.StreamModel") as mock_sm, \
             patch("app.views.StreamView.g_zlm") as mock_zlm, \
             patch("app.views.StreamView.f_dbReadStreamData") as mock_db:
            mock_zlm.getMediaList.return_value = []
            mock_db.return_value = []
            mock_sm.objects.all.return_value.order_by.return_value.values.return_value = []
            response = api_openIndex(request)
            data = json.loads(response.content)
            assert "code" in data


class TestStreamPlayer:
    def test_player_page(self):
        from app.views.StreamView import player
        request = _make_request("GET", "/stream/player", user_id=None)
        request.session = MagicMock()
        request.session.get = MagicMock(return_value=None)
        response = player(request)
        assert response.status_code == 200

"""Tests for remaining views: ControlView, SmallModelView, InnerlView, NvrView, LLMView, IndexView, SystemView."""
import json
import pytest
from unittest.mock import patch, MagicMock
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


# ─── IndexView ───────────────────────────────────────────
class TestIndexView:
    def test_index(self):
        from app.views.IndexView import index
        request = _make_request("GET", "/", user_id=None)
        request.session = MagicMock()
        request.session.get = MagicMock(return_value=None)
        response = index(request)
        assert response.status_code == 200

    def test_api_openIndex(self):
        from app.views.IndexView import api_openIndex
        request = _make_request("GET", "/index/openIndex")
        with patch("app.views.IndexView.OSSystem") as mock_os:
            mock_os.return_value.getOSInfo.return_value = {}
            response = api_openIndex(request)
            data = json.loads(response.content)
            assert data["code"] == 1000

    def test_api_openIndex_post_not_supported(self):
        from app.views.IndexView import api_openIndex
        request = _make_request("POST", "/index/openIndex", data={})
        response = api_openIndex(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_forbidden(self):
        from app.views.IndexView import forbidden
        request = _make_request("GET", "/forbidden", user_id=None)
        request.session = MagicMock()
        request.session.get = MagicMock(return_value=None)
        response = forbidden(request)
        assert response.status_code == 200


# ─── SystemView ──────────────────────────────────────────
class TestSystemView:
    def test_f_readSettings(self):
        from app.views.SystemView import f_readSettings
        result = f_readSettings("zh")
        assert isinstance(result, dict)

    def test_config_page(self):
        from app.views.SystemView import config
        request = _make_request("GET", "/system/config", user_id=None)
        request.session = MagicMock()
        request.session.get = MagicMock(return_value=None)
        response = config(request)
        assert response.status_code == 200

    def test_api_openConfig(self):
        from app.views.SystemView import api_openConfig
        request = _make_request("GET", "/system/openConfig")
        response = api_openConfig(request)
        data = json.loads(response.content)
        assert data["code"] == 1000

    def test_api_openSaveSettings_post(self):
        from app.views.SystemView import api_openSaveSettings
        request = _make_request("POST", "/system/openSaveSettings", data={"lang": "zh"})
        with patch("app.views.SystemView.f_writeSettings", return_value=True):
            response = api_openSaveSettings(request)
            data = json.loads(response.content)
            assert "code" in data


# ─── LLMView ─────────────────────────────────────────────
class TestLLMView:
    def test_mask_api_key(self):
        from app.views.LLMView import _mask_api_key
        assert _mask_api_key("sk-1234567890") == "****7890"
        assert _mask_api_key("1234") == "****"
        assert _mask_api_key(None) == "****"
        assert _mask_api_key("") == "****"

    def test_index_page(self):
        from app.views.LLMView import index
        request = _make_request("GET", "/llm/index", user_id=None)
        request.session = MagicMock()
        request.session.get = MagicMock(return_value=None)
        with patch("app.views.LLMView.LLMModel") as mock_m:
            mock_m.objects.count.return_value = 0
            response = index(request)
            assert response.status_code == 200

    def test_api_openIndex(self):
        from app.views.LLMView import api_openIndex
        request = _make_request("GET", "/llm/openIndex")
        with patch("app.views.LLMView.LLMModel") as mock_m:
            mock_m.objects.count.return_value = 0
            mock_m.objects.order_by.return_value.values.return_value = []
            response = api_openIndex(request)
            data = json.loads(response.content)
            assert data["code"] == 1000


# ─── SmallModelView ──────────────────────────────────────
class TestSmallModelView:
    def test_algo_to_dict(self):
        from app.views.SmallModelView import _algo_to_dict
        mock_algo = MagicMock()
        mock_algo.labels = '["car","person"]'
        mock_algo.id = 1
        mock_algo.name = "test"
        mock_algo.algorithm_type = "detection"
        mock_algo.task_type = "detect"
        mock_algo.inference_engine = "onnx"
        mock_algo.device = "cpu"
        mock_algo.model_file = "model.onnx"
        mock_algo.model_file_size = 1024
        mock_algo.input_width = 640
        mock_algo.input_height = 640
        mock_algo.conf_threshold = 0.5
        mock_algo.iou_threshold = 0.45
        mock_algo.is_default = False
        mock_algo.state = 1
        mock_algo.create_time = "2026-01-01"
        mock_algo.streams.count.return_value = 0
        d = _algo_to_dict(mock_algo, include_streams=False)
        assert d["name"] == "test"
        assert len(d["labels"]) == 2

    def test_algo_parse_page_params(self):
        from app.views.SmallModelView import _algo_parse_page_params
        factory = RequestFactory()
        request = factory.get("/smallmodel/openIndex", {"p": "2", "ps": "5"})
        p, ps = _algo_parse_page_params(request)
        assert p == 2
        assert ps == 5

    def test_algo_parse_page_params_invalid(self):
        from app.views.SmallModelView import _algo_parse_page_params
        factory = RequestFactory()
        request = factory.get("/smallmodel/openIndex", {"p": "abc", "ps": "200"})
        p, ps = _algo_parse_page_params(request)
        assert p == 1
        assert ps == 100

    def test_smallmodel_index_page(self):
        from app.views.SmallModelView import smallmodel_index
        request = _make_request("GET", "/smallmodel/index", user_id=None)
        request.session = MagicMock()
        request.session.get = MagicMock(return_value=None)
        response = smallmodel_index(request)
        assert response.status_code == 200

    def test_smallmodel_openIndex(self):
        from app.views.SmallModelView import smallmodel_openIndex
        request = _make_request("GET", "/smallmodel/openIndex")
        with patch("app.views.SmallModelView.AlgorithmModel") as mock_m:
            mock_qs = MagicMock()
            mock_qs.count.return_value = 5
            mock_qs.__iter__ = MagicMock(return_value=iter([]))
            mock_qs.__getitem__ = MagicMock(return_value=[])
            mock_m.objects.all.return_value.order_by.return_value = mock_qs
            response = smallmodel_openIndex(request)
            data = json.loads(response.content)
            assert data["code"] == 1000


# ─── NvrView ─────────────────────────────────────────────
class TestNvrView:
    def test_record_index_redirect_without_stream(self):
        from app.views.NvrView import record_index
        request = _make_request("GET", "/record/index", user_id=None)
        request.session = MagicMock()
        request.session.get = MagicMock(return_value=None)
        response = record_index(request)
        assert response.status_code == 302

    def test_record_index_with_stream(self):
        from app.views.NvrView import record_index
        request = _make_request("GET", "/record/index", {"stream_id": "1"}, user_id=None)
        request.session = MagicMock()
        request.session.get = MagicMock(return_value=None)
        with patch("app.models.StreamModel") as mock_sm:
            mock_stream = MagicMock()
            mock_stream.nickname = "test"
            mock_stream.record_enable = 0
            mock_sm.objects.filter.return_value.first.return_value = mock_stream
            with patch("app.recording.manager.get_recording_manager") as mock_rm:
                mock_rm.return_value.is_recording.return_value = False
                response = record_index(request)
                assert response.status_code == 200

    def test_get_stream(self):
        from app.views.NvrView import _get_stream
        with patch("app.models.StreamModel") as mock_sm:
            mock_sm.objects.filter.return_value.first.return_value = MagicMock(id=1)
            result = _get_stream({"stream_id": "1"})
            assert result is not None

    def test_get_stream_missing_id(self):
        from app.views.NvrView import _get_stream
        result = _get_stream({})
        assert result is None


# ─── InnerlView ──────────────────────────────────────────
class TestInnerlView:
    def test_get_code_lock(self):
        from app.views.InnerlView import _get_code_lock
        lock1 = _get_code_lock("code1")
        lock2 = _get_code_lock("code1")
        assert lock1 is lock2
        lock3 = _get_code_lock("code2")
        assert lock1 is not lock3

    def test_on_media_update_stream_post_missing_app(self):
        from app.views.InnerlView import api_on_media_update_stream
        request = _make_request("POST", "/inner/on_media_update_stream", data={})
        response = api_on_media_update_stream(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_on_media_update_stream_post_valid(self):
        from app.views.InnerlView import api_on_media_update_stream
        request = _make_request("POST", "/inner/on_media_update_stream", data={
            "app": "live", "name": "test_stream", "ip": "192.168.1.1",
            "port": "5060", "clientId": "client123", "pullStreamUrl": "rtsp://test",
            "forwardState": "1", "cameraName": "Test Camera",
        })
        with patch("app.views.InnerlView.StreamModel") as mock_sm:
            mock_sm.objects.filter.return_value.first.return_value = None
            mock_sm.objects.create.return_value = MagicMock()
            response = api_on_media_update_stream(request)
            data = json.loads(response.content)
            assert "code" in data

    def test_on_media_delete_stream_post(self):
        from app.views.InnerlView import api_on_media_delete_stream
        request = _make_request("POST", "/inner/on_media_delete_stream", data={
            "app": "live", "name": "test",
        })
        with patch("app.views.InnerlView.StreamModel") as mock_sm:
            mock_sm.objects.filter.return_value.delete.return_value = (1, {})
            response = api_on_media_delete_stream(request)
            data = json.loads(response.content)
            assert "code" in data

    def test_on_publish_post(self):
        from app.views.InnerlView import api_on_publish
        request = _make_request("POST", "/inner/on_publish", data={
            "app": "live", "name": "test", "ip": "127.0.0.1", "port": "1935",
        })
        with patch("app.views.InnerlView.StreamModel") as mock_sm:
            mock_sm.objects.filter.return_value.first.return_value = MagicMock()
            response = api_on_publish(request)
            data = json.loads(response.content)
            assert "code" in data

    def test_on_stream_not_found_post(self):
        from app.views.InnerlView import api_on_stream_not_found
        request = _make_request("POST", "/inner/on_stream_not_found", data={
            "app": "live", "name": "test", "ip": "127.0.0.1", "port": "1935",
        })
        with patch("app.views.InnerlView.StreamModel") as mock_sm:
            mock_sm.objects.filter.return_value.first.return_value = None
            response = api_on_stream_not_found(request)
            data = json.loads(response.content)
            assert "code" in data

"""Tests for ControlView — covers ControlView.py (457 stmts)."""
import json
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
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


class TestParseZoneAlgoIds:
    def test_list_input(self):
        from app.views.ControlView import _parse_zone_algo_ids
        assert _parse_zone_algo_ids([1, 2, 3]) == [1, 2, 3]

    def test_json_string_input(self):
        from app.views.ControlView import _parse_zone_algo_ids
        assert _parse_zone_algo_ids('[1,2,3]') == [1, 2, 3]

    def test_csv_string_input(self):
        from app.views.ControlView import _parse_zone_algo_ids
        assert _parse_zone_algo_ids("1,2,3") == [1, 2, 3]

    def test_empty_input(self):
        from app.views.ControlView import _parse_zone_algo_ids
        assert _parse_zone_algo_ids(None) == []
        assert _parse_zone_algo_ids("") == []
        assert _parse_zone_algo_ids(123) == []

    def test_invalid_json(self):
        from app.views.ControlView import _parse_zone_algo_ids
        with pytest.raises(ValueError):
            _parse_zone_algo_ids("not json")


class TestParseControlDetectRate:
    def test_valid_params(self):
        from app.views.ControlView import _parse_control_detect_rate
        interval, frames = _parse_control_detect_rate({"detect_interval_sec": "2", "detect_frames": "3"})
        assert interval == 2.0
        assert frames == 3

    def test_invalid_params(self):
        from app.views.ControlView import _parse_control_detect_rate
        interval, frames = _parse_control_detect_rate({"detect_interval_sec": "abc", "detect_frames": "xyz"})
        assert interval == 1.0
        assert frames == 1

    def test_boundary_values(self):
        from app.views.ControlView import _parse_control_detect_rate
        interval, frames = _parse_control_detect_rate({"detect_interval_sec": "0", "detect_frames": "0"})
        assert interval == 0.1
        assert frames == 1
        interval, frames = _parse_control_detect_rate({"detect_interval_sec": "99999", "detect_frames": "99999"})
        assert interval == 86400.0
        assert frames == 999


class TestControlToDict:
    def test_basic_conversion(self):
        from app.views.ControlView import _control_to_dict
        mock_zone = MagicMock()
        mock_zone.id = 1
        mock_zone.stream_id = 10
        mock_zone.stream = MagicMock()
        mock_zone.stream.nickname = "cam1"
        mock_zone.name = "zone1"
        mock_zone.coordinates = "[]"
        mock_zone.is_required = 1
        mock_zone.loiter_threshold = 10
        mock_zone.detect_interval_sec = 1
        mock_zone.detect_frames = 1
        mock_zone.color = "#ff0000"
        mock_zone.line_a = ""
        mock_zone.line_b = ""
        mock_zone.density_threshold = 0
        mock_zone.state = 1
        mock_zone.create_time = "2026-01-01"
        mock_zone.algorithms.all.return_value.order_by.return_value = []
        d = _control_to_dict(mock_zone)
        assert d["id"] == 1
        assert d["stream_name"] == "cam1"
        assert d["name"] == "zone1"

    def test_no_stream(self):
        from app.views.ControlView import _control_to_dict
        mock_zone = MagicMock()
        mock_zone.stream = None
        mock_zone.algorithms.all.return_value.order_by.return_value = []
        d = _control_to_dict(mock_zone)
        assert d["stream_name"] == ""


class TestGetSetCachedStatus:
    def test_set_and_get(self):
        from app.views.ControlView import _set_cached_status, _get_cached_status
        _set_cached_status({"test": True}, lite=True)
        result = _get_cached_status(lite=True)
        assert result == {"test": True}

    def test_cache_miss(self):
        from app.views.ControlView import _get_cached_status
        from app.views import ControlView
        ControlView._STATUS_CACHE["lite"]["data"] = None
        result = _get_cached_status(lite=True)
        assert result is None


class TestInvalidateCache:
    def test_invalidate(self):
        from app.views.ControlView import invalidate_analysis_status_cache, _set_cached_status, _get_cached_status
        _set_cached_status({"old": True}, lite=True)
        invalidate_analysis_status_cache()
        result = _get_cached_status(lite=True)
        assert result is None


class TestControlViewFunctions:
    def test_control_index(self):
        from app.views.ControlView import control_index
        request = _make_request("GET", "/control/index", user_id=None)
        request.session = MagicMock()
        request.session.get = MagicMock(return_value=None)
        response = control_index(request)
        assert response.status_code == 200

    def test_control_openIndex(self):
        from app.views.ControlView import control_openIndex
        request = _make_request("GET", "/control/openIndex")
        with patch("app.views.ControlView._control_queryset") as mock_qs:
            mock_qs.return_value = []
            response = control_openIndex(request)
            data = json.loads(response.content)
            assert data["code"] == 1000

    def test_control_openIndex_with_stream_id(self):
        from app.views.ControlView import control_openIndex
        request = _make_request("GET", "/control/openIndex", {"stream_id": "1"})
        with patch("app.views.ControlView._control_queryset") as mock_qs:
            mock_qs.return_value = []
            response = control_openIndex(request)
            data = json.loads(response.content)
            assert data["code"] == 1000

    def test_control_openIndex_post(self):
        from app.views.ControlView import control_openIndex
        request = _make_request("POST", "/control/openIndex", data={})
        response = control_openIndex(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_control_openIndex_no_auth(self):
        from app.views.ControlView import control_openIndex
        request = _make_request("GET", "/control/openIndex", user_id=None)
        response = control_openIndex(request)
        data = json.loads(response.content)
        assert data["code"] == 0

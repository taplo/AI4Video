"""Tests for AnalysisView — covers AnalysisView.py (347 stmts)."""
import json
import os
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


class TestParsePageParams:
    def test_valid_params(self):
        from app.views.AnalysisView import _parse_page_params
        factory = RequestFactory()
        request = factory.get("/test", {"p": "2", "ps": "20"})
        p, ps = _parse_page_params(request)
        assert p == 2
        assert ps == 20

    def test_invalid_params(self):
        from app.views.AnalysisView import _parse_page_params
        factory = RequestFactory()
        request = factory.get("/test", {"p": "abc", "ps": "200"})
        p, ps = _parse_page_params(request)
        assert p == 1
        assert ps == 100

    def test_boundary(self):
        from app.views.AnalysisView import _parse_page_params
        factory = RequestFactory()
        request = factory.get("/test", {"p": "0", "ps": "0"})
        p, ps = _parse_page_params(request)
        assert p == 1
        assert ps == 12


class TestBuildPageData:
    def test_basic(self):
        from app.views.AnalysisView import _build_page_data
        factory = RequestFactory()
        request = factory.get("/test")
        request.session = MagicMock()
        request.session.get = MagicMock(return_value="zh")
        result = _build_page_data(request, 1, 10, 25)
        assert result["page_num"] == 3
        assert result["count"] == 25

    def test_empty(self):
        from app.views.AnalysisView import _build_page_data
        factory = RequestFactory()
        request = factory.get("/test")
        request.session = MagicMock()
        request.session.get = MagicMock(return_value="zh")
        result = _build_page_data(request, 1, 10, 0)
        assert result["page_num"] == 1

    def test_page_exceeds_total(self):
        from app.views.AnalysisView import _build_page_data
        factory = RequestFactory()
        request = factory.get("/test")
        request.session = MagicMock()
        request.session.get = MagicMock(return_value="zh")
        result = _build_page_data(request, 100, 10, 5)
        assert result["page"] == 1


class TestAlarmAbsPath:
    def test_empty(self):
        from app.views.AnalysisView import _alarm_abs_path
        assert _alarm_abs_path("") == ""
        assert _alarm_abs_path(None) == ""

    @patch("django.conf.settings")
    def test_valid_path(self, mock_settings):
        from app.views.AnalysisView import _alarm_abs_path
        mock_settings.BASE_DIR = "/tmp"
        result = _alarm_abs_path("test/snap.jpg")
        assert "test/snap.jpg" in result


class TestDeleteSnapshotFile:
    def test_nonexistent_file(self):
        from app.views.AnalysisView import _delete_snapshot_file
        assert _delete_snapshot_file("nonexistent.jpg") is False

    def test_empty_path(self):
        from app.views.AnalysisView import _delete_snapshot_file
        assert _delete_snapshot_file("") is False


class TestAlarmToDict:
    def test_basic(self):
        from app.views.AnalysisView import _alarm_to_dict
        mock_alarm = MagicMock()
        mock_alarm.id = 1
        mock_alarm.stream_id = 10
        mock_alarm.stream = MagicMock()
        mock_alarm.stream.nickname = "cam1"
        mock_alarm.event_type = "entered_zone"
        mock_alarm.timestamp = "2026-01-01"
        mock_alarm.metadata = '{"biz_algorithm_id": 5, "zone_name": "zone1"}'
        mock_alarm.description = "test"
        d = _alarm_to_dict(mock_alarm)
        assert d["id"] == 1
        assert d["stream_name"] == "cam1"
        assert d["event_type"] == "entered_zone"

    def test_invalid_metadata(self):
        from app.views.AnalysisView import _alarm_to_dict
        mock_alarm = MagicMock()
        mock_alarm.metadata = "not json"
        mock_alarm.stream = None
        mock_alarm.description = ""
        d = _alarm_to_dict(mock_alarm)
        assert d["alarm_reason"] == ""


class TestAlarmOpenIndex:
    def test_get(self):
        from app.views.AnalysisView import alarm_openIndex
        request = _make_request("GET", "/alarm/openIndex")
        with patch("app.views.AnalysisView.AlarmModel") as mock_m:
            mock_m.objects.all.return_value.order_by.return_value.count.return_value = 0
            mock_m.objects.all.return_value.order_by.return_value.__getitem__ = MagicMock(return_value=[])
            response = alarm_openIndex(request)
            data = json.loads(response.content)
            assert data["code"] == 1000

    def test_post_not_supported(self):
        from app.views.AnalysisView import alarm_openIndex
        request = _make_request("POST", "/alarm/openIndex", data={})
        response = alarm_openIndex(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_no_auth(self):
        from app.views.AnalysisView import alarm_openIndex
        request = _make_request("GET", "/alarm/openIndex", user_id=None)
        response = alarm_openIndex(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_with_stream_filter(self):
        from app.views.AnalysisView import alarm_openIndex
        request = _make_request("GET", "/alarm/openIndex", {"stream_id": "1"})
        with patch("app.views.AnalysisView.AlarmModel") as mock_m:
            mock_qs = MagicMock()
            mock_m.objects.all.return_value.order_by.return_value = mock_qs
            mock_qs.filter.return_value.count.return_value = 0
            mock_qs.filter.return_value.__getitem__ = MagicMock(return_value=[])
            response = alarm_openIndex(request)
            data = json.loads(response.content)
            assert data["code"] == 1000


class TestAlarmOpenDel:
    def test_post_valid(self):
        from app.views.AnalysisView import alarm_openDel
        request = _make_request("POST", "/alarm/openDel", data={"id": "1"})
        with patch("app.views.AnalysisView.AlarmModel") as mock_m:
            mock_obj = MagicMock()
            mock_obj.metadata = '{"snapshot_path": ""}'
            mock_m.objects.filter.return_value.first.return_value = mock_obj
            response = alarm_openDel(request)
            data = json.loads(response.content)
            assert data["code"] == 1000

    def test_post_invalid_id(self):
        from app.views.AnalysisView import alarm_openDel
        request = _make_request("POST", "/alarm/openDel", data={"id": "0"})
        response = alarm_openDel(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_post_not_found(self):
        from app.views.AnalysisView import alarm_openDel
        request = _make_request("POST", "/alarm/openDel", data={"id": "999"})
        with patch("app.views.AnalysisView.AlarmModel") as mock_m:
            mock_m.objects.filter.return_value.first.return_value = None
            response = alarm_openDel(request)
            data = json.loads(response.content)
            assert data["code"] == 0


class TestAlarmOpenBatchDel:
    def test_post_valid(self):
        from app.views.AnalysisView import alarm_openBatchDel
        request = _make_request("POST", "/alarm/openBatchDel", data={"ids": "[1,2]"})
        with patch("app.views.AnalysisView.AlarmModel") as mock_m:
            mock_m.objects.filter.return_value.__iter__ = MagicMock(return_value=iter([]))
            mock_m.objects.filter.return_value.delete.return_value = (0, {})
            response = alarm_openBatchDel(request)
            data = json.loads(response.content)
            assert data["code"] == 1000

    def test_post_empty_ids(self):
        from app.views.AnalysisView import alarm_openBatchDel
        request = _make_request("POST", "/alarm/openBatchDel", data={"ids": "[]"})
        response = alarm_openBatchDel(request)
        data = json.loads(response.content)
        assert data["code"] == 0


class TestAlarmOpenClearAlarms:
    def test_post(self):
        from app.views.AnalysisView import alarm_openClearAlarms
        request = _make_request("POST", "/alarm/openClearAlarms")
        with patch("app.views.AnalysisView.AlarmModel") as mock_m:
            mock_m.objects.all.return_value.__iter__ = MagicMock(return_value=iter([]))
            mock_m.objects.all.return_value.delete.return_value = (0, {})
            response = alarm_openClearAlarms(request)
            data = json.loads(response.content)
            assert data["code"] == 1000


class TestAnalysisOpenStatus:
    def test_get(self):
        from app.views.AnalysisView import analysis_openStatus
        request = _make_request("GET", "/analysis/openStatus")
        with patch("app.views.ControlView.build_analysis_status_data") as mock_build:
            mock_build.return_value = {}
            response = analysis_openStatus(request)
            data = json.loads(response.content)
            assert data["code"] == 1000

    def test_post_not_supported(self):
        from app.views.AnalysisView import analysis_openStatus
        request = _make_request("POST", "/analysis/openStatus", data={})
        response = analysis_openStatus(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_no_auth(self):
        from app.views.AnalysisView import analysis_openStatus
        request = _make_request("GET", "/analysis/openStatus", user_id=None)
        response = analysis_openStatus(request)
        data = json.loads(response.content)
        assert data["code"] == 0


class TestAnalysisOpenStart:
    def test_post_invalid_stream(self):
        from app.views.AnalysisView import analysis_openStart
        request = _make_request("POST", "/analysis/openStart", data={"stream_id": "0"})
        response = analysis_openStart(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_post_not_supported(self):
        from app.views.AnalysisView import analysis_openStart
        request = _make_request("GET", "/analysis/openStart")
        response = analysis_openStart(request)
        data = json.loads(response.content)
        assert data["code"] == 0


class TestAnalysisOpenStop:
    def test_post(self):
        from app.views.AnalysisView import analysis_openStop
        request = _make_request("POST", "/analysis/openStop", data={"stream_id": "1"})
        with patch("app.analysis.manager.AnalysisManager") as mock_am:
            mock_am.return_value.stop.return_value = (True, "stopped")
            response = analysis_openStop(request)
            data = json.loads(response.content)
            assert data["code"] == 1000

    def test_post_not_supported(self):
        from app.views.AnalysisView import analysis_openStop
        request = _make_request("GET", "/analysis/openStop")
        response = analysis_openStop(request)
        data = json.loads(response.content)
        assert data["code"] == 0


class TestAnalysisOpenReloadZones:
    def test_post(self):
        from app.views.AnalysisView import analysis_openReloadZones
        request = _make_request("POST", "/analysis/openReloadZones", data={"stream_id": "1"})
        with patch("app.analysis.manager.AnalysisManager") as mock_am:
            mock_am.return_value.reload_zones.return_value = True
            response = analysis_openReloadZones(request)
            data = json.loads(response.content)
            assert data["code"] == 1000

    def test_post_not_supported(self):
        from app.views.AnalysisView import analysis_openReloadZones
        request = _make_request("GET", "/analysis/openReloadZones")
        response = analysis_openReloadZones(request)
        data = json.loads(response.content)
        assert data["code"] == 0


class TestAnalysisOpenUpdateInferenceConfig:
    def test_post_no_params(self):
        from app.views.AnalysisView import analysis_openUpdateInferenceConfig
        request = _make_request("POST", "/analysis/openUpdateInferenceConfig", data={})
        response = analysis_openUpdateInferenceConfig(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_post_with_params(self):
        from app.views.AnalysisView import analysis_openUpdateInferenceConfig
        request = _make_request("POST", "/analysis/openUpdateInferenceConfig", data={"shared": "1", "workers": "2"})
        with patch("app.analysis.manager.AnalysisManager") as mock_am:
            mock_am.return_value.set_inference_config.return_value = (True, "ok")
            response = analysis_openUpdateInferenceConfig(request)
            data = json.loads(response.content)
            assert data["code"] == 1000

    def test_get_not_supported(self):
        from app.views.AnalysisView import analysis_openUpdateInferenceConfig
        request = _make_request("GET", "/analysis/openUpdateInferenceConfig")
        response = analysis_openUpdateInferenceConfig(request)
        data = json.loads(response.content)
        assert data["code"] == 0


class TestAnalysisOpenToggleAlgoInstance:
    def test_post_invalid(self):
        from app.views.AnalysisView import analysis_openToggleAlgoInstance
        request = _make_request("POST", "/analysis/openToggleAlgoInstance", data={"algorithm_id": "0"})
        response = analysis_openToggleAlgoInstance(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_post_valid(self):
        from app.views.AnalysisView import analysis_openToggleAlgoInstance
        request = _make_request("POST", "/analysis/openToggleAlgoInstance", data={"algorithm_id": "1", "enabled": "1"})
        with patch("app.analysis.manager.AnalysisManager") as mock_am:
            mock_am.return_value.set_algo_instance_enabled.return_value = (True, "ok")
            response = analysis_openToggleAlgoInstance(request)
            data = json.loads(response.content)
            assert data["code"] == 1000


class TestAnalysisOpenRestartAlgoInstance:
    def test_post_invalid(self):
        from app.views.AnalysisView import analysis_openRestartAlgoInstance
        request = _make_request("POST", "/analysis/openRestartAlgoInstance", data={"algorithm_id": "0"})
        response = analysis_openRestartAlgoInstance(request)
        data = json.loads(response.content)
        assert data["code"] == 0

    def test_post_valid(self):
        from app.views.AnalysisView import analysis_openRestartAlgoInstance
        request = _make_request("POST", "/analysis/openRestartAlgoInstance", data={"algorithm_id": "1"})
        with patch("app.analysis.manager.AnalysisManager") as mock_am:
            mock_am.return_value.restart_algo_instance.return_value = (True, "ok")
            response = analysis_openRestartAlgoInstance(request)
            data = json.loads(response.content)
            assert data["code"] == 1000


class TestAnalysisOpenRestartInferencePool:
    def test_post(self):
        from app.views.AnalysisView import analysis_openRestartInferencePool
        request = _make_request("POST", "/analysis/openRestartInferencePool")
        with patch("app.analysis.manager.AnalysisManager") as mock_am:
            mock_am.return_value.restart_inference_pool.return_value = (True, "ok")
            response = analysis_openRestartInferencePool(request)
            data = json.loads(response.content)
            assert data["code"] == 1000

    def test_get_not_supported(self):
        from app.views.AnalysisView import analysis_openRestartInferencePool
        request = _make_request("GET", "/analysis/openRestartInferencePool")
        response = analysis_openRestartInferencePool(request)
        data = json.loads(response.content)
        assert data["code"] == 0

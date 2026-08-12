"""Tests for AlgorithmView — covers AlgorithmView.py (561 stmts)."""
import json
import pytest
from unittest.mock import MagicMock, patch
from django.test import RequestFactory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _make_biz_mock(**overrides):
    biz = MagicMock()
    biz.id = overrides.get("id", 1)
    biz.name = overrides.get("name", "test_algo")
    biz.flow_type = overrides.get("flow_type", 1)
    biz.small_model_id = overrides.get("small_model_id", 10)
    biz.detector_model_id = overrides.get("detector_model_id", 0)
    biz.target_labels = overrides.get("target_labels", '["person"]')
    biz.llm_id = overrides.get("llm_id", 0)
    biz.llm_prompt = overrides.get("llm_prompt", "")
    biz.llm_validate = overrides.get("llm_validate", "")
    biz.post_process = overrides.get("post_process", "AREA")
    biz.ref_angle = overrides.get("ref_angle", 90.0)
    biz.angle_tolerance = overrides.get("angle_tolerance", 45.0)
    biz.forward_count_threshold = overrides.get("forward_count_threshold", 0)
    biz.reverse_count_threshold = overrides.get("reverse_count_threshold", 0)
    biz.state = overrides.get("state", 1)
    biz.create_time = overrides.get("create_time", "2026-01-01 00:00:00")

    biz.small_model = overrides.get("small_model", MagicMock(name="small_model"))
    if biz.small_model:
        biz.small_model.name = "yolov8n"
        biz.small_model.model_file = "yolov8n.pt"
        biz.small_model.inference_engine = "onnx"

    biz.detector_model = overrides.get("detector_model", None)
    if biz.detector_model:
        biz.detector_model.name = "yolov8_det"
        biz.detector_model.model_file = "yolov8_det.pt"
        biz.detector_model.inference_engine = "onnx"

    biz.llm = overrides.get("llm", None)
    if biz.llm:
        biz.llm.name = "gpt4"
        biz.llm.model_name = "gpt-4"

    biz.zones = MagicMock()
    biz.zones.count.return_value = overrides.get("zone_count", 0)
    return biz


PATCH = "app.views.AlgorithmView"


# ===========================================================================
# Pure-logic tests (no model mocking)
# ===========================================================================

class TestParseLabels:
    def test_list_input(self):
        from app.views.AlgorithmView import _parse_labels
        result = _parse_labels(["person", "car"])
        assert result == ["person", "car"]

    def test_empty_list(self):
        from app.views.AlgorithmView import _parse_labels
        assert _parse_labels([]) == []

    def test_list_with_blanks(self):
        from app.views.AlgorithmView import _parse_labels
        result = _parse_labels(["person", "", "  ", "car"])
        assert result == ["person", "car"]

    def test_list_with_ints(self):
        from app.views.AlgorithmView import _parse_labels
        result = _parse_labels([1, 2, 3])
        assert result == ["1", "2", "3"]

    def test_json_string(self):
        from app.views.AlgorithmView import _parse_labels
        result = _parse_labels('["person", "car"]')
        assert result == ["person", "car"]

    def test_json_string_nested(self):
        from app.views.AlgorithmView import _parse_labels
        result = _parse_labels('[  "a" , "b" ]')
        assert result == ["a", "b"]

    def test_comma_separated(self):
        from app.views.AlgorithmView import _parse_labels
        result = _parse_labels("person,car,bike")
        assert result == ["person", "car", "bike"]

    def test_comma_separated_with_spaces(self):
        from app.views.AlgorithmView import _parse_labels
        result = _parse_labels(" person , car ")
        assert result == ["person", "car"]

    def test_comma_separated_with_blanks(self):
        from app.views.AlgorithmView import _parse_labels
        result = _parse_labels("person,,  ,car")
        assert result == ["person", "car"]

    def test_invalid_json_falls_to_comma(self):
        from app.views.AlgorithmView import _parse_labels
        result = _parse_labels("not json")
        assert result == ["not json"]

    def test_none_returns_empty(self):
        from app.views.AlgorithmView import _parse_labels
        assert _parse_labels(None) == []

    def test_empty_string(self):
        from app.views.AlgorithmView import _parse_labels
        assert _parse_labels("") == []

    def test_integer_input(self):
        from app.views.AlgorithmView import _parse_labels
        assert _parse_labels(42) == []


class TestCheckModelFileExists:
    @patch(f"{PATCH}._resolve_model_abs_path")
    def test_exists(self, mock_resolve):
        from app.views.AlgorithmView import _check_model_file_exists
        mock_resolve.return_value = "/abs/path/model.pt"
        assert _check_model_file_exists("model.pt") is True

    @patch(f"{PATCH}._resolve_model_abs_path")
    def test_not_exists(self, mock_resolve):
        from app.views.AlgorithmView import _check_model_file_exists
        mock_resolve.return_value = ""
        assert _check_model_file_exists("missing.pt") is False

    @patch(f"{PATCH}._resolve_model_abs_path")
    def test_empty(self, mock_resolve):
        from app.views.AlgorithmView import _check_model_file_exists
        mock_resolve.return_value = ""
        assert _check_model_file_exists("") is False


class TestResolveModelAbsPath:
    def test_empty_input(self):
        from app.views.AlgorithmView import _resolve_model_abs_path
        assert _resolve_model_abs_path("") == ""
        assert _resolve_model_abs_path(None) == ""

    @patch("app.analysis.worker_pool.resolve_model_path")
    @patch("os.path.exists", return_value=True)
    def test_valid_path(self, mock_exists, mock_resolve):
        from app.views.AlgorithmView import _resolve_model_abs_path
        mock_resolve.return_value = "/abs/model.pt"
        result = _resolve_model_abs_path("model.pt")
        assert result == "/abs/model.pt"

    @patch("app.analysis.worker_pool.resolve_model_path")
    @patch("os.path.exists", return_value=False)
    def test_path_not_exists(self, mock_exists, mock_resolve):
        from app.views.AlgorithmView import _resolve_model_abs_path
        mock_resolve.return_value = "/abs/model.pt"
        result = _resolve_model_abs_path("model.pt")
        assert result == ""

    @patch("app.analysis.worker_pool.resolve_model_path", side_effect=Exception("err"))
    def test_resolve_raises(self, mock_resolve):
        from app.views.AlgorithmView import _resolve_model_abs_path
        assert _resolve_model_abs_path("model.pt") == ""


class TestBizToDict:
    def test_basic_with_small_model(self):
        from app.views.AlgorithmView import _biz_to_dict
        biz = _make_biz_mock()
        with patch(f"{PATCH}._check_model_file_exists", return_value=True), \
             patch(f"{PATCH}._resolve_model_abs_path", return_value="/abs/yolov8n.pt"):
            d = _biz_to_dict(biz)
        assert d["id"] == 1
        assert d["name"] == "test_algo"
        assert d["flow_type"] == 1
        assert d["small_model_name"] == "yolov8n"
        assert d["small_model_file"] == "yolov8n.pt"
        assert d["small_model_file_exists"] is True
        assert d["small_model_file_path"] == "/abs/yolov8n.pt"
        assert d["small_model_engine"] == "onnx"
        assert d["target_labels"] == ["person"]
        assert d["zone_count"] == 0
        assert d["flow_type_name"] == "小模型+后处理"
        assert d["post_process_name"] == "区域入侵"

    def test_no_small_model(self):
        from app.views.AlgorithmView import _biz_to_dict
        biz = _make_biz_mock(small_model_id=0, small_model=None)
        d = _biz_to_dict(biz)
        assert d["small_model_name"] == ""
        assert d["small_model_file"] == ""
        assert d["small_model_file_exists"] is False
        assert d["small_model_file_path"] == ""

    def test_with_detector_model(self):
        from app.views.AlgorithmView import _biz_to_dict
        det = MagicMock()
        det.name = "yolo_det"
        det.model_file = "det.pt"
        det.inference_engine = "onnx"
        biz = MagicMock()
        biz.id = 1
        biz.name = "test_algo"
        biz.flow_type = 1
        biz.small_model_id = 10
        biz.small_model = MagicMock()
        biz.small_model.name = "yolov8n"
        biz.small_model.model_file = "yolov8n.pt"
        biz.small_model.inference_engine = "onnx"
        biz.detector_model_id = 20
        biz.detector_model = det
        biz.target_labels = '["person"]'
        biz.llm_id = 0
        biz.llm = None
        biz.llm_prompt = ""
        biz.llm_validate = ""
        biz.post_process = "AREA"
        biz.ref_angle = 90.0
        biz.angle_tolerance = 45.0
        biz.forward_count_threshold = 0
        biz.reverse_count_threshold = 0
        biz.state = 1
        biz.create_time = "2026-01-01"
        biz.zones = MagicMock()
        biz.zones.count.return_value = 0
        with patch(f"{PATCH}._check_model_file_exists", return_value=True):
            d = _biz_to_dict(biz)
        assert d["detector_model_name"] == "yolo_det"
        assert d["detector_model_file"] == "det.pt"
        assert d["detector_model_file_exists"] is True

    def test_no_detector_model(self):
        from app.views.AlgorithmView import _biz_to_dict
        biz = _make_biz_mock(detector_model_id=0, detector_model=None)
        d = _biz_to_dict(biz)
        assert d["detector_model_name"] == ""
        assert d["detector_model_file"] == ""
        assert d["detector_model_file_exists"] is False

    def test_with_llm(self):
        from app.views.AlgorithmView import _biz_to_dict
        llm = MagicMock()
        llm.name = "gpt4"
        llm.model_name = "gpt-4"
        biz = _make_biz_mock(llm_id=30, llm=llm)
        d = _biz_to_dict(biz)
        assert d["llm_name"] == "gpt4"

    def test_no_llm(self):
        from app.views.AlgorithmView import _biz_to_dict
        biz = _make_biz_mock(llm_id=0, llm=None)
        d = _biz_to_dict(biz)
        assert d["llm_name"] == ""

    def test_flow_type_llm(self):
        from app.views.AlgorithmView import _biz_to_dict
        biz = _make_biz_mock(flow_type=2)
        d = _biz_to_dict(biz)
        assert d["flow_type_name"] == "大模型+后处理"

    def test_flow_type_both(self):
        from app.views.AlgorithmView import _biz_to_dict
        biz = _make_biz_mock(flow_type=3)
        d = _biz_to_dict(biz)
        assert d["flow_type_name"] == "小模型+大模型+后处理"

    def test_flow_type_detect_reid(self):
        from app.views.AlgorithmView import _biz_to_dict
        biz = _make_biz_mock(flow_type=4)
        d = _biz_to_dict(biz)
        assert d["flow_type_name"] == "检测+ReID+后处理"

    def test_post_process_line_cross(self):
        from app.views.AlgorithmView import _biz_to_dict
        biz = _make_biz_mock(post_process="LINE_CROSS")
        d = _biz_to_dict(biz)
        assert d["post_process_name"] == "越线检测"

    def test_post_process_line_count(self):
        from app.views.AlgorithmView import _biz_to_dict
        biz = _make_biz_mock(post_process="LINE_COUNT")
        d = _biz_to_dict(biz)
        assert d["post_process_name"] == "越线计数"

    def test_post_process_direction(self):
        from app.views.AlgorithmView import _biz_to_dict
        biz = _make_biz_mock(post_process="DIRECTION")
        d = _biz_to_dict(biz)
        assert d["post_process_name"] == "方向入侵"

    def test_post_process_density(self):
        from app.views.AlgorithmView import _biz_to_dict
        biz = _make_biz_mock(post_process="DENSITY")
        d = _biz_to_dict(biz)
        assert d["post_process_name"] == "密度报警"

    def test_post_process_dwell(self):
        from app.views.AlgorithmView import _biz_to_dict
        biz = _make_biz_mock(post_process="DWELL")
        d = _biz_to_dict(biz)
        assert d["post_process_name"] == "滞留报警"

    def test_target_labels_empty_string(self):
        from app.views.AlgorithmView import _biz_to_dict
        biz = _make_biz_mock(target_labels="")
        d = _biz_to_dict(biz)
        assert d["target_labels"] == []

    def test_zone_count(self):
        from app.views.AlgorithmView import _biz_to_dict
        biz = _make_biz_mock()
        biz.zones.count.return_value = 5
        d = _biz_to_dict(biz)
        assert d["zone_count"] == 5


class TestValidateBizFields:
    def _run(self, params, biz_id=0):
        from app.views.AlgorithmView import _validate_biz_fields
        return _validate_biz_fields(params, biz_id=biz_id)

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="算法名称不能为空"):
            self._run({"name": ""})

    def test_whitespace_name_raises(self):
        with pytest.raises(ValueError, match="算法名称不能为空"):
            self._run({"name": "   "})

    def test_invalid_flow_type_defaults_to_1(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_sm = MagicMock()
            mock_sm.task_type = "detect"
            mock_am.objects.filter.return_value.first.return_value = mock_sm
            result = self._run({
                "name": "test",
                "flow_type": "abc",
                "small_model_id": "10",
                "target_labels": '["person"]',
            })
            assert result["flow_type"] == 1

    def test_invalid_flow_type_value_raises(self):
        with pytest.raises(ValueError, match="无效的流程类型"):
            self._run({"name": "test", "flow_type": 99})

    def test_flow_small_no_model_raises(self):
        with pytest.raises(ValueError, match="请选择小模型"):
            self._run({"name": "test", "flow_type": 1, "small_model_id": "0"})

    def test_flow_small_model_not_found(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_am.objects.filter.return_value.first.return_value = None
            with pytest.raises(ValueError, match="小模型不存在或已禁用"):
                self._run({"name": "test", "flow_type": 1, "small_model_id": "10"})

    def test_flow_small_reid_model_raises(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_sm = MagicMock()
            mock_sm.task_type = "reid"
            mock_am.objects.filter.return_value.first.return_value = mock_sm
            with pytest.raises(ValueError, match="ReID 模型请使用"):
                self._run({"name": "test", "flow_type": 1, "small_model_id": "10",
                           "target_labels": '["person"]'})

    def test_flow_small_no_labels_raises(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_sm = MagicMock()
            mock_sm.task_type = "detect"
            mock_am.objects.filter.return_value.first.return_value = mock_sm
            with pytest.raises(ValueError, match="请至少选择一个检测目标"):
                self._run({"name": "test", "flow_type": 1, "small_model_id": "10",
                           "target_labels": "[]"})

    def test_flow_small_valid(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_sm = MagicMock()
            mock_sm.task_type = "detect"
            mock_am.objects.filter.return_value.first.return_value = mock_sm
            result = self._run({
                "name": "test", "flow_type": 1, "small_model_id": "10",
                "target_labels": '["person"]',
            })
            assert result["name"] == "test"
            assert result["flow_type"] == 1
            assert result["small_model_id"] == 10

    def test_flow_llm_no_llm_raises(self):
        with patch(f"{PATCH}.LLMModel") as mock_llm:
            mock_llm.objects.filter.return_value.exists.return_value = False
            with pytest.raises(ValueError, match="请选择大模型"):
                self._run({"name": "test", "flow_type": 2, "llm_id": "0"})

    def test_flow_llm_no_prompt_raises(self):
        with patch(f"{PATCH}.LLMModel") as mock_llm:
            mock_llm.objects.filter.return_value.exists.return_value = True
            with pytest.raises(ValueError, match="请输入大模型提示词"):
                self._run({"name": "test", "flow_type": 2, "llm_id": "5",
                           "llm_prompt": ""})

    def test_flow_llm_no_validate_raises(self):
        with patch(f"{PATCH}.LLMModel") as mock_llm:
            mock_llm.objects.filter.return_value.exists.return_value = True
            with pytest.raises(ValueError, match="请输入提示词校验值"):
                self._run({"name": "test", "flow_type": 2, "llm_id": "5",
                           "llm_prompt": "prompt", "llm_validate": ""})

    def test_flow_llm_valid(self):
        with patch(f"{PATCH}.LLMModel") as mock_llm:
            mock_llm.objects.filter.return_value.exists.return_value = True
            result = self._run({
                "name": "test", "flow_type": 2, "llm_id": "5",
                "llm_prompt": "prompt", "llm_validate": "validate",
            })
            assert result["llm_id"] == 5
            assert result["llm_prompt"] == "prompt"

    def test_flow_both_valid(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am, \
             patch(f"{PATCH}.LLMModel") as mock_llm:
            mock_sm = MagicMock()
            mock_sm.task_type = "detect"
            mock_am.objects.filter.return_value.first.return_value = mock_sm
            mock_llm.objects.filter.return_value.exists.return_value = True
            result = self._run({
                "name": "test", "flow_type": 3, "small_model_id": "10",
                "target_labels": '["person"]',
                "llm_id": "5", "llm_prompt": "p", "llm_validate": "v",
            })
            assert result["flow_type"] == 3

    def test_detect_reid_no_detector_raises(self):
        with pytest.raises(ValueError, match="请选择检测小模型"):
            self._run({
                "name": "test", "flow_type": 4,
                "detector_model_id": "0", "small_model_id": "10",
            })

    def test_detect_reid_no_reid_raises(self):
        with pytest.raises(ValueError, match="请选择 ReID 小模型"):
            self._run({
                "name": "test", "flow_type": 4,
                "detector_model_id": "20", "small_model_id": "0",
            })

    def test_detect_reid_same_model_raises(self):
        with pytest.raises(ValueError, match="检测小模型与 ReID 小模型不能相同"):
            self._run({
                "name": "test", "flow_type": 4,
                "detector_model_id": "10", "small_model_id": "10",
            })

    def test_detect_reid_detector_not_found(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_am.objects.filter.return_value.first.return_value = None
            with pytest.raises(ValueError, match="检测小模型不存在或已禁用"):
                self._run({
                    "name": "test", "flow_type": 4,
                    "detector_model_id": "20", "small_model_id": "10",
                })

    def test_detect_reid_detector_wrong_task_type(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_det = MagicMock()
            mock_det.task_type = "reid"
            mock_am.objects.filter.return_value.first.return_value = mock_det
            with pytest.raises(ValueError, match="检测小模型必须是 YOLO"):
                self._run({
                    "name": "test", "flow_type": 4,
                    "detector_model_id": "20", "small_model_id": "10",
                })

    def test_detect_reid_reid_not_found(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            call_count = [0]
            def filter_side_effect(*args, **kwargs):
                mock_qs = MagicMock()
                call_count[0] += 1
                if call_count[0] == 1:
                    mock_det = MagicMock()
                    mock_det.task_type = "detect"
                    mock_qs.first.return_value = mock_det
                else:
                    mock_qs.first.return_value = None
                return mock_qs
            mock_am.objects.filter.side_effect = filter_side_effect
            with pytest.raises(ValueError, match="ReID 小模型不存在或已禁用"):
                self._run({
                    "name": "test", "flow_type": 4,
                    "detector_model_id": "20", "small_model_id": "10",
                })

    def test_detect_reid_reid_wrong_task_type(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            call_count = [0]
            def filter_side_effect(*args, **kwargs):
                mock_qs = MagicMock()
                call_count[0] += 1
                if call_count[0] == 1:
                    mock_det = MagicMock()
                    mock_det.task_type = "detect"
                    mock_qs.first.return_value = mock_det
                else:
                    mock_reid = MagicMock()
                    mock_reid.task_type = "detect"
                    mock_qs.first.return_value = mock_reid
                return mock_qs
            mock_am.objects.filter.side_effect = filter_side_effect
            with pytest.raises(ValueError, match="ReID 小模型必须是 OSNet"):
                self._run({
                    "name": "test", "flow_type": 4,
                    "detector_model_id": "20", "small_model_id": "10",
                })

    def test_detect_reid_no_labels(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_det = MagicMock()
            mock_det.task_type = "detect"
            mock_reid = MagicMock()
            mock_reid.task_type = "reid"
            mock_am.objects.filter.return_value.first.side_effect = [mock_det, mock_reid]
            with pytest.raises(ValueError, match="请至少选择一个检测目标"):
                self._run({
                    "name": "test", "flow_type": 4,
                    "detector_model_id": "20", "small_model_id": "10",
                    "target_labels": "[]",
                })

    def test_detect_reid_invalid_labels(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_det = MagicMock()
            mock_det.task_type = "detect"
            mock_det.labels = '["person"]'
            mock_reid = MagicMock()
            mock_reid.task_type = "reid"
            mock_am.objects.filter.return_value.first.side_effect = [mock_det, mock_reid]
            with pytest.raises(ValueError, match="检测目标不在检测小模型标签列表中"):
                self._run({
                    "name": "test", "flow_type": 4,
                    "detector_model_id": "20", "small_model_id": "10",
                    "target_labels": '["car"]',
                })

    def test_detect_reid_valid(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_det = MagicMock()
            mock_det.task_type = "detect"
            mock_det.labels = '["person","car"]'
            mock_reid = MagicMock()
            mock_reid.task_type = "reid"
            mock_am.objects.filter.return_value.first.side_effect = [mock_det, mock_reid]
            result = self._run({
                "name": "test", "flow_type": 4,
                "detector_model_id": "20", "small_model_id": "10",
                "target_labels": '["person"]',
            })
            assert result["flow_type"] == 4
            assert result["detector_model_id"] == 20
            assert result["small_model_id"] == 10

    def test_invalid_post_process_raises(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_sm = MagicMock()
            mock_sm.task_type = "detect"
            mock_am.objects.filter.return_value.first.return_value = mock_sm
            with pytest.raises(ValueError, match="无效的后处理逻辑"):
                self._run({"name": "test", "flow_type": 1, "small_model_id": "10",
                           "target_labels": '["person"]', "post_process": "INVALID"})

    def test_line_count_no_threshold_raises(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_sm = MagicMock()
            mock_sm.task_type = "detect"
            mock_am.objects.filter.return_value.first.return_value = mock_sm
            with pytest.raises(ValueError, match="越线计数至少设置一个方向的报警阈值"):
                self._run({
                    "name": "test", "flow_type": 1, "small_model_id": "10",
                    "target_labels": '["person"]', "post_process": "LINE_COUNT",
                    "forward_count_threshold": "0", "reverse_count_threshold": "0",
                })

    def test_line_count_valid(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_sm = MagicMock()
            mock_sm.task_type = "detect"
            mock_am.objects.filter.return_value.first.return_value = mock_sm
            result = self._run({
                "name": "test", "flow_type": 1, "small_model_id": "10",
                "target_labels": '["person"]', "post_process": "LINE_COUNT",
                "forward_count_threshold": "5", "reverse_count_threshold": "0",
            })
            assert result["forward_count_threshold"] == 5

    def test_direction_params(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_sm = MagicMock()
            mock_sm.task_type = "detect"
            mock_am.objects.filter.return_value.first.return_value = mock_sm
            result = self._run({
                "name": "test", "flow_type": 1, "small_model_id": "10",
                "target_labels": '["person"]', "post_process": "DIRECTION",
                "ref_angle": "180.0", "angle_tolerance": "30.0",
            })
            assert result["ref_angle"] == 180.0
            assert result["angle_tolerance"] == 30.0

    def test_negative_thresholds_clamped(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_sm = MagicMock()
            mock_sm.task_type = "detect"
            mock_am.objects.filter.return_value.first.return_value = mock_sm
            result = self._run({
                "name": "test", "flow_type": 1, "small_model_id": "10",
                "target_labels": '["person"]',
                "forward_count_threshold": "-5", "reverse_count_threshold": "-3",
            })
            assert result["forward_count_threshold"] == 0
            assert result["reverse_count_threshold"] == 0

    def test_target_labels_returned_as_json(self):
        with patch(f"{PATCH}.AlgorithmModel") as mock_am:
            mock_sm = MagicMock()
            mock_sm.task_type = "detect"
            mock_am.objects.filter.return_value.first.return_value = mock_sm
            result = self._run({
                "name": "test", "flow_type": 1, "small_model_id": "10",
                "target_labels": '["person","car"]',
            })
            parsed = json.loads(result["target_labels"])
            assert parsed == ["person", "car"]


# ===========================================================================
# View tests — mock models and utilities
# ===========================================================================

def _json_response(res):
    """Fake f_responseJson: return a mock whose .content is JSON."""
    return MagicMock(
        content=json.dumps(res, default=str).encode(),
        status_code=200,
    )


class TestAlgorithmIndex:
    @patch(f"{PATCH}.render", return_value=MagicMock(status_code=200))
    def test_get(self, mock_render):
        from app.views.AlgorithmView import algorithm_index
        request = _make_request("GET", "/algorithm/index")
        response = algorithm_index(request)
        assert response.status_code == 200
        mock_render.assert_called_once()


class TestAlgorithmOpenIndex:
    def test_get(self):
        from app.views.AlgorithmView import algorithm_openIndex
        request = _make_request("GET", "/algorithm/openIndex")
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_m, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            mock_m.objects.select_related.return_value.order_by.return_value = []
            response = algorithm_openIndex(request)
            data = json.loads(response.content)
            assert data["code"] == 1000
            assert data["data"] == []

    def test_post_not_supported(self):
        from app.views.AlgorithmView import algorithm_openIndex
        request = _make_request("POST", "/algorithm/openIndex", data={})
        with patch(f"{PATCH}.LANG_VIEWS_T", return_value="not supported"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            response = algorithm_openIndex(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_no_auth(self):
        from app.views.AlgorithmView import algorithm_openIndex
        request = _make_request("GET", "/algorithm/openIndex", user_id=None)
        with patch(f"{PATCH}.f_checkRequestSafe", return_value=(False, "auth error")), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="auth error"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            response = algorithm_openIndex(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_with_state_filter(self):
        from app.views.AlgorithmView import algorithm_openIndex
        request = _make_request("GET", "/algorithm/openIndex", {"state": "1"})
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_m, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            mock_qs = mock_m.objects.select_related.return_value.order_by.return_value
            mock_qs.filter.return_value = []
            response = algorithm_openIndex(request)
            data = json.loads(response.content)
            assert data["code"] == 1000

    def test_with_flow_type_filter(self):
        from app.views.AlgorithmView import algorithm_openIndex
        request = _make_request("GET", "/algorithm/openIndex", {"flow_type": "2"})
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_m, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            mock_qs = mock_m.objects.select_related.return_value.order_by.return_value
            mock_qs.filter.return_value = []
            response = algorithm_openIndex(request)
            data = json.loads(response.content)
            assert data["code"] == 1000


class TestAlgorithmOpenCheckModels:
    def test_get(self):
        from app.views.AlgorithmView import algorithm_openCheckModels
        request = _make_request("GET", "/algorithm/openCheckModels")
        with patch(f"{PATCH}.AlgorithmModel") as mock_am, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response), \
             patch(f"{PATCH}._check_model_file_exists", return_value=False):
            mock_am.objects.filter.return_value.order_by.return_value = []
            response = algorithm_openCheckModels(request)
            data = json.loads(response.content)
            assert data["code"] == 1000
            assert data["data"]["total"] == 0

    def test_get_with_models(self):
        from app.views.AlgorithmView import algorithm_openCheckModels
        request = _make_request("GET", "/algorithm/openCheckModels")
        mock_algo = MagicMock()
        mock_algo.id = 1
        mock_algo.name = "yolo"
        mock_algo.model_file = "yolo.pt"
        mock_algo.inference_engine = "onnx"
        with patch(f"{PATCH}.AlgorithmModel") as mock_am, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response), \
             patch(f"{PATCH}._check_model_file_exists", return_value=True):
            mock_am.objects.filter.return_value.order_by.return_value = [mock_algo]
            response = algorithm_openCheckModels(request)
            data = json.loads(response.content)
            assert data["code"] == 1000
            assert data["data"]["total"] == 1
            assert data["data"]["ok_count"] == 1
            assert len(data["data"]["ok_list"]) == 1

    def test_post_not_supported(self):
        from app.views.AlgorithmView import algorithm_openCheckModels
        request = _make_request("POST", "/algorithm/openCheckModels", data={})
        with patch(f"{PATCH}.LANG_VIEWS_T", return_value="not supported"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            response = algorithm_openCheckModels(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_no_auth(self):
        from app.views.AlgorithmView import algorithm_openCheckModels
        request = _make_request("GET", "/algorithm/openCheckModels", user_id=None)
        with patch(f"{PATCH}.f_checkRequestSafe", return_value=(False, "auth error")), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="auth error"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            response = algorithm_openCheckModels(request)
            data = json.loads(response.content)
            assert data["code"] == 0


class TestAlgorithmOpenOptions:
    def test_get(self):
        from app.views.AlgorithmView import algorithm_openOptions
        request = _make_request("GET", "/algorithm/openOptions")
        mock_algo = MagicMock()
        mock_algo.id = 1
        mock_algo.name = "yolo"
        mock_algo.labels = '["person"]'
        mock_algo.algorithm_type = "detection"
        mock_algo.task_type = "detect"
        mock_algo.model_file = "yolo.pt"
        mock_algo.inference_engine = "onnx"
        mock_llm = MagicMock()
        mock_llm.id = 1
        mock_llm.name = "gpt4"
        mock_llm.model_name = "gpt-4"
        with patch(f"{PATCH}.AlgorithmModel") as mock_am, \
             patch(f"{PATCH}.LLMModel") as mock_lm, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response), \
             patch(f"{PATCH}._check_model_file_exists", return_value=True):
            mock_am.objects.filter.return_value.order_by.return_value = [mock_algo]
            mock_lm.objects.filter.return_value.order_by.return_value = [mock_llm]
            response = algorithm_openOptions(request)
            data = json.loads(response.content)
            assert data["code"] == 1000
            assert len(data["data"]["small_models"]) == 1
            assert data["data"]["small_models"][0]["name"] == "yolo"
            assert len(data["data"]["llms"]) == 1
            assert len(data["data"]["post_processes"]) == 6
            assert len(data["data"]["flow_types"]) == 4

    def test_post_not_supported(self):
        from app.views.AlgorithmView import algorithm_openOptions
        request = _make_request("POST", "/algorithm/openOptions", data={})
        with patch(f"{PATCH}.LANG_VIEWS_T", return_value="not supported"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            response = algorithm_openOptions(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_no_auth(self):
        from app.views.AlgorithmView import algorithm_openOptions
        request = _make_request("GET", "/algorithm/openOptions", user_id=None)
        with patch(f"{PATCH}.f_checkRequestSafe", return_value=(False, "auth error")), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="auth error"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            response = algorithm_openOptions(request)
            data = json.loads(response.content)
            assert data["code"] == 0


class TestAlgorithmOpenAdd:
    def _patch_biz_consts(self, mock_bam):
        mock_bam.POST_AREA = "AREA"
        mock_bam.POST_LINE_CROSS = "LINE_CROSS"
        mock_bam.POST_LINE_COUNT = "LINE_COUNT"
        mock_bam.POST_DIRECTION = "DIRECTION"
        mock_bam.POST_DENSITY = "DENSITY"
        mock_bam.POST_DWELL = "DWELL"

    def test_post_valid(self):
        from app.views.AlgorithmView import algorithm_openAdd
        request = _make_request("POST", "/algorithm/openAdd", data={"name": "test"})
        mock_sm = MagicMock()
        mock_sm.task_type = "detect"
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_bam, \
             patch(f"{PATCH}.AlgorithmModel") as mock_am, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.f_parsePostParams", return_value={
                 "name": "test", "flow_type": "1", "small_model_id": "10",
                 "target_labels": '["person"]',
             }), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            self._patch_biz_consts(mock_bam)
            mock_am.objects.filter.return_value.first.return_value = mock_sm
            response = algorithm_openAdd(request)
            data = json.loads(response.content)
            assert data["code"] == 1000
            mock_bam.objects.create.assert_called_once()

    def test_post_invalid(self):
        from app.views.AlgorithmView import algorithm_openAdd
        request = _make_request("POST", "/algorithm/openAdd", data={"name": ""})
        with patch(f"{PATCH}.AlgorithmModel") as mock_am, \
             patch(f"{PATCH}.BizAlgorithmModel") as mock_bam, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.f_parsePostParams", return_value={"name": ""}), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            self._patch_biz_consts(mock_bam)
            response = algorithm_openAdd(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_get_not_supported(self):
        from app.views.AlgorithmView import algorithm_openAdd
        request = _make_request("GET", "/algorithm/openAdd")
        with patch(f"{PATCH}.LANG_VIEWS_T", return_value="not supported"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            response = algorithm_openAdd(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_no_auth(self):
        from app.views.AlgorithmView import algorithm_openAdd
        request = _make_request("POST", "/algorithm/openAdd", data={"name": "test"}, user_id=None)
        with patch(f"{PATCH}.f_checkRequestSafe", return_value=(False, "auth error")), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="auth error"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            response = algorithm_openAdd(request)
            data = json.loads(response.content)
            assert data["code"] == 0


class TestAlgorithmOpenEdit:
    def test_post_valid(self):
        from app.views.AlgorithmView import algorithm_openEdit
        request = _make_request("POST", "/algorithm/openEdit", data={"id": "1"})
        mock_biz = MagicMock()
        mock_biz.zones = MagicMock()
        mock_biz.zones.select_related.return_value.all.return_value = []
        mock_sm = MagicMock()
        mock_sm.task_type = "detect"
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_bam, \
             patch(f"{PATCH}.AlgorithmModel") as mock_am, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.f_parsePostParams", return_value={
                 "id": "1", "name": "updated", "flow_type": "1",
                 "small_model_id": "10", "target_labels": '["person"]',
             }), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response), \
             patch(f"{PATCH}._reload_affected_pipelines"):
            mock_bam.POST_AREA = "AREA"
            mock_bam.POST_LINE_CROSS = "LINE_CROSS"
            mock_bam.POST_LINE_COUNT = "LINE_COUNT"
            mock_bam.POST_DIRECTION = "DIRECTION"
            mock_bam.POST_DENSITY = "DENSITY"
            mock_bam.POST_DWELL = "DWELL"
            mock_bam.objects.get.return_value = mock_biz
            mock_am.objects.filter.return_value.first.return_value = mock_sm
            response = algorithm_openEdit(request)
            data = json.loads(response.content)
            assert data["code"] == 1000
            mock_biz.save.assert_called_once()

    def test_post_not_found(self):
        from app.views.AlgorithmView import algorithm_openEdit
        request = _make_request("POST", "/algorithm/openEdit", data={"id": "999"})
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_bam, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.f_parsePostParams", return_value={"id": "999"}), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            mock_bam.objects.get.side_effect = Exception("not found")
            response = algorithm_openEdit(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_get_not_supported(self):
        from app.views.AlgorithmView import algorithm_openEdit
        request = _make_request("GET", "/algorithm/openEdit")
        with patch(f"{PATCH}.LANG_VIEWS_T", return_value="not supported"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            response = algorithm_openEdit(request)
            data = json.loads(response.content)
            assert data["code"] == 0


class TestAlgorithmOpenDel:
    def test_post_valid(self):
        from app.views.AlgorithmView import algorithm_openDel
        request = _make_request("POST", "/algorithm/openDel", data={"id": "1"})
        mock_biz = MagicMock()
        mock_biz.zones = MagicMock()
        mock_biz.zones.select_related.return_value.order_by.return_value = []
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_bam, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.f_parsePostParams", return_value={"id": "1"}), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            mock_bam.objects.get.return_value = mock_biz
            response = algorithm_openDel(request)
            data = json.loads(response.content)
            assert data["code"] == 1000
            mock_biz.delete.assert_called_once()

    def test_post_referenced_zones(self):
        from app.views.AlgorithmView import algorithm_openDel
        request = _make_request("POST", "/algorithm/openDel", data={"id": "1"})
        mock_stream = MagicMock()
        mock_stream.nickname = "cam1"
        mock_zone = MagicMock()
        mock_zone.name = "zone1"
        mock_zone.stream = mock_stream
        mock_zone.stream_id = 10
        mock_biz = MagicMock()
        mock_biz.zones = MagicMock()
        mock_biz.zones.select_related.return_value.order_by.return_value = [mock_zone]
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_bam, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.f_parsePostParams", return_value={"id": "1"}), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            mock_bam.objects.get.return_value = mock_biz
            response = algorithm_openDel(request)
            data = json.loads(response.content)
            assert data["code"] == 0
            assert len(data["data"]["referenced_zones"]) == 1

    def test_post_not_found(self):
        from app.views.AlgorithmView import algorithm_openDel
        request = _make_request("POST", "/algorithm/openDel", data={"id": "999"})
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_bam, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.f_parsePostParams", return_value={"id": "999"}), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            mock_bam.objects.get.side_effect = Exception("not found")
            response = algorithm_openDel(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_get_not_supported(self):
        from app.views.AlgorithmView import algorithm_openDel
        request = _make_request("GET", "/algorithm/openDel")
        with patch(f"{PATCH}.LANG_VIEWS_T", return_value="not supported"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            response = algorithm_openDel(request)
            data = json.loads(response.content)
            assert data["code"] == 0


class TestAlgorithmOpenAssignContext:
    def test_get(self):
        from app.views.AlgorithmView import algorithm_openAssignContext
        request = _make_request("GET", "/algorithm/openAssignContext",
                               {"biz_algorithm_id": "1"})
        mock_biz = _make_biz_mock()
        mock_zone = MagicMock()
        mock_zone.id = 1
        mock_zone.stream_id = 10
        mock_zone.stream = MagicMock()
        mock_zone.stream.nickname = "cam1"
        mock_zone.name = "zone1"
        mock_zone.state = 1
        mock_zone_algos = MagicMock()
        mock_zone_algos.filter.return_value.exists.return_value = True
        mock_zone.algorithms = mock_zone_algos
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_bam, \
             patch(f"{PATCH}.ZoneModel") as mock_zm, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.f_parseGetParams", return_value={"biz_algorithm_id": "1"}), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            mock_bam.objects.get.return_value = mock_biz
            mock_zm.objects.select_related.return_value.order_by.return_value = [mock_zone]
            response = algorithm_openAssignContext(request)
            data = json.loads(response.content)
            assert data["code"] == 1000
            assert len(data["data"]["zones"]) == 1
            assert data["data"]["zones"][0]["selected"] is True

    def test_get_not_found(self):
        from app.views.AlgorithmView import algorithm_openAssignContext
        request = _make_request("GET", "/algorithm/openAssignContext",
                               {"biz_algorithm_id": "999"})
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_bam, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.f_parseGetParams", return_value={"biz_algorithm_id": "999"}), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            mock_bam.objects.get.side_effect = Exception("not found")
            response = algorithm_openAssignContext(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_post_not_supported(self):
        from app.views.AlgorithmView import algorithm_openAssignContext
        request = _make_request("POST", "/algorithm/openAssignContext", data={})
        with patch(f"{PATCH}.LANG_VIEWS_T", return_value="not supported"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            response = algorithm_openAssignContext(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_no_auth(self):
        from app.views.AlgorithmView import algorithm_openAssignContext
        request = _make_request("GET", "/algorithm/openAssignContext",
                               {"biz_algorithm_id": "1"}, user_id=None)
        with patch(f"{PATCH}.f_checkRequestSafe", return_value=(False, "auth error")), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="auth error"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            response = algorithm_openAssignContext(request)
            data = json.loads(response.content)
            assert data["code"] == 0


class TestAlgorithmOpenAssignZones:
    def test_post_valid(self):
        from app.views.AlgorithmView import algorithm_openAssignZones
        request = _make_request("POST", "/algorithm/openAssignZones",
                               data={"biz_algorithm_id": "1", "zone_ids": "[1,2]"})
        mock_biz = MagicMock()
        mock_biz.id = 1
        mock_zone1 = MagicMock()
        mock_zone1.id = 1
        mock_zone1.stream_id = 10
        mock_zone1.algorithms = MagicMock()
        mock_zone1.algorithms.filter.return_value.exists.return_value = False
        mock_zone1.algorithms.count.return_value = 2
        mock_zone2 = MagicMock()
        mock_zone2.id = 2
        mock_zone2.stream_id = 10
        mock_zone2.algorithms = MagicMock()
        mock_zone2.algorithms.filter.return_value.exists.return_value = False
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_bam, \
             patch(f"{PATCH}.ZoneModel") as mock_zm, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.f_parsePostParams", return_value={
                 "biz_algorithm_id": "1", "zone_ids": [1, 2],
             }), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            mock_bam.objects.get.return_value = mock_biz
            mock_zm.objects.filter.return_value.prefetch_related.return_value = []
            response = algorithm_openAssignZones(request)
            data = json.loads(response.content)
            assert data["code"] == 1000

    def test_post_blocked_zone(self):
        from app.views.AlgorithmView import algorithm_openAssignZones
        request = _make_request("POST", "/algorithm/openAssignZones",
                               data={"biz_algorithm_id": "1", "zone_ids": "[]"})
        mock_biz = MagicMock()
        mock_biz.id = 1
        mock_zone = MagicMock()
        mock_zone.id = 1
        mock_zone.name = "zone1"
        mock_zone.algorithms = MagicMock()
        mock_zone.algorithms.count.return_value = 1  # only this algo
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_bam, \
             patch(f"{PATCH}.ZoneModel") as mock_zm, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.f_parsePostParams", return_value={
                 "biz_algorithm_id": "1", "zone_ids": [],
             }), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            mock_bam.objects.get.return_value = mock_biz
            mock_zm.objects.filter.return_value.prefetch_related.return_value = [mock_zone]
            response = algorithm_openAssignZones(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_post_not_found(self):
        from app.views.AlgorithmView import algorithm_openAssignZones
        request = _make_request("POST", "/algorithm/openAssignZones",
                               data={"biz_algorithm_id": "999", "zone_ids": "[]"})
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_bam, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.f_parsePostParams", return_value={
                 "biz_algorithm_id": "999", "zone_ids": [],
             }), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            mock_bam.objects.get.side_effect = Exception("not found")
            response = algorithm_openAssignZones(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_get_not_supported(self):
        from app.views.AlgorithmView import algorithm_openAssignZones
        request = _make_request("GET", "/algorithm/openAssignZones")
        with patch(f"{PATCH}.LANG_VIEWS_T", return_value="not supported"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            response = algorithm_openAssignZones(request)
            data = json.loads(response.content)
            assert data["code"] == 0

    def test_zone_ids_as_json_string(self):
        from app.views.AlgorithmView import algorithm_openAssignZones
        request = _make_request("POST", "/algorithm/openAssignZones",
                               data={"biz_algorithm_id": "1",
                                     "zone_ids": "[3,4]"})
        mock_biz = MagicMock()
        mock_biz.id = 1
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_bam, \
             patch(f"{PATCH}.ZoneModel") as mock_zm, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.f_parsePostParams", return_value={
                 "biz_algorithm_id": "1", "zone_ids": "[3,4]",
             }), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            mock_bam.objects.get.return_value = mock_biz
            mock_zm.objects.filter.return_value.prefetch_related.return_value = []
            response = algorithm_openAssignZones(request)
            data = json.loads(response.content)
            assert data["code"] == 1000

    def test_zone_ids_as_comma_string(self):
        from app.views.AlgorithmView import algorithm_openAssignZones
        request = _make_request("POST", "/algorithm/openAssignZones",
                               data={"biz_algorithm_id": "1",
                                     "zone_ids": "5,6"})
        mock_biz = MagicMock()
        mock_biz.id = 1
        with patch(f"{PATCH}.BizAlgorithmModel") as mock_bam, \
             patch(f"{PATCH}.ZoneModel") as mock_zm, \
             patch(f"{PATCH}.f_checkRequestSafe", return_value=(True, "ok")), \
             patch(f"{PATCH}.f_parsePostParams", return_value={
                 "biz_algorithm_id": "1", "zone_ids": "5,6",
             }), \
             patch(f"{PATCH}.LANG_VIEWS_T", return_value="ok"), \
             patch(f"{PATCH}.f_responseJson", side_effect=_json_response):
            mock_bam.objects.get.return_value = mock_biz
            mock_zm.objects.filter.return_value.prefetch_related.return_value = []
            response = algorithm_openAssignZones(request)
            data = json.loads(response.content)
            assert data["code"] == 1000


class TestReloadAffectedPipelines:
    def test_reload_running(self):
        from app.views.AlgorithmView import _reload_affected_pipelines
        mock_biz = MagicMock()
        mock_zone = MagicMock()
        mock_zone.stream_id = 10
        mock_biz.zones.select_related.return_value.all.return_value = [mock_zone]
        with patch("app.analysis.manager.AnalysisManager") as mock_am:
            mock_mgr = MagicMock()
            mock_am.return_value = mock_mgr
            mock_mgr.is_running.return_value = True
            _reload_affected_pipelines(mock_biz)
            mock_mgr.reload_zones.assert_called_once_with(10)

    def test_reload_not_running(self):
        from app.views.AlgorithmView import _reload_affected_pipelines
        mock_biz = MagicMock()
        mock_zone = MagicMock()
        mock_zone.stream_id = 10
        mock_biz.zones.select_related.return_value.all.return_value = [mock_zone]
        with patch("app.analysis.manager.AnalysisManager") as mock_am:
            mock_mgr = MagicMock()
            mock_am.return_value = mock_mgr
            mock_mgr.is_running.return_value = False
            _reload_affected_pipelines(mock_biz)
            mock_mgr.reload_zones.assert_not_called()

    def test_reload_exception_swallows(self):
        from app.views.AlgorithmView import _reload_affected_pipelines
        mock_biz = MagicMock()
        mock_biz.zones.select_related.return_value.all.side_effect = Exception("err")
        # Should not raise
        _reload_affected_pipelines(mock_biz)

    def test_reload_multiple_streams(self):
        from app.views.AlgorithmView import _reload_affected_pipelines
        mock_biz = MagicMock()
        z1 = MagicMock()
        z1.stream_id = 10
        z2 = MagicMock()
        z2.stream_id = 20
        z3 = MagicMock()
        z3.stream_id = 10  # duplicate
        mock_biz.zones.select_related.return_value.all.return_value = [z1, z2, z3]
        with patch("app.analysis.manager.AnalysisManager") as mock_am:
            mock_mgr = MagicMock()
            mock_am.return_value = mock_mgr
            mock_mgr.is_running.return_value = True
            _reload_affected_pipelines(mock_biz)
            assert mock_mgr.reload_zones.call_count == 2

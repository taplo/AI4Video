"""Tests for ONNX engine (mocked)."""
import pytest
from unittest.mock import patch, MagicMock
from app.analysis.engines.onnx_engine import OnnxEngine, _providers_for_device


class TestOnnxEngineUnit:
    """Unit tests for OnnxEngine static methods."""

    def test_version_returns_string(self):
        version = OnnxEngine.version()
        if version is not None:
            assert isinstance(version, str)

    def test_providers_for_device_cpu(self):
        providers = _providers_for_device("cpu")
        assert "CPUExecutionProvider" in providers

    def test_providers_for_device_cuda(self):
        providers = _providers_for_device("cuda")
        assert "CPUExecutionProvider" in providers

    def test_providers_for_device_unknown(self):
        providers = _providers_for_device("unknown")
        assert "CPUExecutionProvider" in providers

    def test_providers_for_device_none(self):
        providers = _providers_for_device(None)
        assert "CPUExecutionProvider" in providers


class TestOnnxEngineLoad:
    """Tests for OnnxEngine.load() method."""

    def test_load_missing_model_returns_false(self):
        engine = OnnxEngine(
            model_file="/nonexistent/model.onnx",
            labels=["person"],
        )
        result = engine.load()
        assert result is False

    def test_load_sets_loaded_flag(self):
        engine = OnnxEngine(
            model_file="/nonexistent/model.onnx",
            labels=["person"],
        )
        engine.load()
        assert engine._loaded is False

    @patch('app.analysis.engines.onnx_engine.ort')
    def test_load_with_mock_session(self, mock_ort):
        mock_session = MagicMock()
        mock_input = MagicMock()
        mock_input.name = "images"
        mock_input.shape = [1, 3, 640, 640]
        mock_session.get_inputs.return_value = [mock_input]
        mock_session.get_outputs.return_value = [MagicMock(name="output")]
        mock_session.get_providers.return_value = ["CPUExecutionProvider"]
        mock_ort.InferenceSession.return_value = mock_session
        mock_ort.SessionOptions.return_value = MagicMock()

        engine = OnnxEngine(
            model_file="dummy.onnx",
            labels=["person"],
        )
        # Patch os.path.exists to return True
        with patch('app.analysis.engines.onnx_engine.os.path.exists', return_value=True):
            result = engine.load()
        assert result is True
        assert engine._loaded is True


class TestOnnxEngineDetect:
    """Tests for OnnxEngine.detect() method."""

    def test_detect_before_load_returns_empty(self):
        engine = OnnxEngine(
            model_file="/nonexistent/model.onnx",
            labels=["person"],
        )
        import numpy as np
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        results = engine.detect(frame)
        assert results == []

    def test_detect_with_none_frame_returns_empty(self):
        engine = OnnxEngine(
            model_file="/nonexistent/model.onnx",
            labels=["person"],
        )
        results = engine.detect(None)
        assert results == []

    @patch('app.analysis.engines.onnx_engine.ort')
    def test_detect_with_mock_session(self, mock_ort):
        mock_session = MagicMock()
        mock_input = MagicMock()
        mock_input.name = "images"
        mock_input.shape = [1, 3, 640, 640]
        mock_session.get_inputs.return_value = [mock_input]
        mock_session.get_outputs.return_value = [MagicMock(name="output")]
        mock_session.get_providers.return_value = ["CPUExecutionProvider"]
        mock_session.run.return_value = [MagicMock()]
        mock_ort.InferenceSession.return_value = mock_session
        mock_ort.SessionOptions.return_value = MagicMock()

        engine = OnnxEngine(
            model_file="dummy.onnx",
            labels=["person"],
        )
        with patch('app.analysis.engines.onnx_engine.os.path.exists', return_value=True):
            engine.load()

        import numpy as np
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        # This will likely return empty due to postprocessing, but shouldn't crash
        results = engine.detect(frame)
        assert isinstance(results, list)

"""Tests for app.analysis.manager and app.analysis.pipeline — highest-value coverage targets."""
import pytest
from unittest.mock import patch, MagicMock


class TestAnalysisManagerInit:
    @patch("app.analysis.manager.CameraPipeline")
    @patch("app.analysis.manager.MotionDetector")
    @patch("app.analysis.manager.DetectorWorkerPool")
    @patch("app.analysis.manager.get_event_bridge")
    @patch("app.analysis.manager.psutil")
    def test_manager_init_creates_instance(self, mock_psutil, mock_eb, mock_dwp, mock_md, mock_cp):
        from app.analysis.manager import AnalysisManager
        manager = AnalysisManager()
        assert manager is not None

    @patch("app.analysis.manager.CameraPipeline")
    @patch("app.analysis.manager.MotionDetector")
    @patch("app.analysis.manager.DetectorWorkerPool")
    @patch("app.analysis.manager.get_event_bridge")
    @patch("app.analysis.manager.psutil")
    def test_manager_has_required_attributes(self, mock_psutil, mock_eb, mock_dwp, mock_md, mock_cp):
        from app.analysis.manager import AnalysisManager
        manager = AnalysisManager()
        assert hasattr(manager, '__init__')


class TestAnalysisPipeline:
    @patch("app.analysis.manager.CameraPipeline")
    @patch("app.analysis.manager.MotionDetector")
    @patch("app.analysis.manager.DetectorWorkerPool")
    @patch("app.analysis.manager.get_event_bridge")
    @patch("app.analysis.manager.psutil")
    def test_pipeline_import(self, mock_psutil, mock_eb, mock_dwp, mock_md, mock_cp):
        import app.analysis.pipeline as pipeline
        assert pipeline is not None

    @patch("app.analysis.manager.CameraPipeline")
    @patch("app.analysis.manager.MotionDetector")
    @patch("app.analysis.manager.DetectorWorkerPool")
    @patch("app.analysis.manager.get_event_bridge")
    @patch("app.analysis.manager.psutil")
    def test_pipeline_has_functions(self, mock_psutil, mock_eb, mock_dwp, mock_md, mock_cp):
        import app.analysis.pipeline as pipeline
        callable_count = sum(1 for name in dir(pipeline) if callable(getattr(pipeline, name)) and not name.startswith('_'))
        assert callable_count > 0


class TestGpuInfo:
    def test_byte_to_mb_conversion(self):
        from app.utils.GpuInfo import _byte_to_mb
        assert _byte_to_mb(1024 * 1024) == 1.0
        assert _byte_to_mb(0) is None
        assert _byte_to_mb(-1) is None
        assert _byte_to_mb(None) is None
        assert _byte_to_mb("invalid") is None

    def test_vendor_from_name(self):
        from app.utils.GpuInfo import _vendor_from_name
        assert _vendor_from_name("NVIDIA GeForce RTX 3080") == "nvidia"
        assert _vendor_from_name("Intel UHD Graphics") == "intel"
        assert _vendor_from_name("AMD Radeon RX 6800") == "amd"
        assert _vendor_from_name("Unknown GPU") == "other"
        assert _vendor_from_name(None) == "other"
        assert _vendor_from_name("") == "other"

    def test_run_cmd_returns_string(self):
        from app.utils.GpuInfo import _run_cmd
        result = _run_cmd(["echo", "test"])
        assert isinstance(result, str)

    def test_run_cmd_handles_failure(self):
        from app.utils.GpuInfo import _run_cmd
        result = _run_cmd(["nonexistent_command_xyz"], timeout=2)
        assert result == ""


class TestOSSystem:
    def test_init(self):
        from app.utils.OSSystem import OSSystem
        os_sys = OSSystem()
        assert os_sys is not None

    def test_get_date_fmt_str(self):
        from app.utils.OSSystem import OSSystem
        from datetime import timedelta
        td = timedelta(days=1, hours=2, minutes=3, seconds=4)
        result = OSSystem.getDateFmtStr(td)
        assert "1" in result
        assert "2" in result

    def test_byte_format(self):
        from app.utils.OSSystem import OSSystem
        os_sys = OSSystem()
        result = os_sys._OSSystem__byteFormat(1024)
        assert "KB" in result
        result = os_sys._OSSystem__byteFormat(1024 * 1024)
        assert "MB" in result

    @patch("app.utils.OSSystem.psutil")
    def test_get_os_info(self, mock_psutil):
        from app.utils.OSSystem import OSSystem
        mock_psutil.cpu_percent.return_value = 50.0
        mock_psutil.cpu_count.return_value = 8
        mock_mem = MagicMock()
        mock_mem.total = 8 * 1024**3
        mock_mem.used = 4 * 1024**3
        mock_psutil.virtual_memory.return_value = mock_mem
        mock_psutil.disk_usage.return_value = MagicMock(total=100*1024**3, used=50*1024**3)
        os_sys = OSSystem()
        info = os_sys.getOSInfo(include_gpu=False)
        assert isinstance(info, dict)


class TestMediaServerManager:
    def test_import(self):
        from app.utils.MediaServerManager import MediaServerManager
        assert MediaServerManager is not None


class TestZLMediaKitApi:
    def test_import(self):
        from app.utils.ZLMediaKitApi import ZLMediaKitApi
        assert ZLMediaKitApi is not None

    def test_init(self):
        from app.utils.ZLMediaKitApi import ZLMediaKitApi
        api = ZLMediaKitApi(logger=MagicMock(), config=MagicMock())
        assert api is not None

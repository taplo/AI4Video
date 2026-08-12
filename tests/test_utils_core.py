"""Tests for core utilities: GlobalUtils, Utils, LanguageUtils, MediaServerManager, etc."""
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestGlobalUtils:
    def test_import(self):
        from app.utils import GlobalUtils
        assert GlobalUtils is not None

    def test_global_utils_class_exists(self):
        from app.utils.GlobalUtils import GlobalUtils
        assert hasattr(GlobalUtils, '__init__')

    def test_filepath_settings_json(self):
        from app.utils.GlobalUtils import g_filepath_settings_json
        assert g_filepath_settings_json is not None
        assert isinstance(g_filepath_settings_json, str)


class TestUtils:
    def test_import(self):
        from app.utils import Utils
        assert Utils is not None

    def test_buildPageLabels_empty(self):
        from app.utils.Utils import buildPageLabels
        labels = buildPageLabels(page=1, page_num=0, lang="zh")
        assert isinstance(labels, list)

    def test_buildPageLabels_single_page(self):
        from app.utils.Utils import buildPageLabels
        labels = buildPageLabels(page=1, page_num=1, lang="zh")
        assert isinstance(labels, list)

    def test_buildPageLabels_multi_page(self):
        from app.utils.Utils import buildPageLabels
        labels = buildPageLabels(page=2, page_num=5, lang="zh")
        assert isinstance(labels, list)
        assert len(labels) > 0

    def test_group_by_field(self):
        from app.utils.Utils import group_by_field
        items = [{"type": "a", "name": "1"}, {"type": "b", "name": "2"}, {"type": "a", "name": "3"}]
        groups = group_by_field(items, "type")
        assert isinstance(groups, (dict, list))

    def test_gb28181_code_utils(self):
        from app.utils.Utils import GB28181CodeUtils
        utils = GB28181CodeUtils()
        code = utils.generate_by_time()
        assert isinstance(code, str)
        assert len(code) > 0


class TestLanguageUtils:
    def test_import(self):
        from app.utils import LanguageUtils
        assert LanguageUtils is not None

    def test_lang_views_t(self):
        from app.utils.LanguageUtils import LANG_VIEWS_T
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get("/test")
        request.session = {}
        result = LANG_VIEWS_T(request, "msg_success")
        assert isinstance(result, str)

    def test_settings_lang_default(self):
        from app.utils.LanguageUtils import GSettingsLangDefault
        assert GSettingsLangDefault is not None


class TestLLMUtils:
    def test_import(self):
        from app.utils import LLMUtils
        assert LLMUtils is not None

    def test_llm_utils_class(self):
        from app.utils.LLMUtils import LLMUtils
        assert hasattr(LLMUtils, '__init__')


class TestUploadUtils:
    def test_import(self):
        from app.utils import UploadUtils
        assert UploadUtils is not None


class TestLogUtils:
    def test_import(self):
        from app.utils import LogUtils
        assert LogUtils is not None


class TestMediaServerManager:
    def test_import(self):
        from app.utils import MediaServerManager
        assert MediaServerManager is not None

    def test_manager_class(self):
        from app.utils.MediaServerManager import MediaServerManager
        assert hasattr(MediaServerManager, '__init__')


class TestZLMediaKitApi:
    def test_import(self):
        from app.utils import ZLMediaKitApi
        assert ZLMediaKitApi is not None

    def test_init(self):
        from app.utils.ZLMediaKitApi import ZLMediaKitApi
        api = ZLMediaKitApi(logger=MagicMock(), config=MagicMock())
        assert api is not None


class TestGpuInfo:
    def test_byte_to_mb_edge_cases(self):
        from app.utils.GpuInfo import _byte_to_mb
        assert _byte_to_mb(0) is None
        assert _byte_to_mb(-100) is None
        assert _byte_to_mb(None) is None
        assert _byte_to_mb("abc") is None
        assert _byte_to_mb(1024 * 1024) == 1.0

    def test_vendor_from_name_edge_cases(self):
        from app.utils.GpuInfo import _vendor_from_name
        assert _vendor_from_name("") == "other"
        assert _vendor_from_name(None) == "other"
        assert _vendor_from_name("NVIDIA") == "nvidia"
        assert _vendor_from_name("Intel HD") == "intel"
        assert _vendor_from_name("AMD") == "amd"
        assert _vendor_from_name("GeForce RTX 4090") == "nvidia"
        assert _vendor_from_name("Radeon RX 7900") == "amd"
        assert _vendor_from_name("Iris Xe") == "intel"

    def test_run_cmd_empty(self):
        from app.utils.GpuInfo import _run_cmd
        result = _run_cmd([], timeout=1)
        assert result == ""

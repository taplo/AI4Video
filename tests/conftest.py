"""Shared pytest fixtures for AI4Video tests."""
import json
import os
import pytest
from unittest.mock import MagicMock

# Ensure tests run in DEBUG mode so DEBUG-only features (e.g. the OpenAPI
# schema served at /api/schema/) are exercised by default.
os.environ.setdefault('DEBUG', 'true')


@pytest.fixture(autouse=True)
def _set_django_settings(monkeypatch):
    """Ensure test-safe Django settings."""
    monkeypatch.setenv('DJANGO_SECRET_KEY', 'test-secret')
    monkeypatch.setenv('DEBUG', 'true')


@pytest.fixture
def config_data():
    """Minimal valid config.json data."""
    return {
        "safe": "test-safe-key",
        "host": "127.0.0.1",
        "adminPort": 10001,
        "mediaHttpPort": 10002,
        "mediaRtspPort": 10003,
        "mediaRtmpPort": 10004,
        "logDebug": 0,
        "isEnableLoginCaptcha": 0,
        "autoAddStreamProxy": 1,
        "isEnableMediaProxyRtmp": 0,
        "recordingEnabled": 0,
        "mediaStartPath": "",
        "mediaStartConfigPath": "",
        "mediaSecret": "",
        "sipServer": {
            "sipServerIp": "127.0.0.1",
            "sipServerPort": 5060,
            "sipServerId": "41010200002000000001",
            "sipServerRealm": "4101020000",
            "sipServerPass": "12345678",
            "sipServerTimeout": 30,
            "sipServerExpiry": 3600,
            "sipTransferMode": 0,
            "rtpTransferMode": 0,
            "rtpTransferAudioType": 0,
            "autoInviteAfterRecCateLog": 0
        }
    }


@pytest.fixture
def config_file(tmp_path, config_data):
    """Write a temporary config.json and return its path."""
    p = tmp_path / "config.json"
    p.write_text(json.dumps(config_data))
    return str(p)


@pytest.fixture
def mock_g_config(monkeypatch):
    """Replace g_config global with a controllable mock."""
    mock = MagicMock()
    mock.safe = "test-safe-key"
    mock.externalHost = "127.0.0.1"
    mock.adminPort = 10001
    mock.logDebug = 0
    mock.isEnableLoginCaptcha = False
    mock.autoAddStreamProxy = True
    mock.isEnableMediaProxyRtmp = False
    mock.recordingEnabled = False
    mock.sipServer = {}
    monkeypatch.setattr("app.utils.GlobalUtils.g_config", mock)
    return mock


@pytest.fixture
def mock_g_zlm(monkeypatch):
    """Replace g_zlm global with a controllable mock."""
    mock = MagicMock()
    mock.addStreamProxy.return_value = (True, "success")
    mock.delStreamProxy.return_value = (True, "success")
    mock.getMediaList.return_value = []
    mock.get_media_list.return_value = []
    mock.close_streams.return_value = (True, "success")
    monkeypatch.setattr("app.utils.GlobalUtils.g_zlm", mock)
    return mock


@pytest.fixture
def mock_g_logger(monkeypatch):
    """Replace g_logger global with a controllable mock."""
    mock = MagicMock()
    monkeypatch.setattr("app.utils.GlobalUtils.g_logger", mock)
    return mock

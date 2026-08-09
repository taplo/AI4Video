"""Tests for app.utils.Config module."""
import json
import os
import pytest
from app.utils.Config import _bool, _int, _float, _resolve_path, Config


class TestBoolHelper:
    """Unit tests for _bool() helper."""

    def test_none_returns_default_false(self):
        assert _bool(None) is False

    def test_none_returns_custom_default(self):
        assert _bool(None, True) is True

    def test_bool_passthrough_true(self):
        assert _bool(True) is True

    def test_bool_passthrough_false(self):
        assert _bool(False) is False

    def test_int_zero_false(self):
        assert _bool(0) is False

    def test_int_nonzero_true(self):
        assert _bool(1) is True
        assert _bool(42) is True

    def test_float_zero_false(self):
        assert _bool(0.0) is False

    def test_float_nonzero_true(self):
        assert _bool(1.5) is True

    def test_string_true_values(self):
        for val in ("true", "1", "yes", "on", "True", "YES", "ON"):
            assert _bool(val) is True, f"_bool({val!r}) should be True"

    def test_string_false_values(self):
        for val in ("false", "0", "no", "off", "False", "NO", "OFF"):
            assert _bool(val) is False, f"_bool({val!r}) should be False"

    def test_whitespace_handling(self):
        assert _bool("  true  ") is True
        assert _bool("  false  ") is False

    def test_empty_string_false(self):
        assert _bool("") is False


class TestIntHelper:
    """Unit tests for _int() helper."""

    def test_valid_int(self):
        assert _int(42) == 42

    def test_string_int(self):
        assert _int("123") == 123

    def test_none_returns_default(self):
        assert _int(None) == 0
        assert _int(None, 5) == 5

    def test_invalid_string_returns_default(self):
        assert _int("abc") == 0
        assert _int("abc", 7) == 7

    def test_float_truncated(self):
        assert _int(3.9) == 3

    def test_negative_int(self):
        assert _int("-10") == -10


class TestFloatHelper:
    """Unit tests for _float() helper."""

    def test_valid_float(self):
        assert _float(3.14) == pytest.approx(3.14)

    def test_int_to_float(self):
        assert _float(5) == 5.0

    def test_none_returns_default(self):
        assert _float(None) == 0.0
        assert _float(None, 1.5) == 1.5

    def test_invalid_returns_default(self):
        assert _float("abc") == 0.0
        assert _float("abc", 2.5) == 2.5

    def test_string_float(self):
        assert _float("3.14") == pytest.approx(3.14)


class TestResolvePath:
    """Unit tests for _resolve_path() helper."""

    def test_absolute_path_unchanged(self, tmp_path):
        abs_path = str(tmp_path / "test.txt")
        assert _resolve_path(abs_path) == os.path.normpath(abs_path)

    def test_relative_path_joined_with_base(self, tmp_path):
        result = _resolve_path("subdir/file.txt", str(tmp_path))
        expected = os.path.normpath(os.path.join(str(tmp_path), "subdir/file.txt"))
        assert result == expected

    def test_empty_string_returns_empty(self):
        assert _resolve_path("") == ""

    def test_none_returns_empty(self):
        assert _resolve_path(None) == ""

    def test_whitespace_returns_empty(self):
        assert _resolve_path("   ") == ""


class TestConfigInit:
    """Integration tests for Config class."""

    def test_load_valid_config(self, config_file, config_data):
        cfg = Config(config_file)
        assert cfg.safe == config_data["safe"]
        assert cfg.adminPort == config_data["adminPort"]

    def test_missing_file_raises(self, tmp_path):
        missing = str(tmp_path / "nonexistent.json")
        with pytest.raises(Exception, match="read.*error"):
            Config(missing)

    def test_default_values_applied(self, tmp_path):
        minimal = {"safe": "test"}
        p = tmp_path / "config.json"
        p.write_text(json.dumps(minimal))
        cfg = Config(str(p))
        assert cfg.adminPort == 10001
        assert cfg.mediaHttpPort == 10002

    def test_sip_server_defaults(self, tmp_path):
        minimal = {"safe": "test"}
        p = tmp_path / "config.json"
        p.write_text(json.dumps(minimal))
        cfg = Config(str(p))
        assert cfg.sipServer["sipServerIp"] == "127.0.0.1"
        assert cfg.sipServer["sipServerPort"] == 15060


class TestConfigToDict:
    """Tests for Config.to_dict() method."""

    def test_returns_complete_snapshot(self, config_file, config_data):
        cfg = Config(config_file)
        d = cfg.to_dict()
        assert isinstance(d, dict)
        assert "safe" in d
        assert "adminPort" in d
        assert "sipServer" in d

    def test_sip_server_included(self, config_file, config_data):
        cfg = Config(config_file)
        d = cfg.to_dict()
        assert isinstance(d["sipServer"], dict)
        assert "sipServerIp" in d["sipServer"]


class TestConfigSaveFromWeb:
    """Tests for Config.save_from_web() method."""

    def test_merge_string_params(self, config_file, config_data):
        cfg = Config(config_file)
        cfg.save_from_web({"safe": "new-safe-key"})
        assert cfg.safe == "new-safe-key"

    def test_merge_int_params(self, config_file, config_data):
        cfg = Config(config_file)
        cfg.save_from_web({"adminPort": 9999})
        assert cfg.adminPort == 9999

    def test_merge_bool_params(self, config_file, config_data):
        cfg = Config(config_file)
        cfg.save_from_web({"logDebug": 1})
        assert cfg.logDebug == 1

    def test_file_written_on_save(self, config_file, config_data):
        cfg = Config(config_file)
        cfg.save_from_web({"safe": "persisted"})
        with open(config_file, "r") as f:
            saved = json.load(f)
        assert saved["safe"] == "persisted"

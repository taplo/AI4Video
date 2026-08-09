# Phase 5: test-infrastructure — Research

**Date:** 2026-08-09

---

## 1. pytest-django Best Practices and Configuration

### Key Configuration Decisions

- **`DJANGO_SETTINGS_MODULE = framework.settings`** — must be set in `pytest.ini` or `pyproject.toml`
- **Test database:** Django's test framework creates a separate `test_` prefixed database automatically; pytest-django reuses this pattern
- **SQLite in-memory:** The project uses SQLite (`ai4video.sqlite3`); for tests, use `:memory:` via settings override or rely on Django's test DB isolation
- **`pytest.ini` location:** Project root (per user decision D-12: `conftest.py` in `tests/`, `pytest.ini` in root)

### Recommended `pytest.ini`

```ini
[pytest]
DJANGO_SETTINGS_MODULE = framework.settings
python_files = tests.py test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests requiring external services
```

### Required Packages

```
pytest>=7.0
pytest-django>=4.5
pytest-xdist>=3.0      # parallel execution
pytest-cov>=4.0        # coverage reporting
pytest-mock>=3.10      # convenient mock fixtures
```

### Environment Variables for Tests

Add to `framework/settings.py` or via `conftest.py`:
```python
os.environ.setdefault('DJANGO_SECRET_KEY', 'test-secret-key-for-ci')
os.environ.setdefault('DEBUG', 'true')
```

---

## 2. Testing Patterns for Django Projects

### Pattern: Flat `tests/` Directory

Per user decisions D-09 through D-12:
```
tests/
├── conftest.py           # shared fixtures
├── test_config.py        # app/utils/Config.py
├── test_tracker.py       # app/analysis/tracker.py
├── test_utils.py         # app/utils/Utils.py
├── test_models.py        # app/models.py
├── test_middleware.py    # app/middleware.py
├── test_api.py           # API endpoint integration tests
├── test_algorithm.py     # algorithm CRUD + engine factory
├── test_onnx_engine.py   # ONNX engine (unit with mocks)
├── test_analysis_pipeline.py  # pipeline lifecycle
├── test_auth.py          # auth, login, captcha, brute-force
└── test_stream.py        # stream CRUD + proxy creation
```

### Pattern: pytest Fixtures vs Django TestCase

Since user chose **fixtures (D-02)**, prefer `@pytest.fixture` over `setUp/tearDown`:
- Function-scoped fixtures for DB isolation (D-03)
- `@pytest.fixture` with `transaction=True` for tests needing DB writes
- Session-scoped fixtures for expensive setup (e.g., mock ONNX session)

### Pattern: pytest-django `@pytest.mark.django_db`

```python
import pytest

@pytest.mark.django_db
def test_stream_creation():
    from app.models import StreamModel
    stream = StreamModel.objects.create(
        user_id=1, sort=0, code="test001", app="default",
        name="Test", pull_stream_url="rtsp://test",
        pull_stream_type=1, pull_stream_transfer_mode=0,
        pull_stream_ip="", pull_stream_port=0,
        pull_stream_username="", pull_stream_password="",
        nickname="Test Stream", remark="",
        forward_state=0, snap_filepath="",
        camera_sum_num=0, camera_name="", camera_manufacturer="",
        camera_owner="", camera_model="", camera_device_id="",
        camera_parent_id="", camera_civilcode="",
        cascade_device_id="", cascade_enable=0,
    )
    assert stream.pk is not None
    assert str(stream) == "Test Stream"
```

---

## 3. Mocking Strategies for External Services

### What to Mock (from TESTING.md)

| Dependency | Mock Target | Strategy |
|-----------|-------------|----------|
| ZLMediaKit | `app.utils.GlobalUtils.g_zlm` | `unittest.mock.MagicMock` |
| ONNX inference | `onnxruntime.InferenceSession` | Mock session + `run()` return |
| OpenCV | `cv2.imread`, `cv2.resize` | Mock return numpy arrays |
| File system | `os.path.exists`, `open()` | `pytest-mock` or `tmp_path` |
| HTTP calls | `requests.get/post` | `responses` library or `mock.patch` |
| Database | Django test DB | Use `@pytest.mark.django_db` (no mock needed) |
| Logging | `g_logger` | Mock or use `caplog` fixture |

### Mock Pattern for ONNX Engine

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_ort_session():
    with patch('app.analysis.engines.onnx_engine.ort') as mock_ort:
        mock_session = MagicMock()
        mock_input = MagicMock()
        mock_input.name = "images"
        mock_input.shape = [1, 3, 640, 640]
        mock_session.get_inputs.return_value = [mock_input]
        mock_session.get_outputs.return_value = [MagicMock(name="output")]
        mock_session.get_providers.return_value = ["CPUExecutionProvider"]
        mock_ort.InferenceSession.return_value = mock_session
        mock_ort.SessionOptions.return_value = MagicMock()
        yield mock_session
```

### Mock Pattern for ZLMediaKit

```python
@pytest.fixture
def mock_zlm():
    with patch('app.utils.GlobalUtils.g_zlm') as mock:
        mock.add_stream_proxy.return_value = True
        mock.del_stream_proxy.return_value = True
        mock.get_media_list.return_value = []
        yield mock
```

### Mock Pattern for Config

```python
@pytest.fixture
def mock_config(tmp_path):
    import json
    config_data = {"host": "127.0.0.1", "adminPort": 10001, ...}
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data))
    from app.utils.Config import Config
    return Config(str(config_file))
```

---

## 4. Test Organization Patterns

### Test File Structure (per file)

```python
"""Tests for app.utils.Config module."""
import pytest
from app.utils.Config import _bool, _int, _float, _resolve_path, Config


class TestBoolHelper:
    """Unit tests for _bool() helper."""

    def test_none_returns_default(self):
        assert _bool(None) is False
        assert _bool(None, True) is True

    def test_bool_passthrough(self):
        assert _bool(True) is True
        assert _bool(False) is False

    def test_int_coercion(self):
        assert _bool(1) is True
        assert _bool(0) is False

    def test_string_values(self):
        assert _bool("true") is True
        assert _bool("1") is True
        assert _bool("false") is False
        assert _bool("0") is False


class TestConfigInit:
    """Integration tests for Config class."""

    def test_load_valid_config(self, tmp_path):
        ...

    def test_missing_file_raises(self, tmp_path):
        ...
```

### conftest.py Structure

```python
"""Shared pytest fixtures for AI4Video tests."""
import json
import os
import pytest
from unittest.mock import MagicMock

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
        # ... other defaults
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
    monkeypatch.setattr("app.utils.GlobalUtils.g_config", mock)
    return mock
```

---

## 5. GitHub Actions CI/CD Configuration

### Workflow File: `.github/workflows/test.yml`

```yaml
name: CI

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements*.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-django pytest-xdist pytest-cov pytest-mock
          pip install flake8

      - name: Lint with flake8
        run: |
          flake8 app/ tests/ --max-line-length=120 --count --show-source --statistics

      - name: Run tests
        env:
          DJANGO_SECRET_KEY: ci-test-secret-key
          DEBUG: "true"
        run: |
          pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html -n auto

      - name: Upload coverage report
        if: matrix.python-version == '3.11'
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: htmlcov/
```

### Key CI Decisions

- **Triggers:** Push + PR to master (D-13)
- **Python versions:** 3.11, 3.12 matrix (D-14)
- **CI steps:** Lint (flake8) + test (pytest) (D-15)
- **Caching:** pip cache via `actions/cache@v4` (D-16)
- **Parallel:** `pytest -n auto` (pytest-xdist)

---

## 6. Coverage Configuration and Enforcement

### pytest-cov Configuration

Add to `pytest.ini`:
```ini
[pytest]
addopts = --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=60
```

### Coverage Target Breakdown (per D-05, D-06)

| Module | File | Priority | Target Coverage |
|--------|------|----------|----------------|
| Config | `app/utils/Config.py` | High | 80%+ |
| Tracker | `app/analysis/tracker.py` | High | 80%+ |
| Utils | `app/utils/Utils.py` | High | 70%+ |
| Models | `app/models.py` | High | 70%+ |
| ViewsBase | `app/views/ViewsBase.py` | Medium | 60%+ |
| Engine Factory | `app/analysis/engines/factory.py` | Medium | 60%+ |
| Middleware | `app/middleware.py` | Medium | 60%+ |
| ONNX Engine | `app/analysis/engines/onnx_engine.py` | Low (mock-heavy) | 40%+ |
| Pipeline | `app/analysis/pipeline.py` | Low (complex) | 30%+ |

### Coverage Exclusions

```ini
[coverage:run]
omit =
    app/analysis/engines/yolo_pytorch_engine.py
    app/analysis/engines/openvino_engine.py
    app/analysis/engines/reid_onnx_engine.py
    app/recording/*
    app/services/algorithm_test_service.py
    */migrations/*
    */manage.py
```

---

## 7. Specific Test Cases for Each Module

### 7.1 `test_config.py` — Config Module

```python
# Unit tests (pure functions, no Django dependency)
TestBoolHelper:
  - test_none_returns_default_false
  - test_none_returns_custom_default
  - test_bool_passthrough
  - test_int_zero_false, int_nonzero_true
  - test_string_true_values: "true", "1", "yes", "on"
  - test_string_false_values: "false", "0", "no", "off"
  - test_whitespace_handling

TestIntHelper:
  - test_valid_int
  - test_string_int
  - test_none_returns_default
  - test_invalid_string_returns_default
  - test_float_truncated

TestFloatHelper:
  - test_valid_float
  - test_int_to_float
  - test_none_returns_default
  - test_invalid_returns_default

TestResolvePath:
  - test_absolute_path_unchanged
  - test_relative_path_joined_with_base
  - test_empty_string_returns_empty
  - test_none_returns_empty
  - test_backslash_normalization

# Integration tests (Config class, needs tmp file)
TestConfigInit:
  - test_load_valid_config
  - test_missing_file_raises_exception
  - test_gbk_encoding_fallback
  - test_default_values_applied
  - test_sip_server_defaults

TestConfigToDict:
  - test_returns_complete_snapshot
  - test_sip_server_included

TestConfigSaveFromWeb:
  - test_merge_string_params
  - test_merge_int_params
  - test_merge_bool_params
  - test_merge_sip_params
  - test_file_written_on_save
```

### 7.2 `test_tracker.py` — IoU Tracker

```python
TestIoU:
  - test_identical_boxes_returns_1
  - test_no_overlap_returns_0
  - test_partial_overlap
  - test_contained_box
  - test_zero_area_box

TestTrack:
  - test_track_creation_defaults

TestIoUTracker:
  - test_new_track_created_on_first_detection
  - test_existing_track_updated_on_match
  - test_new_track_on_label_mismatch
  - test_missed_count_increments
  - test_track_removed_after_max_missed
  - test_reset_clears_all
  - test_multiple_labels_independent
  - test_custom_iou_threshold
```

### 7.3 `test_utils.py` — Utility Functions

```python
TestBuildPageLabels:
  - test_first_page_no_prev
  - test_middle_page_shows_prev_next
  - test_last_page_no_next
  - test_single_page
  - test_page_beyond_total
  - test_chinese_labels_default

TestGroupByField:
  - test_groups_by_stream_name
  - test_empty_list
  - test_single_group
  - test_multiple_groups

TestGB28181CodeUtils:
  - test_generate_by_time_format
  - test_length_is_20
  - test_custom_area_code
```

### 7.4 `test_models.py` — Django Models

```python
@pytest.mark.django_db
TestStreamModel:
  - test_create_stream
  - test_str_returns_nickname
  - test_default_forward_state
  - test_foreign_key_to_algorithm
  - test_cascade_delete

@pytest.mark.django_db
TestAlgorithmModel:
  - test_create_algorithm
  - test_default_algorithm_type
  - test_engine_choices_valid
  - test_task_type_choices

@pytest.mark.django_db
TestBizAlgorithmModel:
  - test_create_biz_algorithm
  - test_flow_type_choices
  - test_post_process_choices

@pytest.mark.django_db
TestZoneModel:
  - test_create_zone
  - test_many_to_many_algorithms

@pytest.mark.django_db
TestAlarmModel:
  - test_create_alarm
  - test_indexes_exist

@pytest.mark.django_db
TestRecordingModel:
  - test_create_recording

@pytest.mark.django_db
TestLLMModel:
  - test_create_llm

@pytest.mark.django_db
TestLogModel:
  - test_create_log
```

### 7.5 `test_middleware.py` — Middleware

```python
@pytest.mark.django_db
TestSimpleMiddleware:
  - test_whitelist_paths_bypass_auth: /login, /static/, /api/health
  - test_authenticated_user_passes
  - test_unauthenticated_redirects_to_login
  - test_logged_in_user_at_login_redirects_home
  - test_open_api_with_valid_safe_header
  - test_open_api_with_invalid_safe_header
  - test_open_api_without_safe_header
```

### 7.6 `test_auth.py` — Authentication

```python
@pytest.mark.django_db
TestLogin:
  - test_login_page_renders
  - test_valid_credentials_login
  - test_invalid_credentials_rejected
  - test_session_created_on_login
  - test_logout_clears_session

TestCaptcha:
  - test_captcha_generation
  - test_captcha_disabled_when_config_off

TestBruteForceProtection:
  - test_rate_limit_after_n_failures
```

### 7.7 `test_stream.py` — Stream Management

```python
@pytest.mark.django_db
TestStreamCRUD:
  - test_create_stream
  - test_update_stream
  - test_delete_stream
  - test_list_streams
  - test_get_stream_by_id

TestStreamProxy:
  - test_add_stream_proxy
  - test_delete_stream_proxy
```

### 7.8 `test_algorithm.py` — Algorithm Management

```python
@pytest.mark.django_db
TestAlgorithmCRUD:
  - test_create_algorithm
  - test_update_algorithm
  - test_delete_algorithm
  - test_list_algorithms

TestEngineFactory:
  - test_create_onnx_engine
  - test_create_yolo_engine
  - test_unknown_engine_raises
  - test_unavailable_engine_raises
  - test_list_engines
  - test_device_options
```

### 7.9 `test_onnx_engine.py` — ONNX Engine (mocked)

```python
class TestOnnxEngineUnit:
  - test_is_available_when_deps_installed
  - test_is_available_when_deps_missing
  - test_version_returns_string
  - test_providers_for_device_cpu
  - test_providers_for_device_cuda

class TestOnnxEngineLoad:
  - test_load_missing_model_returns_false
  - test_load_sets_loaded_flag
  - test_load_with_mock_session

class TestOnnxEngineDetect:
  - test_detect_before_load_returns_empty
  - test_detect_with_mock_session
  - test_detect_handles_exception
```

### 7.10 `test_analysis_pipeline.py` — Pipeline Lifecycle

```python
class TestPipelineLifecycle:
  - test_pipeline_initialization
  - test_pipeline_start_stop
  - test_pipeline_frame_processing (mocked capture)
```

### 7.11 `test_api.py` — API Integration

```python
@pytest.mark.django_db
TestHealthEndpoint:
  - test_health_returns_200
  - test_health_returns_json

TestStreamAPI:
  - test_openIndex_requires_auth
  - test_api_openAdd_with_valid_params
  - test_api_openAdd_without_auth

TestAlgorithmAPI:
  - test_list_algorithms
  - test_add_algorithm
```

---

## 8. Implementation Plan Summary

### Files to Create

| File | Purpose |
|------|---------|
| `pytest.ini` | pytest configuration |
| `tests/__init__.py` | Make tests a package |
| `tests/conftest.py` | Shared fixtures |
| `tests/test_config.py` | Config module tests |
| `tests/test_tracker.py` | IoU tracker tests |
| `tests/test_utils.py` | Utility function tests |
| `tests/test_models.py` | Django model tests |
| `tests/test_middleware.py` | Middleware auth tests |
| `tests/test_auth.py` | Authentication tests |
| `tests/test_stream.py` | Stream CRUD tests |
| `tests/test_algorithm.py` | Algorithm CRUD + factory |
| `tests/test_onnx_engine.py` | ONNX engine (mocked) |
| `tests/test_analysis_pipeline.py` | Pipeline lifecycle |
| `tests/test_api.py` | API endpoint integration |
| `.github/workflows/test.yml` | CI configuration |

### Files to Modify

| File | Change |
|------|--------|
| `requirements.txt` | Add test dependencies (or create `requirements-dev.txt`) |
| `app/tests.py` | Delete (replaced by `tests/` directory) |

### Execution Order

1. Create `pytest.ini` and `tests/conftest.py`
2. Write unit tests (no DB): `test_config.py`, `test_tracker.py`, `test_utils.py`
3. Write model tests: `test_models.py`
4. Write integration tests: `test_middleware.py`, `test_auth.py`, `test_stream.py`, `test_algorithm.py`
5. Write mock-heavy tests: `test_onnx_engine.py`, `test_analysis_pipeline.py`
6. Write API tests: `test_api.py`
7. Configure `.github/workflows/test.yml`
8. Run full suite, verify 60%+ coverage on core modules

---

*Research: 2026-08-09*

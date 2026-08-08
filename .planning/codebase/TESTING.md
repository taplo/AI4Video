# Testing Patterns

**Analysis Date:** 2026-08-05

## Test Framework

**Runner:**
- Django test framework (default `manage.py test`)
- No pytest configured (no `pytest.ini`, `conftest.py`, `pyproject.toml`)

**Assertion Library:**
- Django's `TestCase` (imported in `app/tests.py` but unused)

**Run Commands:**
```bash
python manage.py test          # Run all tests (Django default)
```

**Note:** No dedicated test runner, no coverage tools, no CI/CD pipeline configured.

## Test File Organization

**Location:**
- Single test file: `app/tests.py` (empty boilerplate)
- No other test files exist in the codebase

**Naming:**
- `app/tests.py` — contains only Django boilerplate:
  ```python
  from django.test import TestCase
  # Create your tests here.
  ```

**Structure:**
```
app/
├── tests.py                    # Empty test file (boilerplate only)
├── services/
│   └── algorithm_test_service.py  # NOT a test file — algorithm offline testing service
```

## Test Structure

**Current State:**
- **No tests exist.** The codebase has zero test coverage.
- `app/tests.py` is an auto-generated Django file that was never populated.
- `app/services/algorithm_test_service.py` is a production service for running algorithm inference tests via the web UI, NOT unit/integration tests.

**Suite Organization:** N/A

## Mocking

**Framework:** None configured

**Patterns:** None established

**What to Mock (if tests were added):**
- `app.utils.GlobalUtils.g_config` — external configuration
- `app.utils.GlobalUtils.g_database` — SQLite database
- `app.utils.GlobalUtils.g_zlm` — ZLMediaKit media server
- `app.utils.GlobalUtils.g_logger` — logging output
- `app.analysis.engines.*` — ML inference engines
- External HTTP calls (`requests.get`/`post`)

**What NOT to Mock:**
- Django ORM models (use Django test database)
- Pure utility functions (`buildPageLabels`, `_iou`, `_color_for_label`)
- Data transformation functions (`_algo_to_dict`, `_parse_labels`)

## Fixtures and Factories

**Test Data:** None established

**Location:** N/A

**Pattern for adding fixtures:**
- Django test fixtures in `app/fixtures/` (JSON/YAML)
- Or inline factory functions in test files

## Coverage

**Requirements:** None enforced

**Current Coverage:** 0% — no tests exist

**View Coverage:**
```bash
# If coverage were configured:
pip install coverage
coverage run manage.py test
coverage report
coverage html  # Generate HTML report
```

## Test Types

**Unit Tests:**
- Scope: Not implemented
- Recommended for:
  - `app/utils/Utils.py` — `buildPageLabels`, `group_by_field`, `GB28181CodeUtils`
  - `app/utils/Config.py` — `_bool`, `_int`, `_float`, `_resolve_path`
  - `app/analysis/tracker.py` — `_iou`, `IoUTracker`
  - `app/analysis/engines/base.py` — `DetectionResult`
  - `app/models.py` — Model field defaults and constraints
  - `app/views/ViewsBase.py` — `f_parseGetParams`, `f_parsePostParams`

**Integration Tests:**
- Scope: Not implemented
- Recommended for:
  - View API endpoints (require Django test client)
  - Database operations (require transaction handling)
  - `app/services/alarm_service.py` — `write_alarm`

**E2E Tests:**
- Framework: Not used
- No Selenium/Playwright/requests-based integration tests

## Common Patterns (Recommended for Future Tests)

**Django View Test:**
```python
from django.test import TestCase, Client
from django.contrib.sessions.middleware import SessionMiddleware

class StreamViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_api_openIndex_requires_auth(self):
        response = self.client.get('/stream/openIndex')
        self.assertEqual(response.status_code, 302)  # Redirects to /login
```

**Model Test:**
```python
from django.test import TestCase
from app.models import StreamModel

class StreamModelTest(TestCase):
    def test_stream_creation(self):
        stream = StreamModel(
            user_id=1,
            code="test001",
            name="Test Stream",
            pull_stream_url="rtsp://test",
            pull_stream_type=1,
        )
        stream.save()
        self.assertEqual(str(stream), "Test Stream")
```

**Utility Function Test:**
```python
from django.test import TestCase
from app.utils.Utils import buildPageLabels

class BuildPageLabelsTest(TestCase):
    def test_first_page(self):
        labels = buildPageLabels(1, 5)
        self.assertEqual(len(labels), 5)
        self.assertTrue(labels[0]["cur"])
```

**Algorithm Engine Test:**
```python
from django.test import TestCase
from app.analysis.engines.base import DetectionResult

class DetectionResultTest(TestCase):
    def test_properties(self):
        det = DetectionResult(box=[10, 20, 100, 200], label="person", score=0.95)
        self.assertEqual(det.box, [10, 20, 100, 200])
        self.assertEqual(det.label, "person")
        self.assertAlmostEqual(det.score, 0.95)
```

**Tracker Test:**
```python
from django.test import TestCase
from app.analysis.tracker import IoUTracker, _iou

class IoUTest(TestCase):
    def test_identical_boxes(self):
        self.assertAlmostEqual(_iou([0, 0, 10, 10], [0, 0, 10, 10]), 1.0)

    def test_no_overlap(self):
        self.assertAlmostEqual(_iou([0, 0, 5, 5], [10, 10, 15, 15]), 0.0)

class IoUTrackerTest(TestCase):
    def test_new_track_created(self):
        tracker = IoUTracker()
        dets = [{"box": [10, 10, 50, 50], "label": "person", "score": 0.9}]
        ids = tracker.update(dets)
        self.assertEqual(len(ids), 1)
```

## Testing Gaps (Priority Order)

**High Priority:**
- `app/utils/Config.py` — Configuration parsing logic (no tests for `_bool`, `_int`, `_resolve_path`)
- `app/analysis/tracker.py` — IoU computation and tracking logic
- `app/utils/Utils.py` — Pagination helpers and code generation
- `app/models.py` — Model field validation and defaults

**Medium Priority:**
- `app/views/ViewsBase.py` — Request parsing and security check
- `app/analysis/engines/factory.py` — Engine creation and availability check
- `app/services/alarm_service.py` — Alarm event writing

**Low Priority:**
- View API endpoints (heavy mocking required)
- `app/analysis/pipeline.py` — Complex multi-threaded processing (hard to unit test)
- `app/services/algorithm_test_service.py` — Offline algorithm testing (requires ML models)

## Test Infrastructure Recommendations

**To add basic testing:**
1. Install pytest: `pip install pytest pytest-django`
2. Create `pytest.ini`:
   ```ini
   [pytest]
   DJANGO_SETTINGS_MODULE = framework.settings
   python_files = tests.py test_*.py
   python_classes = Test*
   python_functions = test_*
   ```
3. Create `conftest.py` with shared fixtures
4. Add test database configuration to `framework/settings.py`

**To add coverage:**
1. Install: `pip install pytest-cov`
2. Run: `pytest --cov=app --cov-report=html`
3. Target: 60%+ coverage for core utilities and models

---

*Testing analysis: 2026-08-05*

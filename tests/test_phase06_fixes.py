"""Regression tests for phase06 security fixes: CR-01 and CR-02."""
import json
import pytest
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock, patch


class TestCR01SafeHeaderAuth:
    """CR-01: /inner/ endpoints must enforce Safe-header authentication."""

    def test_inner_endpoint_without_safe_header_returns_403(self):
        """Requests to /inner/ without Safe header should be rejected with 403."""
        from app.middleware import SimpleMiddleware

        factory = RequestFactory()
        request = factory.get("/inner/hook")
        request.session = {}

        middleware = SimpleMiddleware(lambda r: MagicMock(status_code=200))
        response = middleware.process_request(request)

        assert response is not None
        assert response.status_code == 403
        data = json.loads(response.content)
        assert data["code"] == 403
        assert "safe header required" in data["msg"]

    def test_inner_endpoint_with_wrong_safe_header_returns_403(self):
        """Requests to /inner/ with wrong Safe header should be rejected."""
        from app.middleware import SimpleMiddleware

        factory = RequestFactory()
        request = factory.get("/inner/hook", HTTP_SAFE="wrong-secret")
        request.session = {}

        middleware = SimpleMiddleware(lambda r: MagicMock(status_code=200))
        response = middleware.process_request(request)

        assert response is not None
        assert response.status_code == 403

    def test_inner_endpoint_with_valid_safe_header_passes(self):
        """Requests to /inner/ with valid Safe header should pass through."""
        from app.middleware import SimpleMiddleware

        factory = RequestFactory()
        request = factory.get("/inner/hook", HTTP_SAFE="test-safe-key")
        request.session = {}

        with patch("app.utils.GlobalUtils.g_config") as mock_config:
            mock_config.safe = "test-safe-key"
            middleware = SimpleMiddleware(lambda r: MagicMock(status_code=200))
            response = middleware.process_request(request)

        # Should return None (pass through to next middleware/view)
        assert response is None

    def test_inner_endpoint_with_secret_param_passes(self):
        """Requests to /inner/?secret=xxx with valid secret should pass."""
        from app.middleware import SimpleMiddleware

        factory = RequestFactory()
        request = factory.get("/inner/hook", {"secret": "test-safe-key"})
        request.session = {}

        with patch("app.utils.GlobalUtils.g_config") as mock_config:
            mock_config.safe = "test-safe-key"
            middleware = SimpleMiddleware(lambda r: MagicMock(status_code=200))
            response = middleware.process_request(request)

        assert response is None

    def test_non_inner_endpoint_not_affected_by_safe_check(self):
        """Non-/inner/ endpoints should not trigger Safe-header auth."""
        from app.middleware import SimpleMiddleware

        factory = RequestFactory()
        request = factory.get("/api/health")
        request.session = {}

        middleware = SimpleMiddleware(lambda r: MagicMock(status_code=200))
        response = middleware.process_request(request)

        # /api/health is whitelisted, should pass through
        assert response is None


class TestCR02AuditLog:
    """CR-02: AuditLog model must exist and be usable."""

    def test_audit_log_model_exists(self):
        """AuditLog model should be importable."""
        from app.models import AuditLog
        assert AuditLog is not None

    @pytest.mark.django_db
    def test_audit_log_create(self):
        """AuditLog.objects.create should succeed with valid data."""
        from app.models import AuditLog

        log = AuditLog.objects.create(
            user_id=1,
            username="testuser",
            ip_address="127.0.0.1",
            action="login",
            resource="/login",
            details={"method": "POST", "status_code": 200},
            success=True,
        )
        assert log.pk is not None
        assert log.action == "login"
        assert log.success is True

    def test_audit_log_action_choices(self):
        """AuditLog should support all expected action types."""
        from app.models import AuditLog

        expected_actions = {"login", "logout", "login_failed", "create", "update", "delete"}
        actual_actions = {choice[0] for choice in AuditLog.ACTION_CHOICES}
        assert expected_actions == actual_actions

    def test_audit_log_table_name(self):
        """AuditLog should use the av_audit_log table."""
        from app.models import AuditLog
        assert AuditLog._meta.db_table == "av_audit_log"

    def test_migrations_are_consistent(self):
        """Running makemigrations --check should report no drift."""
        import subprocess
        result = subprocess.run(
            ["uv", "run", "python", "manage.py", "makemigrations", "--check", "--dry-run", "app"],
            capture_output=True,
            text=True,
            cwd="D:\\projects\\AI4Video",
        )
        assert result.returncode == 0, f"Migration drift detected: {result.stderr}"

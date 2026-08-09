"""Tests for app.middleware module."""
import pytest
from django.test import RequestFactory, TestCase
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from app.middleware import SimpleMiddleware


def add_session_to_request(request):
    """Helper to add session middleware to a request."""
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    return request


@pytest.mark.django_db
class TestSimpleMiddleware:
    """Tests for SimpleMiddleware."""

    def test_whitelist_login_bypasses_auth(self):
        factory = RequestFactory()
        request = factory.get("/login")
        request = add_session_to_request(request)
        middleware = SimpleMiddleware(lambda req: None)
        response = middleware.process_request(request)
        # Whitelisted paths should return None (no redirect)
        assert response is None

    def test_whitelist_static_bypasses_auth(self):
        factory = RequestFactory()
        request = factory.get("/static/css/style.css")
        request = add_session_to_request(request)
        middleware = SimpleMiddleware(lambda req: None)
        response = middleware.process_request(request)
        assert response is None

    def test_whitelist_health_bypasses_auth(self):
        factory = RequestFactory()
        request = factory.get("/api/health")
        request = add_session_to_request(request)
        middleware = SimpleMiddleware(lambda req: None)
        response = middleware.process_request(request)
        assert response is None

    def test_authenticated_user_passes(self):
        factory = RequestFactory()
        request = factory.get("/dashboard")
        request = add_session_to_request(request)
        request.session["user"] = {"id": 1, "username": "admin"}
        middleware = SimpleMiddleware(lambda req: None)
        response = middleware.process_request(request)
        assert response is None

    def test_unauthenticated_redirects_to_login(self):
        factory = RequestFactory()
        request = factory.get("/dashboard")
        request = add_session_to_request(request)
        middleware = SimpleMiddleware(lambda req: None)
        response = middleware.process_request(request)
        assert response is not None
        assert response.status_code == 302
        assert response.url == "/login"

    def test_logged_in_user_at_login_returns_none(self):
        factory = RequestFactory()
        request = factory.get("/login")
        request = add_session_to_request(request)
        request.session["user"] = {"id": 1, "username": "admin"}
        middleware = SimpleMiddleware(lambda req: None)
        response = middleware.process_request(request)
        # /login is whitelisted — returns None even for logged-in users
        assert response is None

    def test_open_api_without_safe_header_redirects(self):
        factory = RequestFactory()
        request = factory.get("/open/some-endpoint")
        request = add_session_to_request(request)
        middleware = SimpleMiddleware(lambda req: None)
        response = middleware.process_request(request)
        assert response is not None
        assert response.status_code == 302
        assert response.url == "/login"

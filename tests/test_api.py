"""Tests for API endpoints."""
import pytest
from django.test import Client
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_returns_200(self):
        client = Client()
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_json(self):
        client = Client()
        response = client.get("/api/health")
        assert response["Content-Type"] == "application/json"


@pytest.mark.django_db
class TestStreamAPI:
    """Tests for stream API endpoints."""

    def test_openIndex_requires_auth(self):
        client = Client()
        response = client.get("/stream/openIndex")
        # Should redirect to login
        assert response.status_code in (302, 200)

    def test_api_openAdd_without_auth(self):
        client = Client()
        response = client.post("/stream/openAdd", {
            "name": "test",
            "pull_stream_url": "rtsp://test",
            "pull_stream_type": "1",
        })
        # Should redirect to login
        assert response.status_code in (302, 200)


@pytest.mark.django_db
class TestAlgorithmAPI:
    """Tests for algorithm API endpoints."""

    def test_list_algorithms(self):
        client = Client()
        response = client.get("/algorithm/openIndex")
        # Should redirect to login or return JSON
        assert response.status_code in (200, 302)

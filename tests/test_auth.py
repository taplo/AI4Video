"""Tests for authentication views."""
import pytest
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from app.middleware import SimpleMiddleware
from app.models import StreamModel
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestLogin:
    """Tests for login functionality."""

    def test_login_page_renders(self):
        client = Client()
        response = client.get("/login")
        assert response.status_code == 200

    def test_valid_credentials_login(self):
        User.objects.create_user(username="testuser", password="testpass123")
        client = Client()
        response = client.post("/login", {
            "username": "testuser",
            "password": "testpass123",
        })
        # Should redirect on success
        assert response.status_code in (200, 302)

    def test_invalid_credentials_rejected(self):
        User.objects.create_user(username="testuser", password="testpass123")
        client = Client()
        response = client.post("/login", {
            "username": "testuser",
            "password": "wrongpassword",
        })
        # Should not redirect to /
        assert response.status_code == 200

    def test_session_created_on_login(self):
        User.objects.create_user(username="testuser", password="testpass123")
        client = Client()
        client.post("/login", {
            "username": "testuser",
            "password": "testpass123",
        })
        # Session should have user key
        session = client.session
        assert "user" in session

    def test_logout_clears_session(self):
        User.objects.create_user(username="testuser", password="testpass123")
        client = Client()
        client.post("/login", {
            "username": "testuser",
            "password": "testpass123",
        })
        client.get("/logout")
        session = client.session
        assert "user" not in session


@pytest.mark.django_db
class TestStreamCRUD:
    """Tests for stream CRUD operations."""

    def test_create_stream(self):
        stream = StreamModel.objects.create(
            user_id=1, sort=0, code="crud001", app="default",
            name="crud_stream", pull_stream_url="rtsp://test",
            pull_stream_type=1, pull_stream_transfer_mode=0,
            pull_stream_ip="", pull_stream_port=0,
            pull_stream_username="", pull_stream_password="",
            nickname="CRUD Stream", remark="",
            forward_state=0, snap_filepath="",
            camera_sum_num=0, camera_name="", camera_manufacturer="",
            camera_owner="", camera_model="", camera_device_id="",
            camera_parent_id="", camera_civilcode="",
            cascade_device_id="", cascade_enable=0,
        )
        assert stream.pk is not None

    def test_update_stream(self):
        stream = StreamModel.objects.create(
            user_id=1, sort=0, code="crud002", app="default",
            name="update_stream", pull_stream_url="rtsp://test",
            pull_stream_type=1, pull_stream_transfer_mode=0,
            pull_stream_ip="", pull_stream_port=0,
            pull_stream_username="", pull_stream_password="",
            nickname="Before Update", remark="",
            forward_state=0, snap_filepath="",
            camera_sum_num=0, camera_name="", camera_manufacturer="",
            camera_owner="", camera_model="", camera_device_id="",
            camera_parent_id="", camera_civilcode="",
            cascade_device_id="", cascade_enable=0,
        )
        stream.nickname = "After Update"
        stream.save()
        stream.refresh_from_db()
        assert stream.nickname == "After Update"

    def test_delete_stream(self):
        stream = StreamModel.objects.create(
            user_id=1, sort=0, code="crud003", app="default",
            name="delete_stream", pull_stream_url="rtsp://test",
            pull_stream_type=1, pull_stream_transfer_mode=0,
            pull_stream_ip="", pull_stream_port=0,
            pull_stream_username="", pull_stream_password="",
            nickname="Delete Me", remark="",
            forward_state=0, snap_filepath="",
            camera_sum_num=0, camera_name="", camera_manufacturer="",
            camera_owner="", camera_model="", camera_device_id="",
            camera_parent_id="", camera_civilcode="",
            cascade_device_id="", cascade_enable=0,
        )
        stream_id = stream.pk
        stream.delete()
        assert not StreamModel.objects.filter(pk=stream_id).exists()

    def test_list_streams(self):
        for i in range(3):
            StreamModel.objects.create(
                user_id=1, sort=i, code=f"list{i:03d}", app="default",
                name=f"list_stream_{i}", pull_stream_url="rtsp://test",
                pull_stream_type=1, pull_stream_transfer_mode=0,
                pull_stream_ip="", pull_stream_port=0,
                pull_stream_username="", pull_stream_password="",
                nickname=f"List Stream {i}", remark="",
                forward_state=0, snap_filepath="",
                camera_sum_num=0, camera_name="", camera_manufacturer="",
                camera_owner="", camera_model="", camera_device_id="",
                camera_parent_id="", camera_civilcode="",
                cascade_device_id="", cascade_enable=0,
            )
        streams = StreamModel.objects.all()
        assert streams.count() >= 3

    def test_get_stream_by_id(self):
        stream = StreamModel.objects.create(
            user_id=1, sort=0, code="get001", app="default",
            name="get_stream", pull_stream_url="rtsp://test",
            pull_stream_type=1, pull_stream_transfer_mode=0,
            pull_stream_ip="", pull_stream_port=0,
            pull_stream_username="", pull_stream_password="",
            nickname="Get Stream", remark="",
            forward_state=0, snap_filepath="",
            camera_sum_num=0, camera_name="", camera_manufacturer="",
            camera_owner="", camera_model="", camera_device_id="",
            camera_parent_id="", camera_civilcode="",
            cascade_device_id="", cascade_enable=0,
        )
        found = StreamModel.objects.get(pk=stream.pk)
        assert found.nickname == "Get Stream"

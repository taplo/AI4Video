"""Tests for stream management operations."""
import pytest
from app.models import StreamModel
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestStreamProxy:
    """Tests for stream proxy operations."""

    def test_add_stream_proxy_success(self, mock_g_zlm):
        stream = StreamModel.objects.create(
            user_id=1, sort=0, code="proxy001", app="default",
            name="proxy_stream", pull_stream_url="rtsp://test",
            pull_stream_type=1, pull_stream_transfer_mode=0,
            pull_stream_ip="", pull_stream_port=0,
            pull_stream_username="", pull_stream_password="",
            nickname="Proxy Stream", remark="",
            forward_state=0, snap_filepath="",
            camera_sum_num=0, camera_name="", camera_manufacturer="",
            camera_owner="", camera_model="", camera_device_id="",
            camera_parent_id="", camera_civilcode="",
            cascade_device_id="", cascade_enable=0,
        )
        mock_g_zlm.addStreamProxy.return_value = (True, "success")
        from app.utils.GlobalUtils import GlobalUtils
        ret, msg = GlobalUtils.addStreamProxy(stream)
        assert ret is True
        assert stream.forward_state == 0  # State not changed by addStreamProxy

    def test_add_stream_proxy_failure(self, mock_g_zlm):
        stream = StreamModel.objects.create(
            user_id=1, sort=0, code="proxy002", app="default",
            name="proxy_fail_stream", pull_stream_url="rtsp://test",
            pull_stream_type=1, pull_stream_transfer_mode=0,
            pull_stream_ip="", pull_stream_port=0,
            pull_stream_username="", pull_stream_password="",
            nickname="Proxy Fail Stream", remark="",
            forward_state=0, snap_filepath="",
            camera_sum_num=0, camera_name="", camera_manufacturer="",
            camera_owner="", camera_model="", camera_device_id="",
            camera_parent_id="", camera_civilcode="",
            cascade_device_id="", cascade_enable=0,
        )
        mock_g_zlm.addStreamProxy.return_value = (False, "connection refused")
        from app.utils.GlobalUtils import GlobalUtils
        ret, msg = GlobalUtils.addStreamProxy(stream)
        assert ret is False

    def test_delete_stream_proxy_success(self, mock_g_zlm):
        stream = StreamModel.objects.create(
            user_id=1, sort=0, code="proxy003", app="default",
            name="del_proxy_stream", pull_stream_url="rtsp://test",
            pull_stream_type=1, pull_stream_transfer_mode=0,
            pull_stream_ip="", pull_stream_port=0,
            pull_stream_username="", pull_stream_password="",
            nickname="Del Proxy Stream", remark="",
            forward_state=1, snap_filepath="",
            camera_sum_num=0, camera_name="", camera_manufacturer="",
            camera_owner="", camera_model="", camera_device_id="",
            camera_parent_id="", camera_civilcode="",
            cascade_device_id="", cascade_enable=0,
        )
        mock_g_zlm.delStreamProxy.return_value = (True, "success")
        from app.utils.GlobalUtils import GlobalUtils
        ret, msg = GlobalUtils.delStreamProxy(stream)
        assert ret is True

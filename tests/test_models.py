"""Tests for app.models module."""
import pytest
from datetime import datetime
from app.models import (
    StreamModel, AlgorithmModel, BizAlgorithmModel, ZoneModel,
    AlarmModel, RecordingModel, LLMModel, LogModel
)


@pytest.mark.django_db
class TestStreamModel:
    """Tests for StreamModel."""

    def test_create_stream(self):
        stream = StreamModel.objects.create(
            user_id=1, sort=0, code="test001", app="default",
            name="Test Stream", pull_stream_url="rtsp://test",
            pull_stream_type=1, pull_stream_transfer_mode=0,
            pull_stream_ip="", pull_stream_port=0,
            pull_stream_username="", pull_stream_password="",
            nickname="Test Camera", remark="",
            forward_state=0, snap_filepath="",
            camera_sum_num=0, camera_name="", camera_manufacturer="",
            camera_owner="", camera_model="", camera_device_id="",
            camera_parent_id="", camera_civilcode="",
            cascade_device_id="", cascade_enable=0,
        )
        assert stream.pk is not None

    def test_str_returns_nickname(self):
        stream = StreamModel.objects.create(
            user_id=1, sort=0, code="test002", app="default",
            name="stream2", pull_stream_url="rtsp://test2",
            pull_stream_type=1, pull_stream_transfer_mode=0,
            pull_stream_ip="", pull_stream_port=0,
            pull_stream_username="", pull_stream_password="",
            nickname="Living Room Cam", remark="",
            forward_state=0, snap_filepath="",
            camera_sum_num=0, camera_name="", camera_manufacturer="",
            camera_owner="", camera_model="", camera_device_id="",
            camera_parent_id="", camera_civilcode="",
            cascade_device_id="", cascade_enable=0,
        )
        assert str(stream) == "Living Room Cam"

    def test_default_forward_state(self):
        stream = StreamModel.objects.create(
            user_id=1, sort=0, code="test003", app="default",
            name="stream3", pull_stream_url="rtsp://test3",
            pull_stream_type=1, pull_stream_transfer_mode=0,
            pull_stream_ip="", pull_stream_port=0,
            pull_stream_username="", pull_stream_password="",
            nickname="Cam3", remark="",
            forward_state=0, snap_filepath="",
            camera_sum_num=0, camera_name="", camera_manufacturer="",
            camera_owner="", camera_model="", camera_device_id="",
            camera_parent_id="", camera_civilcode="",
            cascade_device_id="", cascade_enable=0,
        )
        assert stream.forward_state == 0

    def test_cascade_delete(self):
        stream = StreamModel.objects.create(
            user_id=1, sort=0, code="test004", app="default",
            name="stream4", pull_stream_url="rtsp://test4",
            pull_stream_type=1, pull_stream_transfer_mode=0,
            pull_stream_ip="", pull_stream_port=0,
            pull_stream_username="", pull_stream_password="",
            nickname="Cam4", remark="",
            forward_state=0, snap_filepath="",
            camera_sum_num=0, camera_name="", camera_manufacturer="",
            camera_owner="", camera_model="", camera_device_id="",
            camera_parent_id="", camera_civilcode="",
            cascade_device_id="", cascade_enable=0,
        )
        stream_id = stream.pk
        stream.delete()
        assert not StreamModel.objects.filter(pk=stream_id).exists()


@pytest.mark.django_db
class TestAlgorithmModel:
    """Tests for AlgorithmModel."""

    def test_create_algorithm(self):
        algo = AlgorithmModel.objects.create(
            name="YOLOv8 Test",
            algorithm_type="yolo8",
            task_type="detect",
            inference_engine="yolo_pytorch",
            device="cpu",
            model_file="yolov8n.pt",
        )
        assert algo.pk is not None

    def test_default_algorithm_type(self):
        algo = AlgorithmModel.objects.create(name="Default Algo")
        assert algo.algorithm_type == "yolo8"

    def test_engine_choices_valid(self):
        algo = AlgorithmModel.objects.create(
            name="ONNX Algo",
            inference_engine="onnxruntime",
        )
        assert algo.inference_engine == "onnxruntime"

    def test_task_type_choices(self):
        algo = AlgorithmModel.objects.create(
            name="Segment Algo",
            task_type="segment",
        )
        assert algo.task_type == "segment"


@pytest.mark.django_db
class TestBizAlgorithmModel:
    """Tests for BizAlgorithmModel."""

    def test_create_biz_algorithm(self):
        biz = BizAlgorithmModel.objects.create(
            name="Zone Intrusion",
            flow_type=1,
            post_process="AREA",
        )
        assert biz.pk is not None

    def test_flow_type_choices(self):
        biz = BizAlgorithmModel.objects.create(
            name="LLM Flow",
            flow_type=2,
        )
        assert biz.flow_type == 2

    def test_post_process_choices(self):
        biz = BizAlgorithmModel.objects.create(
            name="Line Cross",
            post_process="LINE_CROSS",
        )
        assert biz.post_process == "LINE_CROSS"


@pytest.mark.django_db
class TestZoneModel:
    """Tests for ZoneModel."""

    def test_create_zone(self):
        stream = StreamModel.objects.create(
            user_id=1, sort=0, code="zone001", app="default",
            name="zone_stream", pull_stream_url="rtsp://test",
            pull_stream_type=1, pull_stream_transfer_mode=0,
            pull_stream_ip="", pull_stream_port=0,
            pull_stream_username="", pull_stream_password="",
            nickname="Zone Stream", remark="",
            forward_state=0, snap_filepath="",
            camera_sum_num=0, camera_name="", camera_manufacturer="",
            camera_owner="", camera_model="", camera_device_id="",
            camera_parent_id="", camera_civilcode="",
            cascade_device_id="", cascade_enable=0,
        )
        zone = ZoneModel.objects.create(
            stream=stream,
            name="Entry Zone",
            coordinates="[[0,0],[100,0],[100,100],[0,100]]",
        )
        assert zone.pk is not None

    def test_many_to_many_algorithms(self):
        stream = StreamModel.objects.create(
            user_id=1, sort=0, code="zone002", app="default",
            name="zone_stream2", pull_stream_url="rtsp://test",
            pull_stream_type=1, pull_stream_transfer_mode=0,
            pull_stream_ip="", pull_stream_port=0,
            pull_stream_username="", pull_stream_password="",
            nickname="Zone Stream 2", remark="",
            forward_state=0, snap_filepath="",
            camera_sum_num=0, camera_name="", camera_manufacturer="",
            camera_owner="", camera_model="", camera_device_id="",
            camera_parent_id="", camera_civilcode="",
            cascade_device_id="", cascade_enable=0,
        )
        zone = ZoneModel.objects.create(
            stream=stream,
            name="Test Zone",
            coordinates="[[0,0],[100,0],[100,100],[0,100]]",
        )
        biz = BizAlgorithmModel.objects.create(name="Biz Algo", flow_type=1)
        zone.algorithms.add(biz)
        assert zone.algorithms.count() == 1


@pytest.mark.django_db
class TestAlarmModel:
    """Tests for AlarmModel."""

    def test_create_alarm(self):
        stream = StreamModel.objects.create(
            user_id=1, sort=0, code="alarm001", app="default",
            name="alarm_stream", pull_stream_url="rtsp://test",
            pull_stream_type=1, pull_stream_transfer_mode=0,
            pull_stream_ip="", pull_stream_port=0,
            pull_stream_username="", pull_stream_password="",
            nickname="Alarm Stream", remark="",
            forward_state=0, snap_filepath="",
            camera_sum_num=0, camera_name="", camera_manufacturer="",
            camera_owner="", camera_model="", camera_device_id="",
            camera_parent_id="", camera_civilcode="",
            cascade_device_id="", cascade_enable=0,
        )
        alarm = AlarmModel.objects.create(
            stream=stream,
            event_type="entered_zone",
            description="Person entered restricted area",
            timestamp=datetime.now(),
        )
        assert alarm.pk is not None

    def test_indexes_exist(self):
        indexes = AlarmModel._meta.indexes
        assert len(indexes) == 2


@pytest.mark.django_db
class TestRecordingModel:
    """Tests for RecordingModel."""

    def test_create_recording(self):
        stream = StreamModel.objects.create(
            user_id=1, sort=0, code="rec001", app="default",
            name="rec_stream", pull_stream_url="rtsp://test",
            pull_stream_type=1, pull_stream_transfer_mode=0,
            pull_stream_ip="", pull_stream_port=0,
            pull_stream_username="", pull_stream_password="",
            nickname="Rec Stream", remark="",
            forward_state=0, snap_filepath="",
            camera_sum_num=0, camera_name="", camera_manufacturer="",
            camera_owner="", camera_model="", camera_device_id="",
            camera_parent_id="", camera_civilcode="",
            cascade_device_id="", cascade_enable=0,
        )
        recording = RecordingModel.objects.create(
            stream=stream,
            file_path="/recordings/test.mp4",
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration=60.0,
            file_size=1024000,
        )
        assert recording.pk is not None


@pytest.mark.django_db
class TestLLMModel:
    """Tests for LLMModel."""

    def test_create_llm(self):
        llm = LLMModel.objects.create(
            user_id=1,
            sort=0,
            code="llm001",
            name="GPT-4 Test",
            model_name="gpt-4",
            api_url="https://api.openai.com/v1",
            api_key="test-key",
        )
        assert llm.pk is not None


@pytest.mark.django_db
class TestLogModel:
    """Tests for LogModel."""

    def test_create_log(self):
        log = LogModel.objects.create(
            user_id=1,
            log_type=1,
            content="User logged in",
            state=1,
        )
        assert log.pk is not None
        assert str(log) == "User logged in"

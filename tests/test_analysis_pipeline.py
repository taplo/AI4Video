"""Tests for analysis pipeline lifecycle."""
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from app.analysis.pipeline import CameraPipeline


class TestPipelineLifecycle:
    """Tests for CameraPipeline lifecycle."""

    def test_pipeline_initialization(self):
        pipeline = CameraPipeline(
            stream_id=1,
            stream_code="test_stream",
            rtsp_url="rtsp://test",
        )
        assert pipeline.stream_id == 1
        assert pipeline.stream_code == "test_stream"
        assert pipeline.rtsp_url == "rtsp://test"

    def test_pipeline_default_fps(self):
        pipeline = CameraPipeline(
            stream_id=1,
            stream_code="test",
            rtsp_url="rtsp://test",
        )
        assert pipeline.target_fps == 5
        assert pipeline.analyze_fps == 5.0

    def test_pipeline_custom_fps(self):
        pipeline = CameraPipeline(
            stream_id=1,
            stream_code="test",
            rtsp_url="rtsp://test",
            target_fps=10,
            analyze_fps=2.5,
        )
        assert pipeline.target_fps == 10
        assert pipeline.analyze_fps == 2.5

    def test_pipeline_with_detectors(self):
        mock_engine = MagicMock()
        detectors = [
            {"algorithm_id": 1, "algorithm_name": "yolo8", "engine": mock_engine},
        ]
        pipeline = CameraPipeline(
            stream_id=1,
            stream_code="test",
            rtsp_url="rtsp://test",
            detectors=detectors,
        )
        assert len(pipeline._detectors) == 1
        assert pipeline._detector == mock_engine

    def test_pipeline_attributes(self):
        pipeline = CameraPipeline(
            stream_id=1,
            stream_code="test",
            rtsp_url="rtsp://test",
        )
        assert hasattr(pipeline, 'stream_id')
        assert hasattr(pipeline, '_tracker')
        assert hasattr(pipeline, '_motion')

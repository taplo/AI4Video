"""Tests for algorithm management and engine factory."""
import pytest
from app.models import AlgorithmModel
from app.analysis.engines.factory import EngineFactory, list_engines, device_options
from app.analysis.engines.base import EngineNotAvailableError


@pytest.mark.django_db
class TestAlgorithmCRUD:
    """Tests for algorithm CRUD operations."""

    def test_create_algorithm(self):
        algo = AlgorithmModel.objects.create(
            name="Test YOLOv8",
            algorithm_type="yolo8",
            task_type="detect",
            inference_engine="yolo_pytorch",
            device="cpu",
            model_file="yolov8n.pt",
        )
        assert algo.pk is not None

    def test_update_algorithm(self):
        algo = AlgorithmModel.objects.create(
            name="Update Me",
            algorithm_type="yolo8",
        )
        algo.name = "Updated Name"
        algo.save()
        algo.refresh_from_db()
        assert algo.name == "Updated Name"

    def test_delete_algorithm(self):
        algo = AlgorithmModel.objects.create(
            name="Delete Me",
            algorithm_type="yolo8",
        )
        algo_id = algo.pk
        algo.delete()
        assert not AlgorithmModel.objects.filter(pk=algo_id).exists()

    def test_list_algorithms(self):
        for i in range(3):
            AlgorithmModel.objects.create(
                name=f"Algo {i}",
                algorithm_type="yolo8",
            )
        algos = AlgorithmModel.objects.all()
        assert algos.count() >= 3


class TestEngineFactory:
    """Tests for engine factory."""

    def test_list_engines(self):
        engines = list_engines()
        assert isinstance(engines, list)
        assert len(engines) >= 1

    def test_device_options_onnx(self):
        opts = device_options("onnxruntime")
        assert isinstance(opts, list)
        assert any(o["value"] == "cpu" for o in opts)

    def test_device_options_unknown_falls_back(self):
        opts = device_options("unknown_engine")
        assert isinstance(opts, list)
        assert len(opts) >= 1

    def test_is_available_onnx(self):
        # Just check it doesn't crash
        result = EngineFactory.is_available("onnxruntime")
        assert isinstance(result, bool)

    def test_unknown_engine_raises(self):
        with pytest.raises(EngineNotAvailableError, match="unknown engine"):
            EngineFactory.create("nonexistent_engine")

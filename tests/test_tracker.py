"""Tests for app.analysis.tracker module."""
import pytest
from app.analysis.tracker import _iou, Track, IoUTracker


class TestIoU:
    """Unit tests for _iou() function."""

    def test_identical_boxes_returns_1(self):
        box = (10, 10, 50, 50)
        assert _iou(box, box) == pytest.approx(1.0)

    def test_no_overlap_returns_0(self):
        a = (0, 0, 10, 10)
        b = (20, 20, 30, 30)
        assert _iou(a, b) == pytest.approx(0.0)

    def test_partial_overlap(self):
        a = (0, 0, 20, 20)
        b = (10, 10, 30, 30)
        # intersection: 10x10 = 100, union: 400+400-100 = 700
        assert _iou(a, b) == pytest.approx(100 / 700)

    def test_contained_box(self):
        outer = (0, 0, 100, 100)
        inner = (25, 25, 75, 75)
        # intersection: 50x50 = 2500, union: 10000+2500-2500 = 10000
        assert _iou(outer, inner) == pytest.approx(2500 / 10000)

    def test_zero_area_box(self):
        a = (10, 10, 10, 10)  # zero area
        b = (0, 0, 20, 20)
        assert _iou(a, b) == pytest.approx(0.0)

    def test_touching_boxes_no_overlap(self):
        a = (0, 0, 10, 10)
        b = (10, 0, 20, 10)
        assert _iou(a, b) == pytest.approx(0.0)


class TestTrack:
    """Tests for Track class."""

    def test_track_creation_defaults(self):
        track = Track(track_id=1, label="person", box=(10, 10, 50, 50), score=0.9, born=0)
        assert track.track_id == 1
        assert track.label == "person"
        assert track.box == (10, 10, 50, 50)
        assert track.score == 0.9
        assert track.missed == 0
        assert track.hits == 1
        assert track.born == 0


class TestIoUTracker:
    """Tests for IoUTracker class."""

    def test_new_track_created_on_first_detection(self):
        tracker = IoUTracker(iou_threshold=0.3, max_missed=8)
        dets = [{"box": (10, 10, 50, 50), "label": "person", "score": 0.9}]
        active, ended, new, _ = tracker.update(dets, frame_index=0)
        assert len(active) == 1
        assert len(new) == 1
        assert active[0]["label"] == "person"

    def test_existing_track_updated_on_match(self):
        tracker = IoUTracker(iou_threshold=0.3, max_missed=8)
        dets = [{"box": (10, 10, 50, 50), "label": "person", "score": 0.9}]
        tracker.update(dets, frame_index=0)
        # Slightly shifted detection — should match same track
        dets2 = [{"box": (12, 12, 52, 52), "label": "person", "score": 0.95}]
        active, ended, new, _ = tracker.update(dets2, frame_index=1)
        assert len(active) == 1
        assert len(new) == 0
        assert active[0]["score"] == 0.95

    def test_new_track_on_label_mismatch(self):
        tracker = IoUTracker(iou_threshold=0.3, max_missed=8)
        dets = [{"box": (10, 10, 50, 50), "label": "person", "score": 0.9}]
        tracker.update(dets, frame_index=0)
        # Different label — should create new track
        dets2 = [{"box": (10, 10, 50, 50), "label": "car", "score": 0.9}]
        active, ended, new, _ = tracker.update(dets2, frame_index=1)
        # The car track is new; the person track is still in _tracks (missed=1)
        assert len(new) == 1
        assert new[0] == 2  # car gets track_id 2
        assert len(tracker.all_active()) == 2  # both tracks still alive

    def test_missed_count_increments(self):
        tracker = IoUTracker(iou_threshold=0.3, max_missed=8)
        dets = [{"box": (10, 10, 50, 50), "label": "person", "score": 0.9}]
        tracker.update(dets, frame_index=0)
        # No detections — missed count should increase
        tracker.update([], frame_index=1)
        active = tracker.all_active()
        assert len(active) == 1
        assert active[0].missed == 1

    def test_track_removed_after_max_missed(self):
        tracker = IoUTracker(iou_threshold=0.3, max_missed=3)
        dets = [{"box": (10, 10, 50, 50), "label": "person", "score": 0.9}]
        tracker.update(dets, frame_index=0)
        # Miss 3 frames
        for i in range(1, 4):
            tracker.update([], frame_index=i)
        active = tracker.all_active()
        assert len(active) == 0

    def test_reset_clears_all(self):
        tracker = IoUTracker(iou_threshold=0.3, max_missed=8)
        dets = [{"box": (10, 10, 50, 50), "label": "person", "score": 0.9}]
        tracker.update(dets, frame_index=0)
        tracker.reset()
        assert len(tracker.all_active()) == 0

    def test_multiple_labels_independent(self):
        tracker = IoUTracker(iou_threshold=0.3, max_missed=8)
        dets = [
            {"box": (10, 10, 50, 50), "label": "person", "score": 0.9},
            {"box": (100, 100, 150, 150), "label": "car", "score": 0.8},
        ]
        active, _, new, _ = tracker.update(dets, frame_index=0)
        assert len(active) == 2
        assert len(new) == 2

    def test_custom_iou_threshold(self):
        tracker = IoUTracker(iou_threshold=0.9, max_missed=8)
        # Boxes with low overlap — should not match with high threshold
        dets1 = [{"box": (0, 0, 100, 100), "label": "person", "score": 0.9}]
        tracker.update(dets1, frame_index=0)
        dets2 = [{"box": (50, 50, 150, 150), "label": "person", "score": 0.9}]
        active, _, new, _ = tracker.update(dets2, frame_index=1)
        # With threshold 0.9, the overlap (~0.14) is too low
        assert len(new) == 1

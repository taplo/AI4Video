"""Tests for app.utils.Utils module."""
import pytest
from app.utils.Utils import buildPageLabels, group_by_field, GB28181CodeUtils


class TestBuildPageLabels:
    """Tests for buildPageLabels() function."""

    def test_first_page_no_prev(self):
        labels = buildPageLabels(page=1, page_num=5)
        # First page should not have "prev" navigation
        names = [l["name"] for l in labels]
        assert "上一页" not in names

    def test_middle_page_shows_prev_next(self):
        labels = buildPageLabels(page=3, page_num=5)
        names = [l["name"] for l in labels]
        assert "上一页" in names
        assert "下一页" in names

    def test_last_page_no_next(self):
        labels = buildPageLabels(page=5, page_num=5)
        names = [l["name"] for l in labels]
        assert "下一页" not in names

    def test_single_page(self):
        labels = buildPageLabels(page=1, page_num=1)
        assert len(labels) >= 1

    def test_page_beyond_total(self):
        labels = buildPageLabels(page=10, page_num=5)
        # Should still return labels without crashing
        assert isinstance(labels, list)

    def test_chinese_labels_default(self):
        labels = buildPageLabels(page=2, page_num=5, lang='zh')
        names = [l["name"] for l in labels]
        assert "首页" in names or "上一页" in names

    def test_page_numbers_included(self):
        labels = buildPageLabels(page=2, page_num=5)
        page_nums = [l["page"] for l in labels if isinstance(l["name"], int)]
        assert 1 in page_nums or 2 in page_nums


class TestGroupByField:
    """Tests for group_by_field() function."""

    def test_groups_by_stream_name(self):
        data = [
            {"stream_name": "cam1", "value": 1},
            {"stream_name": "cam2", "value": 2},
            {"stream_name": "cam1", "value": 3},
        ]
        result = group_by_field(data, "stream_name")
        assert len(result) == 2
        # One group should have 2 items, the other 1
        lengths = sorted([len(g) for g in result])
        assert lengths == [1, 2]

    def test_empty_list(self):
        result = group_by_field([], "stream_name")
        assert result == []

    def test_single_group(self):
        data = [
            {"type": "a", "value": 1},
            {"type": "a", "value": 2},
        ]
        result = group_by_field(data, "type")
        assert len(result) == 1
        assert len(result[0]) == 2

    def test_multiple_groups(self):
        data = [
            {"cat": "x"},
            {"cat": "y"},
            {"cat": "z"},
        ]
        result = group_by_field(data, "cat")
        assert len(result) == 3


class TestGB28181CodeUtils:
    """Tests for GB28181CodeUtils class."""

    def test_generate_by_time_format(self):
        gen = GB28181CodeUtils()
        code = gen.generate_by_time()
        assert isinstance(code, str)

    def test_length_is_20(self):
        gen = GB28181CodeUtils()
        code = gen.generate_by_time()
        assert len(code) == 20

    def test_custom_area_code(self):
        gen = GB28181CodeUtils(default_area_code="11000000")
        code = gen.generate_by_time()
        assert code.startswith("11000000")

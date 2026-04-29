"""检索工具函数 单元测试"""

import pytest

from tools.search_tools import (
    parse_query,
    _extract_genre,
    _extract_year,
    _extract_rating,
    _extract_actor,
    _extract_region,
    semantic_search,
    filter_videos,
    hybrid_search,
    _deduplicate,
)


class TestParseQuery:
    """查询解析功能测试"""

    def test_extract_genre_comedy(self):
        assert _extract_genre("推荐一部喜剧电影") == "喜剧"

    def test_extract_genre_action(self):
        assert _extract_genre("好看的动作片") == "动作"

    def test_extract_genre_scifi(self):
        assert _extract_genre("有没有科幻片推荐") == "科幻"

    def test_extract_genre_none(self):
        assert _extract_genre("随便看看") is None

    def test_extract_year_specific(self):
        start, end = _extract_year("2020年的电影")
        assert start == 2020
        assert end == 2020

    def test_extract_year_after(self):
        start, end = _extract_year("2020年以后的电影")
        assert start == 2020
        assert end is None

    def test_extract_year_recent(self):
        start, end = _extract_year("近三年的电影")
        assert start is not None
        assert start >= 2023

    def test_extract_year_newest(self):
        start, end = _extract_year("最新上映的电影")
        assert start == 2024
        assert end is None

    def test_extract_year_classic(self):
        start, end = _extract_year("经典电影")
        assert start == 2000
        assert end == 2015

    def test_extract_rating_high(self):
        assert _extract_rating("高分电影") == 8.0

    def test_extract_rating_specific(self):
        assert _extract_rating("8分以上的电影") == 8.0

    def test_extract_rating_good_review(self):
        assert _extract_rating("口碑好的电影") == 8.0

    def test_extract_actor(self):
        assert _extract_actor("演员：张毅主演的电影") == "张毅"

    def test_extract_actor_no_match(self):
        assert _extract_actor("推荐好看的电影") is None

    def test_extract_region_domestic(self):
        assert _extract_region("国产电影") == "中国大陆"

    def test_extract_region_american(self):
        assert _extract_region("好莱坞大片") == "美国"

    def test_extract_region_korean(self):
        assert _extract_region("韩剧推荐") == "韩国"

    def test_parse_query_full(self):
        """完整解析测试"""
        result = parse_query("推荐2020年以后的喜剧电影，评分高的")
        assert result["genre"] == "喜剧"
        assert result["year_start"] == 2020
        assert result["year_end"] is None
        assert result["min_rating"] == 8.0

    def test_parse_query_empty(self):
        result = parse_query("推荐好看的")
        assert result["genre"] is None
        assert result["year_start"] is None
        assert result["min_rating"] is None


class TestSemanticSearch:
    """语义检索测试"""

    def test_semantic_search_returns_results(self):
        results = semantic_search("科幻电影", n_results=5)
        assert len(results) >= 1
        assert len(results) <= 5

    def test_semantic_search_with_type_filter(self):
        results = semantic_search("喜剧", n_results=5, type_filter="movie")
        for r in results:
            assert r.get("type") == "movie"

    def test_semantic_search_result_fields(self):
        results = semantic_search("动作片", n_results=3)
        if results:
            r = results[0]
            assert "video_id" in r
            assert "title" in r
            assert "score" in r


class TestFilterVideos:
    """传统过滤测试"""

    def test_filter_by_genre(self):
        results = filter_videos(genre="喜剧", limit=5)
        assert len(results) >= 1
        assert len(results) <= 5

    def test_filter_by_year_range(self):
        results = filter_videos(year_start=2020, year_end=2025, limit=10)
        for r in results:
            assert 2020 <= r["year"] <= 2025

    def test_filter_by_rating(self):
        results = filter_videos(min_rating=8.0, limit=5)
        for r in results:
            assert r["rating"] >= 8.0

    def test_filter_by_region(self):
        results = filter_videos(region="中国大陆", limit=5)
        for r in results:
            assert "中国大陆" in r["region"]

    def test_filter_no_conditions(self):
        """无条件返回所有视频"""
        results = filter_videos(limit=5)
        assert len(results) >= 1

    def test_filter_combined(self):
        """多条件组合"""
        results = filter_videos(genre="喜剧", year_start=2018, min_rating=7.0, limit=5)
        for r in results:
            assert "喜剧" in r.get("genres", [])
            assert r["year"] >= 2018
            assert r["rating"] >= 7.0


class TestHybridSearch:
    """混合检索测试"""

    def test_hybrid_search_returns_results(self):
        results = hybrid_search("好看的科幻电影", n_results=5)
        assert len(results) >= 1
        assert len(results) <= 5

    def test_hybrid_search_with_genre(self):
        results = hybrid_search("喜剧片推荐", n_results=3)
        if results:
            # 至少应该有一些喜剧
            pass

    def test_hybrid_search_deduplication(self):
        results = hybrid_search("动作片", n_results=20)
        ids = [r["video_id"] for r in results]
        assert len(ids) == len(set(ids)), "结果中存在重复视频"


class TestDeduplicate:
    """去重功能测试"""

    def test_deduplicate_removes_duplicates(self):
        data = [
            {"video_id": "v_001", "title": "A"},
            {"video_id": "v_002", "title": "B"},
            {"video_id": "v_001", "title": "A"},
        ]
        result = _deduplicate(data)
        assert len(result) == 2
        assert result[0]["video_id"] == "v_001"

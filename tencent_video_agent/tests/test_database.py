"""数据库初始化与查询单元测试"""

import os
import tempfile
from pathlib import Path

import pytest

from db.sqlite_db import (
    get_connection,
    create_tables,
    import_categories,
    import_actors,
    import_directors,
    import_videos,
    get_stats,
    get_video_by_id,
    get_actor_by_id,
    get_videos_by_type,
    search_videos_by_title,
    get_actors_for_video,
    get_directors_for_video,
)
from db.chroma_db import search_similar, format_search_results


# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def sqlite_conn():
    """创建内存 SQLite 数据库用于测试"""
    conn = get_connection(":memory:")
    create_tables(conn)
    import_categories(conn)
    import_actors(conn)
    import_directors(conn)
    import_videos(conn)
    yield conn
    conn.close()


# ── SQLite 表结构测试 ────────────────────────────────────────────────


def test_tables_exist(sqlite_conn):
    """检查所有表是否已创建"""
    tables = sqlite_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    table_names = [r["name"] for r in tables]
    expected = ["actors", "categories", "directors", "video_actors", "video_directors", "videos"]
    for t in expected:
        assert t in table_names, f"缺少表: {t}"


# ── 数据量测试 ────────────────────────────────────────────────────────


def test_record_counts(sqlite_conn):
    """检查各表数据量正确"""
    stats = get_stats(sqlite_conn)
    assert stats["videos"] == 100
    assert stats["actors"] == 60
    assert stats["directors"] == 30
    assert stats["categories"] == 15
    assert stats["video_actor_relations"] > 0
    assert stats["video_director_relations"] > 0


# ── 查询功能测试 ──────────────────────────────────────────────────────


def test_get_video_by_id(sqlite_conn):
    """按 ID 查询视频"""
    video = get_video_by_id(sqlite_conn, "v_movie_001")
    assert video is not None
    assert video["title"] == "星际探索"
    assert video["type"] == "movie"
    assert 2000 <= video["year"] <= 2026

    # 不存在的 ID
    assert get_video_by_id(sqlite_conn, "v_nonexistent") is None


def test_get_actor_by_id(sqlite_conn):
    """按 ID 查询演员"""
    actor = get_actor_by_id(sqlite_conn, "a_001")
    assert actor is not None
    assert actor["name"] == "张毅"
    assert actor["gender"] in ("male", "female")

    # 不存在的 ID
    assert get_actor_by_id(sqlite_conn, "a_999") is None


def test_get_videos_by_type(sqlite_conn):
    """按类型查询视频"""
    movies = get_videos_by_type(sqlite_conn, "movie")
    assert len(movies) == 40
    for m in movies:
        assert m["type"] == "movie"

    documentaries = get_videos_by_type(sqlite_conn, "documentary")
    assert len(documentaries) == 8


def test_search_by_title_keyword(sqlite_conn):
    """按标题关键词搜索"""
    results = search_videos_by_title(sqlite_conn, "星际")
    assert len(results) >= 1
    assert all("星际" in r["title"] for r in results)

    # 无匹配
    results = search_videos_by_title(sqlite_conn, "___不存在的关键词___")
    assert len(results) == 0


def test_get_actors_for_video(sqlite_conn):
    """获取视频的演员列表"""
    actors = get_actors_for_video(sqlite_conn, "v_movie_001")
    assert len(actors) >= 1
    assert all(a["actor_id"].startswith("a_") for a in actors)


def test_get_directors_for_video(sqlite_conn):
    """获取视频的导演列表"""
    directors = get_directors_for_video(sqlite_conn, "v_movie_001")
    assert len(directors) >= 1
    assert all(d["director_id"].startswith("d_") for d in directors)


# ── Chroma 检索测试 ──────────────────────────────────────────────────


def test_chroma_search():
    """Chroma 语义检索基本功能"""
    results = search_similar("喜剧电影推荐", n_results=3)
    formatted = format_search_results(results)

    assert len(formatted) >= 1
    assert len(formatted) <= 3
    for item in formatted:
        assert "video_id" in item
        assert "title" in item
        assert "score" in item


def test_chroma_search_with_filter():
    """Chroma 带过滤条件的检索"""
    results = search_similar("科幻电影", n_results=3, filter_={"type": "movie"})
    formatted = format_search_results(results)

    if formatted:
        # 如果有结果，确保全部是电影
        for item in formatted:
            assert item["type"] == "movie"


def test_chroma_search_result_format():
    """Chroma 检索结果格式验证"""
    results = search_similar("动作片", n_results=5)
    formatted = format_search_results(results)

    for item in formatted:
        assert isinstance(item["video_id"], str)
        assert item["video_id"].startswith("v_")
        assert isinstance(item["title"], str)
        assert isinstance(item["score"], float)
        assert 0 <= item["score"] <= 1

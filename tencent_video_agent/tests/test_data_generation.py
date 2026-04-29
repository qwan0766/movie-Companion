"""腾讯视频模拟数据生成 单元测试"""

import json
import os
import sys
from pathlib import Path

# 添加项目根目录到 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.generate_data import (
    VideoType,
    generate_all,
)

DATA_DIR = PROJECT_ROOT / "data"


# ── 基础测试 ──────────────────────────────────────────────────────────


def test_generated_json_files_exist():
    """检查所有 JSON 文件是否已生成"""
    for filename in ("categories.json", "actors.json", "directors.json", "videos.json"):
        filepath = DATA_DIR / filename
        assert filepath.exists(), f"缺少文件: {filename}"
        assert filepath.stat().st_size > 0, f"文件为空: {filename}"


def test_generated_data_valid_json():
    """检查 JSON 文件格式是否合法"""
    for filename in ("categories.json", "actors.json", "directors.json", "videos.json"):
        data = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
        assert isinstance(data, list), f"{filename}: 根节点不是列表"


# ── 数据量测试 ────────────────────────────────────────────────────────


def test_record_counts():
    """检查各实体数量符合预期范围"""
    categories = json.loads((DATA_DIR / "categories.json").read_text(encoding="utf-8"))
    actors = json.loads((DATA_DIR / "actors.json").read_text(encoding="utf-8"))
    directors = json.loads((DATA_DIR / "directors.json").read_text(encoding="utf-8"))
    videos = json.loads((DATA_DIR / "videos.json").read_text(encoding="utf-8"))

    assert len(categories) == 15, f"分类数量应为 15，实际为 {len(categories)}"
    assert len(actors) == 60, f"演员数量应为 60，实际为 {len(actors)}"
    assert len(directors) == 30, f"导演数量应为 30，实际为 {len(directors)}"
    assert len(videos) == 100, f"视频数量应为 100，实际为 {len(videos)}"


def test_type_distribution():
    """检查各类型视频数量符合分布配置"""
    videos = json.loads((DATA_DIR / "videos.json").read_text(encoding="utf-8"))
    type_counts = {}
    for v in videos:
        t = v["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    assert type_counts.get("movie") == 40, f"电影数量应为 40，实际为 {type_counts.get('movie')}"
    assert type_counts.get("tv") == 25, f"电视剧数量应为 25，实际为 {type_counts.get('tv')}"
    assert type_counts.get("variety") == 15, f"综艺数量应为 15，实际为 {type_counts.get('variety')}"
    assert type_counts.get("animation") == 12, f"动漫数量应为 12，实际为 {type_counts.get('animation')}"
    assert type_counts.get("documentary") == 8, f"纪录片数量应为 8，实际为 {type_counts.get('documentary')}"


# ── 字段合法性测试 ────────────────────────────────────────────────────


def test_video_field_ranges():
    """检查视频字段值是否在合法范围内"""
    videos = json.loads((DATA_DIR / "videos.json").read_text(encoding="utf-8"))
    for v in videos:
        assert 1.0 <= v["rating"] <= 10.0, f"{v['video_id']}: 评分越界 {v['rating']}"
        assert 2000 <= v["year"] <= 2026, f"{v['video_id']}: 年份越界 {v['year']}"
        assert v["vote_count"] >= 1000, f"{v['video_id']}: 评分人数过少 {v['vote_count']}"
        assert v["type"] in [t.value for t in VideoType], f"{v['video_id']}: 无效类型 {v['type']}"
        assert v["status"] in ("completed", "ongoing", "upcoming"), f"{v['video_id']}: 无效状态 {v['status']}"
        assert len(v["title"]) > 0, f"{v['video_id']}: 标题为空"


def test_type_specific_fields():
    """检查不同类型视频的专属字段正确性"""
    videos = json.loads((DATA_DIR / "videos.json").read_text(encoding="utf-8"))
    for v in videos:
        if v["type"] == "movie":
            assert v["duration"] is not None, f"{v['video_id']}: 电影缺少 duration"
            assert v["episode_count"] is None, f"{v['video_id']}: 电影不应有 episode_count"
            assert 90 <= v["duration"] <= 180, f"{v['video_id']}: 电影时长异常 {v['duration']}"
        elif v["type"] in ("tv", "variety", "animation"):
            assert v["episode_count"] is not None, f"{v['video_id']}: {v['type']} 缺少 episode_count"
            assert v["duration"] is None, f"{v['video_id']}: {v['type']} 不应有 duration"
        elif v["type"] == "documentary":
            # 纪录片可以是电影或剧集形式
            pass


def test_actor_field_validity():
    """检查演员字段合法性"""
    actors = json.loads((DATA_DIR / "actors.json").read_text(encoding="utf-8"))
    for a in actors:
        assert a["gender"] in ("male", "female"), f"{a['actor_id']}: 无效性别"
        assert 1 <= a["popularity"] <= 100, f"{a['actor_id']}: 人气值越界"
        assert len(a["name"]) > 0, f"{a['actor_id']}: 姓名为空"


def test_director_field_validity():
    """检查导演字段合法性"""
    directors = json.loads((DATA_DIR / "directors.json").read_text(encoding="utf-8"))
    for d in directors:
        assert 1 <= d["popularity"] <= 100, f"{d['director_id']}: 人气值越界"
        assert len(d["name"]) > 0, f"{d['director_id']}: 姓名为空"


# ── 引用完整性测试 ────────────────────────────────────────────────────


def test_referential_integrity():
    """检查所有外键引用是否有效"""
    videos = json.loads((DATA_DIR / "videos.json").read_text(encoding="utf-8"))
    actors = json.loads((DATA_DIR / "actors.json").read_text(encoding="utf-8"))
    directors = json.loads((DATA_DIR / "directors.json").read_text(encoding="utf-8"))
    categories = json.loads((DATA_DIR / "categories.json").read_text(encoding="utf-8"))

    actor_ids = {a["actor_id"] for a in actors}
    director_ids = {d["director_id"] for d in directors}
    category_names = {c["name"] for c in categories}

    for v in videos:
        # 导演引用
        for did in v["director_ids"]:
            assert did in director_ids, f"{v['video_id']}: 导演 {did} 不存在"
        # 演员引用
        for aid in v["actor_ids"]:
            assert aid in actor_ids, f"{v['video_id']}: 演员 {aid} 不存在"
        # genres 来源于分类名称
        for genre in v["genres"]:
            assert genre in category_names, f"{v['video_id']}: genre '{genre}' 不在分类中"


def test_each_video_has_at_least_one_category():
    """每条视频至少关联一个分类"""
    videos = json.loads((DATA_DIR / "videos.json").read_text(encoding="utf-8"))
    for v in videos:
        assert len(v["genres"]) >= 1, f"{v['video_id']}: 没有关联分类"


def test_each_video_has_director():
    """每条视频至少有一位导演"""
    videos = json.loads((DATA_DIR / "videos.json").read_text(encoding="utf-8"))
    for v in videos:
        assert len(v["director_ids"]) >= 1, f"{v['video_id']}: 没有导演"


def test_each_video_has_actor():
    """每条视频至少有一位演员"""
    videos = json.loads((DATA_DIR / "videos.json").read_text(encoding="utf-8"))
    for v in videos:
        assert len(v["actor_ids"]) >= 1, f"{v['video_id']}: 没有演员"


# ── 可复现性测试 ──────────────────────────────────────────────────────


def test_reproducibility():
    """检查相同 seed 生成相同数据"""
    cats1, actors1, dirs1, vids1 = generate_all()
    cats2, actors2, dirs2, vids2 = generate_all()

    assert len(cats1) == len(cats2)
    assert len(actors1) == len(actors2)
    assert len(dirs1) == len(dirs2)
    assert len(vids1) == len(vids2)

    for i in range(len(vids1)):
        assert vids1[i].video_id == vids2[i].video_id
        assert vids1[i].title == vids2[i].title
        assert vids1[i].rating == vids2[i].rating


# ── 地区分布测试 ──────────────────────────────────────────────────────


def test_region_coverage():
    """检查地区分布是否合理"""
    videos = json.loads((DATA_DIR / "videos.json").read_text(encoding="utf-8"))
    regions = set(v["region"] for v in videos)
    assert "中国大陆" in regions, "缺少中国大陆视频"
    # 至少包含 3 个不同地区
    assert len(regions) >= 3, f"地区覆盖不足: {regions}"

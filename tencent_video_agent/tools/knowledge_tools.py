"""知识查询工具 — Neo4j 优先，SQLite 兜底"""

from pathlib import Path

from db.sqlite_db import (
    get_connection,
    get_db_path,
    get_actors_for_video,
    get_directors_for_video,
)

# ── SQLite 兜底查询 ──────────────────────────────────────────────────


def _get_actor_films_sqlite(actor_name: str) -> list[dict]:
    """SQLite 兜底：查询演员参演作品"""
    db_path = get_db_path()
    conn = get_connection(db_path)
    rows = conn.execute(
        """
        SELECT v.video_id, v.title, v.year, v.rating, v.type, v.region
        FROM videos v
        JOIN video_actors va ON v.video_id = va.video_id
        JOIN actors a ON va.actor_id = a.actor_id
        WHERE a.name LIKE ?
        ORDER BY v.year DESC
        """,
        (f"%{actor_name}%",),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _get_director_films_sqlite(director_name: str) -> list[dict]:
    """SQLite 兜底：查询导演作品"""
    db_path = get_db_path()
    conn = get_connection(db_path)
    rows = conn.execute(
        """
        SELECT v.video_id, v.title, v.year, v.rating, v.type, v.region
        FROM videos v
        JOIN video_directors vd ON v.video_id = vd.video_id
        JOIN directors d ON vd.director_id = d.director_id
        WHERE d.name LIKE ?
        ORDER BY v.year DESC
        """,
        (f"%{director_name}%",),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _get_video_details_sqlite(title: str) -> dict | None:
    """SQLite 兜底：查询视频详细信息"""
    db_path = get_db_path()
    conn = get_connection(db_path)
    row = conn.execute(
        "SELECT * FROM videos WHERE title LIKE ?", (f"%{title}%",)
    ).fetchone()
    if not row:
        conn.close()
        return None

    video = dict(row)
    if isinstance(video.get("genres"), str):
        video["genres"] = video["genres"].split(",") if video["genres"] else []

    # 演员和导演
    video["actors"] = get_actors_for_video(conn, video["video_id"])
    video["directors"] = get_directors_for_video(conn, video["video_id"])
    conn.close()
    return video


def _search_entities_sqlite(keyword: str) -> dict[str, list[dict]]:
    """SQLite 兜底：关键词搜索"""
    db_path = get_db_path()
    conn = get_connection(db_path)

    actors = [
        dict(r) for r in conn.execute(
            "SELECT * FROM actors WHERE name LIKE ? LIMIT 5",
            (f"%{keyword}%",),
        ).fetchall()
    ]

    directors = [
        dict(r) for r in conn.execute(
            "SELECT * FROM directors WHERE name LIKE ? LIMIT 5",
            (f"%{keyword}%",),
        ).fetchall()
    ]

    videos = [
        dict(r) for r in conn.execute(
            "SELECT * FROM videos WHERE title LIKE ? LIMIT 5",
            (f"%{keyword}%",),
        ).fetchall()
    ]

    conn.close()
    return {"actors": actors, "directors": directors, "videos": videos}


# ── Neo4j 检测 ──────────────────────────────────────────────────────


def _neo4j_available() -> bool:
    """检测 Neo4j 服务是否可用"""
    try:
        from knowledge_graph.kg_queries import check_connection
        return check_connection()
    except Exception:
        return False


# ── 统一查询入口 ─────────────────────────────────────────────────────


def knowledge_search(query_type: str, query_value: str) -> dict:
    """统一知识查询入口（自动检测 Neo4j / SQLite 兜底）

    Args:
        query_type: 查询类型
            - "actor_films": 演员作品
            - "director_films": 导演作品
            - "video_details": 视频详情
            - "search": 关键词搜索
        query_value: 查询值

    Returns:
        {"type": str, "data": ..., "source": "neo4j"|"sqlite"}
    """
    if _neo4j_available():
        try:
            from knowledge_graph.kg_queries import (
                get_actor_films,
                get_director_films,
                get_video_details,
                search_entities,
            )

            if query_type == "actor_films":
                data = get_actor_films(query_value)
                return {"type": "actor_films", "data": data, "source": "neo4j"}

            elif query_type == "director_films":
                data = get_director_films(query_value)
                return {"type": "director_films", "data": data, "source": "neo4j"}

            elif query_type == "video_details":
                data = get_video_details(query_value)
                return {"type": "video_details", "data": data, "source": "neo4j"}

            elif query_type == "search":
                data = search_entities(query_value)
                return {"type": "search", "data": data, "source": "neo4j"}

        except Exception:
            pass  # 降级到 SQLite

    # SQLite 兜底
    if query_type == "actor_films":
        data = _get_actor_films_sqlite(query_value)
        return {"type": "actor_films", "data": data, "source": "sqlite"}

    elif query_type == "director_films":
        data = _get_director_films_sqlite(query_value)
        return {"type": "director_films", "data": data, "source": "sqlite"}

    elif query_type == "video_details":
        data = _get_video_details_sqlite(query_value)
        return {"type": "video_details", "data": data, "source": "sqlite"}

    elif query_type == "search":
        data = _search_entities_sqlite(query_value)
        return {"type": "search", "data": data, "source": "sqlite"}

    return {"type": query_type, "data": [], "source": "none"}


# ── 查询类型识别 ────────────────────────────────────────────────────


def detect_query_type(text: str) -> tuple[str, str]:
    """从用户查询中识别查询类型和实体名称

    Args:
        text: 用户输入

    Returns:
        (query_type, entity_name)
    """
    # 演员查询
    import re
    m = re.search(r"(?:演员|.?星).{0,4}(?:演过|拍过|作品|出演|参演|电影|代表作)", text)
    if m:
        # 尝试提取演员名
        name = _extract_entity_name(text, m.start())
        if name:
            return ("actor_films", name)

    # 导演查询
    m = re.search(r"(?:导演).{0,4}(?:拍过|执导|作品|电影|代表作)", text)
    if m:
        name = _extract_entity_name(text, m.start())
        if name:
            return ("director_films", name)

    # "谁演的" → 查演员
    if "谁演" in text or "主演是谁" in text:
        m = re.search(r"[《](.+?)[》]", text)
        if m:
            return ("video_details", m.group(1))
        return ("search", text)

    # "介绍一下" → 查详情
    if "介绍" in text:
        m = re.search(r"[《](.+?)[》]", text)
        if m:
            return ("video_details", m.group(1))
        # 可能查演员或导演
        for prefix in ["演员", "导演"]:
            if prefix in text:
                name = _extract_entity_name(text, text.find(prefix) + len(prefix))
                if name:
                    return (f"{'actor' if '演员' in prefix else 'director'}_films", name)
        # "介绍一下张毅" → 提取"介绍"后面的名字
        m = re.search(r"介绍(?:一下)?([一-鿿]{2,4})", text)
        if m:
            return ("actor_films", m.group(1))
        return ("search", text)

    # 包含演员名 + 作品
    for keyword in ["演过", "拍过", "作品"]:
        if keyword in text:
            name = _extract_entity_name(text, text.find(keyword) - 4, text.find(keyword))
            if name:
                return ("actor_films", name)

    # 书名号内容 → 视频详情
    m = re.search(r"[《](.+?)[》]", text)
    if m:
        return ("video_details", m.group(1))

    return ("search", text)


def _extract_entity_name(text: str, start: int = 0, end: int | None = None) -> str | None:
    """从文本中提取实体名称（2-4个中文字符）"""
    import re
    if end is not None:
        segment = text[start:end]
    else:
        segment = text[max(0, start - 6):start + 2]

    m = re.search(r"([一-鿿]{2,4})", segment)
    return m.group(1) if m else None

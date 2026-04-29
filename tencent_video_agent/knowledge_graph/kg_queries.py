"""Neo4j 知识图谱 — Cypher 查询函数"""

import os
from typing import Any


def _get_driver():
    """获取 Neo4j 驱动（惰性导入）"""
    from neo4j import GraphDatabase
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    return GraphDatabase.driver(uri, auth=(user, password))


def _query(cypher: str, params: dict | None = None) -> list[dict]:
    """执行 Cypher 查询"""
    driver = _get_driver()
    try:
        with driver.session() as session:
            result = session.run(cypher, params or {})
            return [dict(r) for r in result]
    finally:
        driver.close()


def get_actor_films(actor_name: str) -> list[dict]:
    """查询演员参演作品"""
    cypher = """
    MATCH (a:Actor {name: $name})-[:ACTED_IN]->(v:Video)
    RETURN v.title AS title, v.year AS year, v.rating AS rating,
           v.type AS type, v.video_id AS video_id
    ORDER BY v.year DESC
    """
    return _query(cypher, {"name": actor_name})


def get_director_films(director_name: str) -> list[dict]:
    """查询导演作品"""
    cypher = """
    MATCH (d:Director {name: $name})-[:DIRECTED]->(v:Video)
    RETURN v.title AS title, v.year AS year, v.rating AS rating,
           v.type AS type, v.video_id AS video_id
    ORDER BY v.year DESC
    """
    return _query(cypher, {"name": director_name})


def get_video_details(title: str) -> dict | None:
    """查询视频详细信息（含演员、导演、分类）"""
    cypher = """
    MATCH (v:Video {title: $title})
    OPTIONAL MATCH (v)<-[:ACTED_IN]-(a:Actor)
    OPTIONAL MATCH (v)<-[:DIRECTED]-(d:Director)
    OPTIONAL MATCH (v)-[:BELONGS_TO]->(c:Category)
    RETURN v {.video_id, .title, .year, .rating, .type, .description} AS video,
           collect(DISTINCT a {.actor_id, .name}) AS actors,
           collect(DISTINCT d {.director_id, .name}) AS directors,
           collect(DISTINCT c {.category_id, .name}) AS categories
    """
    results = _query(cypher, {"title": title})
    return results[0] if results else None


def get_actor_info(actor_name: str) -> dict | None:
    """查询演员信息（含参演作品统计）"""
    cypher = """
    MATCH (a:Actor {name: $name})
    OPTIONAL MATCH (a)-[:ACTED_IN]->(v:Video)
    RETURN a {.actor_id, .name, .gender, .birth_year, .nationality, .popularity} AS actor,
           count(v) AS film_count,
           CASE WHEN count(v) > 0 THEN round(avg(v.rating), 1) ELSE null END AS avg_rating
    """
    results = _query(cypher, {"name": actor_name})
    return results[0] if results else None


def get_director_info(director_name: str) -> dict | None:
    """查询导演信息（含作品统计）"""
    cypher = """
    MATCH (d:Director {name: $name})
    OPTIONAL MATCH (d)-[:DIRECTED]->(v:Video)
    RETURN d {.director_id, .name, .birth_year, .nationality, .popularity} AS director,
           count(v) AS film_count,
           CASE WHEN count(v) > 0 THEN round(avg(v.rating), 1) ELSE null END AS avg_rating
    """
    results = _query(cypher, {"name": director_name})
    return results[0] if results else None


def search_entities(keyword: str) -> dict[str, list[dict]]:
    """全文搜索（演员/导演/视频）"""
    cypher = """
    CALL {
        MATCH (a:Actor) WHERE a.name CONTAINS $keyword
        RETURN a AS entity, 'actor' AS label LIMIT 5
        UNION
        MATCH (d:Director) WHERE d.name CONTAINS $keyword
        RETURN d AS entity, 'director' AS label LIMIT 5
        UNION
        MATCH (v:Video) WHERE v.title CONTAINS $keyword
        RETURN v AS entity, 'video' AS label LIMIT 5
    }
    RETURN entity, label
    """
    results = _query(cypher, {"keyword": keyword})
    actors: list[dict] = []
    directors: list[dict] = []
    videos: list[dict] = []

    for row in results:
        entity = dict(row["entity"])
        label = row["label"]
        if label == "actor":
            actors.append(entity)
        elif label == "director":
            directors.append(entity)
        elif label == "video":
            videos.append(entity)

    return {"actors": actors, "directors": directors, "videos": videos}


# ── 连接检测 ─────────────────────────────────────────────────────────


def check_connection() -> bool:
    """检查 Neo4j 服务是否可用"""
    try:
        driver = _get_driver()
        driver.verify_connectivity()
        driver.close()
        return True
    except Exception:
        return False

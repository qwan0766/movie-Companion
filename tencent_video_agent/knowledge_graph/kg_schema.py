"""Neo4j 知识图谱 — 数据模型定义与数据导入"""

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# ── Cypher DDL ───────────────────────────────────────────────────────

CREATE_CONSTRAINTS = """
CREATE CONSTRAINT video_id IF NOT EXISTS FOR (v:Video) REQUIRE v.video_id IS UNIQUE;
CREATE CONSTRAINT actor_id IF NOT EXISTS FOR (a:Actor) REQUIRE a.actor_id IS UNIQUE;
CREATE CONSTRAINT director_id IF NOT EXISTS FOR (d:Director) REQUIRE d.director_id IS UNIQUE;
CREATE CONSTRAINT category_id IF NOT EXISTS FOR (c:Category) REQUIRE c.category_id IS UNIQUE;
"""

MERGE_VIDEOS = """
UNWIND $videos AS v
MERGE (video:Video {video_id: v.video_id})
SET video.title = v.title,
    video.year = v.year,
    video.rating = v.rating,
    video.type = v.type,
    video.description = v.description,
    video.region = v.region
"""

MERGE_ACTORS = """
UNWIND $actors AS a
MERGE (actor:Actor {actor_id: a.actor_id})
SET actor.name = a.name,
    actor.gender = a.gender,
    actor.birth_year = a.birth_year,
    actor.nationality = a.nationality,
    actor.popularity = a.popularity
"""

MERGE_DIRECTORS = """
UNWIND $directors AS d
MERGE (director:Director {director_id: d.director_id})
SET director.name = d.name,
    director.birth_year = d.birth_year,
    director.nationality = d.nationality,
    director.popularity = d.popularity
"""

MERGE_CATEGORIES = """
UNWIND $categories AS c
MERGE (cat:Category {category_id: c.category_id})
SET cat.name = c.name
"""

CREATE_ACTED_IN = """
UNWIND $relations AS r
MATCH (a:Actor {actor_id: r.actor_id})
MATCH (v:Video {video_id: r.video_id})
MERGE (a)-[:ACTED_IN]->(v)
"""

CREATE_DIRECTED = """
UNWIND $relations AS r
MATCH (d:Director {director_id: r.director_id})
MATCH (v:Video {video_id: r.video_id})
MERGE (d)-[:DIRECTED]->(v)
"""

CREATE_BELONGS_TO = """
UNWIND $relations AS r
MATCH (v:Video {video_id: r.video_id})
MATCH (c:Category {name: r.genre})
MERGE (v)-[:BELONGS_TO]->(c)
"""


def load_json(filename: str) -> list[dict]:
    """加载 JSON 数据"""
    filepath = DATA_DIR / filename
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def prepare_relations(videos: list[dict]) -> dict:
    """从视频数据中提取关系列表"""
    acted_in = []
    directed = []
    belongs_to = []

    for v in videos:
        for aid in v.get("actor_ids", []):
            acted_in.append({"actor_id": aid, "video_id": v["video_id"]})
        for did in v.get("director_ids", []):
            directed.append({"director_id": did, "video_id": v["video_id"]})
        for genre in v.get("genres", []):
            belongs_to.append({"video_id": v["video_id"], "genre": genre})

    return {
        "acted_in": acted_in,
        "directed": directed,
        "belongs_to": belongs_to,
    }


def import_to_neo4j(driver) -> dict:
    """将 JSON 数据导入 Neo4j

    Args:
        driver: neo4j.GraphDatabase.driver 实例

    Returns:
        导入统计
    """
    videos = load_json("videos.json")
    actors = load_json("actors.json")
    directors = load_json("directors.json")
    categories = load_json("categories.json")
    relations = prepare_relations(videos)

    stats = {"videos": 0, "actors": 0, "directors": 0, "categories": 0,
             "acted_in": 0, "directed": 0, "belongs_to": 0}

    with driver.session() as session:
        # 约束
        for stmt in CREATE_CONSTRAINTS.split(";"):
            if stmt.strip():
                session.run(stmt.strip() + ";")

        # 导入节点
        result = session.run(MERGE_VIDEOS, {"videos": videos})
        stats["videos"] = len(videos)

        session.run(MERGE_ACTORS, {"actors": actors})
        stats["actors"] = len(actors)

        session.run(MERGE_DIRECTORS, {"directors": directors})
        stats["directors"] = len(directors)

        session.run(MERGE_CATEGORIES, {"categories": categories})
        stats["categories"] = len(categories)

        # 导入关系
        session.run(CREATE_ACTED_IN, {"relations": relations["acted_in"]})
        stats["acted_in"] = len(relations["acted_in"])

        session.run(CREATE_DIRECTED, {"relations": relations["directed"]})
        stats["directed"] = len(relations["directed"])

        session.run(CREATE_BELONGS_TO, {"relations": relations["belongs_to"]})
        stats["belongs_to"] = len(relations["belongs_to"])

    return stats


def check_connection(uri: str | None = None, user: str | None = None,
                     password: str | None = None) -> bool:
    """检查 Neo4j 连接是否可用"""
    try:
        from neo4j import GraphDatabase
        uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = user or os.getenv("NEO4J_USER", "neo4j")
        password = password or os.getenv("NEO4J_PASSWORD", "password")
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        driver.close()
        return True
    except Exception:
        return False

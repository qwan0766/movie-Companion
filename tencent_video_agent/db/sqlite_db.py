"""SQLite 数据库初始化与数据导入"""

import json
import os
import sqlite3
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# 默认数据库路径（可通过环境变量覆盖）
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "tencent_video.db"


# ── DDL ──────────────────────────────────────────────────────────────

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS videos (
    video_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    original_title TEXT,
    description TEXT,
    year INTEGER,
    region TEXT,
    language TEXT,
    type TEXT,
    genres TEXT,
    rating REAL,
    vote_count INTEGER,
    episode_count INTEGER,
    duration INTEGER,
    status TEXT
);

CREATE TABLE IF NOT EXISTS actors (
    actor_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    gender TEXT,
    birth_year INTEGER,
    nationality TEXT,
    bio TEXT,
    popularity INTEGER
);

CREATE TABLE IF NOT EXISTS directors (
    director_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    birth_year INTEGER,
    nationality TEXT,
    bio TEXT,
    popularity INTEGER
);

CREATE TABLE IF NOT EXISTS categories (
    category_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS video_actors (
    video_id TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    PRIMARY KEY (video_id, actor_id),
    FOREIGN KEY (video_id) REFERENCES videos(video_id),
    FOREIGN KEY (actor_id) REFERENCES actors(actor_id)
);

CREATE TABLE IF NOT EXISTS video_directors (
    video_id TEXT NOT NULL,
    director_id TEXT NOT NULL,
    PRIMARY KEY (video_id, director_id),
    FOREIGN KEY (video_id) REFERENCES videos(video_id),
    FOREIGN KEY (director_id) REFERENCES directors(director_id)
);
"""


# ── 数据库连接 ───────────────────────────────────────────────────────


def get_db_path() -> Path:
    """获取数据库路径"""
    env_path = os.getenv("SQLITE_DB_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """获取数据库连接"""
    path = db_path or get_db_path()
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ── 建表 ─────────────────────────────────────────────────────────────


def create_tables(conn: sqlite3.Connection) -> None:
    """创建所有表"""
    conn.executescript(CREATE_TABLES_SQL)
    conn.commit()


# ── JSON 导入 ────────────────────────────────────────────────────────


def load_json(filename: str) -> list[dict]:
    """加载 JSON 数据文件"""
    filepath = DATA_DIR / filename
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def import_categories(conn: sqlite3.Connection) -> int:
    """导入分类数据"""
    data = load_json("categories.json")
    conn.executemany(
        "INSERT OR IGNORE INTO categories (category_id, name, description) "
        "VALUES (:category_id, :name, :description)",
        data,
    )
    conn.commit()
    return len(data)


def import_actors(conn: sqlite3.Connection) -> int:
    """导入演员数据"""
    data = load_json("actors.json")
    conn.executemany(
        "INSERT OR IGNORE INTO actors (actor_id, name, gender, birth_year, "
        "nationality, bio, popularity) "
        "VALUES (:actor_id, :name, :gender, :birth_year, :nationality, :bio, :popularity)",
        data,
    )
    conn.commit()
    return len(data)


def import_directors(conn: sqlite3.Connection) -> int:
    """导入导演数据"""
    data = load_json("directors.json")
    conn.executemany(
        "INSERT OR IGNORE INTO directors (director_id, name, birth_year, "
        "nationality, bio, popularity) "
        "VALUES (:director_id, :name, :birth_year, :nationality, :bio, :popularity)",
        data,
    )
    conn.commit()
    return len(data)


def import_videos(conn: sqlite3.Connection) -> tuple[int, int, int]:
    """导入视频数据及关联关系"""
    data = load_json("videos.json")

    # 导入视频主体
    video_rows = []
    video_actor_rows = []
    video_director_rows = []

    for v in data:
        genres_str = ",".join(v.get("genres", []))
        video_rows.append({
            "video_id": v["video_id"],
            "title": v["title"],
            "original_title": v.get("original_title"),
            "description": v.get("description", ""),
            "year": v.get("year"),
            "region": v.get("region", ""),
            "language": v.get("language", ""),
            "type": v.get("type", ""),
            "genres": genres_str,
            "rating": v.get("rating"),
            "vote_count": v.get("vote_count", 0),
            "episode_count": v.get("episode_count"),
            "duration": v.get("duration"),
            "status": v.get("status", ""),
        })

        for aid in v.get("actor_ids", []):
            video_actor_rows.append((v["video_id"], aid))

        for did in v.get("director_ids", []):
            video_director_rows.append((v["video_id"], did))

    conn.executemany(
        "INSERT OR IGNORE INTO videos (video_id, title, original_title, "
        "description, year, region, language, type, genres, rating, "
        "vote_count, episode_count, duration, status) "
        "VALUES (:video_id, :title, :original_title, :description, :year, "
        ":region, :language, :type, :genres, :rating, :vote_count, "
        ":episode_count, :duration, :status)",
        video_rows,
    )

    conn.executemany(
        "INSERT OR IGNORE INTO video_actors (video_id, actor_id) VALUES (?, ?)",
        video_actor_rows,
    )

    conn.executemany(
        "INSERT OR IGNORE INTO video_directors (video_id, director_id) VALUES (?, ?)",
        video_director_rows,
    )

    conn.commit()
    return len(data), len(video_actor_rows), len(video_director_rows)


# ── 查询函数 ─────────────────────────────────────────────────────────


def get_video_by_id(conn: sqlite3.Connection, video_id: str) -> dict | None:
    """根据 ID 查询视频"""
    row = conn.execute("SELECT * FROM videos WHERE video_id = ?", (video_id,)).fetchone()
    return dict(row) if row else None


def get_actor_by_id(conn: sqlite3.Connection, actor_id: str) -> dict | None:
    """根据 ID 查询演员"""
    row = conn.execute("SELECT * FROM actors WHERE actor_id = ?", (actor_id,)).fetchone()
    return dict(row) if row else None


def get_videos_by_type(conn: sqlite3.Connection, type_: str) -> list[dict]:
    """按类型查询视频"""
    rows = conn.execute("SELECT * FROM videos WHERE type = ?", (type_,)).fetchall()
    return [dict(r) for r in rows]


def get_videos_by_year_range(conn: sqlite3.Connection, start: int, end: int) -> list[dict]:
    """按年份范围查询视频"""
    rows = conn.execute(
        "SELECT * FROM videos WHERE year >= ? AND year <= ? ORDER BY year",
        (start, end),
    ).fetchall()
    return [dict(r) for r in rows]


def search_videos_by_title(conn: sqlite3.Connection, keyword: str) -> list[dict]:
    """按标题关键词搜索视频"""
    rows = conn.execute(
        "SELECT * FROM videos WHERE title LIKE ?",
        (f"%{keyword}%",),
    ).fetchall()
    return [dict(r) for r in rows]


def get_actors_for_video(conn: sqlite3.Connection, video_id: str) -> list[dict]:
    """获取某视频的演员"""
    rows = conn.execute(
        "SELECT a.* FROM actors a "
        "JOIN video_actors va ON a.actor_id = va.actor_id "
        "WHERE va.video_id = ?",
        (video_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_directors_for_video(conn: sqlite3.Connection, video_id: str) -> list[dict]:
    """获取某视频的导演"""
    rows = conn.execute(
        "SELECT d.* FROM directors d "
        "JOIN video_directors vd ON d.director_id = vd.director_id "
        "WHERE vd.video_id = ?",
        (video_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_stats(conn: sqlite3.Connection) -> dict:
    """获取数据统计"""
    counts = {}
    for table in ("videos", "actors", "directors", "categories"):
        row = conn.execute(f"SELECT COUNT(*) as cnt FROM {table}").fetchone()
        counts[table] = row["cnt"]

    row = conn.execute("SELECT COUNT(*) as cnt FROM video_actors").fetchone()
    counts["video_actor_relations"] = row["cnt"]

    row = conn.execute("SELECT COUNT(*) as cnt FROM video_directors").fetchone()
    counts["video_director_relations"] = row["cnt"]

    return counts


# ── 初始化 ────────────────────────────────────────────────────────────


def init_database(db_path: Path | None = None) -> sqlite3.Connection:
    """初始化 SQLite 数据库：建表 + 导入数据"""
    conn = get_connection(db_path)

    print("[SQLite] 创建表结构...")
    create_tables(conn)

    print("[SQLite] 导入分类...")
    cat_count = import_categories(conn)
    print(f"  -> {cat_count} 个分类")

    print("[SQLite] 导入演员...")
    actor_count = import_actors(conn)
    print(f"  -> {actor_count} 位演员")

    print("[SQLite] 导入导演...")
    dir_count = import_directors(conn)
    print(f"  -> {dir_count} 位导演")

    print("[SQLite] 导入视频及关联关系...")
    v_count, va_count, vd_count = import_videos(conn)
    print(f"  -> {v_count} 条视频, {va_count} 条演职员关联, {vd_count} 条导演关联")

    stats = get_stats(conn)
    print(f"[SQLite] 总计: {stats}")

    return conn


if __name__ == "__main__":
    init_database()

"""视频检索工具函数 — 语义检索 + 传统过滤 + 混合检索"""

import re
from pathlib import Path

from db.chroma_db import search_similar, format_search_results
from db.sqlite_db import (
    get_connection,
    get_db_path,
)

# ── 类型关键词映射 ───────────────────────────────────────────────────

GENRE_KEYWORDS = {
    "喜剧": ["喜剧", "搞笑", "幽默", "欢乐", "轻松"],
    "动作": ["动作", "打斗", "武打", "功夫", "警匪", "犯罪"],
    "科幻": ["科幻", "科幻", "未来", "外星", "AI", "机器人", "赛博"],
    "爱情": ["爱情", "恋爱", "浪漫", "言情"],
    "悬疑": ["悬疑", "推理", "烧脑", "反转", "侦探"],
    "剧情": ["剧情", "剧情", "故事"],
    "古装": ["古装", "宫廷", "历史", "古代", "武侠"],
    "奇幻": ["奇幻", "魔法", "奇幻"],
    "犯罪": ["犯罪", "警匪", "黑帮", "卧底"],
    "恐怖": ["恐怖", "惊悚", "吓人", "鬼"],
    "战争": ["战争", "战斗", "战役", "军旅"],
    "动画": ["动画", "动漫", "卡通"],
    "纪录片": ["纪录片", "纪实", "真实"],
    "真人秀": ["真人秀", "真人秀"],
    "脱口秀": ["脱口秀", "脱口秀"],
}

TYPE_KEYWORDS = {
    "movie": ["电影", "片子", "影片"],
    "tv": ["电视剧", "剧集", "剧版", "追剧"],
    "variety": ["综艺", "真人秀"],
    "animation": ["动漫", "动画", "番剧"],
    "documentary": ["纪录片", "纪实"],
}

# ── 查询解析 ─────────────────────────────────────────────────────────


def _extract_genre(text: str) -> str | None:
    """从查询中提取类型"""
    for genre, keywords in GENRE_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return genre
    return None


def _extract_video_type(text: str) -> str | None:
    """从查询中提取内容类型"""
    for video_type, keywords in TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return video_type
    return None


def _extract_year(text: str) -> tuple[int | None, int | None]:
    """从查询中提取年份范围

    Returns:
        (year_start, year_end)
    """
    # 中文数字映射
    chinese_num = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
                   "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}

    # 具体年份: 2020年
    m = re.search(r"(\d{4})年", text)
    if m:
        year = int(m.group(1))
        if "后" in text or "以后" in text or "之后" in text:
            return (year, None)
        elif "前" in text or "以前" in text or "之前" in text:
            return (None, year)
        return (year, year)

    # 近N年（支持中文数字: 近三年, 近5年）
    m = re.search(r"近(\d|[一二两三四五六七八九十]+)年", text)
    if m:
        num_str = m.group(1)
        n = int(num_str) if num_str.isdigit() else chinese_num.get(num_str, 3)
        return (2026 - n, None)

    # "经典"和"老片" → 早些年
    if "经典" in text or "老片" in text:
        return (2000, 2015)

    # "最新" → 近两年
    if "最新" in text or "新上映" in text or "最近" in text:
        return (2024, None)

    return (None, None)


def _extract_rating(text: str) -> float | None:
    """从查询中提取最低评分要求"""
    m = re.search(r"(\d+\.?\d*)[分以上]", text)
    if m:
        return float(m.group(1))
    if "高分" in text or "评分高" in text or "口碑好" in text:
        return 8.0
    if "评分" in text and ("高" in text or "好" in text):
        return 8.0
    return None


def _extract_actor(text: str) -> str | None:
    """从查询中提取演员名"""
    m = re.search(r"(?:演员|主演|饰演者|出演者)[：:]?\s*([一-鿿]{2,4}?)(?=[的演主出等，。、]|$)", text)
    if m:
        return m.group(1)
    return None


def _extract_region(text: str) -> str | None:
    """从查询中提取地区偏好"""
    region_map = {
        "国产": "中国大陆",
        "国内": "中国大陆",
        "华语": "中国大陆",
        "美剧": "美国",
        "好莱坞": "美国",
        "美国": "美国",
        "韩剧": "韩国",
        "韩国": "韩国",
        "日剧": "日本",
        "日本": "日本",
        "英剧": "英国",
        "英国": "英国",
    }
    for keyword, region in region_map.items():
        if keyword in text:
            return region
    return None


def parse_query(query: str) -> dict:
    """从自然语言查询中提取结构化过滤条件

    Args:
        query: 用户查询文本

    Returns:
        {"keywords": str, "genre": str|None, "year_start": int|None,
         "year_end": int|None, "min_rating": float|None,
         "actor": str|None, "region": str|None, "type": str|None}
    """
    return {
        "keywords": query,
        "genre": _extract_genre(query),
        "type": _extract_video_type(query),
        "year_start": _extract_year(query)[0],
        "year_end": _extract_year(query)[1],
        "min_rating": _extract_rating(query),
        "actor": _extract_actor(query),
        "region": _extract_region(query),
    }


# ── 语义检索 ─────────────────────────────────────────────────────────


def semantic_search(
    query: str,
    n_results: int = 20,
    type_filter: str | None = None,
    min_rating: float | None = None,
) -> list[dict]:
    """语义相似检索

    Args:
        query: 搜索文本
        n_results: 返回结果数
        type_filter: 类型过滤（movie/tv/variety/animation/documentary）
        min_rating: 最低评分

    Returns:
        按相似度排序的结果列表
    """
    filter_ = {}
    if type_filter:
        filter_["type"] = type_filter
    if min_rating:
        filter_["rating"] = {"$gte": min_rating}

    where = filter_ if filter_ else None
    results = search_similar(query, n_results=n_results, filter_=where)
    formatted = format_search_results(results)
    return formatted


# ── 传统过滤 ─────────────────────────────────────────────────────────


def filter_videos(
    genre: str | None = None,
    year_start: int | None = None,
    year_end: int | None = None,
    actor_name: str | None = None,
    director_name: str | None = None,
    region: str | None = None,
    type_filter: str | None = None,
    min_rating: float | None = None,
    sort_by: str = "rating",
    limit: int = 20,
) -> list[dict]:
    """结构化条件过滤

    Args:
        genre: 类型（喜剧/动作/科幻等）
        year_start: 起始年份
        year_end: 截止年份
        actor_name: 演员姓名
        director_name: 导演姓名
        region: 地区
        type_filter: 内容类型（movie/tv/variety/animation/documentary）
        min_rating: 最低评分
        sort_by: 排序字段（rating/year）
        limit: 结果数量

    Returns:
        过滤后的视频列表
    """
    db_path = get_db_path()
    conn = get_connection(db_path)

    conditions: list[str] = []
    params: list = []

    if genre:
        conditions.append("v.genres LIKE ?")
        params.append(f"%{genre}%")

    if type_filter:
        conditions.append("v.type = ?")
        params.append(type_filter)

    if year_start is not None:
        conditions.append("v.year >= ?")
        params.append(year_start)

    if year_end is not None:
        conditions.append("v.year <= ?")
        params.append(year_end)

    if min_rating is not None:
        conditions.append("v.rating >= ?")
        params.append(min_rating)

    if region:
        conditions.append("v.region LIKE ?")
        params.append(f"%{region}%")

    if actor_name:
        conditions.append("""
            v.video_id IN (
                SELECT va.video_id FROM video_actors va
                JOIN actors a ON va.actor_id = a.actor_id
                WHERE a.name LIKE ?
            )
        """)
        params.append(f"%{actor_name}%")

    if director_name:
        conditions.append("""
            v.video_id IN (
                SELECT vd.video_id FROM video_directors vd
                JOIN directors d ON vd.director_id = d.director_id
                WHERE d.name LIKE ?
            )
        """)
        params.append(f"%{director_name}%")

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    order = "v.rating DESC" if sort_by == "rating" else "v.year DESC"

    sql = f"""
        SELECT v.* FROM videos v
        WHERE {where_clause}
        ORDER BY {order}
        LIMIT ?
    """
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    conn.close()

    results = []
    for row in rows:
        d = dict(row)
        # genres 以逗号分隔存储，转回列表
        if isinstance(d.get("genres"), str):
            d["genres"] = d["genres"].split(",") if d["genres"] else []
        results.append(d)

    return results


# ── 混合检索 ─────────────────────────────────────────────────────────


def _deduplicate(results: list[dict]) -> list[dict]:
    """按 video_id 去重"""
    seen: set[str] = set()
    deduped: list[dict] = []
    for item in results:
        vid = item.get("video_id") or item.get("id", "")
        if vid not in seen:
            seen.add(vid)
            deduped.append(item)
    return deduped


def hybrid_search(query: str, n_results: int = 10) -> list[dict]:
    """混合检索：语义检索 + 传统过滤 + 结果融合

    策略：
    1. parse_query 提取结构化条件
    2. 执行语义检索（获取更多候选）
    3. 执行传统过滤
    4. 融合排序

    Args:
        query: 用户查询
        n_results: 最终返回结果数

    Returns:
        排序后的推荐视频列表
    """
    parsed = parse_query(query)

    type_filter = parsed.get("type")

    # 1. 语义检索（宽召回）
    semantic_results = semantic_search(
        query,
        n_results=max(n_results * 3, 20),
        type_filter=type_filter,
        min_rating=parsed.get("min_rating"),
    )

    # 2. 传统过滤
    filter_results = filter_videos(
        genre=parsed.get("genre"),
        year_start=parsed.get("year_start"),
        year_end=parsed.get("year_end"),
        actor_name=parsed.get("actor"),
        region=parsed.get("region"),
        type_filter=type_filter,
        min_rating=parsed.get("min_rating"),
        limit=max(n_results * 3, 20),
    )

    # 3. 结果融合（ID 集合加速查找）
    filter_by_id = {v["video_id"]: v for v in filter_results}
    filter_ids = set(filter_by_id)

    # 优先：在语义结果中且也通过了过滤的（交集）
    priority: list[dict] = []
    # 补充：语义结果中其余的（按语义分排序）
    secondary: list[dict] = []

    for item in semantic_results:
        if item["video_id"] in filter_ids:
            enriched = {**filter_by_id[item["video_id"]], "score": item.get("score")}
            priority.append(enriched)
        else:
            secondary.append(item)

    # 如果还有剩余名额，从过滤结果中补充
    filter_extra = [v for v in filter_results if v["video_id"] not in {p["video_id"] for p in priority}]

    has_structured_filter = any(
        parsed.get(key) is not None
        for key in ("genre", "type", "year_start", "year_end", "actor", "region", "min_rating")
    )

    if has_structured_filter and filter_results:
        merged = filter_results
    else:
        merged = priority + secondary + filter_extra

    merged = _deduplicate(merged)

    return merged[:n_results]

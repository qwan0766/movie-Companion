"""LangChain Tool 定义 — 标准工具接口层

将现有工具函数包装为 LangChain @tool，供 Agent 和 LLM 调用。
不修改内部实现，仅外部包裹。
"""

from langchain_core.tools import tool


@tool
def hybrid_search_tool(query: str, n_results: int = 10) -> list[dict]:
    """基于语义相似度和传统过滤的混合视频检索

    同时使用 Chroma 语义检索和 SQLite 结构化过滤，
    对结果进行融合去重排序，返回最匹配的视频列表。

    Args:
        query: 用户的搜索查询文本
        n_results: 返回结果数量，默认 10

    Returns:
        按匹配度排序的视频列表，每项含 title/year/rating/genres/video_id 等字段
    """
    from tools.search_tools import hybrid_search
    return hybrid_search(query, n_results=n_results)


@tool
def parse_query_tool(query: str) -> dict:
    """从自然语言查询中提取结构化过滤条件

    支持提取：类型(genre)、年代(year_start/year_end)、
    最低评分(min_rating)、演员(actor)、地区(region)。

    Args:
        query: 用户查询文本

    Returns:
        {"keywords": str, "genre": str|None, "year_start": int|None,
         "year_end": int|None, "min_rating": float|None,
         "actor": str|None, "region": str|None}
    """
    from tools.search_tools import parse_query
    return parse_query(query)


@tool
def knowledge_search_tool(query_type: str, query_value: str) -> dict:
    """知识库查询（Neo4j 优先，SQLite 自动兜底）

    Args:
        query_type: 查询类型
            - "actor_films": 演员参演作品
            - "director_films": 导演执导作品
            - "video_details": 视频详细信息
            - "search": 关键词搜索
        query_value: 查询值（实体名称或关键词）

    Returns:
        {"type": str, "data": ..., "source": "neo4j"|"sqlite"}
    """
    from tools.knowledge_tools import knowledge_search
    return knowledge_search(query_type, query_value)


@tool
def detect_query_type_tool(text: str) -> dict:
    """识别知识查询类型并提取实体名称

    从用户输入中判断查询意图（查演员作品/导演作品/视频详情/关键词搜索）
    并提取对应的实体名称。

    Args:
        text: 用户输入文本

    Returns:
        {"query_type": str, "entity_name": str}
    """
    from tools.knowledge_tools import detect_query_type
    qtype, entity = detect_query_type(text)
    return {"query_type": qtype, "entity_name": entity}


# 工具注册表 — 方便批量导入
TOOL_REGISTRY: list = [
    hybrid_search_tool,
    parse_query_tool,
    knowledge_search_tool,
    detect_query_type_tool,
]

TOOL_MAP: dict[str, object] = {
    "hybrid_search_tool": hybrid_search_tool,
    "parse_query_tool": parse_query_tool,
    "knowledge_search_tool": knowledge_search_tool,
    "detect_query_type_tool": detect_query_type_tool,
}

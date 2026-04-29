"""Tool 定义单元测试"""

from tools.tool_definitions import (
    TOOL_REGISTRY,
    TOOL_MAP,
    hybrid_search_tool,
    parse_query_tool,
    knowledge_search_tool,
    detect_query_type_tool,
)


class TestToolDefinitions:
    """Tool 定义基础测试"""

    def test_tools_have_names(self):
        assert hybrid_search_tool.name == "hybrid_search_tool"
        assert parse_query_tool.name == "parse_query_tool"
        assert knowledge_search_tool.name == "knowledge_search_tool"
        assert detect_query_type_tool.name == "detect_query_type_tool"

    def test_tools_have_descriptions(self):
        for tool in [hybrid_search_tool, parse_query_tool,
                     knowledge_search_tool, detect_query_type_tool]:
            assert tool.description
            assert len(tool.description) > 10

    def test_tools_are_invokable(self):
        for tool in [hybrid_search_tool, parse_query_tool,
                     knowledge_search_tool, detect_query_type_tool]:
            assert hasattr(tool, "invoke")
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")

    def test_registry_count(self):
        assert len(TOOL_REGISTRY) == 4

    def test_tool_map_has_all(self):
        assert "hybrid_search_tool" in TOOL_MAP
        assert "parse_query_tool" in TOOL_MAP
        assert "knowledge_search_tool" in TOOL_MAP
        assert "detect_query_type_tool" in TOOL_MAP

    def test_hybrid_search_tool_invoke(self):
        result = hybrid_search_tool.invoke({"query": "科幻电影", "n_results": 3})
        assert isinstance(result, list)
        assert len(result) <= 3
        if result:
            assert "title" in result[0]
            assert "video_id" in result[0]

    def test_parse_query_tool_invoke(self):
        result = parse_query_tool.invoke({"query": "2020年科幻电影"})
        assert result["genre"] == "科幻"
        assert result["year_start"] == 2020

    def test_knowledge_search_tool_invoke(self):
        result = knowledge_search_tool.invoke({
            "query_type": "search",
            "query_value": "张毅",
        })
        assert "type" in result
        assert "data" in result

    def test_detect_query_type_tool_invoke(self):
        result = detect_query_type_tool.invoke({"text": "介绍一下张毅"})
        assert "query_type" in result
        assert "entity_name" in result

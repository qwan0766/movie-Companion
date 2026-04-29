"""知识查询工具 单元测试"""

from tools.knowledge_tools import (
    knowledge_search,
    detect_query_type,
    _get_actor_films_sqlite,
    _get_director_films_sqlite,
    _get_video_details_sqlite,
    _search_entities_sqlite,
)


class TestSQLiteFallback:
    """SQLite 兜底查询测试"""

    def test_get_actor_films(self):
        results = _get_actor_films_sqlite("张毅")
        assert isinstance(results, list)
        if results:
            assert "title" in results[0]
            assert "year" in results[0]

    def test_get_director_films(self):
        results = _get_director_films_sqlite("郭凡")
        assert isinstance(results, list)
        if results:
            assert "title" in results[0]

    def test_get_video_details(self):
        result = _get_video_details_sqlite("星际探索")
        if result:
            assert "title" in result
            assert "actors" in result
            assert "directors" in result

    def test_search_entities(self):
        result = _search_entities_sqlite("张")
        assert "actors" in result
        assert "directors" in result
        assert "videos" in result


class TestDetectQueryType:
    """查询类型识别测试"""

    def test_actor_films(self):
        qtype, name = detect_query_type("周星驰演过哪些电影")
        assert qtype == "actor_films"
        assert name is not None

    def test_director_films(self):
        qtype, name = detect_query_type("张艺谋导演过哪些作品")
        assert qtype == "director_films"
        assert name is not None

    def test_video_details_with_brackets(self):
        qtype, name = detect_query_type("介绍一下《流浪地球》")
        assert qtype == "video_details"
        assert "流浪地球" in name

    def test_search_fallback(self):
        qtype, name = detect_query_type("随便问问")
        assert qtype == "search"

    def test_who_acted(self):
        qtype, name = detect_query_type("《星际穿越》是谁演的")
        assert qtype == "video_details"
        assert "星际穿越" in name


class TestKnowledgeSearch:
    """统一查询入口测试"""

    def test_actor_films_search(self):
        result = knowledge_search("actor_films", "张毅")
        assert result["type"] == "actor_films"
        assert result["source"] in ("sqlite", "neo4j")  # sqlite by default
        assert isinstance(result["data"], list)

    def test_director_films_search(self):
        result = knowledge_search("director_films", "郭凡")
        assert result["type"] == "director_films"
        assert isinstance(result["data"], list)

    def test_video_details_search(self):
        result = knowledge_search("video_details", "星际")
        assert result["type"] == "video_details"
        assert result["data"] is not None or result["data"] == []

    def test_search_all(self):
        result = knowledge_search("search", "张")
        assert result["type"] == "search"
        assert "actors" in result.get("data", {})
        assert "directors" in result.get("data", {})
        assert "videos" in result.get("data", {})

    def test_unknown_type(self):
        result = knowledge_search("unknown_type", "test")
        assert result["type"] == "unknown_type"
        assert result["data"] == []

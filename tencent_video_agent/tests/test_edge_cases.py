"""边界情况与异常处理专项测试"""

from graph.graph import run_query
from tools.search_tools import hybrid_search, parse_query, semantic_search


class TestEdgeEmptyInput:
    """空输入边界"""

    def test_completely_empty(self):
        result = run_query("")
        assert result.get("user_intent") == "unknown"
        assert result.get("intent_confidence") == 0.0

    def test_only_spaces(self):
        result = run_query("   ")
        assert result.get("user_intent") in ("unknown", "chat")
        assert result.get("response")

    def test_only_newlines(self):
        result = run_query("\n\n\n")
        assert result.get("user_intent") in ("unknown", "chat")


class TestEdgeSpecialInput:
    """特殊字符边界"""

    def test_html_tags(self):
        result = run_query("<script>alert('xss')</script>")
        assert result.get("response")  # 不应崩溃

    def test_sql_injection_attempt(self):
        result = run_query("'; DROP TABLE videos; --")
        assert result.get("response")  # 不应崩溃

    def test_emoji_only(self):
        result = run_query("🎬🎥🍿")
        assert result.get("response")  # 不应崩溃

    def test_mixed_language(self):
        result = run_query("recommend 好看的 movie")
        assert result.get("response")  # 不应崩溃


class TestEdgeLongInput:
    """超长输入边界"""

    def test_very_long_text(self):
        text = "推荐" + "电影" * 500
        result = run_query(text)
        assert result.get("response")  # 不应崩溃

    def test_extremely_long_repeat_char(self):
        text = "a" * 10000
        result = run_query(text)
        assert result.get("response")  # 不应崩溃


class TestEdgeSearch:
    """检索边界"""

    def test_search_nonexistent_content(self):
        results = hybrid_search("xyzzy_nonexistent_12345", n_results=5)
        assert isinstance(results, list)

    def test_semantic_search_empty_result(self):
        results = semantic_search("!!!@@@###", n_results=5)
        assert isinstance(results, list)

    def test_parse_query_empty(self):
        parsed = parse_query("")
        assert parsed["keywords"] == ""
        assert parsed["genre"] is None
        assert parsed["actor"] is None

    def test_parse_query_all_special_chars(self):
        parsed = parse_query("@#$%^&*()")
        assert parsed["genre"] is None
        assert parsed["actor"] is None


class TestEdgeHighFrequency:
    """高频请求边界"""

    def test_rapid_sequential_queries(self):
        """连续快速请求"""
        t_id = "e2e_rapid"
        queries = ["你好", "推荐电影", "介绍一下", "谢谢", "再见"]
        for i, q in enumerate(queries):
            result = run_query(q, thread_id=f"{t_id}_{i}")
            assert result.get("response"), f"第{i+1}次请求 '{q}' 无回复"

    def test_same_thread_rapid(self):
        """同一 thread 快速连续请求"""
        t_id = "e2e_rapid_same"
        for i in range(5):
            result = run_query(f"消息{i}", thread_id=t_id)
            assert result.get("response"), f"同一线程第{i+1}次请求无回复"

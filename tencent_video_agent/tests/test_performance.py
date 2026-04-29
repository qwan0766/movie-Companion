"""性能基准测试 — 响应时间测量（无需外部依赖）"""

import time
from statistics import mean, median

from agents.intent_agent import _classify_intent
from graph.graph import run_query
from tools.knowledge_tools import knowledge_search, detect_query_type
from tools.search_tools import hybrid_search, parse_query, semantic_search


def _measure(func, *args, **kwargs) -> float:
    """测量函数执行耗时（秒）"""
    start = time.perf_counter()
    func(*args, **kwargs)
    return time.perf_counter() - start


class TestPerformanceIntent:
    """意图识别性能"""

    def test_intent_classification_speed(self):
        times = [_measure(_classify_intent, "推荐几部好看的科幻电影") for _ in range(20)]
        avg_ms = mean(times) * 1000
        assert avg_ms < 100, f"意图识别平均耗时 {avg_ms:.2f}ms > 100ms"

    def test_intent_empty_speed(self):
        times = [_measure(_classify_intent, "") for _ in range(20)]
        avg_ms = mean(times) * 1000
        assert avg_ms < 50, f"空文本分类平均耗时 {avg_ms:.2f}ms > 50ms"

    def test_intent_long_text_speed(self):
        long_text = "推荐" + "电影" * 200
        times = [_measure(_classify_intent, long_text) for _ in range(10)]
        avg_ms = mean(times) * 1000
        assert avg_ms < 200, f"长文本分类平均耗时 {avg_ms:.2f}ms > 200ms"


class TestPerformanceSearch:
    """检索性能"""

    def test_parse_query_speed(self):
        times = [_measure(parse_query, "2020年高分科幻电影") for _ in range(20)]
        avg_ms = mean(times) * 1000
        assert avg_ms < 50, f"查询解析平均耗时 {avg_ms:.2f}ms > 50ms"

    def test_semantic_search_speed(self):
        times = [_measure(semantic_search, "科幻电影", n_results=10) for _ in range(10)]
        avg_ms = mean(times) * 1000
        assert avg_ms < 500, f"语义检索平均耗时 {avg_ms:.2f}ms > 500ms"

    def test_hybrid_search_speed(self):
        times = [_measure(hybrid_search, "科幻电影", n_results=10) for _ in range(10)]
        avg_ms = mean(times) * 1000
        assert avg_ms < 1000, f"混合检索平均耗时 {avg_ms:.2f}ms > 1000ms"


class TestPerformanceKnowledge:
    """知识查询性能"""

    def test_knowledge_search_actor_speed(self):
        times = [_measure(knowledge_search, "actor_films", "张毅") for _ in range(10)]
        avg_ms = mean(times) * 1000
        # Neo4j 不可用时含超时降级，阈值放宽
        assert avg_ms < 5000, f"演员作品查询平均耗时 {avg_ms:.2f}ms > 5000ms"

    def test_detect_query_type_speed(self):
        times = [_measure(detect_query_type, "介绍一下张毅") for _ in range(20)]
        avg_ms = mean(times) * 1000
        assert avg_ms < 50, f"查询类型识别平均耗时 {avg_ms:.2f}ms > 50ms"


class TestPerformanceWorkflow:
    """全工作流性能"""

    def test_find_movie_workflow_speed(self):
        times = [_measure(run_query, "推荐科幻电影") for _ in range(5)]
        avg_ms = mean(times) * 1000
        assert avg_ms < 5000, f"找片工作流平均耗时 {avg_ms:.2f}ms > 5000ms"

    def test_chat_workflow_speed(self):
        times = [_measure(run_query, "你好") for _ in range(5)]
        avg_ms = mean(times) * 1000
        assert avg_ms < 3000, f"闲聊工作流平均耗时 {avg_ms:.2f}ms > 3000ms"

    def test_knowledge_workflow_speed(self):
        times = [_measure(run_query, "介绍一下张毅") for _ in range(5)]
        avg_ms = mean(times) * 1000
        assert avg_ms < 5000, f"知识查询工作流平均耗时 {avg_ms:.2f}ms > 5000ms"

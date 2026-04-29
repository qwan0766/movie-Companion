"""性能基准测试 — 响应时间测量"""

import time
from statistics import mean, median

from graph.graph import run_query
from tools.knowledge_tools import knowledge_search
from tools.search_tools import hybrid_search, semantic_search


def _measure(func, *args, **kwargs) -> float:
    """测量函数执行耗时（秒）"""
    start = time.perf_counter()
    func(*args, **kwargs)
    return time.perf_counter() - start


class TestPerformanceSearch:
    """检索性能"""

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
        assert avg_ms < 5000, f"演员作品查询平均耗时 {avg_ms:.2f}ms > 5000ms"

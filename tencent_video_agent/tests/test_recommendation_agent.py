"""推荐生成 Agent 单元测试"""

from agents.recommendation_agent import (
    RecommendationAgent,
    _build_tag,
    _categorize_results,
    _generate_reason,
)


class TestRecommendationAgent:
    """RecommendationAgent 整体测试"""

    def setup_method(self):
        self.agent = RecommendationAgent()

    def test_agent_name(self):
        assert self.agent.name == "recommendation_agent"

    def test_process_with_videos(self):
        """有检索结果时生成推荐"""
        result = self.agent.process({
            "messages": [{"role": "user", "content": "推荐科幻电影"}],
            "user_intent": "find_movie",
            "intent_confidence": 0.85,
            "retrieved_videos": [
                {"video_id": "v1", "title": "星际穿越", "year": "2014",
                 "rating": "9.4", "genres": ["科幻", "冒险"], "region": "美国"},
                {"video_id": "v2", "title": "盗梦空间", "year": "2010",
                 "rating": "9.3", "genres": ["悬疑", "科幻"], "region": "美国"},
                {"video_id": "v3", "title": "月球", "year": "2009",
                 "rating": "8.0", "genres": ["科幻"], "region": "英国"},
            ],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert len(result["response"]) > 0
        assert "星际穿越" in result["response"]
        assert result["next"] == "__end__"

    def test_process_empty_videos(self):
        """无检索结果时返回引导语"""
        result = self.agent.process({
            "messages": [{"role": "user", "content": "推荐电影"}],
            "user_intent": "find_movie",
            "intent_confidence": 0.6,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert "没有找到" in result["response"]

    def test_process_returns_categorized(self):
        """推荐结果分层展示"""
        result = self.agent.process({
            "messages": [{"role": "user", "content": "推荐科幻电影"}],
            "user_intent": "find_movie",
            "intent_confidence": 0.85,
            "retrieved_videos": [
                {"video_id": "v1", "title": "A", "rating": "9.5", "genres": ["科幻"]},
                {"video_id": "v2", "title": "B", "rating": "8.5", "genres": ["剧情"]},
                {"video_id": "v3", "title": "C", "rating": "7.5", "genres": ["喜剧"]},
            ],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        response = result["response"]
        assert "最佳匹配" in response or "🏆" in response

    def test_retrieval_agent_then_recommendation(self):
        """完整流程：retrieval → recommendation"""
        from graph.graph import run_query
        result = run_query("推荐科幻电影")
        assert result.get("user_intent") == "find_movie"
        assert result.get("response")
        # 推荐响应应包含分类标识
        assert any(kw in result["response"] for kw in ["最佳匹配", "值得一看", "精选"])


class TestRecommendationHelpers:
    """推荐辅助函数测试"""

    def test_generate_reason_with_genre(self):
        reason = _generate_reason(
            {"title": "X", "genres": ["科幻"], "rating": "9.0"}, "科幻"
        )
        assert len(reason) > 0
        assert isinstance(reason, str)

    def test_generate_reason_high_rating(self):
        reason = _generate_reason(
            {"title": "X", "genres": ["剧情"], "rating": "9.5"}, None
        )
        # 高评分应返回正面推荐理由
        assert len(reason) > 5
        assert isinstance(reason, str)

    def test_generate_reason_generic(self):
        reason = _generate_reason(
            {"title": "X", "genres": [], "rating": ""}, None
        )
        assert len(reason) > 0

    def test_build_tag_high_score(self):
        tag = _build_tag({"rating": "9.2", "year": "2020"}, {})
        assert tag == "神作"

    def test_build_tag_new_release(self):
        tag = _build_tag({"rating": "", "year": "2025"}, {})
        assert tag == "新片"

    def test_build_tag_default(self):
        tag = _build_tag({"rating": "", "year": "2015"}, {})
        assert tag == "推荐"

    def test_categorize_results(self):
        videos = [
            {"video_id": "v1", "rating": "9.5"},
            {"video_id": "v2", "rating": "8.5"},
            {"video_id": "v3", "rating": "7.0"},
        ]
        cats = _categorize_results(videos, {})
        assert "best_match" in cats
        assert "worth_watching" in cats
        assert "also_good" in cats
        assert len(cats["best_match"]) == 1

    def test_categorize_empty(self):
        assert _categorize_results([], {}) == {}

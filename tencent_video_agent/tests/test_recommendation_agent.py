"""推荐生成 Agent 单元测试"""

from agents.recommendation_agent import (
    RecommendationAgent,
    _build_tag,
    _categorize_results,
)


class TestRecommendationAgent:
    """RecommendationAgent 整体测试"""

    def setup_method(self):
        self.agent = RecommendationAgent()

    def test_agent_name(self):
        assert self.agent.name == "recommendation_agent"

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


class TestRecommendationHelpers:
    """推荐辅助函数测试"""

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

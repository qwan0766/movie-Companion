"""观影计划 Agent 单元测试"""

from agents.plan_agent import PlanAgent, _build_plan_schedule, _format_plan_response


class TestPlanHelpers:
    """计划辅助函数测试"""

    def test_build_schedule_with_videos(self):
        videos = [
            {"title": "A", "year": 2020, "rating": 9.0, "type": "movie", "genres": ["科幻"]},
            {"title": "B", "year": 2021, "rating": 8.5, "type": "tv", "genres": ["悬疑"]},
        ]
        schedule = _build_plan_schedule(videos, "今晚", None)
        assert len(schedule) == 2
        assert schedule[0]["title"] == "A"
        assert schedule[1]["title"] == "B"

    def test_build_schedule_empty(self):
        assert _build_plan_schedule([], "今晚", None) == []

    def test_format_empty_schedule(self):
        result = _format_plan_response([], "今晚", None)
        assert "没有找到" in result

    def test_format_with_schedule(self):
        schedule = [
            {"title": "A", "year": "2020", "rating": "9.0", "type": "movie",
             "genre": ["科幻"], "estimated_time": "~120min", "reason": "开场推荐"},
        ]
        result = _format_plan_response(schedule, "今晚", None)
        assert "A" in result
        assert "开场推荐" in result

    def test_format_with_mood(self):
        schedule = [
            {"title": "A", "year": "2020", "rating": "8.0", "type": "tv",
             "genre": ["喜剧"], "estimated_time": "~45min/集", "reason": "值得一看"},
        ]
        result = _format_plan_response(schedule, "周末", "轻松")
        assert "轻松" in result


class TestPlanAgent:
    """PlanAgent 整体测试"""

    def setup_method(self):
        self.agent = PlanAgent()

    def test_agent_name(self):
        assert self.agent.name == "plan_agent"

    def test_process_empty_messages(self):
        result = self.agent.process({
            "messages": [],
            "user_intent": "",
            "intent_confidence": 0.0,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert "观影需求" in result["response"]

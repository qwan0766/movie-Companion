"""观影计划 Agent 单元测试"""

from agents.plan_agent import PlanAgent, _extract_time_slot, _extract_mood, _format_plan_response


class TestPlanAgent:
    """PlanAgent 整体测试"""

    def setup_method(self):
        self.agent = PlanAgent()

    def test_agent_name(self):
        assert self.agent.name == "plan_agent"

    def test_process_empty_messages(self):
        result = self.agent.process({
            "messages": [],
            "user_intent": "make_plan",
            "intent_confidence": 0.9,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert result["plan"] == {}
        assert "告诉我" in result["response"]
        assert result["next"] == "__end__"

    def test_process_weekend_plan(self):
        """周末观影计划"""
        result = self.agent.process({
            "messages": [{"role": "user", "content": "帮我规划周末看什么电影"}],
            "user_intent": "make_plan",
            "intent_confidence": 0.9,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert result["plan"].get("time_slot") == "周末"
        assert len(result["plan"].get("schedule", [])) >= 1
        assert len(result["response"]) > 0

    def test_process_tonight_plan(self):
        """今晚观影计划"""
        result = self.agent.process({
            "messages": [{"role": "user", "content": "今晚想看好看的电影"}],
            "user_intent": "make_plan",
            "intent_confidence": 0.85,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert result["plan"].get("time_slot") == "今晚"
        assert len(result["plan"].get("schedule", [])) >= 1
        assert len(result["response"]) > 0

    def test_process_with_mood(self):
        """按心情制定计划"""
        result = self.agent.process({
            "messages": [{"role": "user", "content": "推荐轻松搞笑的电影，周末看"}],
            "user_intent": "make_plan",
            "intent_confidence": 0.9,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert result["plan"].get("mood") in ("轻松", None)
        assert result["plan"].get("time_slot") == "周末"

    def test_plan_has_structure(self):
        """验证计划结构完整性"""
        result = self.agent.process({
            "messages": [{"role": "user", "content": "周末科幻电影计划"}],
            "user_intent": "make_plan",
            "intent_confidence": 0.95,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        plan = result["plan"]
        assert "time_slot" in plan
        assert "schedule" in plan
        assert "total_count" in plan
        assert "preferences" in plan
        assert plan["total_count"] >= 0

        if plan["schedule"]:
            item = plan["schedule"][0]
            assert "title" in item
            assert "reason" in item
            assert "estimated_time" in item


class TestPlanHelpers:
    """计划辅助函数测试"""

    def test_extract_time_slot_tonight(self):
        assert _extract_time_slot("今晚看什么") == "今晚"

    def test_extract_time_slot_weekend(self):
        assert _extract_time_slot("周末看电影") == "周末"

    def test_extract_time_slot_default(self):
        assert _extract_time_slot("随便看看") == "今晚"

    def test_extract_mood_relax(self):
        assert _extract_mood("轻松搞笑的") == "轻松"

    def test_extract_mood_exciting(self):
        assert _extract_mood("刺激的悬疑片") == "刺激"

    def test_extract_mood_touching(self):
        assert _extract_mood("感人的电影") == "感动"

    def test_extract_mood_none(self):
        assert _extract_mood("随便推荐几部") is None

    def test_format_empty_schedule(self):
        response = _format_plan_response([], "今晚", None, 0)
        assert "没有找到" in response

    def test_format_with_schedule(self):
        schedule = [
            {"title": "Test Movie", "year": "2024", "rating": "8.5",
             "type": "movie", "genre": ["科幻"], "estimated_time": "~120min",
             "reason": "开场推荐"},
        ]
        response = _format_plan_response(schedule, "今晚", None, 1)
        assert "Test Movie" in response
        assert "8.5" in response
        assert "调整" in response

    def test_format_with_mood(self):
        schedule = [
            {"title": "Test", "year": "2024", "rating": "9.0",
             "type": "movie", "genre": [], "estimated_time": "~120min",
             "reason": "推荐"},
        ]
        response = _format_plan_response(schedule, "周末", "轻松", 1)
        assert "轻松" in response
        assert "周末" in response

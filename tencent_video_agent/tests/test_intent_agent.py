"""意图识别 Agent 单元测试"""

from agents.intent_agent import IntentAgent, _normalize_intent_result


class TestIntentAgent:
    """IntentAgent 整体测试"""

    def setup_method(self):
        self.agent = IntentAgent()

    def test_agent_name(self):
        assert self.agent.name == "intent_agent"

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
        assert result["user_intent"] == "unknown"
        assert result["intent_confidence"] == 0.0
        assert result["need_clarification"] is False

    def test_normalize_low_confidence_to_clarify(self):
        result = _normalize_intent_result({
            "intent": "find_movie",
            "confidence": 0.4,
            "reason": "不确定",
        })
        assert result["user_intent"] == "clarify"
        assert result["need_clarification"] is True
        assert result["clarification_question"]

    def test_normalize_out_of_scope(self):
        result = _normalize_intent_result({
            "intent": "out_of_scope",
            "confidence": 0.86,
            "reason": "请求写代码",
            "suggested_new_intent": "code_generation",
        })
        assert result["user_intent"] == "out_of_scope"
        assert result["need_clarification"] is False
        assert result["suggested_new_intent"] == "code_generation"

    def test_normalize_unexpected_intent_to_out_of_scope(self):
        result = _normalize_intent_result({
            "intent": "book_flight",
            "confidence": 0.8,
            "reason": "订票请求",
        })
        assert result["user_intent"] == "out_of_scope"
        assert result["suggested_new_intent"] == "book_flight"

"""意图识别 Agent 单元测试"""

from agents.intent_agent import IntentAgent


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

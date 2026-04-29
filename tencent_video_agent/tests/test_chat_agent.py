"""对话管理 Agent 单元测试"""

from agents.chat_agent import ChatAgent


class TestChatAgent:
    """ChatAgent 整体测试"""

    def setup_method(self):
        self.agent = ChatAgent()

    def test_agent_name(self):
        assert self.agent.name == "chat_agent"

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
        assert "你好" in result["response"]

"""对话管理 Agent 单元测试"""

from agents.chat_agent import ChatAgent, _is_greeting, _is_thanks


class TestChatUtils:
    """闲聊工具函数测试"""

    def test_is_greeting(self):
        assert _is_greeting("你好")
        assert _is_greeting("您好，我想找片")
        assert _is_greeting("早上好")
        assert _is_greeting("Hi")
        assert not _is_greeting("推荐电影")

    def test_is_thanks(self):
        assert _is_thanks("谢谢")
        assert _is_thanks("感谢你")
        assert _is_thanks("多谢帮忙")
        assert not _is_thanks("推荐电影")


class TestChatAgent:
    """ChatAgent 整体测试"""

    def setup_method(self):
        self.agent = ChatAgent()

    def test_agent_name(self):
        assert self.agent.name == "chat_agent"

    def test_process_greeting(self):
        result = self.agent.process({
            "messages": [{"role": "user", "content": "你好"}],
            "user_intent": "chat",
            "intent_confidence": 0.9,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert "你好" in result["response"] or "嗨" in result["response"] or "欢迎" in result["response"]
        assert result["next"] == "__end__"

    def test_process_thanks(self):
        result = self.agent.process({
            "messages": [{"role": "user", "content": "谢谢"}],
            "user_intent": "chat",
            "intent_confidence": 0.7,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert "不客气" in result["response"] or "高兴" in result["response"] or "不用谢" in result["response"]

    def test_process_unknown_intent(self):
        """未知意图时追问澄清"""
        result = self.agent.process({
            "messages": [{"role": "user", "content": "嗯嗯"}],
            "user_intent": "unknown",
            "intent_confidence": 0.3,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert "没太明白" in result["response"] or "具体" in result["response"] or "找片" in result["response"]

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

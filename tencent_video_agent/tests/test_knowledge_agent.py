"""知识查询 Agent 单元测试"""

from agents.knowledge_agent import KnowledgeAgent


class TestKnowledgeAgent:
    """KnowledgeAgent 整体测试"""

    def setup_method(self):
        self.agent = KnowledgeAgent()

    def test_agent_name(self):
        assert self.agent.name == "knowledge_agent"

    def test_process_actor_query(self):
        result = self.agent.process({
            "messages": [{"role": "user", "content": "张毅演过哪些电影"}],
            "user_intent": "ask_info",
            "intent_confidence": 0.9,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert "knowledge_result" in result
        assert "response" in result
        assert result["next"] == "__end__"

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
        assert "想了解" in result["response"]

    def test_process_video_detail(self):
        result = self.agent.process({
            "messages": [{"role": "user", "content": "介绍一下《星际探索》"}],
            "user_intent": "ask_info",
            "intent_confidence": 0.85,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert "response" in result


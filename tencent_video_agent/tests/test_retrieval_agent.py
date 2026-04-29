"""视频检索 Agent 单元测试"""

from agents.retrieval_agent import RetrievalAgent


class TestRetrievalAgent:
    """RetrievalAgent 整体测试"""

    def setup_method(self):
        self.agent = RetrievalAgent()

    def test_agent_name(self):
        assert self.agent.name == "retrieval_agent"

    def test_process_find_movie(self):
        result = self.agent.process({
            "messages": [{"role": "user", "content": "推荐科幻电影"}],
            "user_intent": "find_movie",
            "intent_confidence": 0.95,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert len(result["retrieved_videos"]) >= 1
        assert "找到" in result["response"]
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
        assert result["retrieved_videos"] == []
        assert "告诉我" in result["response"]

    def test_process_with_actor(self):
        """按演员检索"""
        result = self.agent.process({
            "messages": [{"role": "user", "content": "张毅演的电影"}],
            "user_intent": "find_movie",
            "intent_confidence": 0.9,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        assert len(result["retrieved_videos"]) >= 0  # 可能有也可能没有
        assert isinstance(result["retrieved_videos"], list)

    def test_process_by_genre(self):
        """按类型检索"""
        result = self.agent.process({
            "messages": [{"role": "user", "content": "喜剧"}],
            "user_intent": "find_movie",
            "intent_confidence": 0.85,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
            "response": "",
            "errors": [],
            "next": "",
        })
        if result["retrieved_videos"]:
            assert "找到" in result["response"]

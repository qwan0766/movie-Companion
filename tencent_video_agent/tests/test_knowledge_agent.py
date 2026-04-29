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

    def test_format_actor_result(self):
        result_data = {
            "type": "actor_films",
            "data": [
                {"title": "电影A", "year": 2020, "rating": 8.5},
                {"title": "电影B", "year": 2019, "rating": 7.5},
            ],
            "source": "sqlite",
        }
        formatted = self.agent._format_result(result_data, "测试演员")
        assert "测试演员" in formatted
        assert "电影A" in formatted
        assert "电影B" in formatted

    def test_format_empty_result(self):
        result_data = {"type": "actor_films", "data": [], "source": "sqlite"}
        formatted = self.agent._format_result(result_data, "不存在的人")
        assert "没有找到" in formatted

    def test_format_video_detail(self):
        result_data = {
            "type": "video_details",
            "data": {
                "title": "测试电影",
                "year": 2023,
                "rating": 8.5,
                "genres": ["科幻", "动作"],
                "region": "中国大陆",
                "description": "一部好看的电影",
                "actors": [{"name": "演员A"}, {"name": "演员B"}],
                "directors": [{"name": "导演A"}],
            },
            "source": "sqlite",
        }
        formatted = self.agent._format_result(result_data, "测试电影")
        assert "测试电影" in formatted
        assert "演员A" in formatted
        assert "导演A" in formatted

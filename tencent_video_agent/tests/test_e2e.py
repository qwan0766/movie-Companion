"""端到端全路径测试 — 覆盖所有用户路径"""

from graph.graph import run_query
from graph.state import AgentState


class TestE2EFindMovie:
    """找片全路径"""

    def test_find_movie_by_genre(self):
        result = run_query("推荐科幻电影")
        assert result.get("user_intent") == "find_movie"
        assert result.get("intent_confidence", 0) >= 0.70
        assert len(result.get("retrieved_videos", [])) >= 1
        assert result.get("response")
        assert not result.get("errors", [])

    def test_find_movie_with_actor(self):
        result = run_query("找张毅演的科幻片")
        assert result.get("user_intent") == "find_movie"
        assert result.get("response")

    def test_find_movie_rating_filter(self):
        result = run_query("高分的剧情片")
        assert result.get("user_intent") in ("find_movie", "unknown")


class TestE2EKnowledge:
    """知识查询全路径"""

    def test_ask_actor_info(self):
        result = run_query("介绍一下张毅")
        assert result.get("user_intent") == "ask_info"
        assert result.get("intent_confidence", 0) >= 0.70
        assert result.get("response")
        assert not result.get("errors", [])

    def test_ask_video_detail(self):
        result = run_query("介绍星际穿越")
        assert result.get("user_intent") == "ask_info"
        assert result.get("response")

    def test_ask_director(self):
        result = run_query("谁执导了流浪地球")
        assert result.get("user_intent") == "ask_info"
        assert result.get("response")


class TestE2EPlan:
    """观影计划全路径"""

    def test_weekend_plan(self):
        result = run_query("帮我规划周末看什么")
        assert result.get("user_intent") == "make_plan"
        assert result.get("plan", {}).get("schedule") is not None
        assert result.get("response")

    def test_tonight_plan_request(self):
        result = run_query("帮我规划今晚看什么")
        assert result.get("user_intent") == "make_plan"
        assert result.get("response")


class TestE2EChat:
    """闲聊全路径"""

    def test_greeting(self):
        result = run_query("你好")
        assert result.get("user_intent") == "chat"
        assert any(kw in result.get("response", "") for kw in ["你好", "欢迎", "嗨", "观影"])

    def test_thanks(self):
        result = run_query("谢谢")
        assert result.get("user_intent") == "chat"
        assert result.get("response")

    def test_farewell(self):
        result = run_query("再见")
        assert result.get("user_intent") == "chat"
        assert result.get("response")


class TestE2EMultiTurn:
    """多轮对话全路径"""

    def test_multi_turn_context(self):
        """多轮：先问候再找片，意图应为找片"""
        t_id = "e2e_multi_turn"
        r1 = run_query("你好", thread_id=t_id)
        assert r1.get("user_intent") == "chat"

        r2 = run_query("推荐科幻电影", thread_id=t_id)
        assert r2.get("user_intent") == "find_movie"
        assert len(r2.get("retrieved_videos", [])) >= 1

    def test_multi_turn_chat_then_knowledge(self):
        """多轮：先闲聊再查知识"""
        t_id = "e2e_multi_knowledge"
        run_query("你好", thread_id=t_id)
        r2 = run_query("介绍一下张毅", thread_id=t_id)
        assert r2.get("user_intent") == "ask_info"
        assert r2.get("response")

    def test_thread_isolation(self):
        """不同 thread_id 会话隔离"""
        r1 = run_query("推荐科幻电影", thread_id="e2e_iso_1")
        r2 = run_query("你好", thread_id="e2e_iso_2")
        assert r1.get("user_intent") == "find_movie"
        assert r2.get("user_intent") == "chat"

"""LangGraph 工作流 端到端测试"""

from graph.graph import build_graph, route_after_intent, run_query
from graph.nodes import respond_node
from graph.state import AgentState


class TestWorkflowBuild:
    """工作流构建测试"""

    def test_build_graph(self):
        graph = build_graph()
        assert graph is not None
        # 验证节点注册
        assert "intent_agent" in graph.nodes
        assert "retrieval_agent" in graph.nodes
        assert "knowledge_agent" in graph.nodes
        assert "chat_agent" in graph.nodes
        assert "plan_agent" in graph.nodes
        assert "recommendation_agent" in graph.nodes
        assert "respond_node" in graph.nodes

    def test_get_mermaid(self):
        from graph.graph import get_workflow_mermaid
        mermaid = get_workflow_mermaid()
        assert mermaid is not None
        assert len(mermaid) > 0


class TestWorkflowRouting:
    """工作流路由测试"""

    def test_clarify_route_key(self):
        state = {"user_intent": "clarify"}
        assert route_after_intent(state) == "clarify"

    def test_out_of_scope_route_key(self):
        state = {"user_intent": "out_of_scope"}
        assert route_after_intent(state) == "out_of_scope"

    def test_respond_node_clarification(self):
        result = respond_node({
            "response": "",
            "need_clarification": True,
            "clarification_question": "你想看电影还是电视剧？",
        })
        assert result["response"] == "你想看电影还是电视剧？"

    def test_respond_node_out_of_scope(self):
        result = respond_node({
            "response": "",
            "user_intent": "out_of_scope",
            "suggested_new_intent": "code_generation",
        })
        assert "腾讯视频" in result["response"]
        assert "code_generation" in result["response"]

    def test_find_movie_route(self):
        result = run_query("推荐科幻电影")
        assert result.get("user_intent") == "find_movie"
        assert result.get("intent_confidence", 0) >= 0.70
        assert len(result.get("retrieved_videos", [])) >= 1
        assert len(result.get("response", "")) > 0

    def test_ask_info_route(self):
        result = run_query("介绍一下张毅")
        assert result.get("user_intent") == "ask_info"
        assert len(result.get("response", "")) > 0

    def test_chat_greeting_route(self):
        result = run_query("你好")
        assert result.get("user_intent") == "chat"
        response = result.get("response", "")
        assert any(kw in response for kw in ["你好", "欢迎", "嗨", "观影"])

    def test_make_plan_route(self):
        result = run_query("帮我规划周末看什么")
        assert result.get("user_intent") == "make_plan"
        assert result.get("plan", {}).get("time_slot") is not None
        assert len(result.get("response", "")) > 0

    def test_chat_thanks_route(self):
        result = run_query("谢谢")
        assert result.get("user_intent") == "chat"
        assert len(result.get("response", "")) > 0


class TestWorkflowMultiTurn:
    """多轮对话测试"""

    def test_multi_turn_same_thread(self):
        """同一 thread_id 连续对话"""
        t_id = "test_multi_turn"

        r1 = run_query("你好", thread_id=t_id)
        assert r1.get("user_intent") == "chat"

        r2 = run_query("推荐科幻电影", thread_id=t_id)
        assert r2.get("user_intent") == "find_movie"
        assert len(r2.get("retrieved_videos", [])) >= 1

    def test_different_threads_isolation(self):
        """不同 thread_id 会话隔离"""
        r1 = run_query("你好", thread_id="thread_a")
        r2 = run_query("推荐科幻电影", thread_id="thread_b")

        assert r1.get("user_intent") == "chat"
        assert r2.get("user_intent") == "find_movie"


class TestWorkflowEdgeCases:
    """边界情况测试"""

    def test_unknown_intent_route(self):
        result = run_query("abcdefghijk")
        assert result.get("user_intent") in ("unknown", "chat")
        assert len(result.get("response", "")) > 0

    def test_empty_query(self):
        result = run_query("")
        assert result.get("user_intent") == "unknown"
        assert result.get("intent_confidence") == 0.0

    def test_response_not_empty(self):
        """所有路由都应该有回复"""
        queries = ["推荐电影", "介绍一下", "你好", "嗯嗯"]
        for q in queries:
            result = run_query(q)
            assert result.get("response") is not None, f"路由 {q} 无回复"
            assert len(result.get("response", "")) > 0, f"路由 {q} 回复为空"

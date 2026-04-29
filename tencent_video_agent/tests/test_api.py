"""FastAPI 接口单元测试"""

from fastapi.testclient import TestClient

from api.routes import app

client = TestClient(app)


class TestHealth:
    """健康检查测试"""

    def test_health_check(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestChat:
    """单轮对话测试"""

    def test_chat_find_movie(self):
        resp = client.post("/chat", json={
            "query": "推荐科幻电影",
            "thread_id": "test_find_movie",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_intent"] == "find_movie"
        assert data["intent_confidence"] >= 0.70
        assert len(data["response"]) > 0
        assert isinstance(data["retrieved_videos"], list)
        assert data["thread_id"] == "test_find_movie"

    def test_chat_greeting(self):
        resp = client.post("/chat", json={
            "query": "你好",
            "thread_id": "test_greeting",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_intent"] == "chat"
        assert any(kw in data["response"] for kw in ["你好", "欢迎", "嗨", "观影"])

    def test_chat_ask_info(self):
        resp = client.post("/chat", json={
            "query": "介绍一下张毅",
            "thread_id": "test_ask_info",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_intent"] == "ask_info"
        assert len(data["response"]) > 0

    def test_chat_make_plan(self):
        resp = client.post("/chat", json={
            "query": "帮我规划周末看什么",
            "thread_id": "test_make_plan",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_intent"] == "make_plan"
        assert data["plan"].get("time_slot") is not None
        assert len(data["response"]) > 0

    def test_chat_empty_query(self):
        resp = client.post("/chat", json={
            "query": "",
            "thread_id": "test_empty",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_intent"] == "unknown"
        assert data["intent_confidence"] == 0.0

    def test_chat_unknown_query(self):
        resp = client.post("/chat", json={
            "query": "abcdefghijk",
            "thread_id": "test_unknown",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_intent"] in ("unknown", "chat")
        assert len(data["response"]) > 0


class TestMultiTurn:
    """多轮对话测试"""

    def test_multi_turn(self):
        messages = [
            {"role": "user", "content": "你好"},
            {"role": "user", "content": "推荐科幻电影"},
        ]
        resp = client.post("/chat/multi", json={
            "messages": messages,
            "thread_id": "api_multi_turn",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_intent"] == "find_movie"
        assert len(data["retrieved_videos"]) >= 1
        assert len(data["response"]) > 0


class TestWorkflow:
    """工作流可视化测试"""

    def test_workflow_mermaid(self):
        resp = client.get("/workflow/mermaid")
        assert resp.status_code == 200
        data = resp.json()
        assert "mermaid" in data
        assert len(data["mermaid"]) > 0
        assert "flowchart" in data["mermaid"] or "graph" in data["mermaid"]

"""Test fixtures that keep LLM-dependent workflow tests offline."""

import pytest


class FakeResponse:
    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    def invoke(self, prompt):
        system = prompt[0].get("content", "") if isinstance(prompt, list) else ""
        user = prompt[-1].get("content", "") if isinstance(prompt, list) else str(prompt)
        query = user.rsplit("\n用户：", 1)[-1].strip()

        if "意图识别" in system:
            return FakeResponse(self._intent_response(query))

        if "对话管理" in system:
            return FakeResponse("你好，欢迎来聊观影。")

        if "观影计划" in system or "time_slot" in user:
            return FakeResponse(
                '{"time_slot": "周末", "mood": null, "genre": null, '
                f'"region": null, "keywords": "{query}"}}'
            )

        if "查询类型" in system or "query_type" in user:
            return FakeResponse('{"query_type": "search", "entity_name": "张毅"}')

        return FakeResponse("已找到相关信息。")

    @staticmethod
    def _intent_response(query: str) -> str:
        if not query:
            return '{"intent": "unknown", "confidence": 0.0, "reason": "空输入"}'

        if any(word in query for word in ["爬虫", "Python", "订票", "支付", "Excel"]):
            return (
                '{"intent": "out_of_scope", "confidence": 0.86, '
                '"reason": "超出当前观影助手能力", '
                '"suggested_new_intent": "code_generation"}'
            )

        if query in {"你好", "谢谢", "再见", "嗯嗯"} or query.startswith("消息"):
            return '{"intent": "chat", "confidence": 0.9, "reason": "闲聊"}'

        if any(word in query for word in ["规划", "安排"]):
            return '{"intent": "make_plan", "confidence": 0.95, "reason": "观影计划"}'

        if any(word in query for word in ["介绍", "谁执导", "演过"]):
            return '{"intent": "ask_info", "confidence": 0.95, "reason": "查询信息"}'

        if any(word in query for word in ["推荐", "找", "好看", "高分", "movie"]):
            return '{"intent": "find_movie", "confidence": 0.95, "reason": "找片"}'

        if query == "abcdefghijk" or set(query) <= {"a"}:
            return '{"intent": "unknown", "confidence": 0.0, "reason": "无意义输入"}'

        return '{"intent": "chat", "confidence": 0.8, "reason": "默认闲聊"}'


@pytest.fixture(autouse=True)
def fake_llm(monkeypatch):
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    fake = FakeLLM()
    monkeypatch.setattr("agents.intent_agent.get_llm", lambda: fake)
    monkeypatch.setattr("agents.chat_agent.get_llm", lambda: fake)
    monkeypatch.setattr("agents.knowledge_agent.get_llm", lambda: fake)
    monkeypatch.setattr("agents.plan_agent.get_llm", lambda: fake)

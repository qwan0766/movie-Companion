"""知识查询 Agent — 完全基于 LLM 的查询识别与回答生成"""

import json
from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentState
from tools.knowledge_tools import knowledge_search
from utils.llm_client import get_llm
from utils.prompts import build_query_detect_prompt, build_rag_prompt


def _detect_query_with_llm(user_text: str) -> tuple[str, str]:
    """使用 LLM 识别查询类型和实体名称"""
    llm = get_llm()
    prompt = build_query_detect_prompt(user_text)
    response = llm.invoke(prompt)
    content = response.content.strip()

    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content[:-3].strip()

    result = json.loads(content)
    return result.get("query_type", "search"), result.get("entity_name", "")


def _generate_rag_response(user_text: str, query_type: str, entity_name: str) -> dict:
    """使用 LLM 生成知识问答回复"""
    result = knowledge_search(query_type, entity_name)
    raw_data = result.get("data", [])

    try:
        llm = get_llm()
        data_for_prompt = raw_data if isinstance(raw_data, list) else [raw_data]
        prompt = build_rag_prompt(user_text, data_for_prompt, query_type)
        response = llm.invoke(prompt)
        reply = response.content.strip()
    except Exception:
        reply = f"没有找到与「{entity_name}」相关的信息，请确认名称是否正确。"

    return {"knowledge_result": result, "response": reply}


class KnowledgeAgent(BaseAgent):
    """知识查询 Agent — 完全基于 LLM"""

    name: str = "knowledge_agent"

    def process(self, state: AgentState) -> dict:
        """处理知识查询"""
        messages = state.get("messages", [])
        if not messages:
            return {
                "knowledge_result": {},
                "response": "请问你想了解哪部影视作品或哪位演员/导演的信息？",
                "errors": ["没有用户消息"],
                "next": "__end__",
            }

        last_msg = messages[-1]
        user_text = last_msg if isinstance(last_msg, str) else (
            last_msg.content if hasattr(last_msg, "content")
            else last_msg.get("content", "")
        )

        try:
            query_type, entity_name = _detect_query_with_llm(user_text)
            result = _generate_rag_response(user_text, query_type, entity_name)
        except Exception:
            result = {
                "knowledge_result": {},
                "response": "抱歉，处理你的问题出错了，请稍后再试。",
            }

        return {**result, "next": "__end__"}

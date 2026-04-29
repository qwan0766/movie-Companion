"""对话管理 Agent — 完全基于 LLM 的闲聊处理"""

from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentState
from utils.llm_client import get_llm
from utils.prompts import build_chat_prompt


class ChatAgent(BaseAgent):
    """对话管理 Agent — 完全基于 LLM"""

    name: str = "chat_agent"

    def process(self, state: AgentState) -> dict:
        """处理闲聊/问候类对话"""
        messages = state.get("messages", [])
        if not messages:
            return {
                "response": "你好！有什么可以帮你的吗？",
                "next": "__end__",
            }

        last_msg = messages[-1]
        user_text = last_msg if isinstance(last_msg, str) else (
            last_msg.content if hasattr(last_msg, "content")
            else last_msg.get("content", "")
        )

        try:
            llm = get_llm()
            prompt = build_chat_prompt(user_text)
            response = llm.invoke(prompt)
            reply = response.content.strip()
        except Exception:
            reply = "你好！有什么可以帮你的吗？"

        return {
            "response": reply,
            "next": "__end__",
        }

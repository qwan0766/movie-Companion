"""意图识别 Agent — 完全基于 LLM 的意图分类"""

from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentState
from utils.llm_client import get_llm
from utils.prompts import build_intent_prompt


def _classify_with_llm(user_text: str) -> tuple[str, float, str]:
    """使用 LLM 进行意图分类"""
    import json
    llm = get_llm()
    prompt = build_intent_prompt(user_text)
    response = llm.invoke(prompt)
    content = response.content.strip()

    # 清理可能的 markdown 代码块
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content[:-3].strip()

    result = json.loads(content)
    intent = result.get("intent", "unknown")
    confidence = float(result.get("confidence", 0.0))
    reason = result.get("reason", "LLM 分类")
    return intent, confidence, reason


class IntentAgent(BaseAgent):
    """意图识别 Agent — 完全基于 LLM"""

    name: str = "intent_agent"

    def process(self, state: AgentState) -> dict:
        """对用户最新输入进行意图分类"""
        messages = state.get("messages", [])
        if not messages:
            return {
                "user_intent": "unknown",
                "intent_confidence": 0.0,
                "errors": ["没有用户消息"],
            }

        last_msg = messages[-1]
        if isinstance(last_msg, str):
            user_text = last_msg
        elif hasattr(last_msg, "content"):
            user_text = last_msg.content
        else:
            user_text = last_msg.get("content", "")

        try:
            intent, confidence, _ = _classify_with_llm(user_text)
        except Exception:
            intent, confidence = "unknown", 0.0

        return {
            "user_intent": intent,
            "intent_confidence": confidence,
            "next": intent,
        }

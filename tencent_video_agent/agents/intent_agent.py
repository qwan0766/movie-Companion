"""意图识别 Agent — 基于 LLM 的开放式意图识别"""

from agents.base_agent import BaseAgent
from graph.state import AgentState
from utils.llm_client import get_llm
from utils.prompts import build_intent_prompt


LOW_CONFIDENCE_THRESHOLD = 0.55
DEFAULT_CLARIFICATION_QUESTION = (
    "你是想让我推荐影视、查询影视信息，还是帮你制定观影计划？"
)
def _classify_with_llm(user_text: str) -> dict:
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

    return json.loads(content)


def _normalize_intent_result(result: dict) -> dict:
    """Normalize LLM JSON into graph state fields."""
    intent = result.get("intent", "unknown")
    confidence = float(result.get("confidence", 0.0))
    reason = result.get("reason", "LLM 分类")
    need_clarification = bool(result.get("need_clarification", False))
    clarification_question = result.get("clarification_question", "")
    suggested_new_intent = result.get("suggested_new_intent", "")

    if intent not in {
        "find_movie",
        "ask_info",
        "make_plan",
        "chat",
        "clarify",
        "out_of_scope",
        "unknown",
    }:
        suggested_new_intent = suggested_new_intent or intent
        intent = "out_of_scope"

    if intent not in {"unknown", "out_of_scope"} and confidence < LOW_CONFIDENCE_THRESHOLD:
        intent = "clarify"
        need_clarification = True

    if intent == "clarify":
        need_clarification = True
        clarification_question = clarification_question or DEFAULT_CLARIFICATION_QUESTION

    if intent == "out_of_scope":
        need_clarification = False

    return {
        "user_intent": intent,
        "intent_confidence": confidence,
        "intent_reason": reason,
        "need_clarification": need_clarification,
        "clarification_question": clarification_question,
        "suggested_new_intent": suggested_new_intent,
        "next": intent,
    }


class IntentAgent(BaseAgent):
    """意图识别 Agent — 允许澄清和能力边界判断"""

    name: str = "intent_agent"

    def process(self, state: AgentState) -> dict:
        """对用户最新输入进行意图分类"""
        messages = state.get("messages", [])
        if not messages:
            return {
                "user_intent": "unknown",
                "intent_confidence": 0.0,
                "intent_reason": "没有用户消息",
                "need_clarification": False,
                "clarification_question": "",
                "suggested_new_intent": "",
                "errors": ["没有用户消息"],
            }

        last_msg = messages[-1]
        if isinstance(last_msg, str):
            user_text = last_msg
        elif hasattr(last_msg, "content"):
            user_text = last_msg.content
        else:
            user_text = last_msg.get("content", "")

        if not user_text.strip():
            return _normalize_intent_result({
                "intent": "unknown",
                "confidence": 0.0,
                "reason": "空输入",
            })

        try:
            result = _classify_with_llm(user_text)
        except Exception:
            result = {
                "intent": "unknown",
                "confidence": 0.0,
                "reason": "LLM 分类失败",
            }

        return _normalize_intent_result(result)

"""LangGraph 工作流 — Agent 统一状态定义"""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """所有 Agent 共享的统一状态"""

    messages: Annotated[list, add_messages]
    """完整对话历史（LangGraph 自动管理）"""

    user_intent: str
    """用户意图: find_movie / ask_info / make_plan / chat / clarify / out_of_scope / unknown"""

    intent_confidence: float
    """意图识别置信度 0~1"""

    intent_reason: str
    """意图识别原因"""

    need_clarification: bool
    """是否需要追问用户"""

    clarification_question: str
    """澄清问题"""

    suggested_new_intent: str
    """超出当前能力时建议的新意图类型"""

    retrieved_videos: list[dict]
    """视频检索结果列表"""

    knowledge_result: dict
    """知识查询结果"""

    plan: dict
    """观影计划"""

    response: str
    """最终回复文本"""

    errors: list[str]
    """错误记录"""

    next: str
    """路由控制: 下一站 Agent 名称 / __end__"""

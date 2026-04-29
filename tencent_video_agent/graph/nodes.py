"""LangGraph 工作流 — 节点函数定义

每个节点包装对应 Agent 的 process() 方法，作为 StateGraph 的 Node。
"""

import functools
import logging

from agents.intent_agent import IntentAgent
from agents.retrieval_agent import RetrievalAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.chat_agent import ChatAgent
from agents.plan_agent import PlanAgent
from agents.recommendation_agent import RecommendationAgent
from graph.state import AgentState

# Agent 实例（单例）
intent_agent = IntentAgent()
retrieval_agent = RetrievalAgent()
knowledge_agent = KnowledgeAgent()
chat_agent = ChatAgent()
plan_agent = PlanAgent()
recommendation_agent = RecommendationAgent()

logger = logging.getLogger(__name__)


def safe_node(node_func):
    """节点安全包装器：捕获异常、记录错误、返回安全默认值"""
    @functools.wraps(node_func)
    def wrapper(state: AgentState) -> dict:
        try:
            return node_func(state)
        except Exception as e:
            logger.exception("节点 %s 执行异常: %s", node_func.__name__, e)
            return {
                "response": "抱歉，处理时出了点问题，请稍后再试。",
                "errors": [f"{node_func.__name__}: {str(e)}"],
                "next": "__end__",
            }
    return wrapper


@safe_node
def intent_node(state: AgentState) -> dict:
    """意图识别节点"""
    return intent_agent.process(state)


@safe_node
def retrieval_node(state: AgentState) -> dict:
    """视频检索节点"""
    return retrieval_agent.process(state)


@safe_node
def knowledge_node(state: AgentState) -> dict:
    """知识查询节点"""
    return knowledge_agent.process(state)


@safe_node
def chat_node(state: AgentState) -> dict:
    """对话管理节点"""
    return chat_agent.process(state)


@safe_node
def plan_node(state: AgentState) -> dict:
    """观影计划节点"""
    return plan_agent.process(state)


@safe_node
def recommendation_node(state: AgentState) -> dict:
    """推荐生成节点"""
    return recommendation_agent.process(state)


def respond_node(state: AgentState) -> dict:
    """回复生成节点 — 收集最终回复（不包装，安全兜底）

    按优先级选择回复：response > 数据推断 > 默认问候
    """
    response = state.get("response", "")

    if not response:
        if state.get("retrieved_videos"):
            count = len(state["retrieved_videos"])
            response = f"为你找到 {count} 部视频，想了解更多详情吗？"
        elif state.get("knowledge_result", {}).get("data"):
            response = "已找到相关信息，请问还想了解什么？"
        elif state.get("plan", {}).get("schedule"):
            response = "已为你制定好观影计划，看看是否满意？"
        else:
            response = "请问有什么可以帮你的？"

    return {"response": response, "next": "__end__"}

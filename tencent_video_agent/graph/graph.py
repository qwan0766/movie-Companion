"""LangGraph 工作流 — StateGraph 构建与编译"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from graph.nodes import (
    chat_node,
    intent_node,
    knowledge_node,
    plan_node,
    recommendation_node,
    respond_node,
    retrieval_node,
)
from graph.state import AgentState


def route_after_intent(state: AgentState) -> str:
    """根据意图识别结果路由到对应 Agent"""
    return state.get("user_intent", "unknown")


def build_graph() -> StateGraph:
    """构建并编译 LangGraph 工作流

    工作流结构:
        START → intent_agent
                ├── find_movie → retrieval_agent → recommendation_agent
                ├── ask_info   → knowledge_agent
                ├── make_plan  → plan_agent
                ├── chat       → chat_agent
                ├── unknown    → chat_agent
                ├── clarify    → respond_node
                └── out_of_scope → respond_node
        各 Agent → respond_node → END
    """
    builder = StateGraph(AgentState)

    # 注册节点
    builder.add_node("intent_agent", intent_node)
    builder.add_node("retrieval_agent", retrieval_node)
    builder.add_node("knowledge_agent", knowledge_node)
    builder.add_node("chat_agent", chat_node)
    builder.add_node("plan_agent", plan_node)
    builder.add_node("recommendation_agent", recommendation_node)
    builder.add_node("respond_node", respond_node)

    # START → 意图识别
    builder.add_edge(START, "intent_agent")

    # 意图识别 → 条件路由
    builder.add_conditional_edges(
        "intent_agent",
        route_after_intent,
        {
            "find_movie": "retrieval_agent",
            "ask_info": "knowledge_agent",
            "make_plan": "plan_agent",
            "chat": "chat_agent",
            "unknown": "chat_agent",
            "clarify": "respond_node",
            "out_of_scope": "respond_node",
        },
    )

    # 各 Agent → 回复生成
    builder.add_edge("retrieval_agent", "recommendation_agent")
    builder.add_edge("recommendation_agent", "respond_node")
    builder.add_edge("knowledge_agent", "respond_node")
    builder.add_edge("plan_agent", "respond_node")
    builder.add_edge("chat_agent", "respond_node")

    # 回复生成 → END
    builder.add_edge("respond_node", END)

    # 编译（含记忆机制）
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)

    return graph


def run_query(query: str, thread_id: str = "default") -> dict:
    """运行单次查询

    Args:
        query: 用户输入
        thread_id: 会话 ID（同一 ID 可累积对话历史）

    Returns:
        工作流最终状态
    """
    graph = build_graph()
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = AgentState(
        messages=[{"role": "user", "content": query}],
        user_intent="",
        intent_confidence=0.0,
        intent_reason="",
        need_clarification=False,
        clarification_question="",
        suggested_new_intent="",
        retrieved_videos=[],
        knowledge_result={},
        plan={},
        response="",
        errors=[],
        next="",
    )

    result = graph.invoke(initial_state, config=config)
    return result


def run_multiturn(messages: list[dict], thread_id: str = "default") -> dict:
    """多轮对话运行

    Args:
        messages: 消息列表 [{"role": "user", "content": "..."}, ...]
        thread_id: 会话 ID
    """
    graph = build_graph()
    config = {"configurable": {"thread_id": thread_id}}

    state = AgentState(
        messages=messages,
        user_intent="",
        intent_confidence=0.0,
        intent_reason="",
        need_clarification=False,
        clarification_question="",
        suggested_new_intent="",
        retrieved_videos=[],
        knowledge_result={},
        plan={},
        response="",
        errors=[],
        next="",
    )

    result = graph.invoke(state, config=config)
    return result


def get_workflow_mermaid() -> str:
    """获取工作流的 Mermaid 流程图"""
    graph = build_graph()
    return graph.get_graph().draw_mermaid()

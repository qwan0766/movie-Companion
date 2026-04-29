"""FastAPI 路由 — 封装 LangGraph 工作流为 RESTful 接口"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from api.config import CORS_ORIGINS, SERVICE_NAME, SERVICE_VERSION
from graph.graph import build_graph, get_workflow_mermaid, run_multiturn, run_query

# ── Pydantic 请求/响应模型 ─────────────────────────────────────────────


class ChatRequest(BaseModel):
    """单轮对话请求"""
    query: str = Field(..., description="用户输入文本", min_length=0)
    thread_id: str = Field("default", description="会话 ID，同一 ID 可累积对话历史")


class MultiTurnRequest(BaseModel):
    """多轮对话请求"""
    messages: list[dict] = Field(..., description="消息列表，格式: [{'role': 'user', 'content': '...'}]")
    thread_id: str = Field("default", description="会话 ID")


class ChatResponse(BaseModel):
    """对话响应"""
    user_intent: str = ""
    intent_confidence: float = 0.0
    response: str = ""
    retrieved_videos: list[dict] = []
    knowledge_result: dict = {}
    plan: dict = {}
    errors: list[str] = []
    thread_id: str = "default"


# ── FastAPI 应用 ──────────────────────────────────────────────────────

app = FastAPI(
    title="腾讯视频智能观影助手 API",
    description="基于 LangGraph 的多 Agent 智能观影助手后端服务",
    version=SERVICE_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 路由 ──────────────────────────────────────────────────────────────


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """单轮对话 — 输入用户文本，返回意图分类、检索结果和回复"""
    try:
        result = run_query(request.query, thread_id=request.thread_id)
        return _build_response(result, request.thread_id)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "error_code": "CHAT_ERROR"},
        )


@app.post("/chat/multi", response_model=ChatResponse)
async def chat_multi(request: MultiTurnRequest):
    """多轮对话 — 传入完整消息历史，支持上下文累积"""
    try:
        result = run_multiturn(request.messages, thread_id=request.thread_id)
        return _build_response(result, request.thread_id)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "error_code": "CHAT_MULTI_ERROR"},
        )


@app.get("/workflow/mermaid")
async def workflow_mermaid():
    """获取 LangGraph 工作流 Mermaid 流程图"""
    try:
        mermaid = get_workflow_mermaid()
        return {"mermaid": mermaid}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "error_code": "MERMAID_ERROR"},
        )


# ── 全局异常处理 ─────────────────────────────────────────────────────


@app.exception_handler(Exception)
async def global_exception_handler(request: Any, exc: Exception) -> JSONResponse:
    """全局异常兜底"""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error_code": "INTERNAL_ERROR"},
    )


# ── 工具函数 ─────────────────────────────────────────────────────────


def _build_response(result: dict, thread_id: str) -> ChatResponse:
    """将工作流结果映射为 ChatResponse"""
    return ChatResponse(
        user_intent=result.get("user_intent", ""),
        intent_confidence=result.get("intent_confidence", 0.0),
        response=result.get("response", ""),
        retrieved_videos=result.get("retrieved_videos", []),
        knowledge_result=result.get("knowledge_result", {}),
        plan=result.get("plan", {}),
        errors=result.get("errors", []),
        thread_id=thread_id,
    )

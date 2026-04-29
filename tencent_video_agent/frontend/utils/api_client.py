"""FastAPI 后端客户端封装"""

from typing import Any

import httpx
import streamlit as st

API_BASE_URL = "http://localhost:8000"
REQUEST_TIMEOUT = 60


@st.cache_data(ttl=60, show_spinner=False)
def health_check() -> dict[str, Any]:
    """服务健康检查（缓存 60 秒）"""
    try:
        resp = httpx.get(f"{API_BASE_URL}/health", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def send_chat(query: str, thread_id: str = "default") -> dict[str, Any]:
    """单轮对话

    Args:
        query: 用户输入
        thread_id: 会话 ID

    Returns:
        响应 JSON（含 user_intent / response / retrieved_videos 等字段）
    """
    try:
        resp = httpx.post(
            f"{API_BASE_URL}/chat",
            json={"query": query, "thread_id": thread_id},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except httpx.TimeoutException:
        return {
            "response": "请求超时了，请稍后再试。",
            "errors": ["timeout"],
            "user_intent": "unknown",
            "intent_confidence": 0.0,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
        }
    except httpx.HTTPStatusError as e:
        return {
            "response": f"服务返回错误 ({e.response.status_code})，请稍后再试。",
            "errors": [f"http_{e.response.status_code}"],
            "user_intent": "unknown",
            "intent_confidence": 0.0,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
        }
    except Exception as e:
        return {
            "response": "无法连接到服务，请确认后端已启动（python main.py）。",
            "errors": [f"connection_error: {str(e)}"],
            "user_intent": "unknown",
            "intent_confidence": 0.0,
            "retrieved_videos": [],
            "knowledge_result": {},
            "plan": {},
        }

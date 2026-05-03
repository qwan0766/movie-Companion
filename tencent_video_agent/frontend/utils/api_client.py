"""FastAPI 后端客户端封装（含流式 SSE 支持）"""

from __future__ import annotations

import json
import os
from typing import Any, Generator

import httpx
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")
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


def stream_chat(
    query: str, thread_id: str = "default"
) -> Generator[tuple[str, str], None, None]:
    """SSE 流式对话 — 生成器，产出 (event_type, data) 元组

    Args:
        query: 用户输入
        thread_id: 会话 ID

    Yields:
        (event_type, data) 元组
        - ("stage", "正在分析你的需求...")
        - ("token", "推")   ← 逐字内容
        - ("result", '{"response":"...",...}')
    """
    url = f"{API_BASE_URL}/chat/stream"
    payload = {"query": query, "thread_id": thread_id}

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            with client.stream("POST", url, json=payload) as resp:
                current_event = ""
                for line in resp.iter_lines():
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("event: "):
                        current_event = line[7:]
                    elif line.startswith("data: "):
                        data = line[6:]
                        if current_event == "token":
                            try:
                                data = json.loads(data)
                            except json.JSONDecodeError:
                                pass
                        if current_event:
                            yield current_event, data
                        current_event = ""
    except Exception as e:
        yield "error", str(e)

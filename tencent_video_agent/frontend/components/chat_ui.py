"""对话界面组件 — 基于 st.chat_message"""

from typing import Any

import streamlit as st


def render_message(msg: dict, idx: int) -> None:
    """渲染单条消息气泡

    Args:
        msg: {"role": "user"/"assistant", "content": "...", "data": {...}}
        idx: 消息索引（用于 key）
    """
    role = msg.get("role", "user")
    content = msg.get("content", "")
    avatar = "🧑" if role == "user" else "🤖"

    with st.chat_message(role, avatar=avatar):
        st.markdown(content)


def render_chat_history(messages: list[dict]) -> None:
    """渲染完整对话历史"""
    for i, msg in enumerate(messages):
        # 跳过流式输出阶段临时插入的空数据消息
        data = msg.get("data")
        if data is None and msg["role"] == "assistant" and not msg.get("content", ""):
            continue
        render_message(msg, i)


def get_last_assistant_data(messages: list[dict]) -> dict | None:
    """获取最后一条助手消息附带的数据"""
    for msg in reversed(messages):
        if msg.get("role") == "assistant" and "data" in msg:
            return msg["data"]
    return None

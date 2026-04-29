"""对话界面组件 — 消息气泡 + 历史列表"""

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

    if role == "user":
        st.markdown(
            f"""<div style='
                background-color: #dcf8c6;
                border-radius: 12px;
                padding: 8px 14px;
                margin: 4px 0 4px auto;
                max-width: 85%;
                text-align: right;
                word-wrap: break-word;
            '>🧑 <b>{content}</b></div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""<div style='
                background-color: #f0f0f0;
                border-radius: 12px;
                padding: 8px 14px;
                margin: 4px auto 4px 0;
                max-width: 85%;
                word-wrap: break-word;
            '>🤖 {content}</div>""",
            unsafe_allow_html=True,
        )


def render_chat_history(messages: list[dict]) -> None:
    """渲染完整对话历史

    Args:
        messages: 消息列表
    """
    for i, msg in enumerate(messages):
        render_message(msg, i)


def get_last_assistant_data(messages: list[dict]) -> dict | None:
    """获取最后一条助手消息附带的数据

    Returns:
        如果最后一条消息是 assistant 且有 data 字段则返回，否则 None
    """
    for msg in reversed(messages):
        if msg.get("role") == "assistant" and "data" in msg:
            return msg["data"]
    return None

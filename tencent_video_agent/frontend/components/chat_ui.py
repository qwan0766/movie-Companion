"""Chat UI components with GPT-like message layout."""

from html import escape

import streamlit as st


def _format_message_text(content: str) -> str:
    """Escape user content while preserving line breaks for HTML bubbles."""
    return escape(content).replace("\n", "<br>")


def build_message_html(role: str, content: str, streaming: bool = False) -> str:
    """Build one chat message row without Streamlit's default avatar chrome."""
    safe_content = _format_message_text(content)
    if streaming:
        safe_content = f"{safe_content}<span class='chat-cursor'>▌</span>"

    if role == "user":
        return (
            "<div class='chat-row chat-row-user'>"
            f"<div class='chat-bubble chat-bubble-user'>{safe_content}</div>"
            "</div>"
        )

    return (
        "<div class='chat-row chat-row-assistant'>"
        f"<div class='chat-bubble chat-bubble-assistant'>{safe_content}</div>"
        "</div>"
    )


def render_message(msg: dict) -> None:
    """Render a single chat message bubble."""
    role = msg.get("role", "user")
    content = msg.get("content", "")
    st.markdown(build_message_html(role, content), unsafe_allow_html=True)


def render_chat_history(messages: list[dict]) -> None:
    """Render complete chat history."""
    for msg in messages:
        data = msg.get("data")
        if data is None and msg.get("role") == "assistant" and not msg.get("content", ""):
            continue
        render_message(msg)

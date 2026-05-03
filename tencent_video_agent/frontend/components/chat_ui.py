"""Chat UI components with GPT-like message layout."""

from html import escape
import re

import streamlit as st


def _format_user_text(content: str) -> str:
    """Escape user content; CSS preserves line breaks inside bubbles."""
    return escape(content)


def _format_assistant_text(content: str) -> str:
    """Convert line-based assistant text into stable HTML blocks."""
    parts: list[str] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            parts.append("<div class='chat-spacer'></div>")
            continue

        safe = escape(line)
        if line.startswith("【") and line.endswith("】"):
            parts.append(f"<div class='chat-section-title'>{safe}</div>")
            continue

        m = re.match(r"^(\d+)\.\s*(.+)$", line)
        if m:
            parts.append(
                "<div class='chat-list-item'>"
                f"<span class='chat-list-num'>{m.group(1)}</span>"
                f"<span class='chat-list-body'>{escape(m.group(2))}</span>"
                "</div>"
            )
            continue

        parts.append(f"<div class='chat-line'>{safe}</div>")

    return "".join(parts)


def build_message_html(role: str, content: str, streaming: bool = False) -> str:
    """Build one chat message row without Streamlit's default avatar chrome."""
    safe_content = (
        _format_user_text(content)
        if role == "user"
        else _format_assistant_text(content)
    )
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

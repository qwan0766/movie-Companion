"""腾讯视频智能观影助手 — 流式输出 | 大厂深色简约风格

Design: awesome-design / Coolors / Material Icons
启动方式: streamlit run frontend/app.py
"""

import json
import os
import sys
import uuid
from typing import Any

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import streamlit as st

from frontend.components.chat_ui import render_chat_history
from frontend.components.knowledge_panel import render_knowledge_panel
from frontend.components.plan_panel import render_plan_panel
from frontend.components.video_card import render_video_grid
from frontend.lucide_icons import icon
from frontend.utils.api_client import health_check, stream_chat

st.set_page_config(
    page_title="腾讯视频智能观影助手",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 全局样式 ────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ══════════════════════════════════════════════
   awesome-design · 大厂深色简约风
   #00A1D6 腾讯蓝  |  Material Icons  |  Coolors palette
   ══════════════════════════════════════════════ */

@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700&display=swap');

:root {
    --primary: #00A1D6;
    --primary-hover: #0090C0;
    --primary-light: rgba(0,161,214,0.12);
    --accent-red: #FF4B4B;
    --success-green: #00C853;
    --bg-main: #0F1117;
    --bg-surface: #1A1C23;
    --bg-card: #1E2030;
    --bg-hover: #252840;
    --text-primary: #F0F2F5;
    --text-secondary: #A0A3A8;
    --text-muted: #6B6E78;
    --border: #2A2D3A;
    --radius-sm: 8px;
    --radius-md: 12px;
}
html, body, .stApp { background: var(--bg-main) !important; margin: 0 !important; padding: 0 !important; }
.stApp, p, li, .stMarkdown, .stMarkdown p {
    font-family: "Noto Sans SC", "PingFang SC", "HarmonyOS Sans", system-ui, -apple-system, sans-serif !important;
    color: var(--text-primary) !important;
}
h1 { font-size: 26px !important; font-weight: 700 !important; color: var(--text-primary) !important; letter-spacing: -0.3px !important; margin-top: 0 !important; }
h2 { font-size: 18px !important; font-weight: 600 !important; color: var(--text-primary) !important; }
h3 { font-size: 16px !important; font-weight: 600 !important; color: var(--text-primary) !important; }
h4 { font-size: 15px !important; font-weight: 600 !important; color: var(--text-primary) !important; }

/* ═══ Hide Streamlit chrome ═══ */
#MainMenu, footer, .stDeployButton { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
/* Hide toolbar but show sidebar toggle as floating button */
div[data-testid="stToolbar"] {
    position: fixed !important;
    right: 8px !important;
    top: 8px !important;
    background: transparent !important;
    z-index: 9999 !important;
    padding: 0 !important;
    margin: 0 !important;
    height: auto !important;
    width: auto !important;
}
div[data-testid="stToolbar"] button:first-child { display: inline-flex !important; }
div[data-testid="stToolbar"] button:not(:first-child) { display: none !important; }

/* ═══ Sidebar ═══ */
section[data-testid="stSidebar"] {
    min-width: 260px !important;
    width: 260px !important;
    max-width: 260px !important;
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
    visibility: visible !important;
    opacity: 1 !important;
}
section[data-testid="stSidebar"] > div { padding: 20px 16px !important; }
section[data-testid="stSidebar"] .sb-brand-text { color: var(--text-primary) !important; }
section[data-testid="stSidebar"] .sb-brand-sub { color: var(--text-muted) !important; }
section[data-testid="stSidebar"] .sb-label { color: var(--text-muted) !important; }
section[data-testid="stSidebar"] .stButton > button {
    color: var(--text-secondary) !important;
    border: 1px solid var(--border) !important;
    background: var(--bg-card) !important;
    box-shadow: none !important;
    font-size: 13px !important;
    padding: 6px 12px !important;
    justify-content: flex-start !important;
    height: auto !important;
    border-radius: var(--radius-sm) !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    border-color: var(--primary) !important;
    color: var(--primary) !important;
    background: rgba(0,161,214,0.05) !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--primary) !important;
    color: #fff !important;
    border-color: var(--primary) !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: var(--primary-hover) !important;
    color: #fff !important;
}
section[data-testid="stSidebar"] hr { border-color: var(--border) !important; }
section[data-testid="stSidebar"] .sb-brand { border-bottom-color: var(--border) !important; }
.sb-brand { display:flex; align-items:center; gap:10px; margin-bottom:20px; padding-bottom:16px; border-bottom:1px solid var(--border); }
.sb-brand .lucide-icon { flex-shrink:0; }
.sb-brand-text { font-weight:700 !important; font-size:17px !important; color:var(--text-primary) !important; letter-spacing:.5px; }
.sb-brand-sub { font-size:11px !important; color:var(--text-muted) !important; margin-top:1px !important; }
.sb-label { font-size:10px !important; text-transform:uppercase !important; letter-spacing:1.5px !important; color:var(--text-muted) !important; margin:20px 0 8px 0 !important; }

/* ═══ Buttons ═══ */
.stButton > button {
    background: var(--primary) !important; color: #fff !important;
    border: none !important; border-radius: var(--radius-sm) !important;
    font-weight: 500 !important; font-size: 13px !important; height: 36px !important;
    padding: 0 18px !important; transition: all .2s !important;
}
.stButton > button:hover {
    background: var(--primary-hover) !important;
    box-shadow: 0 2px 12px rgba(0,161,214,0.3) !important;
    transform: translateY(-1px) !important;
}
/* Ghost buttons for secondary actions */
.stButton > button[kind="secondary"] {
    background: transparent !important; border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important; box-shadow: none !important;
    height: 32px !important; font-size: 12px !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--primary) !important; color: var(--primary) !important;
}

/* ═══ Text Input ═══ */
.stTextInput > div > div > input {
    background: var(--bg-card) !important; color: var(--text-primary) !important;
    border: 1px solid var(--border) !important; border-radius: var(--radius-sm) !important;
    padding: 8px 14px !important; font-size: 14px !important;
    caret-color: var(--primary) !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px rgba(0,161,214,0.12) !important;
}
.stTextInput > div > div > input::placeholder { color: var(--text-muted) !important; }

/* ═══ Chat Input ═══ */
[data-testid="stChatInput"] textarea {
    background: var(--bg-card) !important; color: var(--text-primary) !important;
    border: 1px solid var(--border) !important; border-radius: var(--radius-sm) !important;
    padding: 8px 14px !important; font-size: 14px !important;
    caret-color: var(--primary) !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px rgba(0,161,214,0.12) !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--text-muted) !important; }
[data-testid="stChatInput"] { margin-bottom: 8px !important; }

/* ═══ Chat Messages ═══ */
div[data-testid="stChatMessage"] {
    display: flex !important;
    align-items: flex-start !important;
    gap: 8px !important;
    padding: 0 !important;
    margin: 6px 0 !important;
}
div[data-testid="stChatMessageContent"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius-md) var(--radius-md) var(--radius-md) 4px !important;
    padding: 12px 16px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.2) !important;
    border-left: 3px solid var(--primary) !important;
    max-width: 92% !important;
}
div[data-testid="stChatMessageContent"] p {
    margin: 0 0 6px 0 !important; font-size: 14px !important; line-height: 1.65 !important;
    color: var(--text-primary) !important;
}
div[data-testid="stChatMessageContent"] p:last-child { margin-bottom: 0 !important; }
div[data-testid="stChatMessageContent"] strong { color: #fff !important; }
div[data-testid="stChatMessageContent"] code {
    background: rgba(0,0,0,0.3) !important; padding: 1px 6px !important;
    border-radius: 4px !important; font-size: 13px !important;
}
/* User message: right-aligned with right accent border */
[data-testid="stChatMessage"]:has([aria-label="user"]) [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #1E2030, #1A1C23) !important;
    border-left: none !important; border-right: 3px solid var(--primary) !important;
    border-radius: var(--radius-md) var(--radius-md) 4px var(--radius-md) !important;
    margin-left: auto !important;
}
/* User avatar on the right side */
[data-testid="stChatMessage"]:has([aria-label="user"]) [data-testid="stChatMessageAvatar"] {
    order: 2 !important;
}
div[data-testid="stChatMessageAvatar"] { font-size: 20px !important; padding: 2px !important; }

/* ═══ Video Grid — row gap #4 ═══ */
div[data-testid="column"] { gap: 0 !important; }
.video-card-wrap {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important; margin-bottom: 16px !important;  /* ← 行间距 */
    transition: all 0.3s cubic-bezier(0.25,0.46,0.45,0.94) !important;
    cursor: default !important;
}
.video-card-wrap:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5) !important;
    border-color: rgba(0,161,214,0.3) !important;
}
.video-poster { width:100%; aspect-ratio:16/9; display:flex; align-items:center; justify-content:center; position:relative; overflow:hidden; }
.video-poster-icon { font-size:36px !important; opacity:0.7 !important; }
.video-poster-overlay {
    position:absolute; top:0; right:0;
    background:rgba(0,0,0,0.55); padding:3px 10px;
    border-radius:0 0 0 8px; font-size:13px; font-weight:600;
    backdrop-filter:blur(4px); color:#fff;
}
.video-body { padding:12px 14px 14px !important; }
.video-title-row { display:flex; justify-content:space-between; align-items:flex-start; gap:8px; }
.video-title-text { font-size:14px !important; font-weight:600 !important; color:var(--text-primary) !important; line-height:1.4; }
.video-rating { font-weight:700 !important; font-size:13px !important; white-space:nowrap !important; }
.video-rating-high { color:var(--success-green) !important; }
.video-rating-mid { color:var(--primary) !important; }
.video-rating-low { color:var(--text-muted) !important; }
.video-meta { color:var(--text-muted) !important; font-size:11px !important; margin:3px 0 !important; }
.video-desc {
    color:var(--text-secondary) !important; font-size:12px !important;
    line-height:1.5 !important; margin-top:6px !important;
    display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;
}
.video-tag {
    display:inline-block; background:var(--primary-light); color:var(--primary);
    font-size:11px; padding:1px 10px; border-radius:20px; margin:2px 4px 2px 0;
}

/* ═══ Knowledge Panel ═══ */
.k-card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:18px 20px; margin:10px 0; }
.k-card .k-item { padding:3px 0; font-size:14px; color:var(--text-primary); }
.k-card .k-meta { color:var(--text-muted); font-size:12px; margin-top:10px; }

/* ═══ Plan Panel ═══ */
.plan-item { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:14px 18px; margin:6px 0; transition:border-color .2s; }
.plan-item:hover { border-color:var(--primary); }
.plan-num { display:inline-flex; align-items:center; justify-content:center; width:30px; height:30px; background:var(--primary); color:#fff; border-radius:50%; font-weight:700; font-size:13px; flex-shrink:0; }

/* ═══ Section Header ═══ */
.section-header { font-size:17px; font-weight:600; color:var(--text-primary); padding-bottom:6px; border-bottom:2px solid var(--primary); margin-bottom:14px; }

/* ═══ Misc ═══ */
[data-testid="stMetricValue"] { color:var(--primary) !important; font-weight:700 !important; }
[data-testid="stMetricLabel"] { color:var(--text-secondary) !important; font-size:12px !important; }
.stAlert { background:var(--bg-card) !important; border:1px solid var(--border) !important; color:var(--text-primary) !important; }
.stInfo { background:rgba(0,161,214,0.06) !important; border-left:3px solid var(--primary) !important; }
hr { border-color:var(--border) !important; }
.stSpinner > div > div { border-top-color:var(--primary) !important; }
::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }

/* Lucide icons */
.lucide-icon { display:inline-block; vertical-align:middle; }
.video-poster-icon .lucide-icon { width:36px; height:36px; opacity:0.7; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"
if "loading" not in st.session_state:
    st.session_state.loading = False
if "selected_data" not in st.session_state:
    st.session_state.selected_data = None


def reset_session() -> None:
    st.session_state.messages = []
    st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"
    st.session_state.selected_data = None


def send_query(text: str) -> None:
    """快捷发送 query"""
    if text and not st.session_state.loading:
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.loading = True
        st.rerun()


# ═══════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(
    f'<div class="sb-brand">'
    f'{icon("clapperboard", 28, style="color:#00A1D6;")}'
    f'<div>'
    f'<div class="sb-brand-text">腾讯视频</div>'
    f'<div class="sb-brand-sub">智能观影助手</div>'
    f'</div></div>',
    unsafe_allow_html=True)

    if st.button("➕ 新对话", use_container_width=True, type="primary"):
        reset_session()
        st.rerun()

    svc = health_check()
    if svc.get("status") == "ok":
        st.markdown(
            '<div style="display:flex;align-items:center;gap:6px;margin:14px 0;font-size:12px;">'
            '<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--success-green);"></span>'
            '<span style="color:var(--success-green);">服务运行中</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="sb-label">快速尝试</div>', unsafe_allow_html=True)

    # 可点击的快捷按钮 #2
    for label, val in [
        ("🎯 推荐科幻电影", "推荐科幻电影"),
        ("📖 介绍一下张毅", "介绍一下张毅"),
        ("📋 规划周末看什么", "帮我规划周末看什么"),
    ]:
        if st.button(label, use_container_width=True, key=f"sb_{val[:6]}"):
            send_query(val)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

st.markdown(
    f"<h1 style='margin-bottom:2px;'>{icon('clapperboard', 24, style='vertical-align:-4px;')} 智能观影助手</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="color:var(--text-muted);font-size:13px;margin-bottom:18px;">'
    '腾讯视频 · AI 智能推荐与影视咨询</p>',
    unsafe_allow_html=True,
)

chat_col, detail_col = st.columns([0.4, 0.6])

# ═══════ LEFT: CHAT ═══════

with chat_col:
    st.markdown(f"<div class='section-header'>{icon('message-circle', 18)} 对话</div>", unsafe_allow_html=True)

    with st.container(height=520, border=False):
        if not st.session_state.messages:
            st.markdown(f"""
            <div style="text-align:center;padding:60px 20px;">
                <div style="margin-bottom:12px;opacity:0.5;">{icon('clapperboard', 44)}</div>
                <p style="font-size:15px;color:var(--text-secondary);">开始对话吧</p>
                <p style="font-size:12px;color:var(--text-muted);margin-top:4px;">输入你想看的电影类型或演员名字</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            render_chat_history(st.session_state.messages)

        # Streaming
        if st.session_state.loading:
            holder: dict[str, Any] = {"data": None}
            last_q = next(
                (m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"),
                ""
            )
            if last_q:
                def _gen():
                    for ev, dt in stream_chat(last_q, st.session_state.thread_id):
                        if ev == "token":
                            yield dt
                        elif ev == "result":
                            holder["data"] = json.loads(dt)
                        elif ev == "error":
                            yield f"\n(连接错误: {dt})"

                with st.chat_message("assistant", avatar="🤖"):
                    resp = st.write_stream(_gen)

                if holder["data"]:
                    st.session_state.messages.append({
                        "role": "assistant", "content": resp, "data": holder["data"],
                    })
                    st.session_state.selected_data = holder["data"]
                else:
                    st.session_state.messages.append({"role": "assistant", "content": resp})

                st.session_state.loading = False
                st.rerun()

        # 底部留白，避免最后一条消息被裁剪
        if st.session_state.messages:
            st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # ── 输入区 (chat_input 原生支持 Enter 发送，自动清空) ──
    if query := st.chat_input(
        placeholder="例如：推荐科幻电影、介绍一下张毅...",
        disabled=st.session_state.loading,
    ):
        st.session_state.messages.append({"role": "user", "content": query})
        st.session_state.loading = True
        st.rerun()


# ═══════ RIGHT: DETAIL ═══════

with detail_col:
    st.markdown(f"<div class='section-header'>{icon('file-text', 18)} 详情</div>", unsafe_allow_html=True)

    if st.session_state.selected_data is None:
        st.markdown(f"""
        <div style="text-align:center;padding:80px 20px;">
            <div style="margin-bottom:12px;opacity:0.35;">{icon('target', 44)}</div>
            <p style="font-size:15px;color:var(--text-secondary);">开始一段对话</p>
            <p style="font-size:12px;color:var(--text-muted);margin-top:4px;">
                推荐结果、影视知识、观影计划将在这里展示
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        d = st.session_state.selected_data
        intent = d.get("user_intent", "")
        videos = d.get("retrieved_videos", [])
        knowledge = d.get("knowledge_result", {})
        plan = d.get("plan", {})

        if intent == "find_movie" and videos:
            render_video_grid(videos)
        elif intent == "ask_info" and knowledge:
            render_knowledge_panel(knowledge)
        elif intent == "make_plan" and plan:
            render_plan_panel(plan)
        elif intent in ("chat", "unknown"):
            st.info("继续和我聊天吧！有什么观影需求尽管说～")

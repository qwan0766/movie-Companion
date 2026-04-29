"""腾讯视频智能观影助手 — Streamlit 主界面

启动方式: streamlit run frontend/app.py
"""

import os
import sys
import uuid
from typing import Any

# 确保项目根目录在 sys.path 中（解决 streamlit run 的路径问题）
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import streamlit as st

from frontend.components.chat_ui import (
    get_last_assistant_data,
    render_chat_history,
    render_message,
)
from frontend.components.knowledge_panel import render_knowledge_panel
from frontend.components.plan_panel import render_plan_panel
from frontend.components.video_card import render_video_grid
from frontend.utils.api_client import health_check, send_chat

# ── 页面配置 ──────────────────────────────────────────────────────────

st.set_page_config(
    page_title="腾讯视频智能观影助手",
    page_icon="🎬",
    layout="wide",
)

# ── 初始化会话状态 ─────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"

if "loading" not in st.session_state:
    st.session_state.loading = False

if "selected_data" not in st.session_state:
    st.session_state.selected_data = None


def reset_session() -> None:
    """清空当前会话"""
    st.session_state.messages = []
    st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"
    st.session_state.selected_data = None


# ── 顶部标题栏 ──────────────────────────────────────────────────────

title_col, _, btn_col = st.columns([4, 2, 1])
with title_col:
    st.title(":clapper: 腾讯视频智能观影助手")
with btn_col:
    if st.button(":arrows_counterclockwise: 新对话", use_container_width=True):
        reset_session()
        st.rerun()

# 服务状态检查
svc_status = health_check()
if svc_status.get("status") != "ok":
    st.warning(
        ":warning: 后端服务未连接，请确认已执行 `python main.py` 启动 API 服务。"
    )


# ── 双面板布局 ──────────────────────────────────────────────────────

chat_col, detail_col = st.columns([0.4, 0.6])

# ============================== 左侧面板：对话历史 ==============================

with chat_col:
    st.subheader(":speech_balloon: 对话")

    # 对话历史列表
    chat_container = st.container(height=500, border=False)
    with chat_container:
        if not st.session_state.messages:
            st.info("开始对话吧！输入你想看的电影类型或演员名字～")
        else:
            render_chat_history(st.session_state.messages)

    # 输入区域
    with st.container(border=True):
        query = st.text_input(
            "输入消息",
            placeholder="例如：推荐科幻电影、介绍一下张毅、帮我规划周末看什么...",
            label_visibility="collapsed",
            key="query_input",
            disabled=st.session_state.loading,
        )

        col1, col2 = st.columns([4, 1])
        with col2:
            send_btn = st.button(
                "发送",
                type="primary",
                use_container_width=True,
                disabled=st.session_state.loading or not query,
            )

    # 发送消息
    if send_btn and query and not st.session_state.loading:
        st.session_state.loading = True

        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": query})

        # 调用 API
        with st.spinner("思考中..."):
            result = send_chat(query, thread_id=st.session_state.thread_id)

        response_text = result.get("response", "")

        # 添加助手回复（附带完整数据）
        assistant_msg = {
            "role": "assistant",
            "content": response_text,
            "data": result,
        }
        st.session_state.messages.append(assistant_msg)
        st.session_state.selected_data = result
        st.session_state.loading = False
        st.rerun()


# ============================== 右侧面板：详情展示 ==============================

with detail_col:
    st.subheader(":bookmark_tabs: 详情")

    if st.session_state.selected_data is None:
        # 空状态：欢迎信息
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; color: #888;">
            <h3>🎬 开始你的观影之旅</h3>
            <p>试试这样问我：</p>
            <p>🎯 「推荐科幻电影」— 找片推荐</p>
            <p>📖 「介绍一下张毅」— 影视知识</p>
            <p>📋 「帮我规划周末看什么」— 观影计划</p>
            <p>💬 「你好」— 随便聊聊</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        data = st.session_state.selected_data
        intent = data.get("user_intent", "")
        retrieved_videos = data.get("retrieved_videos", [])
        knowledge_result = data.get("knowledge_result", {})
        plan = data.get("plan", {})

        if intent == "find_movie" and retrieved_videos:
            render_video_grid(retrieved_videos)

        elif intent == "ask_info" and knowledge_result:
            render_knowledge_panel(knowledge_result)

        elif intent == "make_plan" and plan:
            render_plan_panel(plan)

        elif intent == "chat" or intent == "unknown":
            # 聊天的响应文本已在左侧显示
            st.info("继续和我聊天吧！有什么观影需求尽管说～")

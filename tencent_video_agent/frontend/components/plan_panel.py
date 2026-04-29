"""观影计划面板组件"""

from typing import Any

import streamlit as st


def render_plan_panel(plan: dict) -> None:
    """渲染观影计划

    Args:
        plan: 计划数据（time_slot, mood, preferences, schedule, total_count）
    """
    if not plan or not plan.get("schedule"):
        st.info("暂无观影计划，试试告诉我你的时间偏好？")
        return

    schedule = plan["schedule"]
    time_slot = plan.get("time_slot", "最近")
    mood = plan.get("mood")

    # 标题
    mood_str = f"，来点{mood}的" if mood else ""
    st.markdown(f"#### :calendar: 为你制定{time_slot}的观影计划{mood_str}")

    # 时间线展示
    for i, item in enumerate(schedule, 1):
        title = item.get("title", "未知")
        rating = item.get("rating", "")
        reason = item.get("reason", "")
        estimated = item.get("estimated_time", "")
        genre = item.get("genre", [])

        if isinstance(genre, str):
            genre = genre.split(",") if genre else []

        with st.container(border=True):
            cols = st.columns([1, 5])

            with cols[0]:
                st.markdown(f"### {i}")

            with cols[1]:
                # 标题和评分
                rating_str = f" ⭐{rating}" if rating else ""
                st.markdown(f"**{title}**{rating_str}")

                # 标签
                tags = " ".join(
                    f":blue-background[{g}]" for g in genre[:2]
                )
                if tags:
                    st.markdown(tags)

                # 推荐理由和时长
                info_parts = []
                if reason:
                    info_parts.append(reason)
                if estimated:
                    info_parts.append(f":hourglass: {estimated}")
                if info_parts:
                    st.caption(" | ".join(info_parts))

    # 底部信息
    total_count = plan.get("total_count", len(schedule))
    total_time = sum(
        120 if item.get("type") == "movie" else 45
        for item in schedule
    )
    hours = total_time // 60
    mins = total_time % 60
    time_hint = f"{hours}h" if mins == 0 else f"{hours}h{mins}min"

    st.divider()
    st.caption(f"共 {total_count} 部，约 {time_hint}")

    if total_count >= 3:
        st.info(":bulb: 观影提示：建议中间适当休息，保护眼睛哦～")

    st.caption("要调整计划吗？告诉我新的需求～")

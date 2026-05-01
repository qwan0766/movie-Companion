"""观影计划面板 — 原生 Streamlit 组件"""

import streamlit as st

from frontend.lucide_icons import icon


def render_plan_panel(plan: dict) -> None:
    if not plan or not plan.get("schedule"):
        st.info("暂无观影计划，试试告诉我你的时间偏好？")
        return

    schedule = plan["schedule"]
    time_slot = plan.get("time_slot", "最近")
    mood = plan.get("mood")

    mood_str = f"，来点{mood}的" if mood else ""
    st.markdown(
        f'<div class="k-card"><h4>{icon("calendar", 18)} 为你制定{time_slot}的观影计划{mood_str}</h4></div>',
        unsafe_allow_html=True,
    )

    for i, item in enumerate(schedule, 1):
        title = item.get("title", "未知")
        rating = item.get("rating", "")
        reason = item.get("reason", "")
        estimated = item.get("estimated_time", "")
        genre = item.get("genre", [])

        if isinstance(genre, str):
            genre = [g.strip() for g in genre.split(",")] if genre else []

        with st.container(border=True):
            cols = st.columns([0.6, 9.4])
            with cols[0]:
                st.markdown(
                    f"<div style='display:flex;align-items:center;justify-content:center;"
                    f"width:34px;height:34px;background:#00A1D6;color:#fff;"
                    f"border-radius:50%;font-weight:700;font-size:15px;'>{i}</div>",
                    unsafe_allow_html=True,
                )
            with cols[1]:
                title_html = f"<b>{title}</b>"
                if rating:
                    title_html += f"&nbsp;&nbsp;<span style='color:#00A1D6;font-weight:600;'>{icon('star', 14)} {rating}</span>"
                st.markdown(title_html, unsafe_allow_html=True)

                if genre:
                    tag_str = " ".join(
                        f":blue-background[{g}]" for g in genre[:2]
                    )
                    st.markdown(tag_str)

                info_parts = []
                if reason:
                    info_parts.append(reason)
                if estimated:
                    info_parts.append(f"{icon('clock', 14)} {estimated}")
                if info_parts:
                    st.caption(" | ".join(info_parts))

    total_count = plan.get("total_count", len(schedule))
    total_time = sum(
        120 if item.get("type") == "movie" else 45 for item in schedule
    )
    h, m = divmod(total_time, 60)
    time_hint = f"{h}h" if m == 0 else f"{h}h{m}min"

    st.divider()
    st.markdown(
        f"共 **:blue[{total_count}]** 部，约 **:blue[{time_hint}]**"
    )

    if total_count >= 3:
        st.info(f"{icon('lightbulb', 16)} 建议中间适当休息，保护眼睛哦～")

    st.caption("要调整计划吗？告诉我新的需求～")

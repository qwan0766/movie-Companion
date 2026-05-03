"""观影计划面板 — 原生 Streamlit 组件"""

from html import escape

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
    html_parts = [
        '<div class="detail-card">',
        f'<div class="detail-card-title">{icon("calendar", 18)} 为你制定{escape(str(time_slot))}的观影计划{escape(mood_str)}</div>',
    ]

    for i, item in enumerate(schedule, 1):
        title = item.get("title", "未知")
        rating = item.get("rating", "")
        reason = item.get("reason", "")
        estimated = item.get("estimated_time", "")
        genre = item.get("genre", [])

        if isinstance(genre, str):
            genre = [g.strip() for g in genre.split(",")] if genre else []

        tag_html = "".join(f'<span class="video-tag">{escape(str(g))}</span>' for g in genre[:3])
        rating_html = (
            f'<span style="color:var(--primary);font-weight:700;">{icon("star", 14)} {escape(str(rating))}</span>'
            if rating else ""
        )
        meta_parts = []
        if reason:
            meta_parts.append(escape(str(reason)))
        if estimated:
            meta_parts.append(f'{icon("clock", 14)} {escape(str(estimated))}')
        meta_html = " | ".join(meta_parts)

        html_parts.extend([
            '<div class="detail-item">',
            '<div class="detail-item-main">',
            f'<span class="plan-num">{i}</span>',
            f'<span>{escape(str(title))}</span>',
            rating_html,
            '</div>',
        ])
        if tag_html:
            html_parts.append(f'<div class="detail-tags">{tag_html}</div>')
        if meta_html:
            html_parts.append(f'<div class="detail-item-meta">{meta_html}</div>')
        html_parts.append('</div>')

    total_count = plan.get("total_count", len(schedule))
    total_time = sum(
        120 if item.get("type") == "movie" else 45 for item in schedule
    )
    h, m = divmod(total_time, 60)
    time_hint = f"{h}h" if m == 0 else f"{h}h{m}min"

    html_parts.append(
        f'<div class="detail-item-meta">共 {total_count} 部，约 {escape(time_hint)}</div>'
    )

    if total_count >= 3:
        html_parts.append(
            f"<div class='plan-tip'>{icon('lightbulb', 16)} 建议中间适当休息，保护眼睛哦～</div>"
        )

    html_parts.append('<div class="detail-item-meta">要调整计划吗？告诉我新的需求。</div>')
    html_parts.append('</div>')
    st.markdown("".join(html_parts), unsafe_allow_html=True)

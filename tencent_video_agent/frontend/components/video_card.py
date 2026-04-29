"""视频推荐卡片 — 16:9 海报占位 + 悬浮阴影 | 大厂简约风格"""

from typing import Any

import streamlit as st

# ── 类型 → 渐变色映射（模拟海报视觉） ──────────────────────────────

GENRE_GRADIENTS: dict[str, str] = {
    "科幻": "linear-gradient(135deg, #0f0c29, #302b63, #24243e)",
    "喜剧": "linear-gradient(135deg, #f12711, #f5af19)",
    "动作": "linear-gradient(135deg, #20002c, #cbb4d4)",
    "爱情": "linear-gradient(135deg, #ee9ca7, #ffdde1)",
    "悬疑": "linear-gradient(135deg, #2c3e50, #3498db)",
    "剧情": "linear-gradient(135deg, #0f2027, #203a43, #2c5364)",
    "动画": "linear-gradient(135deg, #4568dc, #b06ab3)",
    "奇幻": "linear-gradient(135deg, #00b4db, #0083b0)",
    "恐怖": "linear-gradient(135deg, #1a1a2e, #16213e, #0f3460)",
    "纪录片": "linear-gradient(135deg, #2c3e50, #4ca1af)",
    "古装": "linear-gradient(135deg, #8e44ad, #3498db)",
    "战争": "linear-gradient(135deg, #2c3e50, #616161)",
    "武侠": "linear-gradient(135deg, #1a1a2e, #e94560)",
    "冒险": "linear-gradient(135deg, #0f2027, #2980b9)",
    "历史": "linear-gradient(135deg, #3e5151, #dec236)",
}

DEFAULT_GRADIENT = "linear-gradient(135deg, #00A1D6, #005588)"


def _get_gradient(genres: list[str]) -> str:
    for g in genres:
        if g in GENRE_GRADIENTS:
            return GENRE_GRADIENTS[g]
    return DEFAULT_GRADIENT


def _get_genre_icon(genres: list[str]) -> str:
    icon_map = {
        "科幻": "🚀", "喜剧": "😂", "动作": "💥", "爱情": "💕",
        "悬疑": "🔍", "剧情": "🎭", "动画": "✨", "奇幻": "🔮",
        "恐怖": "👻", "纪录片": "🌍", "古装": "🏯", "战争": "⚔️",
        "武侠": "🗡️", "冒险": "🏔️", "历史": "📜",
    }
    for g in genres:
        if g in icon_map:
            return icon_map[g]
    return "🎬"


def render_video_card(video: dict, key: str) -> None:
    """单张视频卡片（海报 + 内容）"""
    title = video.get("title", "未知标题")
    year = video.get("year", "")
    rating = video.get("rating", "")
    genres = video.get("genres", [])
    region = video.get("region", "")
    description = video.get("description", "")

    if isinstance(genres, str):
        genres = genres.split(",") if genres else []

    gradient = _get_gradient(genres)
    icon = _get_genre_icon(genres)
    rating_num = float(rating) if rating else 0

    # 评分 class
    if rating:
        r_class = "video-rating-high" if rating_num >= 9.0 else (
            "video-rating-mid" if rating_num >= 8.0 else "video-rating-low"
        )
    else:
        r_class = ""

    # 元信息
    meta_parts = []
    if year:
        meta_parts.append(str(year))
    if region:
        meta_parts.append(region)
    meta_str = " · ".join(meta_parts)

    # 标签
    tags_html = "".join(
        f'<span class="video-tag">{g}</span>' for g in genres[:3]
    )

    # 简介
    desc_text = description[:90] + "…" if description and len(description) > 90 else (description or "")

    st.markdown(
        f"""<div class="video-card-wrap" style="margin-bottom: 0;">
            <div class="video-poster" style="background: {gradient};">
                <span class="video-poster-icon">{icon}</span>
                <span class="video-poster-overlay">{rating}</span>
            </div>
            <div class="video-body">
                <div class="video-title-row">
                    <span class="video-title-text">{title}</span>
                    <span class="video-rating {r_class}">⭐ {rating}</span>
                </div>
                <div class="video-meta">{meta_str}</div>
                <div class="video-desc">{desc_text}</div>
                <div class="video-tags">{tags_html}</div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_video_grid(videos: list[dict]) -> None:
    """3 列网格（主区域较宽时 3 列，否则 2 列）"""
    if not videos:
        st.info("没有找到匹配的视频。")
        return

    st.markdown(
        f'<p style="color:var(--text-secondary);font-size:14px;margin-bottom:16px;">'
        f'共找到 <strong style="color:var(--primary);font-weight:600;">{len(videos)}</strong> 部视频</p>',
        unsafe_allow_html=True,
    )

    cols_count = 3
    for i in range(0, len(videos), cols_count):
        cols = st.columns(cols_count)
        for j in range(cols_count):
            idx = i + j
            if idx < len(videos):
                with cols[j]:
                    render_video_card(videos[idx], f"v_{idx}")

    st.markdown(
        '<p style="color:var(--text-muted);font-size:12px;text-align:center;'
        'margin-top:12px;">—— 点击卡片上方问详情 ——</p>',
        unsafe_allow_html=True,
    )

"""视频推荐卡片组件 — 丰富卡片网格"""

from typing import Any

import streamlit as st


def render_video_card(video: dict, key: str) -> None:
    """渲染单张视频推荐卡片

    Args:
        video: 视频信息字典（title, year, rating, genres, region, description）
        key: 组件唯一 key（用于 Streamlit 容器）
    """
    title = video.get("title", "未知标题")
    year = video.get("year", "")
    rating = video.get("rating", "")
    genres = video.get("genres", [])
    region = video.get("region", "")
    description = video.get("description", "")

    if isinstance(genres, str):
        genres = genres.split(",") if genres else []

    with st.container(key=key, border=True):
        cols = st.columns([1, 5])

        # 评分列
        rating_str = f"**{rating}**" if rating else ""
        if rating:
            rating_num = float(rating) if rating else 0
            if rating_num >= 9.0:
                rating_display = f":red[{rating_str}]"
            elif rating_num >= 8.0:
                rating_display = f":orange[{rating_str}]"
            else:
                rating_display = rating_str
        else:
            rating_display = ""

        with cols[0]:
            if rating:
                st.metric(label="评分", value=rating)

        with cols[1]:
            # 标题和年份
            title_str = f"**{title}**"
            if year:
                title_str += f"  ({year})"
            st.markdown(title_str)

            # 类型标签
            if genres:
                tags = " ".join(
                    f":blue-background[{g}]" for g in genres[:3]
                )
                st.markdown(tags)

            # 地区
            if region:
                st.caption(f":earth_asia: {region}")

            # 简介（截断）
            if description:
                desc = description[:80] + "..." if len(description) > 80 else description
                st.caption(desc)


def render_video_grid(videos: list[dict]) -> None:
    """2 列网格渲染视频列表

    Args:
        videos: 视频列表
    """
    if not videos:
        st.info("没有找到匹配的视频。")
        return

    st.markdown(f"共找到 **{len(videos)}** 部视频：")

    # 2 列网格
    for i in range(0, len(videos), 2):
        cols = st.columns(2)
        with cols[0]:
            render_video_card(videos[i], f"video_{i}")
        if i + 1 < len(videos):
            with cols[1]:
                render_video_card(videos[i + 1], f"video_{i + 1}")

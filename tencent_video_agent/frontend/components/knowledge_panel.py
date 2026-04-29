"""知识查询结果面板组件"""

from typing import Any

import streamlit as st


def render_knowledge_panel(result: dict) -> None:
    """渲染知识查询结果

    Args:
        result: knowledge_search() 返回的完整结果
    """
    rtype = result.get("type", "")
    data = result.get("data", [])
    source = result.get("source", "sqlite")

    if not data:
        st.info("没有找到相关信息。")
        return

    source_tag = f"数据来源: {source}"

    if rtype == "actor_films":
        _render_actor_films(data, source_tag)
    elif rtype == "director_films":
        _render_director_films(data, source_tag)
    elif rtype == "video_details":
        _render_video_details(data, source_tag)
    elif rtype == "search":
        _render_search_results(data, source_tag)
    else:
        st.warning(f"未知的结果类型: {rtype}")


def _render_actor_films(data: list[dict], source_tag: str) -> None:
    """演员作品列表"""
    if not data:
        st.info("该演员暂无作品信息。")
        return

    actor_name = data[0].get("actor_name", "演员")
    st.markdown(f"#### :clapper: {actor_name} 的作品")

    for v in data[:8]:
        title = v.get("title", "未知")
        year = v.get("year", "")
        rating = v.get("rating", "")
        rating_str = f" ⭐{rating}" if rating else ""
        year_str = f" ({year})" if year else ""

        st.markdown(f"- **{title}**{year_str}{rating_str}")

    if len(data) > 8:
        st.caption(f"...还有 {len(data) - 8} 部作品")

    st.caption(source_tag)


def _render_director_films(data: list[dict], source_tag: str) -> None:
    """导演作品列表"""
    if not data:
        st.info("该导演暂无作品信息。")
        return

    director_name = data[0].get("director_name", "导演")
    st.markdown(f"#### :clapper: {director_name} 执导的作品")

    for v in data[:8]:
        title = v.get("title", "未知")
        year = v.get("year", "")
        rating = v.get("rating", "")
        rating_str = f" ⭐{rating}" if rating else ""
        year_str = f" ({year})" if year else ""

        st.markdown(f"- **{title}**{year_str}{rating_str}")

    if len(data) > 8:
        st.caption(f"...还有 {len(data) - 8} 部作品")

    st.caption(source_tag)


def _render_video_details(data: dict | list, source_tag: str) -> None:
    """视频详情"""
    v = data if isinstance(data, dict) else data[0] if data else {}

    if not v:
        st.info("未找到该视频的详细信息。")
        return

    title = v.get("title", "未知")
    genres = v.get("genres", [])
    year = v.get("year", "未知")
    rating = v.get("rating", "未知")
    region = v.get("region", "未知")
    description = v.get("description", "暂无简介")
    directors = v.get("directors", [])
    actors = v.get("actors", [])

    if isinstance(genres, str):
        genres = genres.split(",") if genres else []

    st.markdown(f"#### :clapper: {title}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("评分", rating)
    with col2:
        st.metric("年份", year)
    with col3:
        genre_str = "/".join(genres[:3]) if genres else "未知"
        st.metric("类型", genre_str)

    if region:
        st.caption(f":earth_asia: {region}")

    st.markdown(f"**简介**：{description}")

    if directors:
        d_names = [d.get("name", "") for d in directors]
        st.markdown(f"**导演**：{' / '.join(d_names)}")

    if actors:
        a_names = [a.get("name", "") for a in actors[:5]]
        suffix = "..." if len(actors) > 5 else ""
        st.markdown(f"**主演**：{' / '.join(a_names)}{suffix}")

    st.caption(source_tag)


def _render_search_results(data: dict, source_tag: str) -> None:
    """混合搜索结果"""
    actors = data.get("actors", [])
    directors = data.get("directors", [])
    videos = data.get("videos", [])

    if not any([actors, directors, videos]):
        st.info("没有找到相关结果。")
        return

    st.markdown("#### :mag: 搜索结果")

    if actors:
        st.markdown("**演员**")
        for a in actors[:3]:
            st.markdown(f"- {a.get('name', '')}")

    if directors:
        st.markdown("**导演**")
        for d in directors[:3]:
            st.markdown(f"- {d.get('name', '')}")

    if videos:
        st.markdown("**视频**")
        for v in videos[:3]:
            st.markdown(f"- {v.get('title', '')} ({v.get('year', '')})")

    st.caption(source_tag)

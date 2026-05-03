"""知识查询结果面板 — 简约卡片风格"""

from html import escape

import streamlit as st

from frontend.lucide_icons import icon


def render_knowledge_panel(result: dict) -> None:
    rtype = result.get("type", "")
    data = result.get("data", [])
    source = result.get("source", "sqlite")

    if not data:
        st.info("没有找到相关信息。")
        return

    if rtype == "actor_films":
        _render_actor_films(data, source)
    elif rtype == "director_films":
        _render_director_films(data, source)
    elif rtype == "video_details":
        _render_video_details(data, source)
    elif rtype == "search":
        _render_search_results(data, source)
    else:
        st.warning(f"未知的结果类型: {rtype}")


def _render_actor_films(data: list[dict], source: str) -> None:
    actor_name = data[0].get("actor_name", "演员")
    items = "".join(
        _film_item(v) for v in data[:10]
    )
    more = f'<div style="color:var(--text-muted);font-size:13px;margin-top:4px;">...还有 {len(data) - 10} 部</div>' if len(data) > 10 else ""
    st.markdown(
        f'<div class="k-card"><h4>{icon("drama", 18)} {escape(str(actor_name))} 的作品</h4>{items}{more}'
        f'<div class="k-meta">{icon("package", 14)} {source}</div></div>',
        unsafe_allow_html=True,
    )


def _render_director_films(data: list[dict], source: str) -> None:
    director_name = data[0].get("director_name", "导演")
    items = "".join(
        _film_item(v) for v in data[:10]
    )
    more = f'<div style="color:var(--text-muted);font-size:13px;margin-top:4px;">...还有 {len(data) - 10} 部</div>' if len(data) > 10 else ""
    st.markdown(
        f'<div class="k-card"><h4>{icon("clapperboard", 18)} {escape(str(director_name))} 执导的作品</h4>{items}{more}'
        f'<div class="k-meta">{icon("package", 14)} {source}</div></div>',
        unsafe_allow_html=True,
    )


def _render_video_details(data: dict | list, source: str) -> None:
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
        genres = [g.strip() for g in genres.split(",")] if genres else []

    d_names = [d.get("name", "") for d in directors]
    a_names = [a.get("name", "") for a in actors[:5]]
    a_suffix = "…" if len(actors) > 5 else ""
    d_str = " / ".join(d_names) if d_names else ""
    a_str = " / ".join(a_names) + a_suffix if a_names else ""
    tags_str = " ".join(f'<span class="video-tag">{escape(str(g))}</span>' for g in genres[:3])

    body = f'<div class="k-card"><h4>{icon("clapperboard", 18)} {escape(str(title))}</h4>'
    body += f'<div style="display:flex;gap:20px;margin:12px 0;font-size:14px;">'
    body += f'<span><span style="color:var(--primary);font-weight:600;">{icon("star", 14)} {escape(str(rating))}</span></span>'
    body += f'<span style="color:var(--text-secondary);">{escape(str(year))}</span>'
    body += f'<span style="color:var(--text-secondary);">{icon("globe", 14)} {escape(str(region))}</span></div>'
    body += f'<div>{tags_str}</div>'
    body += f'<div style="margin-top:10px;font-size:14px;line-height:1.6;color:var(--text-secondary);">{escape(str(description))}</div>'
    if d_str:
        body += f'<div class="k-item" style="margin-top:8px;"><b>导演</b>：{escape(d_str)}</div>'
    if a_str:
        body += f'<div class="k-item"><b>主演</b>：{escape(a_str)}</div>'
    body += f'<div class="k-meta">{icon("package", 14)} {source}</div></div>'

    st.markdown(body, unsafe_allow_html=True)


def _render_search_results(data: dict, source: str) -> None:
    actors = data.get("actors", [])
    directors = data.get("directors", [])
    videos = data.get("videos", [])
    if not any([actors, directors, videos]):
        st.info("没有找到相关结果。")
        return

    sections = ""
    if actors:
        items = "".join(f'<div class="k-item">{icon("drama", 16)} {escape(str(a.get("name", "")))}</div>' for a in actors[:3])
        sections += f'<h4 style="margin-top:12px;">演员</h4>{items}'
    if directors:
        items = "".join(f'<div class="k-item">{icon("clapperboard", 16)} {escape(str(d.get("name", "")))}</div>' for d in directors[:3])
        sections += f'<h4 style="margin-top:12px;">导演</h4>{items}'
    if videos:
        items = "".join(
            f'<div class="k-item">{icon("film", 16)} <b>{escape(str(v.get("title", "")))}</b> '
            f'<span style="color:var(--text-muted);">({escape(str(v.get("year", "")))})</span></div>'
            for v in videos[:3]
        )
        sections += f'<h4 style="margin-top:12px;">视频</h4>{items}'

    st.markdown(
        f'<div class="k-card"><h4>{icon("search", 16)} 搜索结果</h4>{sections}'
        f'<div class="k-meta">{icon("package", 14)} {source}</div></div>',
        unsafe_allow_html=True,
    )


def _film_item(v: dict) -> str:
    title = v.get("title", "未知")
    year = v.get("year", "")
    rating = v.get("rating", "")
    parts = [f'<b>{escape(str(title))}</b>']
    if year:
        parts.append(f'<span style="color:var(--text-muted);">({escape(str(year))})</span>')
    if rating:
        parts.append(f'<span style="color:var(--primary);">{icon("star", 14)} {escape(str(rating))}</span>')
    return f'<div class="k-item">{" ".join(parts)}</div>'

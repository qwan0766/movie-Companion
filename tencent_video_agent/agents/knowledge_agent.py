"""知识查询 Agent — LLM 查询识别 + 结构化知识回复"""

import json
from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentState
from tools.knowledge_tools import knowledge_search
from utils.llm_client import get_llm
from utils.prompts import build_query_detect_prompt


TYPE_LABELS = {
    "movie": "电影",
    "tv": "电视剧",
    "variety": "综艺",
    "animation": "动漫",
    "documentary": "纪录片",
}


def _detect_query_with_llm(user_text: str) -> tuple[str, str]:
    """使用 LLM 识别查询类型和实体名称"""
    llm = get_llm()
    prompt = build_query_detect_prompt(user_text)
    response = llm.invoke(prompt)
    content = response.content.strip()

    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content[:-3].strip()

    result = json.loads(content)
    return result.get("query_type", "search"), result.get("entity_name", "")


def _type_label(value: str) -> str:
    return TYPE_LABELS.get(value, value or "未知类型")


def _format_video_line(index: int, video: dict) -> list[str]:
    title = video.get("title", "未知")
    year = video.get("year", "")
    rating = video.get("rating", "")
    region = video.get("region", "")
    type_label = _type_label(video.get("type", ""))

    meta = []
    if year:
        meta.append(str(year))
    if region:
        meta.append(region)
    if type_label:
        meta.append(type_label)
    if rating:
        meta.append(f"评分 {rating}")

    suffix = f" - {' · '.join(meta)}" if meta else ""
    return [f"{index}. 《{title}》{suffix}"]


def _format_knowledge_response(query_type: str, entity_name: str, data) -> str:
    """Format knowledge result with stable line-based layout."""
    if not data:
        return f"没有找到与「{entity_name}」相关的信息。\n\n可以换一个更具体的作品名、演员名或导演名再试。"

    if query_type == "actor_films":
        lines = [f"找到「{entity_name}」相关作品："]
        for index, item in enumerate(data[:8], 1):
            lines.extend(_format_video_line(index, item))
        if len(data) > 8:
            lines.append(f"还有 {len(data) - 8} 部作品未展示。")
        return "\n".join(lines)

    if query_type == "director_films":
        lines = [f"找到「{entity_name}」执导的作品："]
        for index, item in enumerate(data[:8], 1):
            lines.extend(_format_video_line(index, item))
        if len(data) > 8:
            lines.append(f"还有 {len(data) - 8} 部作品未展示。")
        return "\n".join(lines)

    if query_type == "video_details":
        video = data if isinstance(data, dict) else data[0] if data else {}
        title = video.get("title", entity_name or "该作品")
        genres = video.get("genres", [])
        if isinstance(genres, str):
            genres = [g.strip() for g in genres.split(",")] if genres else []

        lines = [f"《{title}》详情："]
        fields = [
            ("年份", video.get("year")),
            ("地区", video.get("region")),
            ("类型", " / ".join(genres) if genres else None),
            ("评分", video.get("rating")),
            ("简介", video.get("description")),
        ]
        for label, value in fields:
            if value:
                lines.append(f"{label}：{value}")
        return "\n".join(lines)

    if query_type == "search" and isinstance(data, dict):
        lines = [f"找到与「{entity_name}」相关的信息："]
        videos = data.get("videos", [])
        actors = data.get("actors", [])
        directors = data.get("directors", [])
        if videos:
            lines.append("作品：")
            for index, item in enumerate(videos[:5], 1):
                lines.extend(_format_video_line(index, item))
        if actors:
            lines.append("演员：")
            lines.extend(f"{index}. {item.get('name', '')}" for index, item in enumerate(actors[:5], 1))
        if directors:
            lines.append("导演：")
            lines.extend(f"{index}. {item.get('name', '')}" for index, item in enumerate(directors[:5], 1))
        return "\n".join(lines)

    return f"已找到与「{entity_name}」相关的信息。"


def _generate_rag_response(user_text: str, query_type: str, entity_name: str) -> dict:
    """生成结构化知识问答回复"""
    result = knowledge_search(query_type, entity_name)
    reply = _format_knowledge_response(query_type, entity_name or user_text, result.get("data", []))
    return {"knowledge_result": result, "response": reply}


class KnowledgeAgent(BaseAgent):
    """知识查询 Agent — 识别查询后使用统一模板回复"""

    name: str = "knowledge_agent"

    def process(self, state: AgentState) -> dict:
        """处理知识查询"""
        messages = state.get("messages", [])
        if not messages:
            return {
                "knowledge_result": {},
                "response": "请问你想了解哪部影视作品或哪位演员/导演的信息？",
                "errors": ["没有用户消息"],
                "next": "__end__",
            }

        last_msg = messages[-1]
        user_text = last_msg if isinstance(last_msg, str) else (
            last_msg.content if hasattr(last_msg, "content")
            else last_msg.get("content", "")
        )

        try:
            query_type, entity_name = _detect_query_with_llm(user_text)
            result = _generate_rag_response(user_text, query_type, entity_name)
        except Exception:
            result = {
                "knowledge_result": {},
                "response": "抱歉，处理你的问题出错了，请稍后再试。",
            }

        return {**result, "next": "__end__"}

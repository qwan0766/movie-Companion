"""观影计划 Agent — 完全基于 LLM 的参数提取与计划编排"""

import json
from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentState
from tools.search_tools import hybrid_search
from utils.llm_client import get_llm
from utils.prompts import build_plan_parse_prompt

SYSTEM_PROMPT = """你是一个腾讯视频智能助手的观影计划制定Agent。
根据用户的观影需求（时间、类型、人数、心情等），
从片库中筛选合适的视频，并编排成结构化的观影计划。

能力范围:
1. 解析用户的时间安排（今晚、周末、本周等）
2. 理解用户的类型偏好和心情
3. 调用检索工具获取候选片单
4. 按合理顺序编排观影计划
5. 给出推荐理由和观影提示"""


def _parse_plan_with_llm(user_text: str) -> dict:
    """使用 LLM 提取计划参数"""
    llm = get_llm()
    prompt = build_plan_parse_prompt(user_text)
    response = llm.invoke(prompt)
    content = response.content.strip()

    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content[:-3].strip()

    result = json.loads(content)
    return {
        "time_slot": result.get("time_slot") or "今晚",
        "mood": result.get("mood"),
        "genre": result.get("genre"),
        "region": result.get("region"),
        "keywords": result.get("keywords", user_text),
    }


def _build_plan_schedule(videos: list[dict], time_slot: str, mood: str | None) -> list[dict]:
    """编排观影计划时间线"""
    schedule = []
    for i, v in enumerate(videos[:5]):
        estimated = "~120min" if v.get("type") == "movie" else "~45min/集"
        reasons = []
        if i == 0:
            reasons.append("开场推荐")
        elif i == 1:
            reasons.append("渐入佳境")
        elif i >= 2:
            reasons.append("精彩继续" if mood else "值得一看")

        schedule.append({
            "title": v.get("title", ""),
            "year": v.get("year", ""),
            "rating": v.get("rating", ""),
            "type": v.get("type", ""),
            "genre": v.get("genres", []),
            "estimated_time": estimated,
            "reason": reasons[0] if reasons else "推荐观看",
        })
    return schedule


def _format_plan_response(schedule: list[dict], time_slot: str, mood: str | None) -> str:
    """格式化计划为自然语言"""
    if not schedule:
        return ("暂时没有找到合适的影片来制定计划。"
                "你可以告诉我喜欢的类型或时间，我来帮你重新安排！")

    slot_desc = {"今晚": "今晚", "明天": "明天", "周末": "这个周末",
                 "本周": "这周", "今天下午": "今天下午"}.get(time_slot, "最近")
    mood_desc = f"，来点{mood}的" if mood else ""

    lines = [
        f"为你制定{slot_desc}的观影计划{mood_desc}：",
    ]

    for i, item in enumerate(schedule, 1):
        rating_str = f" 评分 {item['rating']}" if item.get("rating") else ""
        genre_str = ""
        if item.get("genre"):
            g = item["genre"]
            genre_str = f" [{', '.join(g[:2])}]" if isinstance(g, list) else f" [{g}]"
        lines.append(
            f"{i}. 《{item['title']}》{rating_str}{genre_str} - "
            f"{item['reason']} | 时长：{item['estimated_time']}"
        )

    total_time = sum(
        120 if item["type"] == "movie" else 45
        for item in schedule
    )
    hours = total_time // 60
    mins = total_time % 60
    time_hint = f"{hours}h" if mins == 0 else f"{hours}h{mins}min"

    total_str = f"共 {len(schedule)} 部，约 {time_hint}"
    lines.append("")
    lines.append(total_str)

    if len(schedule) >= 3:
        lines.append("观影提示：建议中间适当休息，保护眼睛哦～")

    lines.append("")
    lines.append("要调整计划吗？换类型、缩长时间或重新安排都行！")
    return "\n".join(lines)


class PlanAgent(BaseAgent):
    """观影计划 Agent — 完全基于 LLM"""

    name: str = "plan_agent"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.system_prompt = SYSTEM_PROMPT

    def process(self, state: AgentState) -> dict:
        """处理观影计划请求"""
        messages = state.get("messages", [])
        if not messages:
            return {
                "plan": {},
                "response": "请告诉我你的观影需求，比如时间、类型或心情～",
                "errors": ["没有用户消息"],
                "next": "__end__",
            }

        last_msg = messages[-1]
        user_text = last_msg if isinstance(last_msg, str) else (
            last_msg.content if hasattr(last_msg, "content")
            else last_msg.get("content", "")
        )

        try:
            params = _parse_plan_with_llm(user_text)
        except Exception:
            params = {"time_slot": "今晚", "mood": None, "genre": None,
                      "region": None, "keywords": user_text}

        videos = hybrid_search(params["keywords"], n_results=10)
        schedule = _build_plan_schedule(videos, params["time_slot"], params["mood"])

        plan = {
            "time_slot": params["time_slot"],
            "mood": params["mood"],
            "preferences": {
                "genres": [params["genre"]] if params.get("genre") else [],
                "region": params.get("region"),
                "mood": params["mood"],
            },
            "schedule": schedule,
            "total_count": len(schedule),
        }

        existing_videos = state.get("retrieved_videos", [])
        retrieved = existing_videos if existing_videos else videos

        response = _format_plan_response(schedule, params["time_slot"], params["mood"])

        return {
            "plan": plan,
            "retrieved_videos": retrieved,
            "response": response,
            "next": "__end__",
        }

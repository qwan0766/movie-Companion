"""观影计划 Agent — 接收 make_plan 路由，生成结构化观影计划"""

import re
from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentState
from tools.search_tools import hybrid_search, parse_query

SYSTEM_PROMPT = """你是一个腾讯视频智能助手的观影计划制定Agent。
你的职责是根据用户的观影需求（时间、类型、人数、心情等），
从片库中筛选合适的视频，并编排成结构化的观影计划。

能力范围:
1. 解析用户的时间安排（今晚、周末、本周等）
2. 理解用户的类型偏好和心情
3. 调用检索工具获取候选片单
4. 按合理顺序编排观影计划
5. 给出推荐理由和观影提示"""

# ── 时间偏好映射 ───────────────────────────────────────────────────────

TIME_SLOT_PATTERNS: list[tuple[str, str | None, str]] = [
    (r"(今晚|今天晚上|今晚)", "今晚", "晚间"),
    (r"(明天|明天晚上)", "明天", "全天"),
    (r"(周末|周六|周日|星期六|星期天)", "周末", "全天"),
    (r"(这周|本周|这星期)", "本周", "灵活"),
    (r"(下午|今天下午)", "今天下午", "午后"),
]

MOOD_KEYWORDS: dict[str, list[str]] = {
    "轻松": ["轻松", "开心", "欢乐", "搞笑", "愉快", "放松"],
    "刺激": ["刺激", "紧张", "悬疑", "烧脑", "震撼"],
    "感动": ["感动", "感人", "温馨", "温暖", "治愈", "催泪"],
    "经典": ["经典", "怀旧", "老片", "回味"],
    "刺激冒险": ["冒险", "科幻", "奇幻", "动作"],
}


def _extract_time_slot(text: str) -> str:
    """提取时间偏好"""
    for pattern, slot, _ in TIME_SLOT_PATTERNS:
        if re.search(pattern, text):
            return slot
    return "今晚"


def _extract_mood(text: str) -> str | None:
    """提取心情偏好"""
    for mood, keywords in MOOD_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return mood
    return None


def _adjust_query_for_plan(text: str) -> str:
    """根据计划场景调整查询文本，提升检索效果"""
    time_slot = _extract_time_slot(text)
    mood = _extract_mood(text)
    parsed = parse_query(text)

    parts = []
    if parsed.get("genre"):
        parts.append(parsed["genre"])
    if mood:
        parts.append(mood)
    if parsed.get("region"):
        parts.append(parsed["region"])

    query = " ".join(parts) if parts else text
    return query


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


def _format_plan_response(
    schedule: list[dict],
    time_slot: str,
    mood: str | None,
    total_count: int,
) -> str:
    """格式化计划为自然语言"""
    if not schedule:
        return ("暂时没有找到合适的影片来制定计划。"
                "你可以告诉我喜欢的类型或时间，我来帮你重新安排！")

    slot_desc = {"今晚": "今晚", "明天": "明天", "周末": "这个周末",
                 "本周": "这周", "今天下午": "今天下午"}.get(time_slot, "最近")
    mood_desc = f"，来点{mood}的" if mood else ""

    lines = [
        f"为你制定{slot_desc}的观影计划{mood_desc}：\n"
    ]

    for i, item in enumerate(schedule, 1):
        rating_str = f" ⭐{item['rating']}" if item.get("rating") else ""
        genre_str = ""
        if item.get("genre"):
            g = item["genre"]
            genre_str = f" [{', '.join(g[:2])}]" if isinstance(g, list) else f" [{g}]"
        lines.append(
            f"{i}. 《{item['title']}》{rating_str}{genre_str}"
            f"\n   {item['reason']} | 时长：{item['estimated_time']}"
        )

    total_time = sum(
        120 if item["type"] == "movie" else 45
        for item in schedule
    )
    hours = total_time // 60
    mins = total_time % 60
    time_hint = f"{hours}h" if mins == 0 else f"{hours}h{mins}min"

    total_str = f"\n共 {len(schedule)} 部，约 {time_hint}"
    lines.append(total_str)

    if len(schedule) >= 3:
        lines.append("\n💡 观影提示：建议中间适当休息，保护眼睛哦～")

    lines.append("\n要调整计划吗？换类型、缩长时间或重新安排都行！")
    return "\n".join(lines)


class PlanAgent(BaseAgent):
    """观影计划 Agent"""

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

        # 提取偏好
        time_slot = _extract_time_slot(user_text)
        mood = _extract_mood(user_text)
        parsed = parse_query(user_text)

        # 检索候选视频
        search_query = _adjust_query_for_plan(user_text)
        videos = hybrid_search(search_query, n_results=10)

        # 编排计划
        schedule = _build_plan_schedule(videos, time_slot, mood)

        plan = {
            "time_slot": time_slot,
            "mood": mood,
            "preferences": {
                "genres": [parsed["genre"]] if parsed.get("genre") else [],
                "region": parsed.get("region"),
                "mood": mood,
            },
            "schedule": schedule,
            "total_count": len(schedule),
        }

        # 优先使用已有检索结果
        existing_videos = state.get("retrieved_videos", [])
        if not existing_videos and videos:
            retrieved = videos
        else:
            retrieved = existing_videos

        response = _format_plan_response(schedule, time_slot, mood, len(schedule))

        return {
            "plan": plan,
            "retrieved_videos": retrieved,
            "response": response,
            "next": "__end__",
        }

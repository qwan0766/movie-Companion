"""推荐生成 Agent — 结构化展示 + 标签 + 模板推荐语"""

import random
from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentState

SYSTEM_PROMPT = """你是一个腾讯视频智能助手的推荐生成Agent。
根据用户的观影偏好和检索结果，生成个性化的推荐理由和展示。

能力范围:
1. 分析用户偏好（类型、年代、演员、风格等）
2. 对检索结果进行个性化排序和分类
3. 为每部视频生成具体的推荐理由
4. 推荐结果分层展示（最匹配/值得一看/同类推荐）"""

# ── 推荐理由模板 ───────────────────────────────────────────────────────

REASON_TEMPLATES: dict[str, list[str]] = {
    "科幻": ["科幻迷必看，脑洞大开的视觉盛宴", "硬核科幻代表，想象力与科学的完美结合"],
    "喜剧": ["笑点密集，心情不好的时候看它准没错", "轻松幽默的剧情，适合放松时观看"],
    "动作": ["动作场面燃爆，全程无尿点", "打斗设计精良，动作片爱好者的首选"],
    "爱情": ["感人至深的爱情故事，适合静下心来慢慢看", "浪漫温馨，情侣一起看再合适不过"],
    "悬疑": ["剧情多重反转，烧脑程度满分", "悬念设置巧妙，看到最后才恍然大悟"],
    "剧情": ["叙事扎实，演技在线，值得细细品味", "深刻的社会洞察，看完引人深思"],
    "古装": ["服化道精良，古风韵味十足", "历史感厚重，制作精良的古装佳作"],
    "奇幻": ["想象力丰富，构建了一个完整的奇幻世界", "魔法与冒险的精彩融合，沉浸感极强"],
    "恐怖": ["氛围营造出色，胆小慎入", "惊悚程度恰到好处，恐怖片爱好者的优选"],
    "动画": ["画面精美，不仅是给孩⼦看的动画", "动画制作精良，全年龄段都能享受"],
    "纪录片": ["纪实影像的力量，看完收获满满", "内容详实，制作精良的高分纪录片"],
    "犯罪": ["案情节节相扣，犯罪题材的标杆之作", "警匪对决精彩，黑色风格独具魅力"],
}

GENERIC_REASONS = ["评分口碑双丰收，强烈推荐", "观众好评如潮，值得一看", "同类型中的佼佼者，不容错过"]

# ── 标签 ──

RATING_TAG: dict[float, str] = {
    9.0: "神作",
    8.5: "高分",
    8.0: "佳作",
    7.0: "口碑",
}


def _generate_reason(video: dict, user_genre: str | None = None) -> str:
    """为单部视频生成推荐理由（模板）"""
    genres = video.get("genres", [])
    if isinstance(genres, str):
        genres = genres.split(",") if genres else []

    rating = video.get("rating")
    if rating:
        try:
            rating = float(rating)
        except (ValueError, TypeError):
            rating = 0

    matched_genre = None
    for g in genres:
        if g in REASON_TEMPLATES:
            matched_genre = g
            break
    if not matched_genre and user_genre and user_genre in REASON_TEMPLATES:
        matched_genre = user_genre

    if matched_genre:
        return random.choice(REASON_TEMPLATES[matched_genre])
    elif rating and rating >= 9.0:
        return "评分顶尖的神作，不容错过"
    elif rating and rating >= 8.5:
        return "口碑爆棚的高分佳作，强烈推荐"
    else:
        return random.choice(GENERIC_REASONS)


def _build_tag(video: dict, user_prefs: dict) -> str:
    """为视频生成标签"""
    rating = video.get("rating")
    if rating:
        try:
            r = float(rating)
            for threshold, tag in sorted(RATING_TAG.items(), reverse=True):
                if r >= threshold:
                    return tag
        except (ValueError, TypeError):
            pass

    year = video.get("year", "")
    if year:
        try:
            y = int(year)
            if y >= 2024:
                return "新片"
            if y >= 2020:
                return "近年"
        except (ValueError, TypeError):
            pass

    return "推荐"


def _categorize_results(videos: list[dict], user_prefs: dict) -> dict[str, list[dict]]:
    """将结果分层归类"""
    if not videos:
        return {}

    rating_scores = []
    for v in videos:
        r = v.get("rating", 0)
        try:
            rating_scores.append(float(r) if r else 0)
        except (ValueError, TypeError):
            rating_scores.append(0)

    categories: dict[str, list[dict]] = {"best_match": [], "worth_watching": [], "also_good": []}

    for i, v in enumerate(videos):
        score = rating_scores[i] if i < len(rating_scores) else 0
        if score >= 9.0:
            categories["best_match"].append(v)
        elif score >= 8.0:
            categories["worth_watching"].append(v)
        else:
            categories["also_good"].append(v)

    return {k: v for k, v in categories.items() if v}


CATEGORY_LABELS: dict[str, str] = {
    "best_match": "最佳匹配",
    "worth_watching": "值得一看",
    "also_good": "同类推荐",
}

CATEGORY_EMOJIS: dict[str, str] = {
    "best_match": "🏆",
    "worth_watching": "👍",
    "also_good": "🎬",
}


class RecommendationAgent(BaseAgent):
    """推荐生成 Agent — 完全基于 LLM"""

    name: str = "recommendation_agent"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.system_prompt = SYSTEM_PROMPT

    def process(self, state: AgentState) -> dict:
        """生成个性化推荐"""
        videos = state.get("retrieved_videos", [])
        messages = state.get("messages", [])

        if not videos:
            return {
                "response": "暂时没有找到匹配的视频推荐给你，试试换个关键词？",
                "next": "__end__",
            }

        last_msg = messages[-1] if messages else ""
        user_text = last_msg if isinstance(last_msg, str) else (
            last_msg.content if hasattr(last_msg, "content")
            else last_msg.get("content", "")
        )
        categorized = _categorize_results(videos, {})

        # 直接使用结构化数据 + 标签展示（LLM 生成推荐语 API 延时过高）
        lines = ["根据你的偏好，为你精选以下内容：\n"]
        for category_key in ["best_match", "worth_watching", "also_good"]:
            items = categorized.get(category_key, [])
            if not items:
                continue

            label = CATEGORY_LABELS.get(category_key, category_key)
            emoji = CATEGORY_EMOJIS.get(category_key, "•")
            lines.append(f"{emoji} **{label}**")

            for v in items[:3]:
                title = v.get("title", "未知")
                year = v.get("year", "")
                rating = v.get("rating", "")
                year_str = f" ({year})" if year else ""
                rating_str = f" {rating}" if rating else ""
                tag = _build_tag(v, {})
                lines.append(
                    f"  • **{title}**{year_str} ⭐{rating_str} [{tag}]"
                )

            total_in_cat = len(items)
            if total_in_cat > 3:
                lines.append(f"    ...还有 {total_in_cat - 3} 部")
            lines.append("")

        total = sum(len(v) for v in categorized.values())
        if total > 5:
            lines.append(f"共找到 {total} 部相关视频，想看更多细节可以告诉我～")
        else:
            lines.append("感兴趣哪部？我可以告诉你更多详情！")

        return {"response": "\n".join(lines), "next": "__end__"}

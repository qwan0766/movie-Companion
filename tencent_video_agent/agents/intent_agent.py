"""意图识别 Agent — 多轮对话意图分类"""

import re
from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentState

# ── 意图分类关键词规则 ───────────────────────────────────────────────

# 找片意图关键词（权重从高到低）
FIND_MOVIE_PATTERNS = [
    # 强烈信号
    (r"推荐[一几两三四五六七八九十\d部些]", 1.0),
    (r"有[什么哪]((好看|精彩|经典|热门|最新).{0,4})?[的]?[电影剧片综]", 1.0),
    (r"[找求推]((部|些|个).{0,4})?[电影剧片综动纪]", 0.95),
    (r"想看.{0,6}[电影剧片]", 0.95),
    (r"有什么.{0,10}(好看|推荐)", 0.90),
    # 中等信号
    (r"(喜剧|动作|科幻|爱情|悬疑|剧情|古装|奇幻|犯罪|恐怖|战争|动画|纪录片)[的]?[电影剧片]?", 0.85),
    (r"最[近新].{0,4}(电影|剧|片|综艺|动漫)", 0.80),
    (r"评分.{0,4}[高好]", 0.75),
    (r"经典.{0,4}(电影|剧|片)", 0.80),
    # 弱信号
    (r"(电影|电视剧|综艺|动漫|纪录片|影片)", 0.60),
    (r"(好看|精彩|搞笑|感人|刺激)", 0.50),
]

ASK_INFO_PATTERNS = [
    (r"(演员|导演|编剧|主演|角色).{0,6}(是谁|介绍|资料|信息|作品|演过|拍过|执导)", 1.0),
    (r"(介绍|说说|讲讲|科普).{0,6}(演员|导演|影视|电影|剧)", 0.95),
    (r"(谁|哪个演员|哪位导演).{0,12}(演的|拍的|执导|主演)", 0.95),
    (r"还演过|还拍过|代表作|作品有", 0.90),
    (r"(获奖|提名|奖项|奖)", 0.80),
    (r"(评分|评价|口碑|影评)", 0.75),
    (r"(剧情|故事|内容).{0,4}(介绍|讲什么|关于)", 0.85),
]

MAKE_PLAN_PATTERNS = [
    (r"(计划|规划|安排|清单|列表)", 1.0),
    (r"(周末|今晚|明天|这周).{0,6}(看|观影|追)", 0.90),
    (r"帮.{0,4}(计划|规划|安排|做).{0,6}(观影|看|追)", 1.0),
    (r"(观影|看剧|追剧).{0,6}(计划|规划)", 1.0),
    (r"(列|做|制定).{0,4}(个|一份).{0,6}(计划|清单)", 0.95),
]

CHAT_PATTERNS = [
    (r"^(你好|您好|嗨|hi|hello|hey)", 0.90),
    (r"^(早上好|下午好|晚上好|晚安|早安|午安)", 0.90),
    (r"(谢谢|感谢|多谢)", 0.70),
    (r"(再见|拜拜|bye|明天见)", 0.85),
    (r"(天气|心情|哈哈|开心|不错)", 0.60),
    (r"^(好|可以|行|ok|好的|嗯)", 0.50),
]


def _match_patterns(text: str, patterns: list[tuple[str, float]]) -> float:
    """匹配模式列表，返回最高权重（0 表示无匹配）"""
    max_score = 0.0
    for pattern, weight in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            max_score = max(max_score, weight)
    return max_score


def _classify_intent(text: str) -> tuple[str, float, str]:
    """基于规则的意图分类

    Returns:
        (intent, confidence, reason)
    """
    scores: list[tuple[str, float, str]] = []

    fm_score = _match_patterns(text, FIND_MOVIE_PATTERNS)
    scores.append(("find_movie", fm_score, "关键词匹配"))

    ai_score = _match_patterns(text, ASK_INFO_PATTERNS)
    scores.append(("ask_info", ai_score, "关键词匹配"))

    mp_score = _match_patterns(text, MAKE_PLAN_PATTERNS)
    scores.append(("make_plan", mp_score, "关键词匹配"))

    chat_score = _match_patterns(text, CHAT_PATTERNS)
    scores.append(("chat", chat_score, "关键词匹配"))

    # 按置信度降序排列
    scores.sort(key=lambda x: x[1], reverse=True)

    best_intent, best_score, best_reason = scores[0]

    # 阈值判断
    if best_score >= 0.70:
        return best_intent, round(best_score, 2), best_reason
    elif best_score >= 0.40:
        # 低置信度，返回 unknown 但附上最佳猜测
        return "unknown", round(best_score, 2), f"低置信度，最佳猜测: {best_intent}"
    else:
        return "unknown", 0.0, "无法识别意图"


# ── 意图识别 Agent ───────────────────────────────────────────────────

SYSTEM_PROMPT = """你是一个腾讯视频智能助手的意图识别引擎。
你的任务是对用户的输入进行意图分类。

分类类别:
- find_movie: 用户想要找片、推荐、搜索视频
- ask_info: 用户想咨询影视知识、演员/导演信息
- make_plan: 用户想制定观影计划
- chat: 问候、寒暄、与视频无关的话题
- unknown: 无法明确归类"""

FEW_SHOT_EXAMPLES = [
    {"input": "推荐几部好看的悬疑电影", "intent": "find_movie"},
    {"input": "周星驰演过哪些电影", "intent": "ask_info"},
    {"input": "帮我规划周末看什么", "intent": "make_plan"},
    {"input": "你好呀", "intent": "chat"},
]


class IntentAgent(BaseAgent):
    """意图识别 Agent"""

    name: str = "intent_agent"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.system_prompt = SYSTEM_PROMPT
        self.few_shot_examples = FEW_SHOT_EXAMPLES

    def process(self, state: AgentState) -> dict:
        """对用户最新输入进行意图分类"""
        messages = state.get("messages", [])
        if not messages:
            return {
                "user_intent": "unknown",
                "intent_confidence": 0.0,
                "errors": ["没有用户消息"],
            }

        # 取最后一条用户消息
        last_msg = messages[-1]
        user_text = last_msg if isinstance(last_msg, str) else last_msg.get("content", "")

        # 规则分类
        intent, confidence, reason = _classify_intent(user_text)

        return {
            "user_intent": intent,
            "intent_confidence": confidence,
            "next": intent,  # 路由到对应 Agent
        }

    def get_system_prompt(self) -> str:
        """获取完整的 System Prompt（含 Few-shot）"""
        examples_str = "\n".join(
            f"用户: {ex['input']}\n→ intent: {ex['intent']}"
            for ex in self.few_shot_examples
        )
        return f"{self.system_prompt}\n\n示例:\n{examples_str}"

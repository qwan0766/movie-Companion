"""对话管理 Agent — 多轮对话维护 + 闲聊处理"""

import random
from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentState

# ── 闲聊回应模板 ─────────────────────────────────────────────────────

GREETING_RESPONSES = [
    "你好！欢迎来到腾讯视频智能助手，有什么我可以帮你的吗？想看什么类型的电影或剧集？",
    "嗨！我是你的观影小助手，想找什么片尽管告诉我～",
    "你好呀！今天想看点什么？我可以帮你推荐好片！",
]

THANKS_RESPONSES = [
    "不客气！有需要随时找我～",
    "很高兴能帮到你！还有其他想了解的吗？",
    "不用谢，祝你观影愉快！",
]

CLARIFY_RESPONSES = [
    "我没太明白你的意思，你是想找电影看，还是想了解某部影视作品的信息呢？",
    "能说得更具体一些吗？比如你想看什么类型的片子？",
    "请问你是想找片、咨询影视信息，还是制定观影计划呢？",
]

GREETING_KEYWORDS = ["你好", "您好", "嗨", "hi", "hello", "hey", "早上好", "下午好", "晚上好", "晚安", "早安", "午安"]
THANKS_KEYWORDS = ["谢谢", "感谢", "多谢"]

SYSTEM_PROMPT = """你是一个腾讯视频智能助手的对话管理Agent。
你的职责:
1. 以友好热情的语气回应用户的问候和闲聊
2. 在用户意图不明确时主动询问需求
3. 记录对话中用户的偏好信息
4. 在适当时引导用户使用视频推荐功能

回答风格：亲切、专业、简洁。用中文回答。"""


def _is_greeting(text: str) -> bool:
    """判断是否为问候"""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in GREETING_KEYWORDS)


def _is_thanks(text: str) -> bool:
    """判断是否为感谢"""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in THANKS_KEYWORDS)


class ChatAgent(BaseAgent):
    """对话管理 Agent"""

    name: str = "chat_agent"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.system_prompt = SYSTEM_PROMPT

    def process(self, state: AgentState) -> dict:
        """处理闲聊/问候类对话"""
        messages = state.get("messages", [])
        if not messages:
            return {
                "response": "你好！有什么可以帮你的吗？",
                "next": "__end__",
            }

        last_msg = messages[-1]
        user_text = last_msg if isinstance(last_msg, str) else last_msg.get("content", "")

        # 根据输入类型选择回应
        if _is_greeting(user_text):
            response = random.choice(GREETING_RESPONSES)
        elif _is_thanks(user_text):
            response = random.choice(THANKS_RESPONSES)
        elif state.get("user_intent") == "unknown":
            response = random.choice(CLARIFY_RESPONSES)
        else:
            response = f"收到你的消息了。{'你是想找片吗？我可以帮你推荐！' if random.random() < 0.5 else '有什么影视相关的问题尽管问我～'}"

        return {
            "response": response,
            "next": "__end__",
        }

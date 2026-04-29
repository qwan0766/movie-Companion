"""视频检索 Agent — 接收 find_movie 路由，执行混合检索"""

from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentState
from tools.search_tools import hybrid_search, parse_query

SYSTEM_PROMPT = """你是一个腾讯视频智能助手的视频检索Agent。
你的职责是根据用户的找片需求，从片库中检索最匹配的视频内容。

检索策略：
1. 理解用户偏好（类型、年代、演员等）
2. 调用混合检索工具获取候选列表
3. 对结果进行排序和过滤
4. 返回最相关的 Top-N 推荐

注意：如果检索结果为空，如实告知并引导用户调整条件。"""


class RetrievalAgent(BaseAgent):
    """视频检索 Agent"""

    name: str = "retrieval_agent"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.system_prompt = SYSTEM_PROMPT

    def process(self, state: AgentState) -> dict:
        """执行视频检索

        Args:
            state: 当前工作流状态（含 messages 和 user_intent）

        Returns:
            状态更新（填充 retrieved_videos）
        """
        messages = state.get("messages", [])
        if not messages:
            return {
                "retrieved_videos": [],
                "response": "请告诉我你想看什么样的视频？",
                "errors": ["没有用户消息"],
                "next": "__end__",
            }

        # 取最后一条用户消息
        last_msg = messages[-1]
        user_text = last_msg if isinstance(last_msg, str) else last_msg.get("content", "")

        # 解析查询条件
        parsed = parse_query(user_text)

        # 执行混合检索
        results = hybrid_search(user_text, n_results=10)

        # 构建响应
        if not results:
            response = "抱歉，没有找到匹配的视频。你可以试试调整搜索条件，比如换个类型或年代。"
        else:
            # 构建推荐摘要
            genre_info = f" {parsed.get('genre', '')}类" if parsed.get("genre") else ""
            response = f"为你找到以下{genre_info}视频（共{len(results)}部）：\n"
            for i, v in enumerate(results[:5], 1):
                year_str = f" ({v.get('year', '')})" if v.get("year") else ""
                rating_str = f" ⭐{v.get('rating', '')}" if v.get("rating") else ""
                response += f"{i}. 《{v['title']}》{year_str}{rating_str}\n"
            if len(results) > 5:
                response += f"...还有{len(results) - 5}部，可以告诉我更具体的偏好来缩小范围。"
            else:
                response += "以上是你可能感兴趣的内容。要了解更多详情吗？"

        return {
            "retrieved_videos": results,
            "response": response,
            "next": "__end__",
        }

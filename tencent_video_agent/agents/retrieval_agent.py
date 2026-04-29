"""视频检索 Agent — 执行混合检索"""

from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentState
from tools.search_tools import hybrid_search


class RetrievalAgent(BaseAgent):
    """视频检索 Agent"""

    name: str = "retrieval_agent"

    def process(self, state: AgentState) -> dict:
        """执行视频检索"""
        messages = state.get("messages", [])
        if not messages:
            return {
                "retrieved_videos": [],
                "response": "请告诉我你想看什么样的视频？",
                "errors": ["没有用户消息"],
                "next": "__end__",
            }

        last_msg = messages[-1]
        user_text = last_msg if isinstance(last_msg, str) else (
            last_msg.content if hasattr(last_msg, "content")
            else last_msg.get("content", "")
        )

        results = hybrid_search(user_text, n_results=10)

        if not results:
            response = "抱歉，没有找到匹配的视频。你可以试试调整搜索条件，比如换个类型或年代。"
        else:
            response = f"为你找到 {len(results)} 部相关视频。"
            for i, v in enumerate(results[:5], 1):
                year_str = f" ({v.get('year', '')})" if v.get("year") else ""
                rating_str = f" ⭐{v.get('rating', '')}" if v.get("rating") else ""
                response += f"\n{i}. 《{v['title']}》{year_str}{rating_str}"

        return {
            "retrieved_videos": results,
            "response": response,
            "next": "__end__",
        }

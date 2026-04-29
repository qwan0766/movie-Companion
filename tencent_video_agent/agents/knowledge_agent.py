"""知识查询 Agent — 接收 ask_info 路由，执行知识查询"""

from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentState
from tools.knowledge_tools import knowledge_search, detect_query_type

SYSTEM_PROMPT = """你是一个腾讯视频智能助手的知识查询Agent。
你的职责是回答用户关于影视知识的问题，包括演员信息、导演作品、视频详情等。

当用户询问演员/导演/视频信息时，调用知识库查询，
并以清晰、有条理的方式呈现查询结果。"""


class KnowledgeAgent(BaseAgent):
    """知识查询 Agent"""

    name: str = "knowledge_agent"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.system_prompt = SYSTEM_PROMPT

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
        user_text = last_msg if isinstance(last_msg, str) else (last_msg.content if hasattr(last_msg, "content") else last_msg.get("content", ""))

        # 识别查询类型
        query_type, entity_name = detect_query_type(user_text)

        # 执行知识查询
        result = knowledge_search(query_type, entity_name)

        # 格式化结果
        response = self._format_result(result, entity_name)

        return {
            "knowledge_result": result,
            "response": response,
            "next": "__end__",
        }

    def _format_result(self, result: dict, query: str) -> str:
        """格式化查询结果为自然语言"""
        data = result.get("data", [])
        rtype = result.get("type")
        source = result.get("source", "sqlite")

        if rtype == "actor_films":
            if not data:
                return f"没有找到「{query}」的相关作品信息，请确认姓名是否正确。"
            actor_name = data[0].get("actor_name", query)
            lines = [f"以下是{query}参演的作品（共{len(data)}部）："]
            for i, v in enumerate(data[:8], 1):
                lines.append(f"{i}. 《{v['title']}》({v.get('year', '')}) ⭐{v.get('rating', '')}")
            if len(data) > 8:
                lines.append(f"...还有{len(data) - 8}部")
            return "\n".join(lines)

        elif rtype == "director_films":
            if not data:
                return f"没有找到「{query}」的导演作品信息。"
            lines = [f"以下是{query}执导的作品（共{len(data)}部）："]
            for i, v in enumerate(data[:8], 1):
                lines.append(f"{i}. 《{v['title']}》({v.get('year', '')}) ⭐{v.get('rating', '')}")
            if len(data) > 8:
                lines.append(f"...还有{len(data) - 8}部")
            return "\n".join(lines)

        elif rtype == "video_details":
            if not data:
                return f"没有找到「{query}」的详细信息。"
            v = data if isinstance(data, dict) else data[0] if data else {}
            actors = v.get("actors", [])
            directors = v.get("directors", [])
            genres = v.get("genres", [])
            if isinstance(genres, str):
                genres = genres.split(",")

            lines = [
                f"《{v.get('title', query)}》",
                f"类型：{'/'.join(genres) if genres else '未知'}",
                f"年份：{v.get('year', '未知')}  评分：⭐{v.get('rating', '未知')}",
                f"地区：{v.get('region', '未知')}",
                f"简介：{v.get('description', '暂无')}",
            ]
            if directors:
                lines.append(f"导演：{' / '.join(d.get('name', '') for d in directors)}")
            if actors:
                names = [a.get('name', '') for a in actors[:5]]
                lines.append(f"主演：{' / '.join(names)}{'...' if len(actors) > 5 else ''}")
            return "\n".join(lines)

        elif rtype == "search":
            actors = data.get("actors", [])
            directors = data.get("directors", [])
            videos = data.get("videos", [])

            if not any([actors, directors, videos]):
                return f"没有找到与「{query}」相关的信息。"

            lines = [f"关于「{query}」的搜索结果："]
            if actors:
                lines.append(f"\n演员：{' / '.join(a.get('name', '') for a in actors[:3])}")
            if directors:
                lines.append(f"导演：{' / '.join(d.get('name', '') for d in directors[:3])}")
            if videos:
                lines.append(f"视频：{' / '.join(v.get('title', '') for v in videos[:3])}")
            return "\n".join(lines)

        return f"没有找到相关结果，请试试其他关键词。"

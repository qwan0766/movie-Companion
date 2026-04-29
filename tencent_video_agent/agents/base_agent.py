"""Agent 基类 — 所有 Agent 的公共抽象层"""

from abc import ABC, abstractmethod
from typing import Any

from graph.state import AgentState


class BaseAgent(ABC):
    """Agent 抽象基类

    所有具体的 Agent（意图识别、检索、知识查询等）必须继承此类
    并实现 process() 方法。
    """

    name: str = "base_agent"

    def __init__(self, **kwargs: Any) -> None:
        self.name = kwargs.pop("name", self.name)

    @abstractmethod
    def process(self, state: AgentState) -> dict:
        """处理当前状态，返回状态更新

        Args:
            state: 当前工作流状态

        Returns:
            状态更新字典（只包含需要修改的字段）
        """
        ...

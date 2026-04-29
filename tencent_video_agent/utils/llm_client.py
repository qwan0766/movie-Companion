"""统一 LLM 客户端 — 支持 DeepSeek / OpenAI 兼容 API"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 自动加载 .env（项目根目录）
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path, override=True)

# ── 默认配置 ──────────────────────────────────────────────────────────

DEFAULT_PROVIDER = "deepseek"
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_TEMPERATURE = 0.1


def get_llm(**kwargs: Any) -> ChatOpenAI:
    """获取 LLM 实例

    通过环境变量配置：
        LLM_PROVIDER: deepseek | openai （默认 deepseek）
        LLM_API_KEY: API Key
        LLM_MODEL: 模型名（默认 deepseek-v4-flash）
        LLM_BASE_URL: API 地址（默认 https://api.deepseek.com/v1）

    Returns:
        ChatOpenAI 实例（所有兼容 API 统一使用 ChatOpenAI）
    """
    provider = os.getenv("LLM_PROVIDER", DEFAULT_PROVIDER)
    api_key = os.getenv("LLM_API_KEY", "")
    model = os.getenv("LLM_MODEL", DEFAULT_MODEL)
    base_url = os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL)
    temperature = float(os.getenv("LLM_TEMPERATURE", str(DEFAULT_TEMPERATURE)))

    if not api_key:
        raise ValueError(
            "LLM_API_KEY 未设置。请在 .env 中配置 API Key，"
            "或设置环境变量 LLM_API_KEY。"
        )

    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        **kwargs,
    )


def is_llm_enabled() -> bool:
    """检查 LLM 是否启用"""
    return os.getenv("LLM_ENABLED", "false").lower() == "true"

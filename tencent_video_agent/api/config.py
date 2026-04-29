"""API 服务配置"""

import os

API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))
API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() == "true"

CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")

SERVICE_NAME: str = "tencent_video_agent"
SERVICE_VERSION: str = "0.1.0"

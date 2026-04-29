"""腾讯视频智能观影助手 - 入口"""

import uvicorn

from api.config import API_HOST, API_PORT, API_RELOAD


def main() -> None:
    """一键启动 FastAPI 服务"""
    print("腾讯视频智能观影助手 v0.1")
    print(f"API 服务启动: http://{API_HOST}:{API_PORT}")
    print(f"API 文档:     http://{API_HOST}:{API_PORT}/docs")
    print(f"交互式文档:   http://{API_HOST}:{API_PORT}/redoc")
    uvicorn.run(
        "api.routes:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD,
    )


if __name__ == "__main__":
    main()

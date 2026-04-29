"""腾讯视频智能观影助手 - 入口"""


def main() -> None:
    print("腾讯视频智能观影助手 v0.1")
    print("请选择启动模式:")
    print("  1. API 服务: uvicorn api.routes:app --reload")
    print("  2. 前端界面: streamlit run frontend/app.py")
    print("  3. 初始化数据库: python db/init_db.py")


if __name__ == "__main__":
    main()

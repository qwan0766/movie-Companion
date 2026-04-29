"""一键初始化所有数据库（SQLite + Chroma）"""

import sys
from pathlib import Path

# 确保项目根目录在 path 中
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from db.sqlite_db import init_database
from db.chroma_db import init_chroma


def main() -> None:
    """一键初始化 SQLite + Chroma"""
    print("=" * 50)
    print("  腾讯视频智能观影助手 - 数据库初始化")
    print("=" * 50)

    # 1. SQLite
    print("\n[1/2] SQLite 数据库...")
    try:
        init_database()
    except Exception as e:
        print(f"  [ERROR] SQLite 初始化失败: {e}")
        sys.exit(1)

    # 2. Chroma
    print("\n[2/2] Chroma 向量数据库...")
    try:
        init_chroma()
    except Exception as e:
        print(f"  [ERROR] Chroma 初始化失败: {e}")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("  数据库初始化完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()

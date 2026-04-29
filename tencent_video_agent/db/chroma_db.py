"""Chroma 向量数据库模块 - 视频语义检索"""

import json
import os
from pathlib import Path
from typing import Any

import chromadb
from chromadb.api import ClientAPI
from chromadb.errors import NotFoundError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_PERSIST_DIR = PROJECT_ROOT / "data" / "chroma_db"
COLLECTION_NAME = "tencent_videos"


# ── 客户端 ───────────────────────────────────────────────────────────


def get_client(persist_dir: Path | None = None) -> ClientAPI:
    """获取 Chroma 持久化客户端"""
    path = persist_dir or Path(os.getenv("CHROMA_PERSIST_DIR", str(DEFAULT_PERSIST_DIR)))
    path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(path))


# ── 数据准备 ─────────────────────────────────────────────────────────


def _prepare_video_documents() -> list[dict[str, Any]]:
    """从 JSON 加载视频数据，生成 Chroma 文档和元数据"""
    filepath = DATA_DIR / "videos.json"
    with open(filepath, encoding="utf-8") as f:
        videos = json.load(f)

    documents = []
    metadatas = []
    ids = []

    for v in videos:
        genres = ", ".join(v.get("genres", []))
        text = f"{v['title']}\n{v.get('description', '')}\n{genres}"
        documents.append(text)
        metadatas.append({
            "video_id": v["video_id"],
            "title": v["title"],
            "year": v.get("year", 0),
            "type": v.get("type", ""),
            "rating": v.get("rating", 0.0),
            "region": v.get("region", ""),
        })
        ids.append(v["video_id"])

    return {"documents": documents, "metadatas": metadatas, "ids": ids}


# ── 初始化 ───────────────────────────────────────────────────────────


def get_or_create_collection(client: ClientAPI) -> Any:
    """获取或创建视频集合"""
    try:
        collection = client.get_collection(COLLECTION_NAME)
        print(f"[Chroma] 使用已有 collection: '{COLLECTION_NAME}'")
    except NotFoundError:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine", "description": "腾讯视频向量检索"},
        )
        print(f"[Chroma] 已创建 collection: '{COLLECTION_NAME}'")
    return collection


def import_videos_to_chroma(client: ClientAPI | None = None) -> int:
    """将视频数据向量化导入 Chroma"""
    client = client or get_client()
    collection = get_or_create_collection(client)

    # 检查是否已有数据
    existing = collection.count()
    if existing > 0:
        print(f"[Chroma] collection 已有 {existing} 条数据，跳过导入")
        return existing

    data = _prepare_video_documents()
    collection.add(
        documents=data["documents"],
        metadatas=data["metadatas"],
        ids=data["ids"],
    )

    count = collection.count()
    print(f"[Chroma] 已向量化导入 {count} 条视频")
    return count


# ── 检索 ─────────────────────────────────────────────────────────────


def search_similar(
    query: str,
    n_results: int = 5,
    client: ClientAPI | None = None,
    filter_: dict | None = None,
) -> dict:
    """语义相似检索

    Args:
        query: 搜索文本
        n_results: 返回结果数
        client: Chroma 客户端
        filter_: 过滤条件，如 {"type": "movie"}

    Returns:
        包含 documents, metadatas, distances 的字典
    """
    client = client or get_client()
    collection = get_or_create_collection(client)

    kwargs = {
        "query_texts": [query],
        "n_results": n_results,
    }
    if filter_:
        kwargs["where"] = filter_

    results = collection.query(**kwargs)
    return results


def format_search_results(results: dict) -> list[dict]:
    """格式化检索结果为易读的列表"""
    formatted = []
    if not results.get("ids") or not results["ids"][0]:
        return formatted

    for i, doc_id in enumerate(results["ids"][0]):
        meta = results["metadatas"][0][i]
        distance = results["distances"][0][i] if results.get("distances") else 0
        formatted.append({
            "video_id": doc_id,
            "title": meta.get("title", ""),
            "year": meta.get("year", ""),
            "type": meta.get("type", ""),
            "rating": meta.get("rating", ""),
            "score": round(1 - distance, 4),
        })
    return formatted


# ── 一键初始化 ───────────────────────────────────────────────────────


def init_chroma(client: ClientAPI | None = None) -> ClientAPI:
    """初始化 Chroma 并导入数据"""
    client = client or get_client()
    count = import_videos_to_chroma(client)
    print(f"[Chroma] 初始化完成，共 {count} 条")
    return client


if __name__ == "__main__":
    init_chroma()

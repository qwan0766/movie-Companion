# 腾讯视频智能观影助手

基于 LangGraph 的腾讯视频智能观影助手，解决"找片难、疑问多、计划乱"三大痛点。

## 技术栈

- **工作流编排**：LangGraph (StateGraph + Nodes + Edges)
- **LLM 集成**：LangChain + LangGraph
- **API 服务**：FastAPI
- **存储**：SQLite + Chroma（向量数据库）+ Neo4j（知识图谱）
- **前端界面**：Streamlit
- **追踪调试**：LangSmith

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key 等配置

# 3. 初始化数据库（导入模拟数据）
python db/init_db.py

# 4. 启动 API 服务
uvicorn api.routes:app --reload

# 5. 启动前端界面（新终端）
streamlit run frontend/app.py
```

## 项目结构

```
tencent_video_agent/
├── agents/           # 各 Agent 实现
├── graph/            # LangGraph 工作流核心
├── data/             # 模拟数据 & 生成脚本
├── db/               # 数据库初始化与访问
├── vector_db/        # Chroma 向量库
├── knowledge_graph/  # Neo4j 知识图谱
├── api/              # FastAPI 接口
├── frontend/         # Streamlit 前端
├── tools/            # 自定义工具
├── tests/            # 测试用例
├── docs/             # 文档
└── utils/            # 通用工具
```

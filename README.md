# 腾讯视频智能观影助手

基于 **LangGraph** 构建的多 Agent 智能助手，解决腾讯视频用户"**找片难、疑问多、计划乱**"三大痛点，提供智能观影推荐、影视知识问答、观影计划制定一站式服务。

## 技术栈

| 层级 | 技术 |
|------|------|
| 工作流编排 | LangGraph (StateGraph + Nodes + Edges + Checkpoint) |
| LLM 集成 | LangChain + LangGraph |
| API 服务 | FastAPI |
| 存储 | SQLite + Chroma（向量数据库）+ Neo4j（知识图谱） |
| 前端 | Streamlit |
| LLM 模型 | Llama3 / Qwen / 通义千问（可切换 GPT-3.5） |
| 追踪调试 | LangSmith |

## 项目进度

| 阶段 | 内容 | 状态 |
|------|------|------|
| 第一周 | 环境搭建 & 模拟数据生成 | ✅ 已完成 |
| 第二周 | 核心模块开发（Agent + 检索 + 知识库） | ✅ 已完成 |
| 第三周 D1-4 | LangGraph 工作流集成 & 优化 | ✅ 已完成 |
| 第三周 D5 | FastAPI 后端接口开发 | ⏳ 待开始 |
| 第四周 | 前端界面 & 测试 & 文档 | ⏳ 待开始 |

测试覆盖：**146 项测试全部通过**

## 核心功能

- **意图识别**：5 类用户意图分类（找片、咨询、计划、闲聊、其他）
- **视频检索**：语义相似检索 + 传统过滤（类型/年代/演员/评分/地区）混合策略
- **影视知识库**：Neo4j 知识图谱 + RAG 检索（含 SQLite 兜底自动切换）
- **观影计划**：时间/心情解析 + 结构化编排
- **LangGraph 工作流**：条件边路由 + MemorySaver 对话记忆 + Tool Calling
- **LangSmith 追踪**：全链路可观测

## 快速开始

```bash
# 1. 安装依赖
pip install -r tencent_video_agent/requirements.txt

# 2. 配置环境变量
cp tencent_video_agent/.env.example tencent_video_agent/.env
# 编辑 .env 填入必要的 API Key 等配置

# 3. 初始化数据库（导入模拟数据）
cd tencent_video_agent
python db/init_db.py

# 4. 运行测试验证
python -m pytest tests/ -v

# 5. 启动 API 服务
uvicorn api.routes:app --reload

# 6. 启动前端（新终端）
streamlit run frontend/app.py
```

## 项目结构

```
tencent_video_agent/
├── agents/              # Agent 实现（intent / retrieval / knowledge / chat / plan）
├── graph/               # LangGraph 工作流核心（state / nodes / graph）
├── data/                # 模拟数据生成脚本
├── db/                  # 数据库初始化（SQLite + Chroma）
├── vector_db/           # Chroma 向量库
├── knowledge_graph/     # Neo4j 知识图谱（schema / queries）
├── api/                 # FastAPI 接口
├── frontend/            # Streamlit 前端
├── tools/               # 自定义工具（search / knowledge / tool_definitions）
├── tests/               # 测试用例（109+ 项）
├── docs/                # 文档
├── utils/               # 通用工具
├── .env.example
├── requirements.txt
└── main.py

项目进度/              # 各阶段详细计划 & 学习笔记
├── 学习笔记.md          # LangGraph 学习笔记
├── D3-详细计划.md       # Week1 D3 实施计划
└── ...
```

## 工作流架构

```
用户输入 → Intent Agent → 条件路由
                           ├── find_video → Retrieval Agent → 混合检索 → 响应
                           ├── ask_knowledge → Knowledge Agent → 知识图谱 RAG → 响应
                           ├── make_plan → Plan Agent → 观影计划编排 → 响应
                           ├── chat → Chat Agent → 对话管理 → 响应
                           └── other → 默认回复
```

## 开发计划

- [x] Week 1: 环境搭建 + 模拟数据生成与入库
- [x] Week 2 D1-4: 意图识别 Agent + 视频检索系统
- [x] Week 2 D5: 影视知识库（Neo4j + RAG）
- [x] Week 3 D1-2: LangGraph 工作流（StateGraph + 条件路由）
- [x] Week 3 D3-4: 工作流优化（Tool Calling + Plan Agent + LangSmith）
- [ ] Week 3 D5: FastAPI 后端接口开发
- [ ] Week 4 D1-2: Streamlit 前端界面
- [ ] Week 4 D3: 系统测试与性能优化
- [ ] Week 4 D4-5: 文档与演示

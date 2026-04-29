# 腾讯视频智能观影助手 - 开发计划

> 基于 PROJECT_GUIDE.md 整理的开发状态追踪，所有未完成内容标记为「未完成」，除非明确已完成或正在进行。

---

## 项目文件结构

```
movieCompanion/
├── CLAUDE.md             # 开发计划 & 进度追踪
├── PROJECT_GUIDE.md      # 项目指导手册
├── 项目进度/              # 各阶段详细计划 & 学习笔记
│   ├── 学习笔记.md        # LangGraph 学习笔记（Week1 D1-2 ✅）
│   └── D3-详细计划.md     # Week1 D3 详细实施计划
├── tencent_video_agent/  # 【待创建】项目主目录
└── src/                  # （旧代码，待清理）
```

## 项目概览

基于 LangGraph 的腾讯视频智能观影助手，解决"找片难、疑问多、计划乱"三大痛点。

- **工作流编排**：LangGraph (StateGraph + Nodes + Edges + Checkpoint)
- **LLM 集成**：LangChain + LangGraph
- **API 服务**：FastAPI
- **存储**：SQLite + Chroma（向量数据库）+ Neo4j（知识图谱）
- **前端**：Streamlit
- **LLM 模型**：Llama3 / Qwen / 通义千问（可切换 GPT-3.5）
- **追踪调试**：LangSmith

---

## 项目目录结构

```
tencent_video_agent/     # 【未创建】项目主目录
├── agents/              # 各 Agent 实现
├── graph/               # LangGraph 工作流核心
├── data/                # 模拟数据 & 生成脚本
├── vector_db/           # Chroma 向量库
├── knowledge_graph/     # Neo4j 相关
├── api/                 # FastAPI 接口
├── frontend/            # Streamlit 前端
├── tools/               # 自定义工具
├── tests/               # 测试用例
├── docs/                # 文档、笔记、流程图
├── utils/               # 通用工具
├── .env
├── requirements.txt
├── main.py
└── README.md
```

---

## 最终交付物（全部未完成）

- [ ] **交付物 1**：完整可运行的智能观影助手原型（本地一键启动）
- [ ] **交付物 2**：完整技术文档 + 工作流程图（Mermaid / draw.io）
- [ ] **交付物 3**：测试报告（单元测试 + 集成测试 + 端到端测试）
- [ ] **交付物 4**：学习笔记 + 技术调研报告（含踩坑记录、性能数据、优化思路）

---

## 开发计划 & 进度追踪

### 第一周：基础学习与环境搭建

#### 第1-2天：LangGraph 核心概念学习
- [x] **已完成** — 学习笔记（学习笔记.md）
  - LangChain + LangGraph 基础学习 ✅
  - StateGraph、Nodes、Edges、State、Memory 理解 ✅
  - **交付物**：学习笔记 + 技术调研报告 + StateGraph 手绘流程图 ✅ (`学习笔记.md`)

#### 第3天：腾讯视频数据结构熟悉
- [x] **已完成** — 分析视频数据结构（标题、类型、演员、简介、年代、导演等）
- [x] **已完成** — 设计模拟数据生成脚本（generate_data.py）
- [x] **交付物**：模拟数据生成脚本 ✅
  - `tencent_video_agent/data/generate_data.py` — Pydantic 4 实体 + 数据池 + 生成器 + JSON 导出
  - `tencent_video_agent/tests/test_data_generation.py` — 14 项单元测试全部通过
  - 已生成：categories.json (15) / actors.json (60) / directors.json (30) / videos.json (100)
  - 质量验证：引用完整、字段合法、类型分布准确、seed 可复现

#### 第4-5天：开发环境搭建
- [x] **已完成** — 配置 Python 环境 + 安装所有依赖
- [x] **已完成** — 搭建项目标准目录结构（tencent_video_agent/）
- [x] **已完成** — 生成模拟数据并入库
- [x] **交付物**：本地可运行的基础项目结构 + 模拟数据 ✅
  - `requirements.txt` — 全部 20+ 依赖已安装
  - `db/sqlite_db.py` — SQLite 6 张表 + JSON 数据导入
  - `db/chroma_db.py` — Chroma collection 'tencent_videos' + 语义检索
  - `db/init_db.py` — 一键初始化入口
  - 已导入：SQLite 100 条视频 / 60 演员 / 30 导演 / 15 分类 / 454 关联关系
  - 已向量化：Chroma 100 条视频（all-MiniLM-L6-v2 embedding）
  - 测试：11 项数据库测试全部通过（累计 25/25）

---

### 第二周：核心模块开发

#### 第1-2天：用户意图识别 Agent 模块
- [x] **已完成** — 多轮对话意图分类（找片、咨询、计划、闲聊等）
- [x] **已完成** — 设计结构化 Prompt 模板（System + Few-shot）
- [x] **交付物**：3个核心 Agent 初步实现 ✅
  - `agents/base_agent.py` — 抽象基类框架
  - `agents/intent_agent.py` — 5 类意图识别（关键词+规则，含 System Prompt + Few-shot）
  - `agents/chat_agent.py` — 对话管理（问候/感谢/澄清/闲聊）
  - `graph/state.py` — 统一 AgentState 定义
  - 测试：27 项 Agent 测试全部通过（累计 51/51）

#### 第3-4天：视频检索系统
- [x] **已完成** — 搭建 Chroma 向量数据库
- [x] **已完成** — 实现语义相似检索 + 传统过滤（类型、年代、演员）
- [x] **交付物**：向量数据库 + 检索工具函数 ✅
  - `tools/search_tools.py` — parse_query / semantic_search / filter_videos / hybrid_search
  - `agents/retrieval_agent.py` — 混合检索 Agent（含响应生成）
  - parse_query 支持：类型/年代(含中文数字)/评分/演员/地区
  - hybrid_search 策略：语义+过滤 → 权重融合 → 去重排序
  - 测试：37 项检索测试全部通过（累计 88/88）

#### 第5天：影视知识库构建
- [x] **已完成** — 整理/爬取导演、演员、奖项等知识
- [x] **已完成** — 构建 Neo4j 小型知识图谱
- [x] **已完成** — 实现 RAG 检索功能
- [x] **交付物**：知识库 + RAG 单元测试用例 ✅
  - `knowledge_graph/kg_schema.py` — Neo4j 数据模型 + Cypher DDL + 导入脚本
  - `knowledge_graph/kg_queries.py` — 6 个 Cypher 查询函数（演员/导演/视频/搜索）
  - `tools/knowledge_tools.py` — SQLite 兜底 + Neo4j 自动切换 + 查询类型识别
  - `agents/knowledge_agent.py` — 知识查询 Agent（含结果格式化）
  - 测试：22 项知识库测试全部通过（累计 109/109）

---

### 第三周：LangGraph 工作流集成（项目核心）

#### 第1-2天：设计状态图（StateGraph）
- [x] **已完成** — 定义 Agent 间状态流转
- [x] **已完成** — 实现条件边 + 普通边
- [x] **交付物**：完整的 LangGraph 工作流 ✅
  - `graph/nodes.py` — 5 个节点函数（intent/retrieval/knowledge/chat/respond）
  - `graph/graph.py` — StateGraph 构建 + 条件边路由 + MemorySaver + run_query
  - 工作流：START → intent_agent(条件边) → 4 分支 → respond_node → END
  - 记忆：MemorySaver + thread_id 隔离
  - 测试：11 项端到端测试全部通过（累计 120/120）

#### 第3-4天：工作流优化与调试
- [x] **已完成** — LangSmith 追踪集成（环境变量配置 + 自动继承）
- [x] **已完成** — Tool Calling 定义（4 个标准 LangChain @tool）
- [x] **已完成** — MakePlan Agent（plan_agent）替代 chat_agent 兜底
- [x] **已完成** — safe_node 错误包装 + respond_node 智能回复增强
- [x] **交付物**：LangSmith 追踪 + Tool Calling + 优化后工作流 ✅
  - `tools/tool_definitions.py` — 4 个标准 Tool（hybrid_search / parse_query / knowledge_search / detect_query_type）
  - `agents/plan_agent.py` — 观影计划 Agent（时间/心情解析 + 结构化编排 + 格式化输出）
  - `graph/nodes.py` — +plan_node +safe_node 异常包装
  - `graph/graph.py` — make_plan 路由到 plan_agent
  - 测试：146/146 全部通过（+plan_agent: 16 / +tool_definitions: 9 / +workflow: 1）

#### 第5天：后端 API 开发
- [ ] **未完成** — 用 FastAPI 封装整个 Graph
- [ ] **未完成** — 设计 RESTful 接口 + 认证 + 限流
- [ ] **交付物**：工作流程图 + 技术文档初稿

---

### 第四周：系统集成与展示

#### 第1-2天：前端界面开发
- [ ] **未完成** — Streamlit 对话界面 + 推荐结果卡片 + 用户反馈机制
- [ ] **交付物**：完整可运行的前端

#### 第3天：系统测试与优化
- [ ] **未完成** — 端到端功能测试、性能评估、错误处理、边缘案例
- [ ] **交付物**：完整测试报告

#### 第4-5天：项目文档与演示准备
- [ ] **未完成** — 编写用户手册 + 开发文档 + 演示材料
- [ ] **最终交付物**：完整项目 + 全套文档 + 演示 PPT/视频

---

## Vibe Coding 规则

1. 每次只做当前阶段的任务，不跳阶段
2. 先写文档/注释/流程图，再写代码
3. 所有 Agent 采用结构化 Prompt（System Prompt + Few-shot + Tools）
4. 全程开启 LangSmith 追踪
5. 代码符合 PEP8 + 类型提示（Pydantic）
6. 每个功能点写对应测试用例
7. 遇到业务逻辑问题，优先参考腾讯视频真实业务场景

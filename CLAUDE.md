# 腾讯视频智能观影助手 - 开发计划

> 基于 PROJECT_GUIDE.md 整理的开发状态追踪，所有未完成内容标记为「未完成」，除非明确已完成或正在进行。

---

## 项目文件结构

```
movieCompanion/
├── CLAUDE.md             # 开发计划 & 进度追踪 ✅
├── PROJECT_GUIDE.md      # 项目指导手册 ✅
├── 项目进度/              # 7 份详细计划 + 学习笔记 ✅
│   ├── 学习笔记.md
│   ├── D3-详细计划.md ~ W4-D4-5-详细计划.md
├── tencent_video_agent/  # 完整项目主目录 ✅
│   ├── agents/           # 6 个 Agent
│   ├── api/              # FastAPI 路由
│   ├── data/             # 模拟数据生成
│   ├── db/               # SQLite + Chroma
│   │   ├── docs/             # 用户手册 + 开发文档 + 测试报告 + 项目经验
│   ├── frontend/         # Streamlit 前端
│   ├── graph/            # LangGraph 工作流
│   ├── knowledge_graph/  # Neo4j 知识图谱
│   ├── tools/            # 检索/知识/Tool 工具
│   ├── tests/            # 160~195 项测试
│   ├── main.py           # 一键启动
│   └── README.md
└── src/                  # （旧代码，待清理）
```

## 项目概览

基于 LangGraph 的腾讯视频智能观影助手，解决"找片难、疑问多、计划乱"三大痛点。

- **工作流编排**：LangGraph (StateGraph + Nodes + Edges + Checkpoint)
- **LLM 集成**：LangChain + LangGraph
- **API 服务**：FastAPI
- **存储**：SQLite + Chroma（向量数据库）+ Neo4j（知识图谱）
- **前端**：Streamlit
- **LLM 模型**：DeepSeek（deepseek-v4-flash，OpenAI 兼容 API，通过 langchain-openai 接入）
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

## 最终交付物

- [x] **交付物 1**：完整可运行的智能观影助手原型（本地一键启动）✅
- [x] **交付物 2**：完整技术文档 + 工作流程图（Mermaid）✅
- [x] **交付物 3**：测试报告（195 项测试，单元/集成/E2E/性能/边界全覆盖）✅
- [x] **交付物 4**：学习笔记 + 技术调研报告 ✅（`项目进度/学习笔记.md`）

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
- [x] **已完成** — FastAPI 封装（/chat /chat/multi /health /workflow/mermaid）
- [x] **已完成** — Pydantic 请求/响应验证 + CORS + 统一异常处理
- [x] **已完成** — 一键启动入口（main.py → uvicorn）
- [x] **交付物**：完整的 RESTful API 服务 ✅
  - `api/config.py` — 服务配置（host/port/cors）
  - `api/routes.py` — FastAPI 4 个路由 + 请求/响应模型 + 异常处理器
  - `tests/test_api.py` — 9 项 API 测试（单轮/多轮/健康检查/流程图/边界情况）
  - 测试：155/155 全部通过（+9 API）

---

### 第四周：系统集成与展示

#### 第1-2天：前端界面开发
- [x] **已完成** — Streamlit 双面板布局（左对话 + 右详情）
- [x] **已完成** — 对话界面（消息气泡 + 输入框 + 历史记录 + 新对话）
- [x] **已完成** — 推荐结果卡片（2 列网格 + 评分/类型/简介）
- [x] **已完成** — 知识查询面板（演员/导演/视频详情/搜索 4 种）
- [x] **已完成** — 观影计划面板（时间线 + 推荐理由 + 总时长）
- [x] **已完成** — 后端对接（httpx + 异常处理 + 加载状态）
- [x] **交付物**：完整可运行的前端 ✅
  - `frontend/app.py` — 主入口（双面板布局 + 会话管理）
  - `frontend/components/chat_ui.py` — 对话气泡组件
  - `frontend/components/video_card.py` — 2 列网格卡片
  - `frontend/components/knowledge_panel.py` — 知识结果面板
  - `frontend/components/plan_panel.py` — 观影计划面板
  - `frontend/utils/api_client.py` — API 客户端（含异常兜底）
  - 测试：155/155 全部通过

#### 第3天：系统测试与优化
- [x] **已完成** — E2E 全路径测试（14 项，5 条用户路径）
- [x] **已完成** — 性能基准测试（10 项，意图/检索/知识/工作流）
- [x] **已完成** — 边界情况测试（16 项，空/特殊字符/长文本/高频）
- [x] **交付物**：完整测试报告 ✅
  - `tests/test_e2e.py` — 14 项 E2E 测试（找片/知识/计划/闲聊/多轮）
  - `tests/test_edge_cases.py` — 16 项边界测试（空/特殊字符/长文本/高频）
  - `tests/test_performance.py` — 10 项性能基准
  - `docs/测试报告.md` — 完整测试报告
  - 测试：195/195 全部通过（+40 新增）

#### 第4-5天：项目文档与演示准备
- [x] **已完成** — 用户手册（启动/功能/FAQ）
- [x] **已完成** — 开发文档（架构/模块/数据流/配置/测试/扩展）
- [x] **已完成** — README 全面重构（含 Mermaid 架构图）
- [x] **交付物**：完整项目 + 全套文档 ✅
  - `README.md` — 项目总览 + 架构图 + 快速开始
  - `docs/用户手册.md` — 面向用户的操作指南
  - `docs/开发文档.md` — 面向开发者的技术文档
  - `docs/测试报告.md` — 195 项测试结果

---

### 后续优化：Agent 输入全面 LLM 化

#### LLM 替换关键词匹配（输入理解层）
- [x] **IntentAgent** — 完全基于 LLM 意图分类
  - 移除所有 `*_PATTERNS` 关键词字典 / `_match_patterns()` / `_classify_intent()`
  - 使用 `build_intent_prompt()` → `get_llm().invoke()` → JSON 解析
  - 回退：LLM 异常 → unknown

- [x] **ChatAgent** — 完全基于 LLM 对话生成
  - 移除 `GREETING_KEYWORDS` / `THANKS_KEYWORDS` / `_is_greeting()` / `_is_thanks()` 等
  - 使用 `build_chat_prompt()` → `get_llm().invoke()`
  - 回退：静态默认回复

- [x] **KnowledgeAgent** — 完全基于 LLM 查询识别 + RAG
  - 移除 `_format_result()` / 关键词 `detect_query_type()`（旧函数保留在 tools 层）
  - 查询类型识别：`build_query_detect_prompt()` → LLM
  - 回答生成：`knowledge_search()` 检索 → `build_rag_prompt()` → LLM
  - 回退：LLM 异常 → "没有找到相关信息"

- [x] **PlanAgent** — 完全基于 LLM 参数提取
  - 移除 `TIME_SLOT_PATTERNS` / `MOOD_KEYWORDS` / `_extract_time_slot()` / `_extract_mood()`
  - 参数提取：`build_plan_parse_prompt()` → LLM
  - 计划编排：工具 `hybrid_search()` + 模板 `_build_plan_schedule()` + `_format_plan_response()`
  - 回退：LLM 异常 → 默认参数

#### 保持关键词匹配（工具层数据提取）
- [ ] **RetrievalAgent.parse_query** — 保持关键词/正则
  - `tools/search_tools.py` 中的 `_extract_genre()` / `_extract_year()` / `_extract_rating()` 等
  - 理由：结构化数据提取（年份/评分/类型/演员/地区），正则覆盖率 > 90%，毫秒级响应
  - LLM 替换反而会引入延迟 + 不确定性

- [ ] **RecommendationAgent 输出** — 保持模板生成
  - `REASON_TEMPLATES` 按类型随机选取推荐语
  - 理由：每部视频调 LLM 5-10s，10 部 = 50-100s，用户不可接受
  - 已实现 batch LLM prompt（`build_batch_recommend_prompt`），但未启用

#### 关键决策文档
- [x] **docs/项目经验.md** — LLM vs 关键词匹配的选型原则
  - Agent 层（输入理解）→ LLM
  - 工具层（数据提取）→ 关键词/正则
  - 原则：理解意图用 LLM，提取参数用关键词

#### 基础设施完善
- [x] **utils/llm_client.py** — 自动 `load_dotenv()` 从项目根目录加载 `.env`
  - 解决从任意入口（服务/测试/脚本）启动时环境变量未加载的问题
- [x] **utils/prompts.py** — 新增 5 套 LLM Prompt 模板
  - `build_query_detect_prompt` / `build_chat_prompt` / `build_query_parse_prompt`
  - `build_plan_parse_prompt` / `build_batch_recommend_prompt`
- [x] **frontend/utils/api_client.py** — 超时 30s → 60s（适配 DeepSeek API 延迟）
- [x] **Neo4j** — 代码完整（schema + 7 个 Cypher 查询 + 自动降级），服务未启动时自动使用 SQLite 兜底

1. 每次只做当前阶段的任务，不跳阶段
2. 先写文档/注释/流程图，再写代码
3. 所有 Agent 采用结构化 Prompt（System Prompt + Few-shot + Tools）
4. 全程开启 LangSmith 追踪
5. 代码符合 PEP8 + 类型提示（Pydantic）
6. 每个功能点写对应测试用例
7. 遇到业务逻辑问题，优先参考腾讯视频真实业务场景

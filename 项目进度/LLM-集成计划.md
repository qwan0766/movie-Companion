# LLM 集成计划 — 让 Agent 真正"智能"

> **状态**：待执行 | **预估工时**：2-3 天
> **前置依赖**：全部 4 周基础功能已完成（208 项测试通过）

---

## 一、现状与目标

### 现状问题

当前所有 Agent 均基于**规则/关键词匹配**：

| Agent | 当前实现 | 问题 |
|-------|---------|------|
| IntentAgent | 正则+权重打分 | "张毅演的电影" 置信度不足，无法理解复杂语义 |
| RecommendationAgent | 模板拼接推荐语 | 所有用户看到同样的推荐理由，不个性化 |
| KnowledgeAgent | 数据直接格式化 | 没有"理解"查询意图，只是一对一字段映射 |
| ChatAgent | 关键词匹配固定回复 | 无法理解上下文做真正的闲聊 |
| PlanAgent | 规则编排时间线 | 无法根据用户具体需求动态调整 |

### 接入 LLM 后的目标

| Agent | LLM 增强方式 | 效果 |
|-------|-------------|------|
| IntentAgent | LLM 分类替代正则 | 理解"有没有类似星际穿越的片子"这类复杂查询 |
| RecommendationAgent | LLM 生成推荐语 | 每部视频有真实个性化推荐理由 |
| KnowledgeAgent | RAG → LLM 总结 | 检索后 LLM 组织回答，更自然 |
| ChatAgent | LLM 自由对话 | 真正聊天，而非模板匹配 |
| PlanAgent | LLM 编排计划 | 根据心情/人数/时长动态调整 |

---

## 二、方案选择

### 方案选定：DeepSeek API（OpenAI 兼容）

使用 DeepSeek 的 OpenAI 兼容 API：

| 项 | 说明 |
|---|------|
| 模型 | deepseek-v4-flash |
| API 地址 | https://api.deepseek.com/v1 |
| 接入方式 | `langchain-openai` 的 `ChatOpenAI`（改 base_url） |
| 成本 | DeepSeek 定价，极低 |
| 性能 | 响应快，质量高 |

通过环境变量配置：

```env
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-your-key
LLM_MODEL=deepseek-v4-flash
LLM_BASE_URL=https://api.deepseek.com/v1
```

默认走 DeepSeek，`.env` 中切换 `LLM_PROVIDER=openai` 即可换其他兼容服务。

---

## 三、LLM 集成架构

### 3.1 统一 LLM 客户端

新建 `utils/llm_client.py`，封装 LLM 调用：

```python
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

def get_llm() -> ChatOpenAI | ChatOllama:
    """根据配置返回 LLM 实例"""
    provider = os.getenv("LLM_PROVIDER", "ollama")
    if provider == "openai":
        return ChatOpenAI(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            temperature=0.1,
        )
    # Ollama 默认
    return ChatOllama(
        model=os.getenv("LLM_MODEL", "qwen2.5:7b"),
        temperature=0.1,
    )
```

### 3.2 集成方式：双轨制

不删除现有规则代码，新增 LLM 路径，通过配置开关：

```python
class IntentAgent(BaseAgent):
    def process(self, state):
        user_text = self._extract_text(state)
        
        if os.getenv("LLM_ENABLED", "false") == "true":
            return self._process_with_llm(user_text)
        else:
            return self._process_with_rules(user_text)  # 现有规则
```

这样做的好处：
- 随时开关 LLM，方便对比效果
- 原有 208 项测试不受影响
- 在 CI/无 GPU 环境自动走规则

### 3.3 Prompt 模板

intent_agent 的 LLM Prompt：

```
你是一个腾讯视频智能助手的意图识别引擎。
请将用户的输入分类为以下意图之一：
- find_movie：找片、推荐、搜索视频
- ask_info：咨询演员/导演/影视知识
- make_plan：制定观影计划
- chat：问候、闲聊
- unknown：无法明确归类

请只返回 JSON：
{"intent": "find_movie", "confidence": 0.95, "reason": "用户明确要求推荐科幻电影"}
```

---

## 四、分阶段实施

### 阶段一：LLM 基础设施（预计 4h）

| 步骤 | 内容 | 产出 |
|------|------|------|
| 1 | 安装依赖（langchain-openai, langchain-ollama） | requirements.txt 更新 |
| 2 | 编写 `utils/llm_client.py`（统一 LLM 客户端） | LLM 调用封装 |
| 3 | 更新 `.env.example`（LLM_PROVIDER, LLM_ENABLED 等） | 配置就绪 |
| 4 | 编写 `tests/test_llm_client.py` | 客户端测试 |

### 阶段二：IntentAgent LLM 增强（预计 3h）

| 步骤 | 内容 | 产出 |
|------|------|------|
| 1 | 设计 LLM Prompt + Few-shot | 意图分类 Prompt |
| 2 | 实现 `_process_with_llm()` 方法 | LLM 分类路径 |
| 3 | 结构化输出解析（JSON → AgentState） | 输出适配 |
| 4 | 测试：对比规则 vs LLM 分类效果 | 对比报告 |

### 阶段三：KnowledgeAgent RAG（预计 3h）

| 步骤 | 内容 | 产出 |
|------|------|------|
| 1 | 检索后调用 LLM 总结 | RAG 实现 |
| 2 | 设计 RAG Prompt（检索结果 + 用户问题 → 自然回答） | Prompt 模板 |
| 3 | 测试 RAG 输出质量 | 质量验证 |

### 阶段四：RecommendationAgent LLM 增强（预计 2h）

| 步骤 | 内容 | 产出 |
|------|------|------|
| 1 | LLM 生成个性化推荐理由 | 真实推荐语 |
| 2 | 替换模板拼接逻辑 | 质量提升 |

---

## 五、文件清单

| 文件 | 操作 | 内容 |
|------|------|------|
| `utils/__init__.py` | **新建** | 包初始化 |
| `utils/llm_client.py` | **新建** | 统一 LLM 客户端 |
| `utils/prompts.py` | **新建** | 所有 Prompt 模板集中管理 |
| `agents/intent_agent.py` | **修改** | +LLM 分类路径 |
| `agents/knowledge_agent.py` | **修改** | +RAG 生成路径 |
| `agents/recommendation_agent.py` | **修改** | +LLM 推荐语路径 |
| `tests/test_llm_client.py` | **新建** | LLM 客户端测试 |
| `.env.example` | **修改** | +LLM 配置项 |
| `requirements.txt` | **修改** | +langchain-openai, langchain-ollama |

---

## 六、质量验收标准

- [ ] `LLM_ENABLED=false` 时所有行为不变，208 项测试全通过
- [ ] `LLM_ENABLED=true` 时意图识别准确率 > 90%（人工评估 20 条）
- [ ] RAG 回答自然度高于模板拼接
- [ ] 推荐理由个性化，不重复
- [ ] 双 Provider（Ollama / OpenAI）可切换
- [ ] 响应时间：意图分类 < 2s，推荐生成 < 5s

---

## 七、不纳入本次计划的内容

以下内容虽在 PROJECT_GUIDE.md 中提到，但与 LLM 集成无关，建议后续单独处理：

- 用户认证 + 限流（W3 D5 要求）
- 用户反馈机制（前端点赞/点踩）
- 用户历史记录持久化（SQLiteSaver）
- 演示 PPT/视频
- 独立 `/recommend` `/plan` 接口

---

> **下一步**：确认方案后开始实施 LLM 集成。

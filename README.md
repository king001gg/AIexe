# AURA · AI 智能伴侣（企业级 Agent）

AURA 是一款基于 **Streamlit** + **DeepSeek** 构建的 **AI 智能伴侣 / Agent** 应用。
它不仅是聊天机器人，更是一个可**调用工具、检索私有知识库、具备长期记忆、可观测成本**的企业级 agent。

## ✨ 功能特性

### Agent 核心能力
- **工具调用（Function Calling）**：内置计算器、日期时间、知识库检索、长期记忆读写等工具，采用 ReAct 循环（模型 → 工具 → 观测 → 循环）
- **RAG 知识库**：上传 `.txt/.md` 文档，基于纯 Python BM25 检索，让 AI 基于你的私有知识回答
- **长期记忆**：跨会话记住用户偏好与事实（SQLite 持久化）

### 对话体验
- 流式对话、多会话管理（新建/切换/重命名/删除）、自动标题
- 5 种 AI 性格模式：温柔体贴 / 幽默风趣 / 理性冷静 / 活泼可爱 / 知性优雅
- 双模型支持：`deepseek-chat`（通用对话）/ `deepseek-reasoner`（深度推理）
- 个性化设置：自定义用户昵称、AI 名称、性格

### 企业工程化
- **配置管理**：`.env` 环境变量（API Key、模型、超时、重试次数等）
- **结构化日志**：控制台 + `logs/app.log` 滚动日志
- **Token 用量 / 成本统计**：SQLite 持久化，界面实时展示累计 token 与成本
- **异常重试**：超时/连接/限流/5xx 自动指数退避重试
- **安全**：密钥不入库、不进会话 JSON；计算器用 `ast` 白名单安全求值
- **测试**：pytest 覆盖工具 / agent 循环 / RAG / 记忆 / 用量
- **容器化**：Dockerfile + docker-compose

## 🛠 技术栈

| 组件 | 技术 |
| --- | --- |
| 前端 | [Streamlit](https://streamlit.io/) |
| 大模型 | [DeepSeek](https://platform.deepseek.com/)（OpenAI 兼容接口 + Function Calling） |
| 存储 | SQLite（记忆/知识库/用量）+ JSON（会话） |
| 检索 | 纯 Python BM25（无向量库/嵌入模型依赖） |
| 语言 | Python 3.12 |

> 采用**轻量自研**路线：不引入 LangChain / ChromaDB 等重依赖，核心仅依赖 `streamlit`、`openai`、`python-dotenv`。

## 📁 项目结构

```
AIexe/
├── app.py                    # 应用入口
├── requirements.txt
├── .env.example              # 环境变量模板
├── Dockerfile / docker-compose.yml
├── config/
│   ├── settings.py           # 配置（读 .env）
│   └── logging_config.py     # 结构化日志
├── models/
│   ├── conversation.py       # 会话管理（JSON）
│   └── memory.py             # 长期记忆（SQLite）
├── services/
│   ├── deepseek.py           # DeepSeek 客户端（重试/超时/tools）
│   ├── agent.py              # ReAct agent 循环
│   ├── usage.py              # Token 用量/成本统计
│   └── rag/                  # RAG：chunker / retriever(BM25) / knowledge_base
├── tools/
│   ├── base.py               # 工具基类
│   ├── registry.py           # 工具注册表 → function-calling spec
│   ├── catalog.py            # 内置工具目录
│   └── builtin/              # 计算器 / 日期时间 / 知识库检索 / 记忆
├── ui/                       # sidebar / header / chat / knowledge / styles
└── tests/                    # 单元测试
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.12+
- [DeepSeek API Key](https://platform.deepseek.com/)

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 DEEPSEEK_API_KEY
```

也可以在应用侧边栏中直接填入 API Key（会话内有效）。

### 4. 启动应用

```bash
python -m streamlit run app.py
```

浏览器打开 <http://localhost:8501>。

### 5. Docker 部署

```bash
cp .env.example .env   # 先准备 .env
docker compose up --build
```

## ⚙️ 环境变量

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek 平台密钥 | 空 |
| `DEEPSEEK_BASE_URL` | API 地址 | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 模型 | `deepseek-chat` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `REQUEST_TIMEOUT` | 请求超时（秒） | `60` |
| `MAX_RETRIES` | 最大重试次数 | `3` |
| `MAX_AGENT_ITERATIONS` | Agent 最大工具循环轮次 | `5` |

## 🧰 内置工具

| 工具 | 说明 |
| --- | --- |
| 🧮 计算器 | 四则运算等精确计算（`ast` 白名单安全求值） |
| 🕐 日期时间 | 查询当前日期、时间与星期 |
| 📚 知识库检索 | 在私有知识库中检索相关内容 |
| 🧠 保存记忆 | 保存长期记忆（键值对） |
| 🧠 检索记忆 | 检索已保存的长期记忆 |

可在侧边栏「Agent 工具」区单独开关每个工具。

## 🧪 测试

```bash
python -m pytest -q
```

覆盖：工具执行与注册、agent 循环（含 tool_calls 处理）、RAG 分块与 BM25 检索、长期记忆、Token 统计。

## 📄 许可

本项目仅用于学习与个人使用。

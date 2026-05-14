# Fintech Brain - 智能金融投研与风控大脑

> 基于 LangGraph 多 Agent 架构的金融投资研究与风险控制 AI 系统

## 项目介绍

**智能金融投研与风控大脑** (Finance Brain) 是一个基于 LangGraph 多 Agent 架构的金融投资研究与风险控制 AI 系统。用户通过自然语言提问，系统自动识别意图，结合 RAG 混合检索与知识图谱，提供专业的投研分析和风控评估。

### 核心功能

**1. 智能投研对话**
- 用户通过自然语言提问，系统自动识别意图（投研分析 / 风控评估 / 通用对话）
- 基于 LangGraph 构建多 Agent 工作流：路由器 → 检索 → 知识图谱 → 专业分析 → 输出

**2. RAG 混合检索**
- 向量检索（Milvus）+ BM25 关键词检索，通过 RRF 融合排序
- 集成 Reranker 二次精排，提升召回精度
- 支持上传金融研报、PDF 文档并自动索引

**3. 知识图谱**
- 使用 Neo4j 构建金融领域知识图谱（公司、行业、风险关系等）
- Agent 在分析时自动查询知识图谱获取关联信息

**4. 风控看板**
- 可视化展示风险预警、待审项目、信用/市场/操作风险趋势
- 风险分布饼图，支持多维度风险监控

**5. 文档管理**
- 上传、管理金融研报和分析文档
- 集成 MinerU 解析器处理 PDF

### 面向人群

1. **金融投研分析师** — 快速检索研报、分析行业/公司、生成投研报告
2. **风控合规人员** — 风险评估、合规审查、风险预警监控
3. **基金经理 / 投资经理** — 辅助决策支持，整合多源信息
4. **金融机构技术团队** — 可作为内部 AI 投研工具的原型或基础框架

---

## 目录

- [技术栈](#技术栈)
- [系统架构](#系统架构)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [环境变量](#环境变量)
- [API 接口](#api-接口)
- [智能体系统](#智能体系统)
- [RAG 检索系统](#rag-检索系统)
- [知识图谱](#知识图谱)
- [数据库模型](#数据库模型)
- [前端说明](#前端说明)
- [开发指南](#开发指南)

---

## 技术栈

### 后端

| 类别 | 技术 |
|---|---|
| 语言 | Python 3.11 |
| Web 框架 | FastAPI + Uvicorn |
| ORM | SQLAlchemy (async) + Alembic |
| 数据库 | MySQL 8.0 |
| 缓存 | Redis 7 |
| 向量数据库 | Milvus 2.4 |
| 知识图谱 | Neo4j 5 |
| LLM/Agent | LangGraph + LangChain + LangChain-OpenAI |
| 文档解析 | MinerU (magic-pdf) |
| 日志 | Loguru |

### 前端

| 类别 | 技术 |
|---|---|
| 框架 | Vue 3.4 |
| 构建工具 | Vite 5.4 |
| 状态管理 | Pinia 2.1 |
| 路由 | Vue Router 4.3 |
| UI 组件库 | Element Plus 2.7 |
| 图表 | ECharts 5.5 + vue-echarts |
| Markdown | markdown-it |
| HTTP 客户端 | Axios |

### 基础设施

| 服务 | 镜像 | 端口 | 用途 |
|---|---|---|---|
| MySQL | mysql:8.0 | 3306 | 主数据库 |
| Redis | redis:7-alpine | 6379 | 缓存 |
| etcd | quay.io/coreos/etcd:v3.5.5 | 2379 | Milvus 元数据存储 |
| Milvus-MinIO | minio/minio | 9010/9011 | Milvus 对象存储 |
| Milvus | milvusdb/milvus:v2.4.0 | 19530, 9091 | 向量数据库 |
| Neo4j | neo4j:5-community | 7474, 7687 | 知识图谱数据库 |
| Backend | 自定义构建 | 8000 | FastAPI 应用 |
| Frontend | nginx:alpine | 80 | Vue SPA |

---

## 系统架构

### 整体流程

```
用户请求 (Vue 3 SPA)
    │
    ▼
FastAPI 路由层 (api/)
    │
    ├── /api/auth/*      → auth_service → MySQL
    ├── /api/chat/*      → chat_service → LangGraph Agent
    ├── /api/documents/* → document_service → 本地文件存储 + MySQL
    ├── /api/knowledge/* → Neo4j 直接查询
    └── /api/dashboard/* → 模拟数据
    │
    ▼
LangGraph 多智能体工作流
    │
    ├─ router (意图分类: research / risk / chat)
    │
    ├─ [chat 路径] → response → END
    │
    └─ [research/risk 路径]
         │
         ▼
       retrieval (混合检索: Milvus 向量搜索 + BM25 关键词搜索 → RRF 融合 → 重排序)
         │
         ▼
       kg_query (Neo4j 知识图谱查询)
         │
         ├── [research] → research_node (投研分析) → END
         └── [risk]     → risk_control_node (风控评估) → END
```

### 混合检索管线

```
用户查询
    │
    ├── Embedding API (BGE-large-zh-v1.5) → 查询向量
    │       │
    │       ▼
    │   Milvus 向量搜索 (COSINE, top 20)
    │
    └── jieba 分词 → BM25 关键词搜索 (top 20)
            │
            ▼
        RRF 融合 (Reciprocal Rank Fusion, k=60)
            │
            ▼
        BGE-Reranker 重排序 (top 5)
            │
            ▼
        上下文注入 → LLM 生成
```

---

## 项目结构

```
fintech-brain/
├── .env                          # 环境变量配置
├── .gitignore
├── docker-compose.yml            # Docker 编排
├── Makefile                      # 开发命令
├── README.md
│
├── backend/                      # Python 后端
│   ├── pyproject.toml            # 项目依赖
│   ├── Dockerfile
│   ├── alembic/
│   │   └── env.py                # 数据库迁移配置
│   └── app/
│       ├── main.py               # FastAPI 应用入口
│       ├── config.py             # 配置管理 (pydantic-settings)
│       ├── deps.py               # 依赖注入 (认证)
│       │
│       ├── core/                 # 核心层
│       │   ├── database.py       # SQLAlchemy 异步引擎
│       │   ├── redis.py          # Redis 客户端
│       │   ├── security.py       # JWT + bcrypt
│       │   └── logging.py        # Loguru 日志配置
│       │
│       ├── models/               # ORM 模型
│       │   ├── user.py           # 用户模型
│       │   ├── conversation.py   # 会话 + 消息模型
│       │   └── document.py       # 文档模型
│       │
│       ├── schemas/              # Pydantic 请求/响应模型
│       │   ├── auth.py           # 认证相关
│       │   ├── chat.py           # 对话相关
│       │   └── document.py       # 文档相关
│       │
│       ├── api/                  # API 路由
│       │   ├── auth.py           # /api/auth/*
│       │   ├── chat.py           # /api/chat/*
│       │   ├── documents.py      # /api/documents/*
│       │   ├── knowledge.py      # /api/knowledge/*
│       │   └── dashboard.py      # /api/dashboard/*
│       │
│       ├── services/             # 业务逻辑
│       │   ├── auth_service.py   # 认证服务
│       │   ├── chat_service.py   # 对话服务 (调用 LangGraph)
│       │   ├── document_service.py # 文档 CRUD
│       │   └── cache_service.py  # Redis 缓存
│       │
│       ├── agents/               # LangGraph 多智能体
│       │   ├── state.py          # 共享状态定义
│       │   ├── graph.py          # 工作流编排
│       │   ├── nodes/
│       │   │   ├── router.py     # 意图路由
│       │   │   ├── retrieval.py  # RAG 检索
│       │   │   ├── knowledge_graph.py # 知识图谱查询
│       │   │   ├── research.py   # 投研分析
│       │   │   ├── risk_control.py # 风控评估
│       │   │   └── response.py   # 通用回复
│       │   └── tools/
│       │       ├── search_tool.py     # 文档搜索工具
│       │       ├── calculator.py      # 金融计算器
│       │       └── kg_tool.py         # 知识图谱查询工具
│       │
│       ├── rag/                  # RAG 检索系统
│       │   ├── milvus_client.py  # Milvus 向量数据库客户端
│       │   ├── embeddings.py     # Embedding 服务调用
│       │   ├── bm25.py           # BM25 关键词检索
│       │   ├── reranker.py       # 重排序服务调用
│       │   └── retriever.py      # 混合检索编排 (RRF 融合)
│       │
│       ├── knowledge_graph/      # 知识图谱
│       │   ├── neo4j_client.py   # Neo4j 异步客户端
│       │   ├── queries.py        # 预定义 Cypher 查询
│       │   └── extractor.py      # LLM 实体/关系抽取
│       │
│       └── parser/
│           └── mineru_parser.py  # MinerU 文档解析
│
└── frontend/                     # Vue 3 前端
    ├── package.json
    ├── vite.config.js
    ├── Dockerfile
    ├── nginx.conf                # 生产环境 Nginx 配置
    └── src/
        ├── main.js               # 应用入口
        ├── App.vue               # 根组件
        ├── router/
        │   └── index.js          # 路由配置
        ├── stores/
        │   ├── user.js           # 用户状态 (Pinia)
        │   └── chat.js           # 对话状态 (Pinia)
        ├── api/
        │   ├── request.js        # Axios 实例 (JWT 拦截器)
        │   ├── auth.js           # 认证 API
        │   ├── chat.js           # 对话 API
        │   └── document.js       # 文档 API
        ├── utils/
        │   └── index.js          # 工具函数
        └── views/
            ├── Login.vue         # 登录页
            ├── Register.vue      # 注册页
            ├── Chat.vue          # 主对话界面
            ├── Dashboard.vue     # 风控看板
            ├── Documents.vue     # 文档管理
            └── KnowledgeGraph.vue # 知识图谱可视化
```

---

## 快速开始

### 前置要求

- Docker & Docker Compose
- Node.js 20+ (本地开发前端)
- Python 3.11+ (本地开发后端)

### 方式一：Docker Compose 一键启动

```bash
# 克隆项目
git clone <repo-url>
cd fintech-brain

# 复制并编辑环境变量
cp .env.example .env   # 或直接编辑 .env

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

启动后访问：
- 前端：http://localhost:80
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 方式二：本地开发

```bash
# 安装所有依赖
make install

# 启动基础设施 (MySQL, Redis, Milvus, Neo4j)
make up

# 启动后端 (热重载)
make backend

# 启动前端 (另一个终端)
make frontend
```

### 数据库迁移

```bash
# 生成迁移脚本
make db-migrate msg="initial migration"

# 执行迁移
make db-upgrade
```

---

## 环境变量

项目通过 `.env` 文件配置，所有变量均可通过环境变量覆盖。

### LLM 配置

| 变量 | 默认值 | 说明 |
|---|---|---|
| `JUDGE_MODEL_NAME` | `gpt-4` | 意图分类和生成使用的模型 |
| `API_KEY` | - | LLM API Key |
| `BASE_URL` | `https://api.openai.com/v1` | LLM API 地址 |

### SiliconFlow (Embedding + Reranker)

| 变量 | 默认值 | 说明 |
|---|---|---|
| `SILICONFLOW_API_KEY` | - | 硅基流动 API Key |
| `SILICONFLOW_BASE_URL` | `https://api.siliconflow.cn/v1` | 硅基流动 API 地址 |
| `EMBEDDING_MODEL` | `BAAI/bge-large-zh-v1.5` | Embedding 模型名 |
| `RERANKER_MODEL` | `BAAI/bge-reranker-v2-m3` | Reranker 模型名 |

### MySQL

| 变量 | 默认值 | 说明 |
|---|---|---|
| `MYSQL_HOST` | `localhost` | 主机 |
| `MYSQL_PORT` | `3306` | 端口 |
| `MYSQL_USER` | `root` | 用户名 |
| `MYSQL_PASSWORD` | `password` | 密码 |
| `MYSQL_DATABASE` | `finance_brain` | 数据库名 |

### Redis

| 变量 | 默认值 | 说明 |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis 连接地址 |

### Milvus

| 变量 | 默认值 | 说明 |
|---|---|---|
| `MILVUS_HOST` | `localhost` | 主机 |
| `MILVUS_PORT` | `19530` | 端口 |

### Neo4j

| 变量 | 默认值 | 说明 |
|---|---|---|
| `NEO4J_URI` | `bolt://localhost:7687` | 连接地址 |
| `NEO4J_USER` | `neo4j` | 用户名 |
| `NEO4J_PASSWORD` | `root1234` | 密码 |

### 文件存储

| 变量 | 默认值 | 说明 |
|---|---|---|
| `UPLOAD_DIR` | `uploads` | 上传文件存储目录 |

### JWT

| 变量 | 默认值 | 说明 |
|---|---|---|
| `JWT_SECRET_KEY` | `your-secret-key-...` | JWT 签名密钥 (生产环境必须修改) |
| `JWT_ALGORITHM` | `HS256` | 签名算法 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access Token 有效期 (分钟) |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh Token 有效期 (天) |

---

## API 接口

### 认证 `/api/auth`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| POST | `/api/auth/register` | 用户注册 | 否 |
| POST | `/api/auth/login` | 用户登录 | 否 |
| POST | `/api/auth/refresh` | 刷新 Token | 否 |
| GET | `/api/auth/me` | 获取当前用户信息 | 是 |

### 对话 `/api/chat`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| POST | `/api/chat/` | 发送消息并获取智能体回复 | 是 |
| GET | `/api/chat/conversations` | 获取会话列表 | 是 |
| GET | `/api/chat/conversations/{id}` | 获取会话详情 (含消息历史) | 是 |

**POST /api/chat 请求体：**

```json
{
  "message": "分析一下贵州茅台的投资价值",
  "conversation_id": 1
}
```

**响应：**

```json
{
  "conversation_id": 1,
  "message": "...(智能体回复)...",
  "intent": "research"
}
```

### 文档 `/api/documents`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| POST | `/api/documents/upload` | 上传文档 (multipart/form-data) | 是 |
| GET | `/api/documents/` | 获取文档列表 | 是 |
| GET | `/api/documents/{id}` | 获取文档详情 | 是 |

支持的文件类型：PDF, DOCX, DOC, TXT, CSV, PNG, JPEG。

### 知识图谱 `/api/knowledge`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/api/knowledge/search?q=` | 搜索实体 | 是 |
| GET | `/api/knowledge/entity/{name}` | 获取实体关系 | 是 |
| GET | `/api/knowledge/graph?center=&depth=` | 获取子图 (节点 + 边) | 是 |

### 风控看板 `/api/dashboard`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/api/dashboard/overview` | 概览数据 | 是 |
| GET | `/api/dashboard/risk-trends` | 风险趋势 (6个月) | 是 |
| GET | `/api/dashboard/risk-distribution` | 风险分布 | 是 |

### 健康检查

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/health` | 服务健康检查 | 否 |

---

## 智能体系统

### LangGraph 工作流

系统使用 LangGraph 构建有向无环图 (DAG) 驱动的多智能体工作流。

**节点定义：**

| 节点 | 职责 | 温度 |
|---|---|---|
| `router` | 意图分类 (research / risk / chat) | 0.0 |
| `retrieval` | RAG 混合检索 | - |
| `kg_query` | 知识图谱实体关系查询 | - |
| `research` | 投研分析生成 | 0.3 |
| `risk_control` | 风控评估生成 | 0.2 |
| `response` | 通用对话回复 | 0.5 |

**路由逻辑：**

```
router ──┬── [intent=research] ──→ retrieval → kg_query → research → END
         ├── [intent=risk]     ──→ retrieval → kg_query → risk_control → END
         └── [intent=chat]     ──→ response → END
```

### 意图分类

路由器通过 LLM 将用户输入分类为三种意图：

- **research (投研分析)**：涉及股票分析、行业研究、财务数据解读、投资建议等
- **risk (风控评估)**：涉及风险评估、合规检查、风险预警、压力测试等
- **chat (通用对话)**：日常问答、功能咨询等

### AgentState 共享状态

```python
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]  # 消息列表 (追加语义)
    intent: str                               # 分类意图
    retrieved_docs: list[dict]                # RAG 检索结果
    kg_results: list[dict]                    # 知识图谱查询结果
    context: str                              # 组装后的上下文
    response: str                             # 最终 LLM 回复
```

---

## RAG 检索系统

### 向量数据库 (Milvus)

- **Collection**: `finance_documents`
- **向量维度**: 1024 (BGE-large-zh-v1.5)
- **索引类型**: IVF_FLAT
- **距离度量**: COSINE
- **字段**: `id`, `doc_id`, `chunk_index`, `content` (VARCHAR 8192), `metadata` (VARCHAR 4096), `embedding` (FLOAT_VECTOR 1024)

### BM25 关键词检索

- 使用 `rank_bm25` 库的 BM25Okapi 算法
- 中文分词：jieba
- 内存索引，适合中小规模文档集

### 混合检索与融合

检索流程：

1. **查询向量化**：调用 Embedding API 获取查询向量
2. **向量搜索**：Milvus ANN 搜索，返回 top 20
3. **关键词搜索**：BM25 搜索，返回 top 20
4. **RRF 融合**：Reciprocal Rank Fusion 算法合并两路结果
   - `score = Σ 1/(k + rank + 1)`，k=60
5. **重排序**：调用 BGE-Reranker 对融合结果重排序，返回 top 5

### 文档解析 (MinerU)

使用 MinerU (`magic-pdf` CLI) 解析 PDF/DOCX 等文档为结构化文本，然后按 512 字符 (64 字符重叠) 切分为文本块。

---

## 知识图谱

### 实体类型

| 类型 | 说明 |
|---|---|
| Company | 公司 |
| Person | 人物 |
| Industry | 行业 |
| RiskEvent | 风险事件 |
| FinancialIndicator | 财务指标 |
| Policy | 政策法规 |

### 关系类型

| 关系 | 说明 |
|---|---|
| BELONGS_TO | 属于 (公司→行业) |
| HAS_INDICATOR | 拥有指标 (公司→财务指标) |
| CAUSES | 导致 (风险事件→风险事件) |
| TRIGGERS | 触发 |
| INVESTS_IN | 投资 |
| COMPETES_WITH | 竞争 |
| REGULATED_BY | 受监管 |

### 预定义查询

- `company_relations`：公司所有关系
- `risk_chain`：风险事件因果链 (1-3 跳)
- `industry_peers`：同行业公司
- `financial_indicators`：公司财务指标 (按期间倒序)

### 实体抽取

通过 LLM 从金融文本中自动抽取实体和关系，生成结构化 JSON 后写入 Neo4j。

---

## 数据库模型

### users 表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer, PK | 自增主键 |
| username | String(50), unique, indexed | 用户名 |
| email | String(100), unique, indexed | 邮箱 |
| hashed_password | String(128) | bcrypt 哈希密码 |
| is_active | Boolean, default=True | 是否激活 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### conversations 表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer, PK | 自增主键 |
| user_id | Integer, FK→users.id | 所属用户 |
| title | String(200), default="新对话" | 会话标题 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### messages 表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer, PK | 自增主键 |
| conversation_id | Integer, FK→conversations.id | 所属会话 |
| role | String(20) | `user` / `assistant` / `system` |
| content | Text | 消息内容 |
| intent | String(20), nullable | `research` / `risk` / `chat` |
| created_at | DateTime | 创建时间 |

### documents 表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer, PK | 自增主键 |
| filename | String(255) | 原始文件名 |
| file_path | String(500) | 存储路径 |
| file_size | Integer | 文件大小 (字节) |
| content_type | String(100) | MIME 类型 |
| status | String(20) | `pending` / `parsing` / `completed` / `failed` |
| chunk_count | Integer, default=0 | 解析后的文本块数 |
| parsed_content | Text, nullable | 解析后的文本内容 |
| error_message | Text, nullable | 处理错误信息 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

---

## 前端说明

### 页面路由

| 路径 | 组件 | 说明 | 需认证 |
|---|---|---|---|
| `/login` | Login.vue | 登录页 | 否 |
| `/register` | Register.vue | 注册页 | 否 |
| `/` | → `/chat` | 重定向 | - |
| `/chat` | Chat.vue | 主对话界面 | 是 |
| `/dashboard` | Dashboard.vue | 风控看板 | 是 |
| `/documents` | Documents.vue | 文档管理 | 是 |
| `/knowledge` | KnowledgeGraph.vue | 知识图谱可视化 | 是 |

### 主要页面功能

**Chat.vue (主对话界面)**
- 左侧栏：会话列表、导航按钮 (看板/文档/知识图谱)、退出登录
- 对话区：用户消息 (蓝色右侧)、助手消息 (白色左侧)，支持 Markdown 渲染
- 意图标签：投研分析 / 风控评估 / 通用对话
- 输入框：回车发送，加载中禁用

**Dashboard.vue (风控看板)**
- 4 个 KPI 卡片：风险预警数、待审阅项、已索引文档、知识实体数
- 折线图：近 6 个月信用/市场/操作风险趋势
- 饼图：风险类别分布 (信用/市场/操作/流动性/合规)

**Documents.vue (文档管理)**
- 文件上传：支持 PDF, DOC, DOCX, TXT, CSV, PNG, JPG
- 文档列表：ID、文件名、类型、大小、状态 (颜色标签)、分块数、上传时间

**KnowledgeGraph.vue (知识图谱)**
- 实体搜索框
- 搜索结果列表 (实体类型标签)
- ECharts 力导向图可视化：节点按类别着色，边标注关系类型，支持拖拽缩放

### 前端认证机制

- Token 存储于 `localStorage`
- Axios 请求拦截器自动附加 `Authorization: Bearer <token>`
- 响应拦截器：401 自动跳转登录页，其他错误弹出 Element Plus 提示
- Vue Router 导航守卫：未认证用户重定向到 `/login`

---

## 开发指南

### Makefile 命令

```bash
make up              # 启动 Docker 基础设施
make down            # 停止 Docker 基础设施
make build           # 构建 Docker 镜像
make logs            # 查看容器日志
make backend         # 本地启动后端 (热重载, 端口 8000)
make frontend        # 本地启动前端 (Vite dev server)
make db-migrate msg="描述"  # 生成 Alembic 迁移脚本
make db-upgrade      # 执行数据库迁移
make install         # 安装前后端依赖
```

### 后端开发

```bash
cd backend

# 安装依赖
pip install -e .

# 安装开发依赖
pip install -e ".[dev]"

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
pytest

# 代码检查
ruff check .
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器 (端口 5173，自动代理 /api 到后端)
npm run dev

# 构建生产版本
npm run build
```

### 添加新的 API 端点

1. 在 `backend/app/schemas/` 中定义请求/响应模型
2. 在 `backend/app/services/` 中实现业务逻辑
3. 在 `backend/app/api/` 中定义路由
4. 在 `backend/app/main.py` 中注册路由

### 添加新的智能体节点

1. 在 `backend/app/agents/nodes/` 中创建节点函数，签名为 `(state: AgentState) -> dict`
2. 在 `backend/app/agents/graph.py` 的 `build_graph()` 中注册节点和边
3. 如需新的意图类型，更新 `router.py` 的分类提示词

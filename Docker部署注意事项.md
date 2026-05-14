## 问题总结

### 1. jieba 模块缺失

- 问题: `ModuleNotFoundError: No module named 'jieba'`
- 原因: `pyproject.toml` 中缺少 `jieba` 依赖声明
- 解决: 添加 `"jieba>=0.42.1"` 到依赖，重新构建后端镜像

### 2. 容器内 localhost 无法访问其他服务

- 问题: Milvus、Neo4j 连接失败

- 原因: Docker 容器内 `localhost` 指向容器自身，不是宿主机或其他容器

- 解决

  .env中把主机名改为 Docker 服务名

  - `MILVUS_HOST=localhost` → `MILVUS_HOST=milvus-standalone`
  - `NEO4J_URI=bolt://127.0.0.1:7687` → `NEO4J_URI=bolt://neo4j:7687`
  - `REDIS_URL=redis://127.0.0.1:6379/0` → `REDIS_URL=redis://redis:6379/0`

### 3. Neo4j 容器未启动

- 问题: Neo4j 连接失败
- 原因: `docker compose up -d` 没有自动启动 neo4j 服务
- 解决: `docker compose up -d neo4j`

### 4. Neo4j 连接未初始化

- 问题: `'NoneType' object has no attribute 'session'`
- 原因: `main.py` 中没有调用 `neo4j_client.connect()`
- 解决: 在 lifespan 中添加 Neo4j 连接初始化

### 5. 前端超时显示"请求失败"

- 问题: LLM 调用需要 50-75 秒，前端 60 秒超时
- 原因: axios 超时设置太短
- 解决: `timeout: 60000` → `timeout: 300000`（5分钟）

### 6. 前端修改不生效

- 问题: 改了代码但没有效果
- 原因: `docker compose restart` 不会重新加载打包好的静态文件
- 解决: `docker compose build frontend && docker compose up -d --force-recreate frontend`

------

关键教训:

- Docker 容器间通信用服务名而非 localhost
- 修改前端代码后需要重新构建镜像，不是重启
- `pyproject.toml` 要声明所有依赖
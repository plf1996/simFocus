# simFocus - AI 虚拟焦点小组平台

simFocus 是一个 AI 驱动的虚拟焦点小组平台，通过模拟多角色实时讨论，为用户提供多元视角、深度洞察和创意灵感。

## 功能特性

### MVP (P0) 核心功能

- **用户系统**
  - 邮箱注册/登录
  - 个人中心（管理 API 密钥）

- **议题管理**
  - 创建议题
  - 议题列表

- **角色系统**
  - 自定义角色创建（基础版）
  - 预设角色库（50 个角色）

- **讨论引擎**
  - 多角色自由讨论模式
  - 实时观察界面
  - 基础讨论控制（开始、暂停、结束）

- **报告生成**
  - 讨论总结报告（基础版）
  - 在线报告查看

- **历史记录**
  - 查看历史讨论
  - 查看历史报告

- **API 管理**
  - 配置 LLM API
  - API 使用监控

## 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **LLM 集成**: OpenAI API, Anthropic API
- **认证**: JWT (HMAC-SHA256)
- **加密**: AES-256-GCM (API 密钥)

### 前端
- **框架**: Vue 3
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **样式**: Tailwind CSS
- **HTTP 客户端**: Axios
- **WebSocket**: Socket.IO Client

## 项目结构

```
simFocus/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心模块（配置、数据库、安全、Redis）
│   │   ├── models/        # SQLAlchemy 模型
│   │   ├── schemas/       # Pydantic Schemas
│   │   ├── services/      # 业务逻辑层
│   │   └── main.py        # FastAPI 应用入口
│   ├── init-db/           # 数据库初始化脚本
│   ├── requirements.txt    # Python 依赖
│   ├── Dockerfile         # 后端 Docker 配置
│   └── .env.example       # 环境变量示例
│
├── frontend/              # 前端应用
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── components/   # 可复用组件
│   │   ├── stores/       # Pinia 状态管理
│   │   ├── services/     # API 调用
│   │   ├── router/       # 路由配置
│   │   └── assets/       # 静态资源
│   ├── package.json       # Node.js 依赖
│   ├── vite.config.js     # Vite 配置
│   ├── tailwind.config.js # Tailwind CSS 配置
│   └── Dockerfile        # 前端 Docker 配置
│
└── docker-compose.yml     # Docker Compose 配置
```

## 快速开始

### 前置要求

- Docker & Docker Compose
- LLM API 密钥（OpenAI 或 Anthropic）

### 启动步骤

1. **克隆项目**

```bash
git clone <repository-url>
cd simFocus
```

2. **配置环境变量**

复制并编辑后端环境变量文件：

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，至少配置以下内容：

```env
# Security
SECRET_KEY=your-secret-key-at-least-32-characters-long
ENCRYPTION_KEY=your-32-byte-encryption-key-here

# LLM API
OPENAI_API_KEY=sk-your-openai-api-key
# 或
ANTHROPIC_API_KEY=your-anthropic-api-key
```

3. **启动服务**

```bash
# 返回项目根目录
cd ..

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

4. **访问应用**

- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

5. **初始化数据库**

首次启动后，数据库表会自动创建。预设角色数据已包含在初始化脚本中。

## 开发指南

### 后端开发

```bash
cd backend

# 安装依赖（本地开发）
pip install -r requirements.txt

# 运行开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

### 数据库迁移

```bash
cd backend

# 创建新迁移
alembic revision --autogenerate -m "description"

# 应用迁移
alembic upgrade head
```

## API 文档

启动后端服务后，访问以下地址查看自动生成的 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 核心功能说明

### 角色发言策略

1. **Round-robin（轮询）**（MVP 默认）
   - 严格按顺序轮流发言
   - 每个角色在每轮中发言一次

2. **Dynamic（动态）**（P1 功能）
   - 根据角色活跃度和重要性动态调整
   - 平衡发言次数

### 讨论模式

1. **自由讨论模式**: 角色自由发言，系统保持对话平衡
2. **结构化辩论模式**: 分为正反方，每轮系统指定发言角色
3. **创意发散模式**: 基于"是的，而且"原则，角色在他人观点基础上延伸
4. **共识构建模式**: 目标是寻找共同点，角色积极妥协

### 安全性

- API 密钥使用 AES-256-GCM 加密存储
- JWT 令牌认证（24 小时有效期）
- HTTPS/WSS 加密通信
- 速率限制（防止滥用）

## 部署

### 生产环境部署

1. **修改环境变量**

更新 `backend/.env`，使用生产环境的配置：

```env
ENVIRONMENT=production
SECRET_KEY=your-production-secret-key
ENCRYPTION_KEY=your-production-encryption-key

# 数据库（使用生产数据库地址）
DATABASE_URL=postgresql+asyncpg://user:password@production-db-host:5432/simfocus

# Redis（使用生产 Redis 地址）
REDIS_URL=redis://production-redis-host:6379/0
```

2. **使用 Docker Compose 部署**

```bash
docker-compose up -d
```

3. **使用 Kubernetes 部署**（待补充）

## 常见问题

### Q: 如何添加自定义角色？

A: 登录后访问"角色"页面，点击"创建角色"，填写角色信息即可。

### Q: 如何开始讨论？

A: 先创建议题，然后在议题页面点击"创建讨论"，选择 3-7 个角色后开始。

### Q: 支持哪些 LLM API？

A: MVP 阶段支持 OpenAI（GPT-4/GPT-3.5），后续将支持 Anthropic（Claude）和 OpenAI 兼容的第三方 API。

### Q: 讨论如何保存？

A: 所有讨论内容自动保存到数据库，可以随时在"讨论历史"中查看。

## 后续计划

### V1.1 - 体验优化
- 支持多个 LLM API
- 智能角色推荐
- 高级讨论控制（加速播放、插入问题）

### V1.2 - 内容扩展
- 扩展角色库到 100+ 角色
- 报告导出（PDF、Markdown）
- 分享链接功能

### V2.0 - 协作版本
- 团队工作区
- 团队角色库
- 评论和批注

## 许可证

MIT License

## 联系方式

- 项目地址: https://github.com/simfocus/simfocus
- 文档: https://docs.simfocus.com
- 问题反馈: https://github.com/simfocus/simfocus/issues

# 环境变量配置说明

## 📁 配置文件结构

项目使用三个 `.env` 文件分层管理配置：

```
simFocus/
├── .env                    # Docker Compose 和根目录配置
├── backend/
│   └── .env                # 后端服务配置（本地开发）
└── frontend/
    └── .env                # 前端构建配置（Vite）
```

## 🔧 各配置文件作用

### 1. 根目录 `.env`
- **作用域**: Docker Compose
- **用途**: 定义 docker-compose.yml 中使用的环境变量
- **关键配置**:
  - 数据库连接配置（POSTGRES_USER/PASSWORD/DB）
  - 后端和前端的完整配置

### 2. `backend/.env`
- **作用域**: Backend 服务
- **用途**: 后端 Python 应用的配置
- **读取方式**: pydantic-settings
- **关键配置**:
  - DATABASE_URL
  - REDIS_URL
  - SECRET_KEY / ENCRYPTION_KEY
  - EMBEDDING_API_KEY / EMBEDDING_BASE_URL / EMBEDDING_MODEL
  - KEYCLOAK_* 配置

### 3. `frontend/.env`
- **作用域**: Frontend 构建
- **用途**: Vite 构建时注入的环境变量
- **命名规则**: 必须以 `VITE_` 开头
- **关键配置**:
  - VITE_KEYCLOAK_ENABLED
  - VITE_KEYCLOAK_SERVER_URL
  - VITE_KEYCLOAK_REALM
  - VITE_KEYCLOAK_CLIENT_ID
  - VITE_AUTH_MODE
  - VITE_API_BASE_URL

## 📋 环境变量清单

### Backend 必需配置
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
REDIS_URL=redis://host:port/0
SECRET_KEY=your-secret-key-min-32-chars
ENCRYPTION_KEY=your-32-byte-encryption-key
```

### Backend 可选配置
```bash
# LLM Providers
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx

# Embedding
EMBEDDING_API_KEY=sk-xxx
EMBEDDING_BASE_URL=https://api.example.com/v1
EMBEDDING_MODEL=text-embedding-v4

# Keycloak SSO
KEYCLOAK_ENABLED=true
KEYCLOAK_SERVER_URL=https://keycloak.example.com/
KEYCLOAK_REALM=simfocus
KEYCLOAK_FRONTEND_CLIENT_ID=simfocus-frontend
KEYCLOAK_BACKEND_CLIENT_ID=simfocus-backend
KEYCLOAK_BACKEND_CLIENT_SECRET=your-client-secret
```

### Frontend 配置（全部以 VITE_ 开头）
```bash
VITE_KEYCLOAK_ENABLED=true
VITE_KEYCLOAK_SERVER_URL=https://keycloak.example.com/
VITE_KEYCLOAK_REALM=simfocus
VITE_KEYCLOAK_CLIENT_ID=simfocus-frontend
VITE_AUTH_MODE=backend-proxy
VITE_API_BASE_URL=http://localhost:8000
```

## 🚀 Docker Compose 配置传递

docker-compose.yml 中的配置传递机制：

```yaml
services:
  backend:
    env_file:
      - .env                    # 从根目录读取
    environment:
      DATABASE_URL: postgresql+asyncpg://...  # 覆盖 .env 中的值
      REDIS_URL: redis://redis:6379/0        # 覆盖 .env 中的值
    volumes:
      - ./backend:/app          # 挂载代码（包含 backend/.env）

  frontend:
    args:
      VITE_API_BASE_URL: ${VITE_API_BASE_URL}  # 构建参数
    volumes:
      - ./frontend:/app         # 挂载代码（包含 frontend/.env）
```

## 🔒 安全注意事项

1. **不要提交 .env 文件到 Git**
   - 所有 `.env` 文件已在 `.gitignore` 中
   - 只提交 `.env.example` 文件

2. **敏感信息管理**
   - 生产环境使用密钥管理服务（如 AWS Secrets Manager、Vault）
   - 不要在代码中硬编码密钥

3. **环境隔离**
   - 开发环境：使用 `.env` 文件
   - 生产环境：使用环境变量或密钥管理服务

## 🛠️ 本地开发设置

### 1. 复制示例配置
```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. 修改配置值
根据你的实际环境修改各配置文件中的值

### 3. 启动服务
```bash
docker-compose up -d
```

## 📝 配置更新后的操作

### 修改 Backend 配置
```bash
docker-compose restart backend
```

### 修改 Frontend 配置
```bash
docker-compose restart frontend
```

### 修改根目录配置（影响 docker-compose）
```bash
docker-compose down
docker-compose up -d
```

## ⚠️ 常见问题

### Q: SSO 登录按钮不显示？
**A**: 检查 `frontend/.env` 中的 `VITE_KEYCLOAK_ENABLED=true`

### Q: Backend 无法连接数据库？
**A**: 检查 `backend/.env` 中的 `DATABASE_URL` 是否正确

### Q: 前端无法请求后端 API？
**A**: 检查 `frontend/.env` 中的 `VITE_API_BASE_URL` 是否正确

### Q: 修改配置后不生效？
**A**: Vite 会自动检测 `.env` 变化并重启，如果没有重启请手动重启服务

## 🔄 配置文件同步

当需要添加新的环境变量时，需要更新以下文件：

1. **根目录 `.env`** - Docker Compose 使用
2. **`backend/.env`** - 后端服务使用
3. **`frontend/.env`** - 前端构建使用（如果是前端配置）
4. **`.env.example`** - 配置模板（提交到 Git）
5. **代码文件** - 更新读取环境变量的代码

保持所有配置文件的一致性非常重要！

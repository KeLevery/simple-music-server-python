# Simple Music Server (Python / FastAPI)

基于 **FastAPI + SQLAlchemy + MySQL + Redis + MinIO** 构建的轻量级音乐平台后端服务。本项目为原 Spring Boot 后端向 Python 技术栈平滑迁移的实现版本，完全兼容前端（Web 客户端与 Admin 后台管理端）的现有 API、JWT 认证与业务契约。

---

## 🛠️ 技术栈

- **框架**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **ORM / 数据库驱动**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) + `PyMySQL`
- **数据库迁移**: [Alembic](https://alembic.sqlalchemy.org/)
- **缓存**: [Redis](https://redis.io/) (Token 黑名单 / 白名单与数据缓存)
- **对象存储**: [MinIO](https://min.io/) (音频与图片媒体存储)
- **安全与认证**: `PyJWT` (HS256 签名) + `passlib` / `hashlib` (MD5 加盐密码兼容)
- **数据校验**: [Pydantic v2](https://docs.pydantic.dev/)
- **测试框架**: [pytest](https://docs.pytest.org/) + `httpx` (集成测试与迁移基线比对)

---

## 📂 项目结构

```text
server-python/
├── alembic/                # 数据库迁移脚本
├── app/
│   ├── api/                # API 路由层 (Admin, User, Song, Playlist, Artist, Banner, etc.)
│   ├── core/               # 核心配置、异常处理、统一响应格式、安全认证
│   ├── db/                 # 数据库模型 (Models) 与连接会话 (Session)
│   ├── infrastructure/     # 基础设施适配层 (Redis, MinIO)
│   ├── schemas/            # Pydantic 校验与数据传输对象 (DTO/VO)
│   ├── services/           # 业务逻辑服务层 (Services)
│   └── main.py             # FastAPI 应用入口与中间件配置
├── tests/                  # 接口测试与兼容性回归测试套件
├── .env.example            # 环境变量配置模板
├── Dockerfile              # 容器化构建文件
├── pyproject.toml          # 项目构建与依赖管理
└── requirements.txt        # Python 依赖清单
```

---

## 🚀 快速开始

### 1. 安装依赖

推荐使用 Python 3.10+ 虚拟环境：

```bash
# 创建并激活虚拟环境
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写本地配置：

```bash
cp .env.example .env
```

主要配置项说明：
```ini
SERVER_HOST=0.0.0.0
SERVER_PORT=9080

# MySQL 配置 (兼容 vibe_music 数据库中的 tb_* 表结构)
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=vibe_music

# Redis 缓存
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=root
REDIS_DB=1

# MinIO 对象存储
MINIO_ENDPOINT=127.0.0.1:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=vibe-music-data
MINIO_PUBLIC_URL=http://localhost:9000

# JWT 密钥 (与原 Spring Boot 保持一致)
JWT_SECRET_KEY=SIMPLE_MUSIC
JWT_ALGORITHM=HS256
```

### 3. 运行服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 9080 --reload
```

服务启动后可访问：
- 接口文档 (Swagger UI): `http://localhost:9080/docs`
- 接口文档 (ReDoc): `http://localhost:9080/redoc`
- 健康检查: `http://localhost:9080/api/health`

---

## 🧪 运行测试

运行全量单元测试与接口迁移测试：

```bash
pytest
```

---

## 🐳 Docker 部署

```bash
# 构建镜像
docker build -t simple-music-server-python:latest .

# 运行容器
docker run -d -p 9080:9080 --env-file .env --name simple-music-server simple-music-server-python:latest
```


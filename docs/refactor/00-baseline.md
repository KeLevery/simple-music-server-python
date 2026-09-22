# Simple Music (Vibe Music) 重构基线文档 (Milestone 0)

> 本文档为 Java (Spring Boot 3) 向 Python (FastAPI) 迁移重构的顶层基线规范，记录了整个工程的技术上下文、架构拓扑与兼容性底线。

---

## 1. 系统全貌与子系统拓扑

```
+-------------------------------------------------------------+
|                       Web Clients                           |
|  1. Client: Vue 3 + Vite + Pinia + Tailwind CSS (Port 5173) |
|  2. Admin:  Vue 3 + Pure Admin + Element Plus (Port 8848)   |
+------------------------------+------------------------------+
                               |
                               v HTTP / RESTful API
+-------------------------------------------------------------+
|                  Reverse Proxy (Nginx)                      |
|  - 前端路由分发 / 静态代理                                  |
|  - 后端统一反代至 API 网关 (Port 9080)                     |
+------------------------------+------------------------------+
                               |
                               v (保持 100% 相同 API 契约)
+-------------------------------------------------------------+
|                  Backend API Server (9080)                  |
|  - 当前: Java 17 + Spring Boot 3.3.7 + MyBatis-Plus        |
|  - 重构目标: Python 3.12+ + FastAPI + SQLAlchemy 2.0 Async  |
+---------+--------------------+-------------------+----------+
          |                    |                   |
          v                    v                   v
+------------------+  +-----------------+  +------------------+
|  MySQL 8.0 (DB)  |  | Redis 7.x (DB1) |  |   MinIO Server   |
|  - 库名: vibe_music  |  | - Token 白名单   |  | - Bucket:        |
|  - 10 张核心表    |  | - 验证码/缓存   |  |   vibe-music-data|
+------------------+  +-----------------+  +------------------+
```

---

## 2. 核心重构目标与约束条件

1. **前端 100% 零修改**：客户端 (`vibe-music-client`) 和管理端 (`vibe-music-admin`) 代码不修改一行即可无缝连通新 Python 后端。
2. **数据 100% 零破坏**：直接复用原 MySQL 数据库（`vibe_music`）、表结构（`tb_*`）、MinIO 对象存储（`vibe-music-data`）。
3. **认证无感平滑切换**：
   - 必须兼容现有用户数据库中的 **MD5 密码** 校验。
   - 必须与 Java 版本的 JWT 生成与校验逻辑保持完全一致，包括 Claims 内部嵌套层级。
   - 必须复用 Redis 中的 Token 白名单校验机制。
4. **统一响应结构保持**：所有 HTTP 接口统一返回 `{ "code": 0/1, "message": "...", "data": ... }`，分页返回 `{ "total": N, "items": [...] }`。

---

## 3. 契约文档导航

- [01-api-contract.md](./01-api-contract.md) —— 全量 27 个 API 接口详细契约清单
- [02-jwt-contract.md](./02-jwt-contract.md) —— JWT 结构、签名算法、Redis 白名单与密码加密契约
- [03-database-contract.md](./03-database-contract.md) —— MySQL 表结构字典与 SQLAlchemy Model 映射契约
- [04-minio-contract.md](./04-minio-contract.md) —— MinIO 存储 Bucket、路径规则与媒体流契约
- [05-migration-rules.md](./05-migration-rules.md) —— 重构执行铁律（开发与审查守则）

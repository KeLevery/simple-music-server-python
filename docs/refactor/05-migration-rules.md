# 05 - 重构执行铁律与开发守则 (Migration Rules)

> 🚨 **本文档为 AI Agent (Antigravity / Claude Code) 及开发者的最高执行铁律**。在后续任何编码阶段，均不得违反以下准则。

---

## 铁律 1：API 契约必须 100% 保持一致（前端零改动）

1. **响应包装**：所有接口必须统一返回 `{ "code": 0/1, "message": "...", "data": ... }`。
2. **状态码规范**：常规业务失败（如“用户名或密码错误”、“歌单不存在”）**必须返回 HTTP 200**，并通过 `code: 1` 表达错误。只有鉴权拦截失败时才返回 `HTTP 401` 或 `403`。
3. **JSON 字段命名与 Null 处理**：
   - 对外输出的 JSON 字段严格遵循现有 API 契约（如 `songName`, `songId`, `coverUrl`, `userAvatar`）。
   - 空列表必须返回 `[]`，严禁返回 `null`；分页对象必须包含 `total` 和 `items`。

---

## 铁律 2：数据库结构与历史数据零破坏

1. **禁止破坏性 DDL**：严禁执行 `DROP TABLE`、`ALTER TABLE`、修改已有字段类型或删除字段。
2. **密码校验兼容**：用户和管理员密码校验**必须使用 MD5 Hex (32位小写)**，严禁私自改为 bcrypt 导致老用户无法登录。
3. **Model 物理字段映射**：SQLAlchemy Model 内部属性名采用 snake_case 映射数据库字段，由 Pydantic Schemas 负责向前端转换为 CamelCase。

---

## 3. JWT 与 Redis 白名单铁律

1. **签名参数**：算法 `HS256`，密钥字符串 `"SIMPLE_MUSIC"`。
2. **Claims 嵌套结构**：业务数据必须放置在 payload 的 `"claims"` 键下（如 `payload["claims"]["role"]`）。
3. **Redis 白名单同步**：登录成功必须向 Redis (DB 1) 写入 `set(token, token, ex=21600)`；鉴权时必须检查 Redis 是否存在该 token。

---

## 4. FastAPI 异步与架构铁律

1. **不照搬 Java 冗余层级**：统一采用 `api (Router) -> services -> db (SQLAlchemy Async)` 简洁链路，不写无意义的空壳 Repository / Interface。
2. **Session 隔离**：`AsyncSession` 必须通过 FastAPI `Depends(get_db)` 管理生命周期，严禁跨请求或并发 Task 共享 Session。
3. **避免隐式 IO**：异步 SQLAlchemy 严禁使用隐式 lazy loading，多表查询使用 `selectinload` 或 `join`，杜绝 `MissingGreenlet` 错误。
4. **权限与异常机制**：
   - 权限校验一律使用 `Depends(require_user)` / `Depends(require_admin)`。
   - 业务逻辑报错一律 `raise AppException("错误提示")`，由全局 Exception Handler 转换为统一 `Result.fail()`。

---

## 5. 阶段性验证与自测铁律

- 每个模块实现完成后，必须运行自动化契约测试，对比新 Python 接口与旧 Java 接口的：
  1. HTTP 状态码
  2. JSON Key 完整性
  3. 分页结构
  4. 错误处理与提示信息

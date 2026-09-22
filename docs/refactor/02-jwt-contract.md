# 02 - JWT 鉴权与密码哈希契约 (JWT & Auth Contract)

> ⚠️ **关键兼容性发现**：
> 1. Java 后端中使用的密码哈希**不是 BCrypt，而是标准 32 位小写 MD5 Hex**。
> 2. JWT Payload 中将业务数据**嵌套存放在 `claims` 键下**，而非顶层 claims。
> 3. Token 会同步放入 **Redis 白名单**，过期时间为 6 小时。

---

## 1. 密码加密契约 (Password Hashing)

- **算法**：MD5 (UTF-8 编码，32 位小写 Hex 字符串)
- **Java 实现**：`org.springframework.util.DigestUtils.md5DigestAsHex(password.getBytes())`
- **Python 等价实现**：
  ```python
  import hashlib

  def hash_password(password: str) -> str:
      return hashlib.md5(password.encode('utf-8')).hexdigest()

  def verify_password(plain_password: str, hashed_password: str) -> bool:
      return hash_password(plain_password) == hashed_password
  ```
- **数据库存储示例**：`df10ef8509dc176d733d59549e7dbfaf`
- **安全演进建议**：第一阶段必须兼容现有 MD5 密码验证；后续在用户登录成功时，可在后台自动升级为 bcrypt/argon2 密文。

---

## 2. JWT 规范 (Token Structure)

- **签名算法**：`HMAC256` (`HS256`)
- **密钥 (Secret Key)**：`"SIMPLE_MUSIC"`
- **Token 有效期**：JWT 内置 `exp` 为 1 小时 (`System.currentTimeMillis() + 60 * 60 * 1000`)
- **Header**：
  ```json
  {
    "alg": "HS256",
    "typ": "JWT"
  }
  ```

### 2.1 用户端 (ROLE_USER) Payload 契约
```json
{
  "claims": {
    "role": "ROLE_USER",
    "userId": 1,
    "username": "kevin",
    "email": "user@example.com"
  },
  "exp": 1727003600
}
```

### 2.2 管理端 (ROLE_ADMIN) Payload 契约
```json
{
  "claims": {
    "role": "ROLE_ADMIN",
    "adminId": 1,
    "username": "admin_1"
  },
  "exp": 1727003600
}
```

---

## 3. Redis 会话与白名单契约 (Redis Session)

- **Database**: `1` (在 `application.yml` 中配置为 `spring.data.redis.database: 1`)
- **Key**: `<token>` (完整 JWT 字符串)
- **Value**: `<token>`
- **TTL**: 6 小时 (`6 * 3600` 秒)
- **登出行为 (Logout)**：
  - 调用 `POST /admin/logout` 时执行 `redis.delete(token)`，使 Token 立即失效。

---

## 4. 拦截与权限校验逻辑 (RBAC & Dependency)

在 FastAPI 中，鉴权与权限拦截应使用 `Depends` 实现：

```python
# 逻辑步骤：
# 1. 提取 Header "Authorization: Bearer <token>"
# 2. 检查 Redis (DB 1) 中是否存在 key == token，不存在则报 401 "登录已过期，请重新登录"
# 3. 使用 PyJWT(key="SIMPLE_MUSIC", algorithms=["HS256"]) 解密 token
# 4. 提取 payload["claims"]
# 5. 校验 claims["role"] == "ROLE_ADMIN" 或 "ROLE_USER"，不匹配则报 403 "无权限访问"
```

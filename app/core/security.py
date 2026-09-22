import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from app.core.config import settings
from app.core.exceptions import UnauthorizedException

def hash_password(password: str) -> str:
    """
    密码 MD5 加密（契约对齐 Java Spring Boot DigestUtils.md5DigestAsHex）
    返回 32 位小写 Hex 字符串
    """
    return hashlib.md5(password.encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验密码"""
    return hash_password(plain_password) == hashed_password

def create_access_token(claims: dict[str, Any], expires_seconds: int | None = None) -> str:
    """
    生成 JWT 字符串，格式严格对齐 Java JwtUtil:
    Payload 结构:
    {
        "claims": { ... },
        "exp": <timestamp>
    }
    """
    expire_sec = expires_seconds or settings.JWT_EXPIRATION_SECONDS
    expire_time = datetime.now(timezone.utc) + timedelta(seconds=expire_sec)

    payload = {
        "claims": claims,
        "exp": expire_time
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

def decode_access_token(token: str) -> dict[str, Any]:
    """
    解码 JWT 并提取业务 claims 字典
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        claims = payload.get("claims")
        if not claims or not isinstance(claims, dict):
            raise UnauthorizedException("令牌格式无效")
        return claims
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("登录已过期，请重新登录")
    except (jwt.InvalidTokenError, Exception):
        raise UnauthorizedException("令牌解析失败，请重新登录")

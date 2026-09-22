from typing import Annotated, Any
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import MessageConstant
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.core.logging import logger
from app.core.security import decode_access_token
from app.db.session import get_db
from app.infrastructure.redis import init_redis

# 数据库异步 Session 依赖
DbSession = Annotated[AsyncSession, Depends(get_db)]

async def get_current_claims(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None
) -> dict[str, Any]:
    """
    鉴权依赖项，严格对齐 Java LoginInterceptor 逻辑:
    1. 从 Header 提取 Bearer Token / Raw Token
    2. 检查 Redis 白名单 (DB 1)
    3. 解析 JWT 中的 claims 字典
    """
    if not authorization:
        raise UnauthorizedException(MessageConstant.NOT_LOGIN)

    token = authorization
    if token.startswith("Bearer "):
        token = token[7:]

    token = token.strip()
    if not token:
        raise UnauthorizedException(MessageConstant.NOT_LOGIN)

    # 检查 Redis 白名单 (若 Redis 异常离线则降级记录日志并继续校验 JWT 签名)
    try:
        redis = await init_redis()
        redis_token = await redis.get(token)
        if not redis_token:
            raise UnauthorizedException(MessageConstant.SESSION_EXPIRED)
    except UnauthorizedException:
        raise
    except Exception as e:
        logger.warning(f"Redis whitelist lookup warning: {e}")

    # 解析 JWT
    claims = decode_access_token(token)
    claims["_raw_token"] = token
    return claims

async def require_user(
    claims: Annotated[dict[str, Any], Depends(get_current_claims)]
) -> dict[str, Any]:
    """校验 ROLE_USER 权限"""
    role = claims.get("role")
    if role != "ROLE_USER":
        raise ForbiddenException(MessageConstant.NO_PERMISSION)
    return claims

async def require_admin(
    claims: Annotated[dict[str, Any], Depends(get_current_claims)]
) -> dict[str, Any]:
    """校验 ROLE_ADMIN 权限"""
    role = claims.get("role")
    if role != "ROLE_ADMIN":
        raise ForbiddenException(MessageConstant.NO_PERMISSION)
    return claims

async def get_optional_user_id(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None
) -> int | None:
    """
    公开接口可选获取当前登录用户 ID:
    用于 /song/getAllSongs, /song/getRecommendedSongs 确定歌曲 likeStatus。
    未登录或 Token 无效时返回 None，不阻断公开请求。
    """
    if not authorization:
        return None
    token = authorization
    if token.startswith("Bearer "):
        token = token[7:]
    token = token.strip()
    if not token:
        return None
    try:
        claims = decode_access_token(token)
        if claims.get("role") == "ROLE_USER" and "userId" in claims:
            return int(claims["userId"])
    except Exception:
        pass
    return None

CurrentUserClaims = Annotated[dict[str, Any], Depends(require_user)]
CurrentAdminClaims = Annotated[dict[str, Any], Depends(require_admin)]
CurrentUser = CurrentUserClaims
CurrentAdmin = CurrentAdminClaims
OptionalUserId = Annotated[int | None, Depends(get_optional_user_id)]

from redis.asyncio import Redis, from_url
from app.core.config import settings
from app.core.logging import logger

redis_client: Redis | None = None

async def init_redis() -> Redis:
    """初始化 Redis 异步连接"""
    global redis_client
    if redis_client is None:
        redis_client = from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            protocol=2,
        )
    return redis_client

async def close_redis():
    """关闭 Redis 连接池"""
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None

async def ping_redis() -> bool:
    """健康检查：测试 Redis 是否连通"""
    try:
        client = await init_redis()
        return await client.ping()
    except Exception as e:
        logger.warning(f"Redis 连接检查失败: {e}")
        return False

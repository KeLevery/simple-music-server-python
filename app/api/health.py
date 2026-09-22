from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.response import Result
from app.db.session import get_db
from app.infrastructure.redis import ping_redis
from app.infrastructure.minio import ping_minio

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=Result[dict])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    系统健康检查接口：
    检查服务自身运行状态、MySQL 数据库连通性、Redis 连通性、MinIO 连通性
    """
    # 检查 MySQL
    mysql_ok = False
    try:
        res = await db.execute(text("SELECT 1"))
        mysql_ok = res.scalar() == 1
    except Exception:
        mysql_ok = False

    # 检查 Redis
    redis_ok = await ping_redis()

    # 检查 MinIO
    minio_ok = ping_minio()

    status_data = {
        "status": "healthy" if (mysql_ok and redis_ok) else "degraded",
        "mysql": mysql_ok,
        "redis": redis_ok,
        "minio": minio_ok,
    }

    return Result.success(data=status_data, message="服务健康检查正常")

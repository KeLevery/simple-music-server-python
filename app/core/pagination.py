from typing import TypeVar
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from app.core.response import PageResult

T = TypeVar("T")

async def paginate(
    session: AsyncSession,
    statement: Select,
    page_num: int = 1,
    page_size: int = 20,
) -> PageResult[T]:
    """
    通用 SQLAlchemy 异步分页查询工具函数:
    1. 计算符合条件的总条数 total
    2. offset / limit 切片获取当前页 items
    """
    if page_num < 1:
        page_num = 1
    if page_size < 1:
        page_size = 20

    # 计算总数 (去掉原本的 order_by 避免额外排序开销)
    count_statement = select(func.count()).select_from(statement.order_by(None).subquery())
    total = (await session.scalar(count_statement)) or 0

    # 切片查询
    paged_statement = statement.offset((page_num - 1) * page_size).limit(page_size)
    result = await session.execute(paged_statement)
    items = list(result.scalars().all())

    return PageResult(total=total, items=items)

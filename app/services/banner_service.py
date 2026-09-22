from typing import Any
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import MessageConstant
from app.core.response import Result, PageResult
from app.db.models.banner import Banner
from app.infrastructure.minio import delete_file
from app.schemas.playlist import BannerVO
from app.schemas.admin import BannerDTO

class BannerService:

    @staticmethod
    async def get_all_banners(db: AsyncSession, dto: BannerDTO) -> Result[PageResult[BannerVO]]:
        """获取所有轮播图列表（管理端），对齐 Java BannerServiceImpl.getAllBanners"""
        stmt = select(Banner)
        count_stmt = select(func.count(Banner.id))

        if dto.bannerStatus is not None:
            status_val = dto.bannerStatus
            if isinstance(status_val, dict) and "id" in status_val:
                status_val = status_val["id"]
            try:
                status_int = int(status_val)
                stmt = stmt.where(Banner.status == status_int)
                count_stmt = count_stmt.where(Banner.status == status_int)
            except (ValueError, TypeError):
                pass

        total = (await db.scalar(count_stmt)) or 0
        if total == 0:
            return Result.success(message=MessageConstant.DATA_NOT_FOUND, data=PageResult(total=0, items=[]))

        stmt = stmt.order_by(Banner.id.desc()).offset((dto.pageNum - 1) * dto.pageSize).limit(dto.pageSize)
        result = await db.execute(stmt)
        banners = result.scalars().all()

        vo_list = [
            BannerVO(
                bannerId=b.id,
                bannerUrl=b.banner_url,
                bannerStatus=b.status,
            )
            for b in banners
        ]

        return Result.success(data=PageResult(total=total, items=vo_list))

    @staticmethod
    async def add_banner(db: AsyncSession, banner_url: str) -> Result[str]:
        """新增轮播图，对齐 Java BannerServiceImpl.addBanner"""
        banner = Banner(banner_url=banner_url, status=0)
        db.add(banner)
        await db.commit()
        return Result.success(message=MessageConstant.ADD + MessageConstant.SUCCESS)

    @staticmethod
    async def update_banner(db: AsyncSession, banner_id: int, banner_url: str) -> Result[str]:
        """编辑轮播图图片，对齐 Java BannerServiceImpl.updateBanner"""
        stmt = select(Banner).where(Banner.id == banner_id)
        banner = (await db.execute(stmt)).scalar_one_or_none()
        if banner is None:
            return Result.fail(MessageConstant.DATA_NOT_FOUND)

        if banner.banner_url:
            delete_file(banner.banner_url)

        banner.banner_url = banner_url
        await db.commit()
        return Result.success(message=MessageConstant.UPDATE + MessageConstant.SUCCESS)

    @staticmethod
    async def update_banner_status(db: AsyncSession, banner_id: int, banner_status: int) -> Result[str]:
        """更新轮播图状态，对齐 Java BannerServiceImpl.updateBannerStatus"""
        if banner_status not in (0, 1):
            return Result.fail(MessageConstant.BANNER_STATUS_INVALID)

        stmt = select(Banner).where(Banner.id == banner_id)
        banner = (await db.execute(stmt)).scalar_one_or_none()
        if banner is None:
            return Result.fail(MessageConstant.UPDATE + MessageConstant.FAILED)

        banner.status = banner_status
        await db.commit()
        return Result.success(message=MessageConstant.UPDATE + MessageConstant.SUCCESS)

    @staticmethod
    async def delete_banner(db: AsyncSession, banner_id: int) -> Result[str]:
        """删除轮播图，对齐 Java BannerServiceImpl.deleteBanner"""
        stmt = select(Banner).where(Banner.id == banner_id)
        banner = (await db.execute(stmt)).scalar_one_or_none()
        if banner is None:
            return Result.fail(MessageConstant.DATA_NOT_FOUND)

        if banner.banner_url:
            delete_file(banner.banner_url)

        await db.delete(banner)
        await db.commit()
        return Result.success(message=MessageConstant.DELETE + MessageConstant.SUCCESS)

    @staticmethod
    async def delete_banners(db: AsyncSession, banner_ids: list[int]) -> Result[str]:
        """批量删除轮播图，对齐 Java BannerServiceImpl.deleteBanners"""
        if not banner_ids:
            return Result.fail(MessageConstant.DELETE + MessageConstant.FAILED)

        stmt = select(Banner).where(Banner.id.in_(banner_ids))
        banners = (await db.execute(stmt)).scalars().all()
        for b in banners:
            if b.banner_url:
                delete_file(b.banner_url)

        del_stmt = delete(Banner).where(Banner.id.in_(banner_ids))
        res = await db.execute(del_stmt)
        if res.rowcount == 0:
            return Result.fail(MessageConstant.DELETE + MessageConstant.FAILED)

        await db.commit()
        return Result.success(message=MessageConstant.DELETE + MessageConstant.SUCCESS)

    @staticmethod
    async def get_banner_list(db: AsyncSession) -> Result[list[BannerVO]]:
        """获取前台展示轮播图列表 (至多 9 条有效 Banner)"""
        stmt = (
            select(Banner)
            .where(Banner.status == 0)
            .order_by(Banner.id.desc())
            .limit(9)
        )
        result = await db.execute(stmt)
        banners = result.scalars().all()

        vo_list = [
            BannerVO(
                bannerId=b.id,
                bannerUrl=b.banner_url,
                bannerStatus=b.status,
            )
            for b in banners
        ]

        return Result.success(data=vo_list)

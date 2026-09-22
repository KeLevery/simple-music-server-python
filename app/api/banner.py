from fastapi import APIRouter
from app.api.deps import DbSession
from app.core.response import Result
from app.schemas.playlist import BannerVO
from app.services.banner_service import BannerService

router = APIRouter(tags=["Banner"])

@router.get("/banner/getBannerList", response_model=Result[list[BannerVO]])
async def get_banner_list(db: DbSession):
    """
    获取前台轮播图列表
    URL: GET /banner/getBannerList
    权限: 公开 (Public)
    """
    return await BannerService.get_banner_list(db)

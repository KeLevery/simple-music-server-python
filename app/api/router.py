from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.user import router as user_router
from app.api.admin import router as admin_router
from app.api.song import router as song_router
from app.api.artist import router as artist_router
from app.api.playlist import router as playlist_router
from app.api.favorite import router as favorite_router
from app.api.banner import router as banner_router

api_router = APIRouter()

# 基础与健康检查路由
api_router.include_router(health_router)

# 用户与管理员认证路由
api_router.include_router(user_router)
api_router.include_router(admin_router)

# 核心音乐数据业务路由 (Milestone 3)
api_router.include_router(song_router)
api_router.include_router(artist_router)

# 歌单、收藏与轮播图路由 (Milestone 4)
api_router.include_router(playlist_router)
api_router.include_router(favorite_router)
api_router.include_router(banner_router)

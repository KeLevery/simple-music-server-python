from typing import Any
from fastapi import APIRouter
from app.api.deps import DbSession, OptionalUserId
from app.core.response import Result, PageResult
from app.schemas.playlist import PlaylistDTO, PlaylistVO
from app.services.playlist_service import PlaylistService

router = APIRouter(prefix="/playlist", tags=["Playlist"])

@router.get("/getRecommendedPlaylists", response_model=Result[list[PlaylistVO]])
async def get_recommended_playlists(db: DbSession, user_id: OptionalUserId):
    """
    获取推荐歌单
    URL: GET /playlist/getRecommendedPlaylists
    权限: 公开 (Public)
    """
    return await PlaylistService.get_recommended_playlists(db, user_id=user_id)

@router.post("/getAllPlaylists", response_model=Result[PageResult[PlaylistVO]])
async def get_all_playlists(db: DbSession, dto: PlaylistDTO | None = None):
    """
    获取所有歌单（歌单广场）
    URL: POST /playlist/getAllPlaylists
    权限: 公开 (Public)
    """
    dto = dto or PlaylistDTO()
    return await PlaylistService.get_all_playlists(db, dto)

@router.get("/getPlaylistDetail/{playlist_id}", response_model=Result[dict[str, Any]])
async def get_playlist_detail(playlist_id: int, db: DbSession, user_id: OptionalUserId):
    """
    获取歌单详情
    URL: GET /playlist/getPlaylistDetail/{id}
    权限: 公开 (Public)
    """
    return await PlaylistService.get_playlist_detail(db, playlist_id=playlist_id, user_id=user_id)

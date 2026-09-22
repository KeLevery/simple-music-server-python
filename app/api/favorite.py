from fastapi import APIRouter, Query
from app.api.deps import DbSession, CurrentUserClaims
from app.core.response import Result, PageResult
from app.schemas.playlist import PlaylistVO, FavoriteSearchDTO
from app.schemas.music import SongVO
from app.services.favorite_service import FavoriteService

router = APIRouter(prefix="/favorite", tags=["Favorite"])

@router.post("/getFavoritePlaylists", response_model=Result[PageResult[PlaylistVO]])
async def get_favorite_playlists(
    claims: CurrentUserClaims,
    db: DbSession,
    dto: FavoriteSearchDTO | None = None
):
    """
    获取当前用户收藏的歌单列表
    URL: POST /favorite/getFavoritePlaylists
    权限: 需登录 (ROLE_USER)
    """
    user_id = int(claims["userId"])
    dto = dto or FavoriteSearchDTO()
    return await FavoriteService.get_favorite_playlists(db, user_id=user_id, dto=dto)

@router.post("/getFavoriteSongs", response_model=Result[PageResult[SongVO]])
async def get_favorite_songs(
    claims: CurrentUserClaims,
    db: DbSession,
    dto: FavoriteSearchDTO | None = None
):
    """
    获取当前用户收藏的歌曲列表
    URL: POST /favorite/getFavoriteSongs
    权限: 需登录 (ROLE_USER)
    """
    user_id = int(claims["userId"])
    dto = dto or FavoriteSearchDTO()
    return await FavoriteService.get_favorite_songs(db, user_id=user_id, dto=dto)

@router.post("/collectSong", response_model=Result[None])
async def collect_song(
    claims: CurrentUserClaims,
    db: DbSession,
    song_id: int = Query(..., alias="songId")
):
    """
    收藏歌曲
    URL: POST /favorite/collectSong?songId=123
    权限: 需登录 (ROLE_USER)
    """
    user_id = int(claims["userId"])
    return await FavoriteService.collect_song(db, user_id=user_id, song_id=song_id)

@router.delete("/cancelCollectSong", response_model=Result[None])
async def cancel_collect_song(
    claims: CurrentUserClaims,
    db: DbSession,
    song_id: int = Query(..., alias="songId")
):
    """
    取消收藏歌曲
    URL: DELETE /favorite/cancelCollectSong?songId=123
    权限: 需登录 (ROLE_USER)
    """
    user_id = int(claims["userId"])
    return await FavoriteService.cancel_collect_song(db, user_id=user_id, song_id=song_id)

@router.post("/collectPlaylist", response_model=Result[None])
async def collect_playlist(
    claims: CurrentUserClaims,
    db: DbSession,
    playlist_id: int = Query(..., alias="playlistId")
):
    """
    收藏歌单
    URL: POST /favorite/collectPlaylist?playlistId=123
    权限: 需登录 (ROLE_USER)
    """
    user_id = int(claims["userId"])
    return await FavoriteService.collect_playlist(db, user_id=user_id, playlist_id=playlist_id)

@router.delete("/cancelCollectPlaylist", response_model=Result[None])
async def cancel_collect_playlist(
    claims: CurrentUserClaims,
    db: DbSession,
    playlist_id: int = Query(..., alias="playlistId")
):
    """
    取消收藏歌单
    URL: DELETE /favorite/cancelCollectPlaylist?playlistId=123
    权限: 需登录 (ROLE_USER)
    """
    user_id = int(claims["userId"])
    return await FavoriteService.cancel_collect_playlist(db, user_id=user_id, playlist_id=playlist_id)

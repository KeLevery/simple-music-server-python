from fastapi import APIRouter
from app.api.deps import DbSession, OptionalUserId
from app.core.response import Result, PageResult
from app.schemas.music import SongDTO, SongVO, SongDetailVO
from app.services.song_service import SongService

router = APIRouter(prefix="/song", tags=["Song"])

@router.get("/getRecommendedSongs", response_model=Result[list[SongVO]])
async def get_recommended_songs(db: DbSession, user_id: OptionalUserId):
    """
    获取推荐歌曲
    URL: GET /song/getRecommendedSongs
    权限: 公开 (Public)
    """
    return await SongService.get_recommended_songs(db, user_id=user_id)

@router.post("/getAllSongs", response_model=Result[PageResult[SongVO]])
async def get_all_songs(dto: SongDTO, db: DbSession, user_id: OptionalUserId):
    """
    分页获取所有歌曲（歌曲库/搜索）
    URL: POST /song/getAllSongs
    权限: 公开 (Public)
    """
    return await SongService.get_all_songs(db, dto, user_id=user_id)

@router.get("/getSongDetail/{song_id}", response_model=Result[SongDetailVO])
async def get_song_detail(song_id: int, db: DbSession, user_id: OptionalUserId):
    """
    获取歌曲详情
    URL: GET /song/getSongDetail/{id}
    权限: 公开 (Public)
    """
    return await SongService.get_song_detail(db, song_id=song_id, user_id=user_id)

from typing import Any
from fastapi import APIRouter
from app.api.deps import DbSession
from app.core.response import Result, PageResult
from app.schemas.music import ArtistDTO, ArtistVO
from app.services.artist_service import ArtistService

router = APIRouter(prefix="/artist", tags=["Artist"])

@router.post("/getAllArtists", response_model=Result[PageResult[ArtistVO]])
async def get_all_artists(dto: ArtistDTO, db: DbSession):
    """
    分页获取歌手列表
    URL: POST /artist/getAllArtists
    权限: 公开 (Public)
    """
    return await ArtistService.get_all_artists(db, dto)

@router.get("/getArtistDetail/{artist_id}", response_model=Result[dict[str, Any]])
async def get_artist_detail(artist_id: int, db: DbSession):
    """
    获取歌手详情及名下歌曲
    URL: GET /artist/getArtistDetail/{id}
    权限: 公开 (Public)
    """
    return await ArtistService.get_artist_detail(db, artist_id=artist_id)

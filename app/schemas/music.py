from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, Field

# ==================== Song Schemas ====================

class SongDTO(BaseModel):
    """歌曲查询请求参数，严格对齐 Java SongDTO"""
    pageNum: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=20, ge=1, description="每页数量")
    songName: str | None = Field(default=None, description="歌曲名")
    artistName: str | None = Field(default=None, description="歌手名")
    album: str | None = Field(default=None, description="专辑名")

class SongVO(BaseModel):
    """歌曲展示对象，严格对齐 Java SongVO 字段名 (CamelCase)"""
    songId: int
    songName: str
    artistName: str = "群星"
    album: str | None = None
    duration: str | None = None
    coverUrl: str | None = None
    audioUrl: str | None = None
    likeStatus: int = 0
    releaseTime: date | None = None

class SongDetailVO(BaseModel):
    """歌曲详情展示对象，严格对齐 Java SongDetailVO"""
    songId: int
    songName: str
    artistName: str = "群星"
    album: str | None = None
    lyric: str | None = None
    duration: str | None = None
    coverUrl: str | None = None
    audioUrl: str | None = None
    releaseTime: date | None = None
    likeStatus: int = 0
    comments: list[Any] = Field(default_factory=list)

# ==================== Artist Schemas ====================

class ArtistDTO(BaseModel):
    """歌手查询请求参数，严格对齐 Java ArtistDTO"""
    pageNum: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=20, ge=1, description="每页数量")
    artistName: str | None = Field(default=None, description="歌手姓名")
    gender: int | None = Field(default=None, description="性别：0-男，1-女，2-组合")
    area: str | None = Field(default=None, description="地区")

class ArtistVO(BaseModel):
    """歌手展示对象，严格对齐 Java ArtistVO"""
    artistId: int
    artistName: str
    gender: int | None = None
    birth: date | None = None
    area: str | None = None
    introduction: str | None = None
    avatar: str | None = None
    createTime: datetime | None = None

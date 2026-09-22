from pydantic import BaseModel, Field

class PlaylistDTO(BaseModel):
    """歌单查询请求参数，严格对齐 Java PlaylistDTO"""
    pageNum: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=20, ge=1, description="每页数量")
    title: str | None = Field(default=None, description="歌单标题")
    style: str | None = Field(default=None, description="歌单风格")

class PlaylistVO(BaseModel):
    """歌单展示对象，严格对齐 Java PlaylistVO"""
    playlistId: int
    title: str
    coverUrl: str | None = None
    introduction: str | None = None
    style: str | None = None

class BannerVO(BaseModel):
    """轮播图展示对象，对齐 Java BannerVO"""
    bannerId: int
    bannerUrl: str
    bannerStatus: int = 0

class FavoriteSearchDTO(BaseModel):
    """收藏列表查询参数"""
    pageNum: int = Field(default=1, ge=1)
    pageSize: int = Field(default=20, ge=1)
    songName: str | None = None

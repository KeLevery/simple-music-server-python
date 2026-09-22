from typing import Annotated, Any
from fastapi import APIRouter, Header, UploadFile, File, Form, Query, Path, Body
from app.api.deps import DbSession, CurrentAdmin
from app.core.response import Result, PageResult
from app.infrastructure.minio import upload_file
from app.schemas.auth import AdminDTO
from app.schemas.music import ArtistDTO, ArtistVO
from app.schemas.playlist import PlaylistDTO, PlaylistVO, BannerVO
from app.schemas.admin import (
    UserSearchDTO, UserAddDTO, UserDTO, UserManagementVO,
    ArtistAddDTO, ArtistUpdateDTO, ArtistNameVO,
    SongAndArtistDTO, SongAddDTO, SongUpdateDTO, SongAdminVO,
    PlaylistAddDTO, PlaylistUpdateDTO,
    BannerDTO, FeedbackDTO, FeedbackVO,
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.artist_service import ArtistService
from app.services.song_service import SongService
from app.services.playlist_service import PlaylistService
from app.services.banner_service import BannerService
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/admin", tags=["Admin"])

# ==================== 1. 管理员鉴权 ====================

@router.post("/login", response_model=Result[str])
async def login(dto: AdminDTO, db: DbSession):
    """
    管理员登录
    URL: POST /admin/login
    权限: 公开 (Public)
    """
    return await AuthService.login_admin(db, dto)

@router.post("/logout", response_model=Result[None])
async def logout(authorization: Annotated[str | None, Header(alias="Authorization")] = None):
    """
    管理员登出
    URL: POST /admin/logout
    权限: 请求头带 Authorization Token
    """
    return await AuthService.logout_admin(authorization)

# ==================== 2. 统计接口 ====================

@router.get("/getAllUsersCount", response_model=Result[int])
async def get_all_users_count(admin: CurrentAdmin, db: DbSession):
    """获取所有用户数量"""
    return await UserService.get_all_users_count(db)

@router.get("/getAllArtistsCount", response_model=Result[int])
async def get_all_artists_count(
    admin: CurrentAdmin,
    db: DbSession,
    gender: int | None = Query(default=None),
    area: str | None = Query(default=None)
):
    """获取所有歌手数量"""
    return await ArtistService.get_all_artists_count(db, gender=gender, area=area)

@router.get("/getAllSongsCount", response_model=Result[int])
async def get_all_songs_count(
    admin: CurrentAdmin,
    db: DbSession,
    style: str | None = Query(default=None)
):
    """获取所有歌曲数量"""
    return await SongService.get_all_songs_count(db, style=style)

@router.get("/getAllPlaylistsCount", response_model=Result[int])
async def get_all_playlists_count(
    admin: CurrentAdmin,
    db: DbSession,
    style: str | None = Query(default=None)
):
    """获取所有歌单数量"""
    return await PlaylistService.get_all_playlists_count(db, style=style)

# ==================== 3. 用户管理 ====================

@router.post("/getAllUsers", response_model=Result[PageResult[UserManagementVO]])
async def get_all_users(admin: CurrentAdmin, db: DbSession, dto: UserSearchDTO):
    """获取所有用户列表（分页）"""
    return await UserService.get_all_users(db, dto)

@router.post("/addUser", response_model=Result[str])
async def add_user(admin: CurrentAdmin, db: DbSession, dto: UserAddDTO):
    """新增用户"""
    return await UserService.add_user(db, dto)

@router.put("/updateUser", response_model=Result[str])
async def update_user(admin: CurrentAdmin, db: DbSession, dto: UserDTO):
    """修改用户信息"""
    return await UserService.update_user(db, dto)

@router.patch("/updateUserStatus/{id}/{status}", response_model=Result[str])
async def update_user_status(
    admin: CurrentAdmin,
    db: DbSession,
    id: int = Path(..., description="用户ID"),
    status: int = Path(..., description="用户状态: 0-启用, 1-禁用")
):
    """更新用户状态"""
    return await UserService.update_user_status(db, id, status)

@router.delete("/deleteUser/{id}", response_model=Result[str])
async def delete_user(admin: CurrentAdmin, db: DbSession, id: int = Path(..., description="用户ID")):
    """删除用户"""
    return await UserService.delete_user(db, id)

@router.delete("/deleteUsers", response_model=Result[str])
async def delete_users(admin: CurrentAdmin, db: DbSession, user_ids: list[int] = Body(...)):
    """批量删除用户"""
    return await UserService.delete_users(db, user_ids)

# ==================== 4. 歌手管理 ====================

@router.post("/getAllArtists", response_model=Result[PageResult[ArtistVO]])
async def get_all_artists(admin: CurrentAdmin, db: DbSession, dto: ArtistDTO):
    """获取歌手列表（管理端）"""
    return await ArtistService.get_all_artists_and_detail(db, dto)

@router.post("/addArtist", response_model=Result[str])
async def add_artist(admin: CurrentAdmin, db: DbSession, dto: ArtistAddDTO):
    """新增歌手"""
    return await ArtistService.add_artist(db, dto)

@router.put("/updateArtist", response_model=Result[str])
async def update_artist(admin: CurrentAdmin, db: DbSession, dto: ArtistUpdateDTO):
    """编辑歌手"""
    return await ArtistService.update_artist(db, dto)

@router.patch("/updateArtistAvatar/{id}", response_model=Result[str])
async def update_artist_avatar(
    admin: CurrentAdmin,
    db: DbSession,
    id: int = Path(..., description="歌手ID"),
    avatar: UploadFile = File(..., description="头像文件")
):
    """上传歌手头像"""
    avatar_url = upload_file(avatar, "artists")
    return await ArtistService.update_artist_avatar(db, id, avatar_url)

@router.delete("/deleteArtist/{id}", response_model=Result[str])
async def delete_artist(admin: CurrentAdmin, db: DbSession, id: int = Path(..., description="歌手ID")):
    """删除歌手"""
    return await ArtistService.delete_artist(db, id)

@router.delete("/deleteArtists", response_model=Result[str])
async def delete_artists(admin: CurrentAdmin, db: DbSession, artist_ids: list[int] = Body(...)):
    """批量删除歌手"""
    return await ArtistService.delete_artists(db, artist_ids)

# ==================== 5. 歌曲管理 ====================

@router.get("/getAllArtistNames", response_model=Result[list[ArtistNameVO]])
async def get_all_artist_names(admin: CurrentAdmin, db: DbSession):
    """获取所有歌手名称列表"""
    return await SongService.get_all_artist_names(db)

@router.post("/getAllSongsByArtist", response_model=Result[PageResult[SongAdminVO]])
async def get_all_songs_by_artist(admin: CurrentAdmin, db: DbSession, dto: SongAndArtistDTO):
    """获取歌曲列表（管理端）"""
    return await SongService.get_all_songs_by_artist(db, dto)

@router.post("/addSong", response_model=Result[str])
async def add_song(admin: CurrentAdmin, db: DbSession, dto: SongAddDTO):
    """新增歌曲"""
    return await SongService.add_song(db, dto)

@router.put("/updateSong", response_model=Result[str])
async def update_song(admin: CurrentAdmin, db: DbSession, dto: SongUpdateDTO):
    """编辑歌曲"""
    return await SongService.update_song(db, dto)

@router.patch("/updateSongCover/{id}", response_model=Result[str])
async def update_song_cover(
    admin: CurrentAdmin,
    db: DbSession,
    id: int = Path(..., description="歌曲ID"),
    cover: UploadFile = File(..., description="封面文件")
):
    """更新歌曲封面"""
    cover_url = upload_file(cover, "songCovers")
    return await SongService.update_song_cover(db, id, cover_url)

@router.patch("/updateSongAudio/{id}", response_model=Result[str])
async def update_song_audio(
    admin: CurrentAdmin,
    db: DbSession,
    id: int = Path(..., description="歌曲ID"),
    audio: UploadFile = File(..., description="音频文件")
):
    """更新歌曲音频"""
    audio_url = upload_file(audio, "songs")
    return await SongService.update_song_audio(db, id, audio_url)

@router.delete("/deleteSong/{id}", response_model=Result[str])
async def delete_song(admin: CurrentAdmin, db: DbSession, id: int = Path(..., description="歌曲ID")):
    """删除歌曲"""
    return await SongService.delete_song(db, id)

@router.delete("/deleteSongs", response_model=Result[str])
async def delete_songs(admin: CurrentAdmin, db: DbSession, song_ids: list[int] = Body(...)):
    """批量删除歌曲"""
    return await SongService.delete_songs(db, song_ids)

# ==================== 6. 歌单管理 ====================

@router.post("/getAllPlaylists", response_model=Result[PageResult[PlaylistVO]])
async def get_all_playlists(admin: CurrentAdmin, db: DbSession, dto: PlaylistDTO):
    """获取歌单列表（管理端）"""
    return await PlaylistService.get_all_playlists(db, dto)

@router.post("/addPlaylist", response_model=Result[str])
async def add_playlist(admin: CurrentAdmin, db: DbSession, dto: PlaylistAddDTO):
    """新增歌单"""
    return await PlaylistService.add_playlist(db, dto)

@router.put("/updatePlaylist", response_model=Result[str])
async def update_playlist(admin: CurrentAdmin, db: DbSession, dto: PlaylistUpdateDTO):
    """编辑歌单"""
    return await PlaylistService.update_playlist(db, dto)

@router.patch("/updatePlaylistCover/{id}", response_model=Result[str])
async def update_playlist_cover(
    admin: CurrentAdmin,
    db: DbSession,
    id: int = Path(..., description="歌单ID"),
    cover: UploadFile = File(..., description="封面文件")
):
    """上传歌单封面"""
    cover_url = upload_file(cover, "playlists")
    return await PlaylistService.update_playlist_cover(db, id, cover_url)

@router.delete("/deletePlaylist/{id}", response_model=Result[str])
async def delete_playlist(admin: CurrentAdmin, db: DbSession, id: int = Path(..., description="歌单ID")):
    """删除歌单"""
    return await PlaylistService.delete_playlist(db, id)

@router.delete("/deletePlaylists", response_model=Result[str])
async def delete_playlists(admin: CurrentAdmin, db: DbSession, ids: list[int] = Body(...)):
    """批量删除歌单"""
    return await PlaylistService.delete_playlists(db, ids)

# ==================== 7. 轮播图管理 ====================

@router.post("/getAllBanners", response_model=Result[PageResult[BannerVO]])
async def get_all_banners(admin: CurrentAdmin, db: DbSession, dto: BannerDTO):
    """获取轮播图列表"""
    return await BannerService.get_all_banners(db, dto)

@router.post("/addBanner", response_model=Result[str])
async def add_banner(
    admin: CurrentAdmin,
    db: DbSession,
    banner: UploadFile = File(..., description="轮播图文件")
):
    """新增轮播图"""
    banner_url = upload_file(banner, "banners")
    return await BannerService.add_banner(db, banner_url)

@router.post("/updateBanner/{id}", response_model=Result[str])
async def update_banner(
    admin: CurrentAdmin,
    db: DbSession,
    id: int = Path(..., description="轮播图ID"),
    banner: UploadFile = File(..., description="轮播图文件")
):
    """编辑轮播图"""
    banner_url = upload_file(banner, "banners")
    return await BannerService.update_banner(db, id, banner_url)

@router.patch("/updateBannerStatus/{id}", response_model=Result[str])
async def update_banner_status(
    admin: CurrentAdmin,
    db: DbSession,
    id: int = Path(..., description="轮播图ID"),
    status: int = Query(..., description="状态: 0-启用, 1-禁用")
):
    """更新轮播图状态"""
    return await BannerService.update_banner_status(db, id, status)

@router.delete("/deleteBanner/{id}", response_model=Result[str])
async def delete_banner(admin: CurrentAdmin, db: DbSession, id: int = Path(..., description="轮播图ID")):
    """删除轮播图"""
    return await BannerService.delete_banner(db, id)

@router.delete("/deleteBanners", response_model=Result[str])
async def delete_banners(admin: CurrentAdmin, db: DbSession, ids: list[int] = Body(...)):
    """批量删除轮播图"""
    return await BannerService.delete_banners(db, ids)

# ==================== 8. 反馈管理 ====================

@router.post("/getAllFeedbacks", response_model=Result[PageResult[FeedbackVO]])
async def get_all_feedbacks(admin: CurrentAdmin, db: DbSession, dto: FeedbackDTO):
    """获取反馈列表"""
    return await FeedbackService.get_all_feedbacks(db, dto)

@router.delete("/deleteFeedback/{id}", response_model=Result[str])
async def delete_feedback(admin: CurrentAdmin, db: DbSession, id: int = Path(..., description="反馈ID")):
    """删除反馈"""
    return await FeedbackService.delete_feedback(db, id)

@router.delete("/deleteFeedbacks", response_model=Result[str])
async def delete_feedbacks(admin: CurrentAdmin, db: DbSession, feedback_ids: list[int] = Body(...)):
    """批量删除反馈"""
    return await FeedbackService.delete_feedbacks(db, feedback_ids)

# ==================== 9. 测试接口 ====================

@router.get("/get", response_model=Result[None])
async def get_test():
    """测试用接口"""
    return Result.success()

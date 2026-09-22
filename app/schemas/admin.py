import re
from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, Field, EmailStr, field_validator
from app.core.constants import MessageConstant

PASSWORD_REGEX = re.compile(r"^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z\W]{8,18}$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_-]{4,16}$")
PHONE_REGEX = re.compile(r"^1[3456789]\d{9}$")

# ==================== User Management Schemas ====================

class UserSearchDTO(BaseModel):
    """用户查询请求参数"""
    pageNum: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=20, ge=1, description="每页数量")
    username: str | None = Field(default=None, description="用户名")
    phone: str | None = Field(default=None, description="手机号")
    userStatus: Any = Field(default=None, description="用户状态: 0-启用, 1-禁用")

class UserAddDTO(BaseModel):
    """新增用户参数"""
    username: str = Field(..., description="用户名 (4-16位)")
    password: str = Field(..., description="密码 (8-18位数字、字母、符号任意两种组合)")
    phone: str | None = Field(default=None, description="手机号")
    email: EmailStr = Field(..., description="邮箱")
    introduction: str | None = Field(default=None, max_length=100, description="简介")
    userStatus: Any = Field(default=None, description="状态: 1-启用, 0-禁用")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not USERNAME_REGEX.match(v):
            raise ValueError(MessageConstant.USERNAME + MessageConstant.FORMAT_ERROR)
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not PASSWORD_REGEX.match(v):
            raise ValueError(MessageConstant.PASSWORD + MessageConstant.FORMAT_ERROR)
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v and not PHONE_REGEX.match(v):
            raise ValueError(MessageConstant.PHONE + MessageConstant.FORMAT_ERROR)
        return v

class UserDTO(BaseModel):
    """修改用户参数"""
    userId: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名 (4-16位)")
    phone: str | None = Field(default=None, description="手机号")
    email: EmailStr = Field(..., description="邮箱")
    introduction: str | None = Field(default=None, max_length=100, description="简介")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not USERNAME_REGEX.match(v):
            raise ValueError(MessageConstant.USERNAME + MessageConstant.FORMAT_ERROR)
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v and not PHONE_REGEX.match(v):
            raise ValueError(MessageConstant.PHONE + MessageConstant.FORMAT_ERROR)
        return v

class UserManagementVO(BaseModel):
    """管理员查看用户列表项"""
    userId: int
    username: str
    phone: str | None = None
    email: str
    userAvatar: str | None = None
    introduction: str | None = None
    createTime: datetime | None = None
    updateTime: datetime | None = None
    userStatus: int = 0

# ==================== Artist Schemas ====================

class ArtistAddDTO(BaseModel):
    """新增歌手请求参数"""
    artistName: str = Field(..., description="歌手名")
    gender: int = Field(default=0, description="性别：0-男，1-女，2-组合/乐队")
    birth: str | None = Field(default=None, description="出生日期 YYYY-MM-DD")
    area: str | None = Field(default=None, description="地区")
    introduction: str | None = Field(default=None, description="简介")

class ArtistUpdateDTO(BaseModel):
    """修改歌手请求参数"""
    artistId: int = Field(..., description="歌手ID")
    artistName: str | None = Field(default=None, description="歌手名")
    gender: int | None = Field(default=None, description="性别")
    birth: str | None = Field(default=None, description="出生日期 YYYY-MM-DD")
    area: str | None = Field(default=None, description="地区")
    introduction: str | None = Field(default=None, description="简介")

class ArtistNameVO(BaseModel):
    """歌手名称简要VO"""
    artistId: int
    artistName: str

# ==================== Song Schemas ====================

class SongAndArtistDTO(BaseModel):
    """管理员查询歌曲列表参数"""
    pageNum: int = Field(default=1, ge=1)
    pageSize: int = Field(default=20, ge=1)
    artistId: int | None = None
    songName: str | None = None
    album: str | None = None

class SongAddDTO(BaseModel):
    """管理员新增歌曲参数"""
    artistId: int | None = None
    songName: str = Field(..., description="歌名")
    album: str | None = None
    style: str | None = None
    releaseTime: str | date | None = None

class SongUpdateDTO(BaseModel):
    """管理员修改歌曲参数"""
    songId: int = Field(..., description="歌曲ID")
    artistId: int | None = None
    songName: str | None = None
    album: str | None = None
    style: str | None = None
    releaseTime: str | date | None = None

class SongAdminVO(BaseModel):
    """管理员歌曲展示对象"""
    songId: int
    artistName: str | None = "群星"
    songName: str
    album: str | None = None
    lyric: str | None = None
    duration: str | None = None
    style: str | None = None
    coverUrl: str | None = None
    audioUrl: str | None = None
    releaseTime: date | None = None

# ==================== Playlist Schemas ====================

class PlaylistAddDTO(BaseModel):
    """新增歌单参数"""
    title: str = Field(..., description="歌单标题")
    introduction: str | None = None
    style: str | None = None

class PlaylistUpdateDTO(BaseModel):
    """修改歌单参数"""
    playlistId: int = Field(..., description="歌单ID")
    title: str | None = None
    introduction: str | None = None
    style: str | None = None

# ==================== Banner Schemas ====================

class BannerDTO(BaseModel):
    """轮播图查询参数"""
    pageNum: int = Field(default=1, ge=1)
    pageSize: int = Field(default=20, ge=1)
    bannerStatus: Any = None

# ==================== Feedback Schemas ====================

class FeedbackDTO(BaseModel):
    """反馈查询参数"""
    pageNum: int = Field(default=1, ge=1)
    pageSize: int = Field(default=20, ge=1)
    keyword: str | None = None

class FeedbackVO(BaseModel):
    """反馈展示对象"""
    feedbackId: int
    userId: int
    feedback: str
    createTime: datetime | None = None

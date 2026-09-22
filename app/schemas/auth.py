import re
from pydantic import BaseModel, Field, EmailStr, field_validator
from app.core.constants import MessageConstant

PASSWORD_REGEX = re.compile(r"^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z\W]{8,18}$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_-]{4,16}$")

class UserLoginDTO(BaseModel):
    """用户登录请求参数，严格对齐 Java UserLoginDTO"""
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., description="用户密码 (8-18位数字、字母、符号任意两种组合)")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not PASSWORD_REGEX.match(v):
            raise ValueError(MessageConstant.PASSWORD + MessageConstant.FORMAT_ERROR)
        return v

class AdminDTO(BaseModel):
    """管理员登录请求参数，严格对齐 Java AdminDTO"""
    username: str = Field(..., description="管理员用户名 (4-16位字符)")
    password: str = Field(..., description="管理员密码 (8-18位)")

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

class UserVO(BaseModel):
    """用户个人信息展示对象，严格对齐 Java UserVO 字段名 (CamelCase)"""
    userId: int
    username: str
    phone: str | None = None
    email: str
    userAvatar: str | None = None
    introduction: str | None = None

from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class User(Base):
    __tablename__ = "tb_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="用户 id")
    username: Mapped[str] = mapped_column(String(20), nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(64), nullable=False, comment="用户密码 (MD5)")
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="手机号")
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="邮箱")
    user_avatar: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="用户头像 url")
    introduction: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="用户简介")
    create_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="创建时间")
    update_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="更新时间")
    status: Mapped[int] = mapped_column(Integer, default=0, comment="用户状态：0-启用，1-禁用")

from datetime import date
from sqlalchemy import BigInteger, String, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Artist(Base):
    __tablename__ = "tb_artist"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="歌手 id")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="歌手姓名")
    gender: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="性别：0-男，1-女，2-组合")
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="歌手头像 url")
    birth: Mapped[date | None] = mapped_column(Date, nullable=True, comment="出生日期")
    area: Mapped[str | None] = mapped_column(String(30), nullable=True, comment="歌手国籍/地区")
    introduction: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="歌手简介")

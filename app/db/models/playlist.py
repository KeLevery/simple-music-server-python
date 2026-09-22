from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Playlist(Base):
    __tablename__ = "tb_playlist"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="歌单 id")
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="歌单标题")
    cover_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="歌单封面 url")
    introduction: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="歌单简介")
    style: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="歌单风格")

from datetime import date
from sqlalchemy import BigInteger, String, Text, Date
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Song(Base):
    __tablename__ = "tb_song"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="歌曲 id")
    artist_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="歌手 id")
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="歌名")
    album: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="专辑名")
    lyric: Mapped[str | None] = mapped_column(Text, nullable=True, comment="歌词")
    duration: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="歌曲时长")
    style: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="歌曲风格")
    cover_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="封面 url")
    audio_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="音频 url")
    release_time: Mapped[date | None] = mapped_column(Date, nullable=True, comment="发行时间")

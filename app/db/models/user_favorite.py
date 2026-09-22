from datetime import datetime
from sqlalchemy import BigInteger, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class UserFavorite(Base):
    __tablename__ = "tb_user_favorite"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="id")
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="用户 id")
    type: Mapped[int] = mapped_column(Integer, nullable=False, comment="收藏类型：0-歌曲，1-歌单")
    song_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="收藏歌曲 id")
    playlist_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="收藏歌单 id")
    create_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="创建时间")

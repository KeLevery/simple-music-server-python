from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Genre(Base):
    __tablename__ = "tb_genre"

    song_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="歌曲 id")
    style_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="风格 id")

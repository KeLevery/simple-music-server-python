from sqlalchemy import BigInteger, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Banner(Base):
    __tablename__ = "tb_banner"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="轮播图 id")
    banner_url: Mapped[str] = mapped_column(String(255), nullable=False, comment="轮播图 url")
    status: Mapped[int] = mapped_column(Integer, default=0, comment="状态：0-启用，1-禁用")

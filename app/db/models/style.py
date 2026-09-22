from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Style(Base):
    __tablename__ = "tb_style"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="风格 id")
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="风格名称")

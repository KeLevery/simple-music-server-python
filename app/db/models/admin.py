from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Admin(Base):
    __tablename__ = "tb_admin"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="管理员 id")
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, comment="管理员用户名")
    password: Mapped[str] = mapped_column(String(64), nullable=False, comment="管理员密码 (MD5)")

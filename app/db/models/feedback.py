from datetime import datetime
from sqlalchemy import BigInteger, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Feedback(Base):
    __tablename__ = "tb_feedback"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="反馈 id")
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="用户 id")
    feedback: Mapped[str] = mapped_column(Text, nullable=False, comment="反馈内容")
    create_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="创建时间")

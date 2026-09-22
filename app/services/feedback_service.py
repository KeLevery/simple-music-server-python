from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import MessageConstant
from app.core.response import Result, PageResult
from app.db.models.feedback import Feedback
from app.schemas.admin import FeedbackDTO, FeedbackVO

class FeedbackService:

    @staticmethod
    async def get_all_feedbacks(db: AsyncSession, dto: FeedbackDTO) -> Result[PageResult[FeedbackVO]]:
        """获取所有反馈列表，对齐 Java FeedbackServiceImpl.getAllFeedbacks"""
        stmt = select(Feedback)
        count_stmt = select(func.count(Feedback.id))

        if dto.keyword:
            stmt = stmt.where(Feedback.feedback.like(f"%{dto.keyword.strip()}%"))
            count_stmt = count_stmt.where(Feedback.feedback.like(f"%{dto.keyword.strip()}%"))

        total = (await db.scalar(count_stmt)) or 0
        if total == 0:
            return Result.success(message=MessageConstant.DATA_NOT_FOUND, data=PageResult(total=0, items=[]))

        stmt = stmt.order_by(Feedback.create_time.desc()).offset((dto.pageNum - 1) * dto.pageSize).limit(dto.pageSize)
        result = await db.execute(stmt)
        feedbacks = result.scalars().all()

        vo_list = [
            FeedbackVO(
                feedbackId=f.id,
                userId=f.user_id,
                feedback=f.feedback,
                createTime=f.create_time,
            )
            for f in feedbacks
        ]

        return Result.success(data=PageResult(total=total, items=vo_list))

    @staticmethod
    async def delete_feedback(db: AsyncSession, feedback_id: int) -> Result[str]:
        """删除反馈，对齐 Java FeedbackServiceImpl.deleteFeedback"""
        stmt = delete(Feedback).where(Feedback.id == feedback_id)
        res = await db.execute(stmt)
        if res.rowcount == 0:
            return Result.fail(MessageConstant.DELETE + MessageConstant.FAILED)

        await db.commit()
        return Result.success(message=MessageConstant.DELETE + MessageConstant.SUCCESS)

    @staticmethod
    async def delete_feedbacks(db: AsyncSession, feedback_ids: list[int]) -> Result[str]:
        """批量删除反馈，对齐 Java FeedbackServiceImpl.deleteFeedbacks"""
        if not feedback_ids:
            return Result.fail(MessageConstant.DELETE + MessageConstant.FAILED)

        stmt = delete(Feedback).where(Feedback.id.in_(feedback_ids))
        res = await db.execute(stmt)
        if res.rowcount == 0:
            return Result.fail(MessageConstant.DELETE + MessageConstant.FAILED)

        await db.commit()
        return Result.success(message=MessageConstant.DELETE + MessageConstant.SUCCESS)

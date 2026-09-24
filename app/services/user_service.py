from datetime import datetime
from typing import Any
from sqlalchemy import select, func, or_, desc, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import MessageConstant
from app.core.response import Result, PageResult
from app.core.security import hash_password
from app.db.models.user import User
from app.db.models.user_favorite import UserFavorite
from app.schemas.admin import UserSearchDTO, UserAddDTO, UserDTO, UserManagementVO

class UserService:

    @staticmethod
    async def get_all_users_count(db: AsyncSession) -> Result[int]:
        """获取所有用户数量，对齐 Java UserServiceImpl.getAllUsersCount"""
        stmt = select(func.count(User.id))
        count = await db.scalar(stmt) or 0
        return Result.success(data=count)

    @staticmethod
    async def get_all_users(db: AsyncSession, dto: UserSearchDTO) -> Result[PageResult[UserManagementVO]]:
        """获取所有用户列表（分页与过滤），对齐 Java UserServiceImpl.getAllUsers"""
        stmt = select(User)
        count_stmt = select(func.count(User.id))

        conditions = []
        if dto.username:
            conditions.append(User.username.like(f"%{dto.username}%"))
        if dto.phone:
            conditions.append(User.phone.like(f"%{dto.phone}%"))
        if dto.userStatus is not None:
            status_val = dto.userStatus
            if isinstance(status_val, dict) and "id" in status_val:
                status_val = status_val["id"]
            try:
                status_int = int(status_val)
                conditions.append(User.status == status_int)
            except (ValueError, TypeError):
                pass

        if conditions:
            stmt = stmt.where(*conditions)
            count_stmt = count_stmt.where(*conditions)

        total = await db.scalar(count_stmt) or 0
        if total == 0:
            return Result.success(message=MessageConstant.DATA_NOT_FOUND, data=PageResult(total=0, items=[]))

        stmt = stmt.order_by(desc(User.create_time)).offset((dto.pageNum - 1) * dto.pageSize).limit(dto.pageSize)
        result = await db.execute(stmt)
        users = result.scalars().all()

        records = [
            UserManagementVO(
                userId=u.id,
                username=u.username,
                phone=u.phone,
                email=u.email,
                userAvatar=u.user_avatar,
                introduction=u.introduction,
                createTime=u.create_time,
                updateTime=u.update_time,
                userStatus=u.status,
            )
            for u in users
        ]
        return Result.success(data=PageResult(total=total, items=records))

    @staticmethod
    async def add_user(db: AsyncSession, dto: UserAddDTO) -> Result[str]:
        """新增用户，对齐 Java UserServiceImpl.addUser"""
        # 查重: 用户名, 手机号, 邮箱
        or_conds = [User.username == dto.username, User.email == dto.email]
        if dto.phone:
            or_conds.append(User.phone == dto.phone)

        check_stmt = select(User).where(or_(*or_conds))
        existing_result = await db.execute(check_stmt)
        existing_users = existing_result.scalars().all()

        for u in existing_users:
            if u.username == dto.username:
                return Result.fail(MessageConstant.USERNAME + MessageConstant.ALREADY_EXISTS)
            if dto.phone and u.phone == dto.phone:
                return Result.fail(MessageConstant.PHONE + MessageConstant.ALREADY_EXISTS)
            if u.email == dto.email:
                return Result.fail(MessageConstant.EMAIL + MessageConstant.ALREADY_EXISTS)

        # 状态处理：Java 端传 1 代表启用 (存 DB 为 0), 传 0 代表禁用 (存 DB 为 1)
        db_status = 0
        if dto.userStatus is not None:
            status_val = dto.userStatus
            if isinstance(status_val, dict) and "id" in status_val:
                status_val = status_val["id"]
            try:
                if int(status_val) == 0:
                    db_status = 1
                elif int(status_val) == 1:
                    db_status = 0
            except (ValueError, TypeError):
                pass

        now = datetime.now()
        new_user = User(
            username=dto.username,
            password=hash_password(dto.password),
            phone=dto.phone,
            email=dto.email,
            introduction=dto.introduction,
            status=db_status,
            create_time=now,
            update_time=now,
        )
        db.add(new_user)
        await db.commit()
        return Result.success(message=MessageConstant.ADD + MessageConstant.SUCCESS)

    @staticmethod
    async def update_user(db: AsyncSession, dto: UserDTO) -> Result[str]:
        """修改用户信息，对齐 Java UserServiceImpl.updateUser"""
        # 检查用户名是否重复
        stmt_u = select(User).where(User.username == dto.username, User.id != dto.userId)
        if (await db.execute(stmt_u)).scalar_one_or_none():
            return Result.fail(MessageConstant.USERNAME + MessageConstant.ALREADY_EXISTS)

        # 检查手机号是否重复
        if dto.phone:
            stmt_p = select(User).where(User.phone == dto.phone, User.id != dto.userId)
            if (await db.execute(stmt_p)).scalar_one_or_none():
                return Result.fail(MessageConstant.PHONE + MessageConstant.ALREADY_EXISTS)

        # 检查邮箱是否重复
        stmt_e = select(User).where(User.email == dto.email, User.id != dto.userId)
        if (await db.execute(stmt_e)).scalar_one_or_none():
            return Result.fail(MessageConstant.EMAIL + MessageConstant.ALREADY_EXISTS)

        stmt_target = select(User).where(User.id == dto.userId)
        user = (await db.execute(stmt_target)).scalar_one_or_none()
        if user is None:
            return Result.fail(MessageConstant.DATA_NOT_FOUND)

        user.username = dto.username
        user.phone = dto.phone
        user.email = dto.email
        user.introduction = dto.introduction
        user.update_time = datetime.now()

        await db.commit()
        return Result.success(message=MessageConstant.UPDATE + MessageConstant.SUCCESS)

    @staticmethod
    async def update_user_status(db: AsyncSession, user_id: int, user_status: int) -> Result[str]:
        """更新用户状态，对齐 Java UserServiceImpl.updateUserStatus"""
        if user_status not in (0, 1):
            return Result.fail(MessageConstant.USER_STATUS_INVALID)

        stmt = select(User).where(User.id == user_id)
        user = (await db.execute(stmt)).scalar_one_or_none()
        if user is None:
            return Result.fail(MessageConstant.UPDATE + MessageConstant.FAILED)

        user.status = user_status
        user.update_time = datetime.now()
        await db.commit()
        return Result.success(message=MessageConstant.UPDATE + MessageConstant.SUCCESS)

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> Result[str]:
        """删除用户，对齐 Java UserServiceImpl.deleteUser"""
        # 级联删除该用户的收藏记录
        del_fav = delete(UserFavorite).where(UserFavorite.user_id == user_id)
        await db.execute(del_fav)

        stmt = delete(User).where(User.id == user_id)
        res = await db.execute(stmt)
        if res.rowcount == 0:
            return Result.fail(MessageConstant.DELETE + MessageConstant.FAILED)
        await db.commit()
        return Result.success(message=MessageConstant.DELETE + MessageConstant.SUCCESS)

    @staticmethod
    async def delete_users(db: AsyncSession, user_ids: list[int]) -> Result[str]:
        """批量删除用户，对齐 Java UserServiceImpl.deleteUsers"""
        if not user_ids:
            return Result.fail(MessageConstant.DELETE + MessageConstant.FAILED)

        # 级联删除用户的收藏记录
        del_fav = delete(UserFavorite).where(UserFavorite.user_id.in_(user_ids))
        await db.execute(del_fav)

        stmt = delete(User).where(User.id.in_(user_ids))
        res = await db.execute(stmt)
        if res.rowcount == 0:
            return Result.fail(MessageConstant.DELETE + MessageConstant.FAILED)
        await db.commit()
        return Result.success(message=MessageConstant.DELETE + MessageConstant.SUCCESS)

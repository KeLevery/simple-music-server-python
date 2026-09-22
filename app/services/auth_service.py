from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.constants import MessageConstant
from app.core.logging import logger
from app.core.response import Result
from app.core.security import verify_password, create_access_token
from app.db.models.user import User
from app.db.models.admin import Admin
from app.infrastructure.redis import init_redis
from app.schemas.auth import UserLoginDTO, AdminDTO, UserVO

class AuthService:

    @staticmethod
    async def login_user(db: AsyncSession, dto: UserLoginDTO) -> Result[str]:
        """
        用户登录逻辑，完全复刻 Java UserServiceImpl.login:
        1. 查 tb_user by email -> 不存在返回 "邮箱错误"
        2. 查 status != 0 -> 返回 "账号被锁定"
        3. MD5 密码匹配 -> 不匹配返回 "密码错误"
        4. 生成带有 claims 嵌套字典的 JWT
        5. 写入 Redis 白名单 (DB 1, 6小时)
        6. 返回 { code: 0, message: "登录成功", data: token }
        """
        stmt = select(User).where(User.email == dto.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return Result.fail(MessageConstant.EMAIL + MessageConstant.ERROR)

        if user.status != 0:
            return Result.fail(MessageConstant.ACCOUNT_LOCKED)

        if not verify_password(dto.password, user.password):
            return Result.fail(MessageConstant.PASSWORD + MessageConstant.ERROR)

        # 构造 claims (与 Java 对齐)
        claims = {
            "role": "ROLE_USER",
            "userId": user.id,
            "username": user.username,
            "email": user.email,
        }
        token = create_access_token(claims)

        # 写入 Redis 白名单
        try:
            redis = await init_redis()
            await redis.set(token, token, ex=settings.REDIS_TOKEN_EXPIRE_SECONDS)
        except Exception as e:
            logger.warning(f"Redis write token warning: {e}")

        return Result.success(data=token, message=MessageConstant.LOGIN + MessageConstant.SUCCESS)

    @staticmethod
    async def get_user_info(db: AsyncSession, user_id: int) -> Result[UserVO]:
        """
        获取当前用户信息，复刻 Java UserServiceImpl.getUserInfo
        """
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return Result.fail(MessageConstant.DATA_NOT_FOUND)

        user_vo = UserVO(
            userId=user.id,
            username=user.username,
            phone=user.phone,
            email=user.email,
            userAvatar=user.user_avatar,
            introduction=user.introduction,
        )
        return Result.success(data=user_vo)

    @staticmethod
    async def login_admin(db: AsyncSession, dto: AdminDTO) -> Result[str]:
        """
        管理员登录逻辑，完全复刻 Java AdminServiceImpl.login:
        1. 查 tb_admin by username -> 不存在返回 "用户名错误"
        2. MD5 密码匹配 -> 不匹配返回 "密码错误"
        3. 生成含有 claims 嵌套字典的 JWT (role="ROLE_ADMIN", adminId, username)
        4. 写入 Redis 白名单 (DB 1, 6小时)
        5. 返回 { code: 0, message: "登录成功", data: token }
        """
        stmt = select(Admin).where(Admin.username == dto.username)
        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()

        if admin is None:
            return Result.fail(MessageConstant.USERNAME + MessageConstant.ERROR)

        if not verify_password(dto.password, admin.password):
            return Result.fail(MessageConstant.PASSWORD + MessageConstant.ERROR)

        claims = {
            "role": "ROLE_ADMIN",
            "adminId": admin.id,
            "username": admin.username,
        }
        token = create_access_token(claims)

        # 写入 Redis 白名单
        try:
            redis = await init_redis()
            await redis.set(token, token, ex=settings.REDIS_TOKEN_EXPIRE_SECONDS)
        except Exception as e:
            logger.warning(f"Redis write token warning: {e}")

        return Result.success(data=token, message=MessageConstant.LOGIN + MessageConstant.SUCCESS)

    @staticmethod
    async def logout_admin(raw_token: str | None) -> Result[None]:
        """
        管理员登出逻辑，复刻 Java AdminServiceImpl.logout
        """
        if not raw_token:
            return Result.fail(MessageConstant.LOGOUT + MessageConstant.FAILED)

        token = raw_token
        if token.startswith("Bearer "):
            token = token[7:]
        token = token.strip()

        try:
            redis = await init_redis()
            deleted = await redis.delete(token)
            if deleted:
                return Result.success(message=MessageConstant.LOGOUT + MessageConstant.SUCCESS)
        except Exception as e:
            logger.warning(f"Redis delete token warning: {e}")

        return Result.success(message=MessageConstant.LOGOUT + MessageConstant.SUCCESS)

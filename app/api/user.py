from fastapi import APIRouter
from app.api.deps import DbSession, CurrentUserClaims
from app.core.response import Result
from app.schemas.auth import UserLoginDTO, UserVO
from app.services.auth_service import AuthService

router = APIRouter(prefix="/user", tags=["User"])

@router.post("/login", response_model=Result[str])
async def login(dto: UserLoginDTO, db: DbSession):
    """
    用户登录
    URL: POST /user/login
    权限: 公开 (Public)
    """
    return await AuthService.login_user(db, dto)

@router.get("/getUserInfo", response_model=Result[UserVO])
async def get_user_info(claims: CurrentUserClaims, db: DbSession):
    """
    获取当前登录用户信息
    URL: GET /user/getUserInfo
    权限: 需登录 (ROLE_USER)
    """
    user_id = int(claims["userId"])
    return await AuthService.get_user_info(db, user_id)

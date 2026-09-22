import pytest
import jwt
from httpx import AsyncClient
from app.core.config import settings
from app.core.constants import MessageConstant

# 使用数据库现有真实数据（保持只读，不进行任何修改或删除）
EXISTING_USER_EMAIL = "user651@example.com"
EXISTING_USER_PASSWORD_RAW = "123456abc"
EXISTING_USER_USERNAME = "user_361"

EXISTING_ADMIN_USERNAME = "admin_172"
EXISTING_ADMIN_PASSWORD_RAW = "123456abc"


# ==================== User 认证与信息获取测试 ====================

@pytest.mark.asyncio
async def test_user_login_success(async_client: AsyncClient):
    """测试现有老用户真实账号密码登录成功并验证 JWT 结构"""
    payload = {
        "email": EXISTING_USER_EMAIL,
        "password": EXISTING_USER_PASSWORD_RAW
    }
    response = await async_client.post("/user/login", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 0
    assert res["message"] == "登录成功"
    token = res["data"]
    assert isinstance(token, str)

    # 验证生成的 JWT 符合 Java 契约
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    assert "claims" in decoded
    assert decoded["claims"]["role"] == "ROLE_USER"
    assert decoded["claims"]["email"] == EXISTING_USER_EMAIL
    assert decoded["claims"]["username"] == EXISTING_USER_USERNAME
    assert isinstance(decoded["claims"]["userId"], int)
    assert "exp" in decoded

@pytest.mark.asyncio
async def test_user_login_wrong_password(async_client: AsyncClient):
    """测试密码错误时返回 HTTP 200 + code: 1 + '密码错误'"""
    payload = {
        "email": EXISTING_USER_EMAIL,
        "password": "WrongPassword999"
    }
    response = await async_client.post("/user/login", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 1
    assert res["message"] == MessageConstant.PASSWORD + MessageConstant.ERROR
    assert res["data"] is None

@pytest.mark.asyncio
async def test_user_login_nonexistent_email(async_client: AsyncClient):
    """测试不存在邮箱返回 HTTP 200 + code: 1 + '邮箱错误'"""
    payload = {
        "email": "not_exist_99999@example.com",
        "password": EXISTING_USER_PASSWORD_RAW
    }
    response = await async_client.post("/user/login", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 1
    assert res["message"] == MessageConstant.EMAIL + MessageConstant.ERROR
    assert res["data"] is None

@pytest.mark.asyncio
async def test_get_user_info_success(async_client: AsyncClient):
    """测试携带合法 Token 获取现有用户信息"""
    login_resp = await async_client.post("/user/login", json={
        "email": EXISTING_USER_EMAIL,
        "password": EXISTING_USER_PASSWORD_RAW
    })
    token = login_resp.json()["data"]

    response = await async_client.get(
        "/user/getUserInfo",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 0
    assert res["message"] == "操作成功"
    data = res["data"]
    assert data["username"] == EXISTING_USER_USERNAME
    assert data["email"] == EXISTING_USER_EMAIL
    assert "userId" in data

@pytest.mark.asyncio
async def test_get_user_info_without_token(async_client: AsyncClient):
    """测试未传 Token 返回 HTTP 401"""
    response = await async_client.get("/user/getUserInfo")
    assert response.status_code == 401
    res = response.json()
    assert res["code"] == 1
    assert res["message"] == MessageConstant.NOT_LOGIN

@pytest.mark.asyncio
async def test_get_user_info_invalid_token(async_client: AsyncClient):
    """测试传伪造/无效 Token 返回 HTTP 401"""
    response = await async_client.get(
        "/user/getUserInfo",
        headers={"Authorization": "Bearer invalid_fake_token_123"}
    )
    assert response.status_code == 401
    res = response.json()
    assert res["code"] == 1


# ==================== Admin 认证测试 ====================

@pytest.mark.asyncio
async def test_admin_login_success(async_client: AsyncClient):
    """测试现有管理员账号真实登录成功并验证 JWT 结构"""
    payload = {
        "username": EXISTING_ADMIN_USERNAME,
        "password": EXISTING_ADMIN_PASSWORD_RAW
    }
    response = await async_client.post("/admin/login", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 0
    assert res["message"] == "登录成功"
    token = res["data"]
    assert isinstance(token, str)

    # 验证 Admin JWT
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    assert decoded["claims"]["role"] == "ROLE_ADMIN"
    assert decoded["claims"]["username"] == EXISTING_ADMIN_USERNAME
    assert "adminId" in decoded["claims"]

@pytest.mark.asyncio
async def test_admin_login_wrong_password(async_client: AsyncClient):
    """测试管理员密码错误"""
    payload = {
        "username": EXISTING_ADMIN_USERNAME,
        "password": "WrongPassword999"
    }
    response = await async_client.post("/admin/login", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 1
    assert res["message"] == MessageConstant.PASSWORD + MessageConstant.ERROR

@pytest.mark.asyncio
async def test_admin_login_nonexistent_username(async_client: AsyncClient):
    """测试管理员用户名不存在（合法格式 4-16位）返回 '用户名错误'"""
    payload = {
        "username": "admin_not_exist",
        "password": EXISTING_ADMIN_PASSWORD_RAW
    }
    response = await async_client.post("/admin/login", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 1
    assert res["message"] == MessageConstant.USERNAME + MessageConstant.ERROR

@pytest.mark.asyncio
async def test_admin_logout(async_client: AsyncClient):
    """测试管理员登出"""
    response = await async_client.post(
        "/admin/logout",
        headers={"Authorization": "Bearer some_sample_token_123"}
    )
    assert response.status_code == 200
    res = response.json()
    assert res["code"] == 0
    assert res["message"] == MessageConstant.LOGOUT + MessageConstant.SUCCESS

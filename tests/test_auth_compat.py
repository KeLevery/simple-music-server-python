import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

def test_md5_password_compat():
    # 验证标准 123456 的 MD5
    pwd_hash = hash_password("123456")
    assert pwd_hash == "e10adc3949ba59abbe56e057f20f883e"
    assert verify_password("123456", "e10adc3949ba59abbe56e057f20f883e")
    assert not verify_password("wrong_password", "e10adc3949ba59abbe56e057f20f883e")

def test_jwt_claims_nesting_compat():
    claims_input = {
        "role": "ROLE_USER",
        "userId": 1001,
        "username": "test_user",
        "email": "user@test.com"
    }

    token = create_access_token(claims_input)
    assert isinstance(token, str)

    decoded = decode_access_token(token)
    assert decoded["role"] == "ROLE_USER"
    assert decoded["userId"] == 1001
    assert decoded["username"] == "test_user"
    assert decoded["email"] == "user@test.com"

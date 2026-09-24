import pytest
import io
from fastapi import UploadFile
from httpx import AsyncClient
from app.core.exceptions import AppException
from app.infrastructure.minio import upload_file, delete_file

# ==================== CORS 安全性测试 ====================

@pytest.mark.asyncio
async def test_cors_trusted_origin_allowed(async_client: AsyncClient):
    """测试合法的本地前端 Origin 正确获得 CORS 头"""
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
    }
    response = await async_client.options("/user/login", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert response.headers.get("access-control-allow-credentials") == "true"

@pytest.mark.asyncio
async def test_cors_untrusted_origin_rejected(async_client: AsyncClient):
    """测试未授权的恶意 Origin 不会被动态反射允许"""
    headers = {
        "Origin": "http://evil-attacker.com",
        "Access-Control-Request-Method": "POST",
    }
    response = await async_client.options("/user/login", headers=headers)
    # 不匹配的 Origin 不会返回 allow-origin: http://evil-attacker.com
    assert response.headers.get("access-control-allow-origin") != "http://evil-attacker.com"


# ==================== MinIO 上传安全校验测试 ====================

def test_upload_file_disallowed_extension():
    """测试上传不允许的文件扩展名（如 .exe / .html / .sh）被拦截"""
    file_bytes = b"echo 'hack'"
    fake_file = UploadFile(
        file=io.BytesIO(file_bytes),
        filename="malicious.exe",
        headers={"content-type": "application/x-msdownload"}
    )
    with pytest.raises(AppException) as exc_info:
        upload_file(fake_file, "artists")
    assert "不支持的图片格式" in str(exc_info.value.message)

def test_upload_file_audio_disallowed_extension():
    """测试上传歌曲时不允许的音频扩展名被拦截"""
    file_bytes = b"image content"
    fake_file = UploadFile(
        file=io.BytesIO(file_bytes),
        filename="not_audio.png",
        headers={"content-type": "image/png"}
    )
    with pytest.raises(AppException) as exc_info:
        upload_file(fake_file, "songs")
    assert "不支持的音频格式" in str(exc_info.value.message)

def test_upload_file_size_exceeded():
    """测试上传超大文件时被尺寸限制拦截"""
    oversized_bytes = b"A" * (11 * 1024 * 1024)  # 11MB > 10MB
    fake_file = UploadFile(
        file=io.BytesIO(oversized_bytes),
        filename="huge.png",
        headers={"content-type": "image/png"}
    )
    with pytest.raises(AppException) as exc_info:
        upload_file(fake_file, "banners")
    assert "文件大小超出限制" in str(exc_info.value.message)

def test_delete_file_invalid_prefix_graceful():
    """测试传递非法前缀 URL 时平稳处理不报错"""
    # 不属于当前 bucket 的 URL 应该安全退出，不抛出未捕获异常
    delete_file("http://attacker.com/other-bucket/secret.txt")
    delete_file(None)
    delete_file("")

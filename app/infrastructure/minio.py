import os
import re
import uuid
from io import BytesIO
from pathlib import Path
from fastapi import UploadFile
from minio import Minio
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import AppException
from app.core.constants import MessageConstant

_minio_client: Minio | None = None

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
AUDIO_EXTENSIONS = {".mp3", ".flac", ".wav", ".m4a", ".ogg", ".aac"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10 MB
MAX_AUDIO_SIZE = 50 * 1024 * 1024   # 50 MB

def get_minio_client() -> Minio:
    """获取 MinIO 客户端实例"""
    global _minio_client
    if _minio_client is None:
        _minio_client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
    return _minio_client

def ping_minio() -> bool:
    """健康检查：测试 MinIO 是否能访问 Bucket"""
    try:
        client = get_minio_client()
        return client.bucket_exists(settings.MINIO_BUCKET)
    except Exception as e:
        logger.warning(f"MinIO 连接检查失败: {e}")
        return False

def upload_file(file: UploadFile, folder: str) -> str:
    """上传文件到 MinIO 并返回可访问的 URL（含文件类型、大小校验与异常屏蔽）"""
    try:
        raw_name = file.filename or "file"
        safe_basename = os.path.basename(raw_name)
        ext = Path(safe_basename).suffix.lower()

        # 1. 严格校验文件扩展名与大小上限
        if folder in ("artists", "songCovers", "playlists", "banners"):
            if ext not in IMAGE_EXTENSIONS:
                raise AppException(f"不支持的图片格式: {ext or '未知'}")
            max_size = MAX_IMAGE_SIZE
        elif folder == "songs":
            if ext not in AUDIO_EXTENSIONS:
                raise AppException(f"不支持的音频格式: {ext or '未知'}")
            max_size = MAX_AUDIO_SIZE
        else:
            max_size = MAX_IMAGE_SIZE

        # 2. 安全读取，防止无上限读取导致内存溢出 (OOM)
        content = file.file.read(max_size + 1)
        if len(content) > max_size:
            max_mb = max_size // (1024 * 1024)
            raise AppException(f"文件大小超出限制，最大允许 {max_mb}MB")

        client = get_minio_client()
        if not client.bucket_exists(settings.MINIO_BUCKET):
            client.make_bucket(settings.MINIO_BUCKET)

        # 3. 净化文件名，防止路径穿越
        clean_name = re.sub(r"[^\w\.\-]", "_", safe_basename)
        filename = f"{folder}/{uuid.uuid4()}-{clean_name}"

        client.put_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=filename,
            data=BytesIO(content),
            length=len(content),
            content_type=file.content_type or "application/octet-stream",
        )
        protocol = "https" if settings.MINIO_SECURE else "http"
        endpoint = f"{protocol}://{settings.MINIO_ENDPOINT}"
        return f"{endpoint}/{settings.MINIO_BUCKET}/{filename}"
    except AppException:
        raise
    except Exception as e:
        logger.error(f"文件上传失败: {e}", exc_info=True)
        raise AppException(f"{MessageConstant.FILE_UPLOAD}{MessageConstant.FAILED}，请稍后重试")

def delete_file(file_url: str | None) -> None:
    """从 MinIO 删除文件"""
    if not file_url:
        return
    try:
        client = get_minio_client()
        protocol = "https" if settings.MINIO_SECURE else "http"
        endpoint = f"{protocol}://{settings.MINIO_ENDPOINT}"
        prefix = f"{endpoint}/{settings.MINIO_BUCKET}/"
        if file_url.startswith(prefix):
            object_name = file_url[len(prefix):]
        elif f"/{settings.MINIO_BUCKET}/" in file_url:
            object_name = file_url.split(f"/{settings.MINIO_BUCKET}/", 1)[1]
        else:
            return

        client.remove_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_name,
        )
    except Exception as e:
        logger.warning(f"文件删除失败: {e}")

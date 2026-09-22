import uuid
from io import BytesIO
from fastapi import UploadFile
from minio import Minio
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import AppException
from app.core.constants import MessageConstant

_minio_client: Minio | None = None

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
    """上传文件到 MinIO 并返回可访问的 URL"""
    try:
        client = get_minio_client()
        if not client.bucket_exists(settings.MINIO_BUCKET):
            client.make_bucket(settings.MINIO_BUCKET)

        filename = f"{folder}/{uuid.uuid4()}-{file.filename}"
        content = file.file.read()
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
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        raise AppException(f"{MessageConstant.FILE_UPLOAD}{MessageConstant.FAILED}：{e}")

def delete_file(file_url: str | None) -> None:
    """从 MinIO 删除文件"""
    if not file_url:
        return
    try:
        client = get_minio_client()
        protocol = "https" if settings.MINIO_SECURE else "http"
        endpoint = f"{protocol}://{settings.MINIO_ENDPOINT}"
        prefix = f"{endpoint}/{settings.MINIO_BUCKET}/"
        object_name = file_url.replace(prefix, "")
        client.remove_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_name,
        )
    except Exception as e:
        logger.warning(f"文件删除失败: {e}")

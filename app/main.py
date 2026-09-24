from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    UnauthorizedException,
    ForbiddenException,
)
from app.core.logging import setup_logging, logger
from app.db.session import engine
from app.infrastructure.redis import init_redis, close_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    logger.info("Initializing Simple Music Python API Server...")
    try:
        await init_redis()
        logger.info("Redis client connected.")
    except Exception as e:
        logger.warning(f"Redis initialization warning: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Simple Music Python API Server...")
    await close_redis()
    await engine.dispose()
    logger.info("Resources released successfully.")

app = FastAPI(
    title="Simple Music API (Python)",
    version="1.0.0",
    description="Simple Music (Vibe Music) 全栈重构 FastAPI 服务端",
    docs_url="/docs" if settings.DEBUG or settings.ENVIRONMENT == "development" else None,
    redoc_url=None,
    lifespan=lifespan,
)

# CORS 跨域中间件 (遵循标准凭据规范与白名单校验)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- 全局异常处理器 (契约对齐) -----------------

@app.exception_handler(AppException)
async def handle_app_exception(request: Request, exc: AppException):
    """
    通用业务异常拦截：
    返回 HTTP 200 + { "code": exc.code, "message": exc.message, "data": None }
    兼容现有前端 Axios 拦截器
    """
    return JSONResponse(
        status_code=200,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": None,
        }
    )

@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    """
    Pydantic 请求参数校验失败：
    提取第一条错误信息并返回 HTTP 200 + { "code": 1, "message": "...", "data": None }
    """
    errors = exc.errors()
    msg = "参数校验错误"
    if errors:
        first_err = errors[0]
        field = ".".join(str(loc) for loc in first_err.get("loc", []))
        msg = f"{field}: {first_err.get('msg', '参数格式不正确')}"

    return JSONResponse(
        status_code=200,
        content={
            "code": 1,
            "message": msg,
            "data": None,
        }
    )

@app.exception_handler(UnauthorizedException)
async def handle_unauthorized_exception(request: Request, exc: UnauthorizedException):
    """
    未登录或 Token 失效：
    返回 HTTP 401
    """
    return JSONResponse(
        status_code=401,
        content={
            "code": 1,
            "message": exc.message,
            "data": None,
        }
    )

@app.exception_handler(ForbiddenException)
async def handle_forbidden_exception(request: Request, exc: ForbiddenException):
    """
    角色权限不足：
    返回 HTTP 403
    """
    return JSONResponse(
        status_code=403,
        content={
            "code": 1,
            "message": exc.message,
            "data": None,
        }
    )

@app.exception_handler(Exception)
async def handle_unexpected_exception(request: Request, exc: Exception):
    """
    未捕获系统异常兜底：
    返回 HTTP 200 + { "code": 1, "message": "系统繁忙，请稍后重试", "data": None }
    """
    logger.error(f"Unhandled system exception: {exc}", exc_info=True)
    msg = str(exc) if settings.DEBUG else "系统繁忙，请稍后再试"
    return JSONResponse(
        status_code=200,
        content={
            "code": 1,
            "message": f"系统异常: {msg}",
            "data": None,
        }
    )

# 注册所有路由
app.include_router(api_router)

class AppException(Exception):
    """
    通用业务异常：
    抛出此异常时，全局 Handler 会捕获并返回 HTTP 200 + { "code": code, "message": message, "data": None }
    以保持与前端 Axios 拦截器行为一致。
    """
    def __init__(self, message: str = "操作失败", code: int = 1):
        self.message = message
        self.code = code
        super().__init__(message)

class NotFoundException(AppException):
    def __init__(self, message: str = "数据未找到"):
        super().__init__(message=message, code=1)

class UnauthorizedException(Exception):
    """未登录或 Token 失效，返回 HTTP 401"""
    def __init__(self, message: str = "登录已过期，请重新登录"):
        self.message = message
        super().__init__(message)

class ForbiddenException(Exception):
    """权限不足，返回 HTTP 403"""
    def __init__(self, message: str = "无权限访问"):
        self.message = message
        super().__init__(message)

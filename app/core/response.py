from typing import Generic, TypeVar, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class PageResult(BaseModel, Generic[T]):
    """通用分页返回结果对象，契约对齐 Java PageResult<T>"""
    total: int = 0
    items: list[T] = Field(default_factory=list)

class Result(BaseModel, Generic[T]):
    """
    通用 API 响应封装，契约对齐 Java Result<T>:
    code: 0-成功, 1-失败/业务异常
    message: 提示信息
    data: 响应数据
    """
    code: int = 0
    message: str = "操作成功"
    data: T | None = None

    @classmethod
    def success(cls, data: Any = None, message: str = "操作成功") -> "Result[Any]":
        return cls(code=0, message=message, data=data)

    @classmethod
    def fail(cls, message: str = "操作失败", code: int = 1) -> "Result[None]":
        return cls(code=code, message=message, data=None)

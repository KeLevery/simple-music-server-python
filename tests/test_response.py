import pytest
from app.core.response import Result, PageResult
from app.core.exceptions import AppException

def test_result_success():
    res = Result.success(data={"id": 1, "name": "test"}, message="成功")
    d = res.model_dump()
    assert d["code"] == 0
    assert d["message"] == "成功"
    assert d["data"] == {"id": 1, "name": "test"}

def test_result_fail():
    res = Result.fail(message="操作失败", code=1)
    d = res.model_dump()
    assert d["code"] == 1
    assert d["message"] == "操作失败"
    assert d["data"] is None

def test_page_result():
    page = PageResult(total=100, items=[{"id": 1}, {"id": 2}])
    d = page.model_dump()
    assert d["total"] == 100
    assert len(d["items"]) == 2

def test_page_result_empty():
    page = PageResult()
    d = page.model_dump()
    assert d["total"] == 0
    assert d["items"] == []

def test_app_exception():
    exc = AppException("业务错误测试", code=1)
    assert exc.message == "业务错误测试"
    assert exc.code == 1

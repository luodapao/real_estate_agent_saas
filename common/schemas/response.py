"""
全局通用Pydantic响应模型
定义统一的API响应格式
"""

from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, ConfigDict

# 泛型类型
T = TypeVar('T')


class ORMBaseModel(BaseModel):
    """ORM基础模型 - 所有需要使用from_orm的模型都应继承此类"""
    model_config = ConfigDict(from_attributes=True)


class BaseResponse(BaseModel):
    """基础响应模型"""
    code: int
    message: str
    data: Optional[T] = None
    
    model_config = ConfigDict(from_attributes=True)


class SuccessResponse(BaseModel, Generic[T]):
    """成功响应模型"""
    code: int = 200
    message: str = "操作成功"
    data: Optional[T] = None


class PageResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    code: int = 200
    message: str = "操作成功"
    data: Optional[List[T]] = None
    total: int = 0
    page: int = 1
    size: int = 10


class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: int
    message: str
    data: Optional[T] = None


def success(data: T = None, message: str = "操作成功") -> dict:
    """快捷返回成功响应"""
    return {
        "code": 200,
        "message": message,
        "data": data
    }


def success_page(data: List[T], total: int, page: int, size: int) -> dict:
    """快捷返回分页成功响应"""
    return {
        "code": 200,
        "message": "操作成功",
        "data": data,
        "total": total,
        "page": page,
        "size": size
    }


def error(code: int, message: str) -> dict:
    """快捷返回错误响应"""
    return {
        "code": code,
        "message": message,
        "data": None
    }
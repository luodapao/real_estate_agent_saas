"""
房地产SaaS财务管理系统 - 基础响应模型
用于API接口的通用响应数据格式
"""

from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar, List

T = TypeVar('T')


class PageRequest(BaseModel):
    """分页请求模型"""
    page: int = Field(1, description="页码", ge=1)
    size: int = Field(10, description="每页条数", ge=1, le=100)
    keyword: Optional[str] = Field(None, description="搜索关键字")
    
    @property
    def page_size(self):
        return self.size


class PageResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    code: int = Field(0, description="状态码")
    message: str = Field("success", description="响应消息")
    data: Optional[List[T]] = Field(None, description="数据列表")
    total: int = Field(0, description="总记录数")
    page: int = Field(1, description="当前页码")
    size: int = Field(10, description="每页条数")


class ApiResponse(BaseModel, Generic[T]):
    """通用API响应模型"""
    code: int = Field(0, description="状态码：0成功，非0失败")
    message: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "success") -> 'ApiResponse[T]':
        """成功响应"""
        return cls(code=0, message=message, data=data)

    @classmethod
    def error(cls, message: str = "error", code: int = -1) -> 'ApiResponse[T]':
        """失败响应"""
        return cls(code=code, message=message, data=None)


class IdRequest(BaseModel):
    """ID请求模型"""
    id: int = Field(..., description="记录ID")


class BatchIdRequest(BaseModel):
    """批量ID请求模型"""
    ids: List[int] = Field(..., description="记录ID列表")
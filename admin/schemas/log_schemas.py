"""
后台管理系统 - 日志管理模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from common.schemas.response import ORMBaseModel


# ========== 登录日志模型 ==========

class LoginLogResponse(ORMBaseModel):
    """登录日志响应模型"""
    log_id: int = Field(..., description="日志ID")
    tenant_id: int = Field(..., description="租户ID")
    user_id: int = Field(..., description="用户ID")
    account: str = Field(..., description="登录账号")
    login_ip: str = Field(..., description="登录IP")
    login_time: Optional[datetime] = Field(None, description="登录时间")
    login_result: int = Field(..., description="登录结果：1-成功，0-失败")
    error_msg: Optional[str] = Field(None, description="错误信息")
    user_agent: Optional[str] = Field(None, description="客户端信息")


class LoginLogListResponse(ORMBaseModel):
    """登录日志列表响应模型"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    size: int = Field(..., description="每页数量")
    data: List[LoginLogResponse] = Field(..., description="登录日志列表")


# ========== 操作日志模型 ==========

class OperationLogResponse(ORMBaseModel):
    """操作日志响应模型"""
    log_id: int = Field(..., description="日志ID")
    tenant_id: int = Field(..., description="租户ID")
    user_id: int = Field(..., description="操作用户ID")
    user_name: str = Field(..., description="操作用户名")
    module: str = Field(..., description="操作模块")
    action: str = Field(..., description="操作类型")
    request_url: str = Field(..., description="请求URL")
    request_params: Optional[str] = Field(None, description="请求参数")
    response_result: int = Field(..., description="操作结果：1-成功，0-失败")
    error_msg: Optional[str] = Field(None, description="错误信息")
    ip: Optional[str] = Field(..., description="操作IP")
    created_at: Optional[datetime] = Field(None, description="操作时间")


class OperationLogListResponse(ORMBaseModel):
    """操作日志列表响应模型"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    size: int = Field(..., description="每页数量")
    data: List[OperationLogResponse] = Field(..., description="操作日志列表")


# ========== 日志列表模型 ==========

class LogListResponse(ORMBaseModel):
    """日志列表响应模型（通用）"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    size: int = Field(..., description="每页数量")
    data: List[dict] = Field(..., description="日志列表")

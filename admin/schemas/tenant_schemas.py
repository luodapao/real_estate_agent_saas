"""
后台管理系统 - 租户管理模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== 租户管理模型 ==========

class TenantCreate(BaseModel):
    """创建租户请求模型"""
    tenant_name: str = Field(..., description="租户名称", max_length=100)
    tenant_code: str = Field(..., description="租户编码", max_length=50)
    contact_name: Optional[str] = Field(None, description="联系人", max_length=50)
    contact_mobile: Optional[str] = Field(None, description="联系电话", max_length=20)
    contact_email: Optional[str] = Field(None, description="联系邮箱", max_length=100)
    address: Optional[str] = Field(None, description="地址", max_length=200)
    status: Optional[int] = Field(1, description="状态：1-正常，2-禁用")
    expire_date: Optional[str] = Field(None, description="过期日期")
    remark: Optional[str] = Field(None, description="备注")


class TenantUpdate(BaseModel):
    """更新租户请求模型"""
    tenant_name: Optional[str] = Field(None, description="租户名称", max_length=100)
    contact_name: Optional[str] = Field(None, description="联系人", max_length=50)
    contact_mobile: Optional[str] = Field(None, description="联系电话", max_length=20)
    contact_email: Optional[str] = Field(None, description="联系邮箱", max_length=100)
    address: Optional[str] = Field(None, description="地址", max_length=200)
    status: Optional[int] = Field(None, description="状态")
    expire_date: Optional[str] = Field(None, description="过期日期")
    remark: Optional[str] = Field(None, description="备注")


class TenantResponse(BaseModel):
    """租户响应模型"""
    tenant_id: int = Field(..., description="租户ID")
    tenant_name: str = Field(..., description="租户名称")
    tenant_code: str = Field(..., description="租户编码")
    contact_name: Optional[str] = Field(None, description="联系人")
    contact_mobile: Optional[str] = Field(None, description="联系电话")
    contact_email: Optional[str] = Field(None, description="联系邮箱")
    address: Optional[str] = Field(None, description="地址")
    status: int = Field(..., description="状态")
    expire_date: Optional[datetime] = Field(None, description="过期日期")
    remark: Optional[str] = Field(None, description="备注")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class TenantListResponse(BaseModel):
    """租户列表响应模型"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    size: int = Field(..., description="每页数量")
    data: List[TenantResponse] = Field(..., description="租户列表")

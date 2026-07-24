"""
后台管理系统 - 角色管理模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from common.schemas.response import ORMBaseModel


# ========== 角色管理模型 ==========

class RoleCreate(BaseModel):
    """创建角色请求模型"""
    role_name: str = Field(..., description="角色名称", max_length=100)
    role_code: str = Field(..., description="角色编码", max_length=50)
    role_type: Optional[int] = Field(1, description="角色类型：1-系统角色，2-自定义角色")
    status: Optional[int] = Field(1, description="状态：1-正常，2-禁用")
    remark: Optional[str] = Field(None, description="备注")


class RoleUpdate(BaseModel):
    """更新角色请求模型"""
    role_name: Optional[str] = Field(None, description="角色名称", max_length=100)
    role_code: Optional[str] = Field(None, description="角色编码", max_length=50)
    status: Optional[int] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")


class RoleResponse(ORMBaseModel):
    """角色响应模型"""
    role_id: int = Field(..., description="角色ID")
    tenant_id: int = Field(..., description="租户ID")
    role_name: str = Field(..., description="角色名称")
    role_code: str = Field(..., description="角色编码")
    role_type: int = Field(..., description="角色类型")
    status: int = Field(..., description="状态")
    remark: Optional[str] = Field(None, description="备注")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class RoleListResponse(ORMBaseModel):
    """角色列表响应模型"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    size: int = Field(..., description="每页数量")
    data: List[RoleResponse] = Field(..., description="角色列表")


# ========== 角色菜单模型 ==========

class RoleMenuRequest(BaseModel):
    """角色分配菜单请求模型"""
    menu_ids: List[int] = Field(..., description="菜单ID列表")


# ========== 角色用户模型 ==========

class RoleUserRequest(BaseModel):
    """角色分配用户请求模型"""
    user_ids: List[int] = Field(..., description="用户ID列表")

"""
后台管理系统 - 菜单管理模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from common.schemas.response import ORMBaseModel


# ========== 菜单管理模型 ==========

class MenuCreate(BaseModel):
    """创建菜单请求模型"""
    parent_id: Optional[int] = Field(0, description="父菜单ID")
    menu_name: str = Field(..., description="菜单名称", max_length=100)
    menu_code: str = Field(..., description="菜单编码", max_length=100)
    menu_type: int = Field(..., description="菜单类型：1-目录，2-菜单，3-按钮")
    path: Optional[str] = Field(None, description="路由路径", max_length=255)
    component: Optional[str] = Field(None, description="组件路径", max_length=255)
    icon: Optional[str] = Field(None, description="图标", max_length=100)
    sort_order: Optional[int] = Field(0, description="排序号")
    status: Optional[int] = Field(1, description="状态：1-正常，2-禁用")
    permission: Optional[str] = Field(None, description="权限标识", max_length=100)
    remark: Optional[str] = Field(None, description="备注")


class MenuUpdate(BaseModel):
    """更新菜单请求模型"""
    menu_name: Optional[str] = Field(None, description="菜单名称", max_length=100)
    menu_code: Optional[str] = Field(None, description="菜单编码", max_length=100)
    path: Optional[str] = Field(None, description="路由路径", max_length=255)
    component: Optional[str] = Field(None, description="组件路径", max_length=255)
    icon: Optional[str] = Field(None, description="图标", max_length=100)
    sort_order: Optional[int] = Field(None, description="排序号")
    status: Optional[int] = Field(None, description="状态")
    permission: Optional[str] = Field(None, description="权限标识", max_length=100)
    remark: Optional[str] = Field(None, description="备注")


class MenuResponse(ORMBaseModel):
    """菜单响应模型"""
    menu_id: int = Field(..., description="菜单ID")
    tenant_id: int = Field(..., description="租户ID")
    parent_id: int = Field(..., description="父菜单ID")
    menu_name: str = Field(..., description="菜单名称")
    menu_code: str = Field(..., description="菜单编码")
    menu_type: int = Field(..., description="菜单类型")
    path: Optional[str] = Field(None, description="路由路径")
    component: Optional[str] = Field(None, description="组件路径")
    icon: Optional[str] = Field(None, description="图标")
    sort_order: int = Field(..., description="排序号")
    status: int = Field(..., description="状态")
    permission: Optional[str] = Field(None, description="权限标识")
    remark: Optional[str] = Field(None, description="备注")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class MenuListResponse(ORMBaseModel):
    """菜单列表响应模型"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    size: int = Field(..., description="每页数量")
    data: List[MenuResponse] = Field(..., description="菜单列表")


class MenuTreeResponse(ORMBaseModel):
    """菜单树响应模型"""
    menu_id: int = Field(..., description="菜单ID")
    menu_name: str = Field(..., description="菜单名称")
    menu_code: str = Field(..., description="菜单编码")
    menu_type: int = Field(..., description="菜单类型")
    path: Optional[str] = Field(None, description="路由路径")
    component: Optional[str] = Field(None, description="组件路径")
    icon: Optional[str] = Field(None, description="图标")
    sort_order: int = Field(..., description="排序号")
    permission: Optional[str] = Field(None, description="权限标识")
    children: Optional[List['MenuTreeResponse']] = Field(None, description="子菜单")


# ========== 菜单授权模型 ==========

class GrantMenuRequest(BaseModel):
    """角色分配菜单请求模型"""
    menu_ids: List[int] = Field(..., description="菜单ID列表")


# 更新引用
MenuTreeResponse.update_forward_refs()

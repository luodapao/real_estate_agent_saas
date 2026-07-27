"""
后台管理系统 - 用户管理模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from common.schemas.response import ORMBaseModel


# ========== 登录模型 ==========

class LoginRequest(BaseModel):
    """登录请求模型"""
    account: str = Field(..., description="登录账号", max_length=50)
    password: str = Field(..., description="密码", max_length=100)


class LoginResponse(ORMBaseModel):
    """登录响应模型"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(..., description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user: 'UserResponse' = Field(..., description="用户信息")


# ========== 用户管理模型 ==========

class UserCreate(BaseModel):
    """创建用户请求模型"""
    account: str = Field(..., description="登录账号", max_length=50)
    name: str = Field(..., description="用户姓名", max_length=50)
    password: str = Field(..., description="密码", max_length=100)
    mobile: Optional[str] = Field(None, description="手机号", max_length=20)
    email: Optional[str] = Field(None, description="邮箱", max_length=100)
    avatar: Optional[str] = Field(None, description="头像", max_length=500)
    dept_id: Optional[int] = Field(None, description="部门ID")
    status: Optional[int] = Field(1, description="状态：1-正常，2-禁用，3-锁定，4-待审核")
    user_type: Optional[int] = Field(1, description="用户类型：1-内部用户，2-分销渠道后台管理员、3-外部经纪人")
    remark: Optional[str] = Field(None, description="备注")


class UserUpdate(BaseModel):
    """更新用户请求模型"""
    name: Optional[str] = Field(None, description="用户姓名", max_length=50)
    mobile: Optional[str] = Field(None, description="手机号", max_length=20)
    email: Optional[str] = Field(None, description="邮箱", max_length=100)
    avatar: Optional[str] = Field(None, description="头像", max_length=500)
    dept_id: Optional[int] = Field(None, description="部门ID")
    status: Optional[int] = Field(None, description="状态")
    user_type: Optional[int] = Field(None, description="用户类型")
    remark: Optional[str] = Field(None, description="备注")


class UserResponse(ORMBaseModel):
    """用户响应模型"""
    user_id: int = Field(..., description="用户ID")
    tenant_id: int = Field(..., description="租户ID")
    account: str = Field(..., description="登录账号")
    name: str = Field(..., description="用户姓名")
    mobile: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    avatar: Optional[str] = Field(None, description="头像")
    dept_id: Optional[int] = Field(None, description="部门ID")
    status: int = Field(..., description="状态")
    user_type: int = Field(..., description="用户类型")
    remark: Optional[str] = Field(None, description="备注")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class UserDetailResponse(ORMBaseModel):
    """用户详情响应模型"""
    user_id: int = Field(..., description="用户ID")
    tenant_id: int = Field(..., description="租户ID")
    account: str = Field(..., description="登录账号")
    name: str = Field(..., description="用户姓名")
    mobile: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    avatar: Optional[str] = Field(None, description="头像")
    dept_id: Optional[int] = Field(None, description="部门ID")
    status: int = Field(..., description="状态")
    user_type: int = Field(..., description="用户类型")
    last_login_time: Optional[datetime] = Field(None, description="最后登录时间")
    last_login_ip: Optional[str] = Field(None, description="最后登录IP")
    remark: Optional[str] = Field(None, description="备注")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class UserListResponse(BaseModel):
    """用户列表响应模型"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    size: int = Field(..., description="每页数量")
    data: List[UserResponse] = Field(..., description="用户列表")


# ========== 密码管理模型 ==========

class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""
    old_password: str = Field(..., description="旧密码", max_length=100)
    new_password: str = Field(..., description="新密码", max_length=100)


class ResetPasswordRequest(BaseModel):
    """重置密码请求模型"""
    new_password: str = Field(..., description="新密码", max_length=100)


# ========== 角色分配模型 ==========

class GrantRoleRequest(BaseModel):
    """分配角色请求模型"""
    role_ids: List[int] = Field(..., description="角色ID列表")


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str = Field(..., description="刷新令牌")


# 更新引用
LoginResponse.update_forward_refs()

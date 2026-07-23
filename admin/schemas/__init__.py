"""
Admin Schemas - 管理模块数据模型定义
"""
from .user_schemas import (
    UserCreate, UserUpdate, UserResponse, UserDetailResponse,
    LoginRequest, LoginResponse, ChangePasswordRequest,
    ResetPasswordRequest, GrantRoleRequest, UserListResponse,
    RefreshTokenRequest
)
from .role_schemas import (
    RoleCreate, RoleUpdate, RoleResponse, RoleListResponse,
    RoleMenuRequest, RoleUserRequest
)
from .menu_schemas import (
    MenuCreate, MenuUpdate, MenuResponse, MenuListResponse,
    MenuTreeResponse, GrantMenuRequest
)
from .tenant_schemas import (
    TenantCreate, TenantUpdate, TenantResponse, TenantListResponse
)
from .dict_schemas import (
    DictItemCreate, DictItemUpdate, DictItemResponse,
    DictListResponse
)
from .log_schemas import (
    LoginLogResponse, LoginLogListResponse,
    OperationLogResponse, OperationLogListResponse
)

__all__ = [
    # User Schemas
    'UserCreate', 'UserUpdate', 'UserResponse', 'UserDetailResponse',
    'LoginRequest', 'LoginResponse', 'ChangePasswordRequest',
    'ResetPasswordRequest', 'GrantRoleRequest', 'UserListResponse',
    'RefreshTokenRequest',
    # Role Schemas
    'RoleCreate', 'RoleUpdate', 'RoleResponse', 'RoleListResponse',
    'RoleMenuRequest', 'RoleUserRequest',
    # Menu Schemas
    'MenuCreate', 'MenuUpdate', 'MenuResponse', 'MenuListResponse',
    'MenuTreeResponse', 'GrantMenuRequest',
    # Tenant Schemas
    'TenantCreate', 'TenantUpdate', 'TenantResponse', 'TenantListResponse',
    # Dict Schemas
    'DictItemCreate', 'DictItemUpdate', 'DictItemResponse', 'DictListResponse',
    # Log Schemas
    'LoginLogResponse', 'LoginLogListResponse',
    'OperationLogResponse', 'OperationLogListResponse'
]

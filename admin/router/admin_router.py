"""
软商用户路由 - 平台管理入口
业务逻辑：
1. 平台超级管理员（tenant_id=0, user_type=0）：创建租户、管理租户、创建超级用户
2. 认证接口（公开）：登录、登出、刷新令牌、修改密码
3. 不开放自主注册，由超级用户创建账号
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from core.db_base import get_db
from admin.service.user_service import UserService
from admin.service.tenant_service import TenantService
from admin.service.log_service import LogService
from admin.schemas.user_schemas import (
    LoginRequest, LoginResponse, ChangePasswordRequest,
    RefreshTokenRequest, PlatformUserCreate, PlatformUserUpdate,
    UserResponse, UserDetailResponse
)
from admin.schemas.tenant_schemas import (
    TenantCreate, TenantUpdate, TenantResponse, TenantListResponse
)
from config.exception import success_response, error_response
from config.constants import LOGIN_TYPE
from admin.router.auth_deps import require_platform_admin


# ========== 主路由 ==========
router = APIRouter(prefix="/api/admin", tags=["软商用户管理"])


# ========== 认证接口（公开）==========
@router.post("/login", summary="用户登录", response_model=LoginResponse)
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录接口（平台超级管理员和租户管理员通用）"""
    try:
        agent_identifier = request.headers.get('X-Agent-Identifier', 'default')
        ip = request.client.host if request.client else "unknown"
        result = UserService.login(db, login_data.account, login_data.password, agent_identifier, ip)
        
        # 记录登录日志
        LogService.add_login_log(db, result['user']['tenant_id'], result['user']['user_id'], 
                               login_data.account, LOGIN_TYPE['NORMAL'], 1, 
                               "登录成功", ip)
        
        return success_response(data=result)
    except Exception as e:
        # 记录登录失败日志
        ip = request.client.host if request.client else "unknown"
        LogService.add_login_log(db, 0, 0, login_data.account, 
                               LOGIN_TYPE['NORMAL'], 0, str(e), ip)
        return error_response(5000, str(e))


@router.post("/refresh-token", summary="刷新令牌")
async def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """刷新访问令牌接口"""
    try:
        result = UserService.refresh_token(db, data.refresh_token)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@router.post("/logout", summary="用户登出")
async def logout(request: Request, db: Session = Depends(get_db)):
    """用户登出接口"""
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        UserService.logout(db, token)
        return success_response(message="登出成功")
    except Exception as e:
        return error_response(str(e))


@router.post("/change-password", summary="修改密码")
async def change_password(request: Request, data: ChangePasswordRequest, db: Session = Depends(get_db)):
    """修改密码接口（所有已登录用户）"""
    try:
        user_info = request.state.user_info
        UserService.change_password(db, user_info['user_id'], data.old_password, data.new_password)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "POST", 
                                    "/api/admin/change-password", str(data.dict()), 1, 
                                    "修改密码成功", request.client.host if request.client else "unknown")
        
        return success_response(message="密码修改成功")
    except Exception as e:
        return error_response(str(e))


# ========== 平台管理路由组（仅平台超级管理员）==========
platform_router = APIRouter(prefix="/platform", tags=["平台管理"])


# 平台超级用户管理
@platform_router.post("/users", summary="创建平台超级用户", response_model=UserResponse)
async def create_platform_user(request: Request, data: PlatformUserCreate, 
                               db: Session = Depends(get_db), 
                               admin_info: dict = Depends(require_platform_admin)):
    """创建平台超级用户（仅平台超级管理员）"""
    try:
        result = UserService.create_platform_user(db, data)
        
        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'], 
                                    admin_info['login_name'], "系统管理", "POST", 
                                    "/api/admin/platform/users", str(data.model_dump()), 1, 
                                    "创建平台超级用户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="创建成功")
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.get("/users", summary="分页查询平台超级用户列表")
async def get_platform_user_list(request: Request, user_name: Optional[str] = None, 
                                 login_name: Optional[str] = None, status: Optional[int] = None, 
                                 page: int = 1, size: int = 10, db: Session = Depends(get_db),
                                 admin_info: dict = Depends(require_platform_admin)):
    """分页查询平台超级用户列表（仅平台超级管理员）"""
    try:
        result = UserService.get_platform_user_list(db, user_name, login_name, status, page, size)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.get("/users/{user_id}", summary="查询平台超级用户详情", response_model=UserDetailResponse)
async def get_platform_user(user_id: int, db: Session = Depends(get_db),
                            admin_info: dict = Depends(require_platform_admin)):
    """查询平台超级用户详情（仅平台超级管理员）"""
    try:
        result = UserService.get_user(db, user_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.put("/users/{user_id}", summary="更新平台超级用户", response_model=UserResponse)
async def update_platform_user(request: Request, user_id: int, data: PlatformUserUpdate, 
                               db: Session = Depends(get_db),
                               admin_info: dict = Depends(require_platform_admin)):
    """更新平台超级用户（仅平台超级管理员）"""
    try:
        result = UserService.update_platform_user(db, user_id, data)
        
        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'], 
                                    admin_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/platform/users/{user_id}", str(data.model_dump()), 1, 
                                    "更新平台超级用户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="更新成功")
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.delete("/users/{user_id}", summary="删除平台超级用户")
async def delete_platform_user(request: Request, user_id: int, db: Session = Depends(get_db),
                               admin_info: dict = Depends(require_platform_admin)):
    """删除平台超级用户（仅平台超级管理员）"""
    try:
        result = UserService.delete_user(db, user_id)
        
        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'], 
                                    admin_info['login_name'], "系统管理", "DELETE", 
                                    f"/api/admin/platform/users/{user_id}", "", 1, 
                                    "删除平台超级用户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="删除成功")
    except Exception as e:
        return error_response(5000, str(e))


# 租户管理（平台超级管理员管理租户）
@platform_router.post("/tenants", summary="创建租户", response_model=TenantResponse)
async def create_tenant(request: Request, data: TenantCreate, 
                        db: Session = Depends(get_db),
                        admin_info: dict = Depends(require_platform_admin)):
    """创建租户（仅平台超级管理员）"""
    try:
        result = TenantService.create_tenant(db, data)
        
        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'], 
                                    admin_info['login_name'], "系统管理", "POST", 
                                    "/api/admin/platform/tenants", str(data.model_dump()), 1, 
                                    "创建租户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="创建成功")
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.get("/tenants", summary="分页查询租户列表", response_model=TenantListResponse)
async def get_tenant_list(request: Request, tenant_name: Optional[str] = None, 
                          status: Optional[int] = None, page: int = 1, size: int = 10, 
                          db: Session = Depends(get_db),
                          admin_info: dict = Depends(require_platform_admin)):
    """分页查询租户列表（仅平台超级管理员）"""
    try:
        result = TenantService.get_tenant_list(db, tenant_name, status, page, size)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.get("/tenants/{tenant_id}", summary="查询租户详情", response_model=TenantResponse)
async def get_tenant(tenant_id: int, db: Session = Depends(get_db),
                     admin_info: dict = Depends(require_platform_admin)):
    """查询租户详情（仅平台超级管理员）"""
    try:
        result = TenantService.get_tenant(db, tenant_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.put("/tenants/{tenant_id}", summary="更新租户", response_model=TenantResponse)
async def update_tenant(request: Request, tenant_id: int, data: TenantUpdate, 
                        db: Session = Depends(get_db),
                        admin_info: dict = Depends(require_platform_admin)):
    """更新租户（仅平台超级管理员）"""
    try:
        result = TenantService.update_tenant(db, tenant_id, data)
        
        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'], 
                                    admin_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/platform/tenants/{tenant_id}", str(data.model_dump()), 1, 
                                    "更新租户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="更新成功")
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.delete("/tenants/{tenant_id}", summary="删除租户")
async def delete_tenant(request: Request, tenant_id: int, db: Session = Depends(get_db),
                        admin_info: dict = Depends(require_platform_admin)):
    """删除租户（仅平台超级管理员）"""
    try:
        result = TenantService.delete_tenant(db, tenant_id)
        
        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'], 
                                    admin_info['login_name'], "系统管理", "DELETE", 
                                    f"/api/admin/platform/tenants/{tenant_id}", "", 1, 
                                    "删除租户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="删除成功")
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.put("/tenants/{tenant_id}/enable", summary="启用租户", response_model=TenantResponse)
async def enable_tenant(request: Request, tenant_id: int, db: Session = Depends(get_db),
                        admin_info: dict = Depends(require_platform_admin)):
    """启用租户（仅平台超级管理员）"""
    try:
        result = TenantService.enable_tenant(db, tenant_id)
        
        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'], 
                                    admin_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/platform/tenants/{tenant_id}/enable", "", 1, 
                                    "启用租户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="启用成功")
    except Exception as e:
        return error_response(5000, str(e))


@platform_router.put("/tenants/{tenant_id}/disable", summary="禁用租户", response_model=TenantResponse)
async def disable_tenant(request: Request, tenant_id: int, db: Session = Depends(get_db),
                         admin_info: dict = Depends(require_platform_admin)):
    """禁用租户（仅平台超级管理员）"""
    try:
        result = TenantService.disable_tenant(db, tenant_id)
        
        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'], 
                                    admin_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/platform/tenants/{tenant_id}/disable", "", 1, 
                                    "禁用租户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="禁用成功")
    except Exception as e:
        return error_response(5000, str(e))


# 挂载平台管理子路由
router.include_router(platform_router)
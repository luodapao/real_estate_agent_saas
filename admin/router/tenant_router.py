"""
租户管理路由 - 租户超级管理员管理本租户下的用户
业务逻辑：
1. 租户超级管理员（tenant_id>0, user_type=1）：管理本租户下的用户
2. 不开放自主注册，由租户超级管理员创建账号
3. 预管理接口（公开）：生成一次性管理票据 superuserControlTicket，无长轮询
"""
import uuid
import json
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from core.db_base import get_db
from core.redis_base import redis_client
from admin.service.user_service import UserService
from admin.service.log_service import LogService
from admin.service.tenant_service import TenantService
from admin.schemas.user_schemas import (
    UserCreate, UserUpdate, UserResponse,
    UserDetailResponse, UserListResponse, ResetPasswordRequest,
    GrantRoleRequest,
    PrepareSuperuserControlReq, PrepareSuperuserControlResp,
    VerifySuperuserControlReq
)
from config.exception import success_response, error_response
from core.auth_deps import require_tenant_admin


# ========== 租户管理路由（租户超级管理员）==========
router = APIRouter(prefix="/api/admin/tenant", tags=["租户管理"])


# ========== 预管理接口（公开，供 Agent 调用生成管理票据）==========

@router.post("/prepare-superuser-control", summary="预管理（生成一次性超级用户管理票据）",
             response_model=PrepareSuperuserControlResp)
async def prepare_superuser_control(req: PrepareSuperuserControlReq, db: Session = Depends(get_db)):
    """预管理接口：生成一次性票据 superuserControlTicket（UUID），返回管理页URL
    与 prepare-login 不同：不使用长轮询，用户通过 Agent 下发的链接直接在浏览器操作管理页"""
    try:
        # 校验租户存在并获取租户名（用于管理页标题展示）
        tenant = TenantService.get_tenant(db, req.tenantId)
        tenant_name = tenant.tenant_name if tenant else f"租户{req.tenantId}"

        ticket = str(uuid.uuid4())
        expire_seconds = req.expireSeconds or 600

        ticket_data = {
            "tenantId": req.tenantId,
            "tenantName": tenant_name,
            "mcpSessionId": req.mcpSessionId,
            "status": "pending",
            "token": None
        }

        redis_client.setex(
            f"superuser:ticket:{ticket}",
            expire_seconds,
            json.dumps(ticket_data)
        )

        # 公网地址，默认端口8000
        control_url = f"http://14.103.221.98:8000/superuser-control?ticket={ticket}"

        return success_response(data={
            "controlUrl": control_url,
            "ticket": ticket
        })
    except Exception as e:
        return error_response(5000, str(e))


@router.post("/verify-superuser-control", summary="校验管理票据")
async def verify_superuser_control(req: VerifySuperuserControlReq):
    """校验管理票据，返回租户信息（用于管理页展示租户名、判断票据有效性）"""
    try:
        raw = redis_client.get(f"superuser:ticket:{req.ticket}")
        if not raw:
            return error_response(4000, "链接已过期，请重新在AI窗口发起管理")
        ticket_data = json.loads(raw)
        return success_response(data=ticket_data)
    except Exception as e:
        return error_response(5000, str(e))


# 租户内用户管理
@router.post("/users", summary="创建租户用户", response_model=UserResponse)
async def create_tenant_user(request: Request, data: UserCreate, 
                             db: Session = Depends(get_db),
                             admin_info: dict = Depends(require_tenant_admin)):
    """创建租户用户（仅租户超级管理员）"""
    try:
        result = UserService.create_user(db, admin_info['tenant_id'], data)
        
        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'], 
                                    admin_info['login_name'], "系统管理", "POST", 
                                    "/api/admin/tenant/users", str(data.model_dump()), 1, 
                                    "创建租户用户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="创建成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.get("/users", summary="分页查询租户用户列表")
async def get_tenant_user_list(request: Request, user_name: Optional[str] = None, 
                               login_name: Optional[str] = None, status: Optional[int] = None, 
                               page: int = 1, size: int = 10, db: Session = Depends(get_db),
                               admin_info: dict = Depends(require_tenant_admin)):
    """分页查询租户用户列表（仅租户超级管理员）"""
    try:
        result = UserService.get_user_list(db, admin_info['tenant_id'], user_name, login_name, status, page, size)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@router.get("/users/{user_id}", summary="查询租户用户详情", response_model=UserDetailResponse)
async def get_tenant_user(user_id: int, db: Session = Depends(get_db),
                          admin_info: dict = Depends(require_tenant_admin)):
    """查询租户用户详情（仅租户超级管理员）"""
    try:
        result = UserService.get_user(db, user_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@router.put("/users/{user_id}", summary="更新租户用户", response_model=UserResponse)
async def update_tenant_user(request: Request, user_id: int, data: UserUpdate, 
                             db: Session = Depends(get_db),
                             admin_info: dict = Depends(require_tenant_admin)):
    """更新租户用户（仅租户超级管理员）"""
    try:
        result = UserService.update_user(db, user_id, data)
        
        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'], 
                                    admin_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/tenant/users/{user_id}", str(data.model_dump()), 1, 
                                    "更新租户用户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="更新成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.delete("/users/{user_id}", summary="删除租户用户")
async def delete_tenant_user(request: Request, user_id: int, db: Session = Depends(get_db),
                             admin_info: dict = Depends(require_tenant_admin)):
    """删除租户用户（仅租户超级管理员）"""
    try:
        result = UserService.delete_user(db, user_id)
        
        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'], 
                                    admin_info['login_name'], "系统管理", "DELETE", 
                                    f"/api/admin/tenant/users/{user_id}", "", 1, 
                                    "删除租户用户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="删除成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.put("/users/{user_id}/reset-password", summary="重置租户用户密码")
async def reset_tenant_user_password(request: Request, user_id: int, data: ResetPasswordRequest, 
                                     db: Session = Depends(get_db),
                                     admin_info: dict = Depends(require_tenant_admin)):
    """重置租户用户密码（仅租户超级管理员）"""
    try:
        UserService.reset_password(db, user_id, data)
        
        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'], 
                                    admin_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/tenant/users/{user_id}/reset-password", str(data.model_dump()), 1, 
                                    "重置租户用户密码成功", request.client.host if request.client else "unknown")
        
        return success_response(message="密码重置成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.put("/users/{user_id}/unlock", summary="解锁租户用户")
async def unlock_tenant_user(request: Request, user_id: int, db: Session = Depends(get_db),
                             admin_info: dict = Depends(require_tenant_admin)):
    """解锁租户用户（仅租户超级管理员）"""
    try:
        result = UserService.unlock_user(db, user_id)
        
        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'], 
                                    admin_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/tenant/users/{user_id}/unlock", "", 1, 
                                    "解锁租户用户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="解锁成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.post("/users/{user_id}/grant-role", summary="分配租户用户角色")
async def grant_tenant_user_role(request: Request, user_id: int, data: GrantRoleRequest, 
                                 db: Session = Depends(get_db),
                                 admin_info: dict = Depends(require_tenant_admin)):
    """给租户用户分配角色（仅租户超级管理员）"""
    try:
        result = UserService.grant_role(db, admin_info['tenant_id'], user_id, data)
        
        # 记录操作日志
        LogService.add_operation_log(db, admin_info['tenant_id'], admin_info['user_id'], 
                                    admin_info['login_name'], "系统管理", "POST", 
                                    f"/api/admin/tenant/users/{user_id}/grant-role", str(data.model_dump()), 1, 
                                    "分配租户用户角色成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="分配成功")
    except Exception as e:
        return error_response(5000, str(e))
"""
用户管理路由
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from core.db_base import get_db
from admin.service.user_service import UserService
from admin.service.log_service import LogService
from admin.schemas.user_schemas import (
    UserCreate, UserUpdate, UserResponse, UserDetailResponse,
    UserListResponse, ResetPasswordRequest, GrantRoleRequest
)
from config.exception import success_response, error_response

router = APIRouter(prefix="/user", tags=["用户管理"])


@router.get("/{user_id}", summary="查询用户详情", response_model=UserDetailResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """查询用户详情接口"""
    try:
        result = UserService.get_user(db, user_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@router.get("/", summary="分页查询用户列表")
async def get_user_list(request: Request, user_name: Optional[str] = None, 
                       login_name: Optional[str] = None, status: Optional[int] = None, 
                       page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    """分页查询用户列表接口"""
    try:
        user_info = request.state.user_info
        result = UserService.get_user_list(db, user_info['tenant_id'], user_name, login_name, status, page, size)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@router.post("/", summary="创建用户", response_model=UserResponse)
async def create_user(request: Request, data: UserCreate, db: Session = Depends(get_db)):
    """创建用户接口（支持公开注册和管理员创建）"""
    try:
        user_info = request.state.user_info
        
        # 获取租户ID（公开注册时使用默认租户ID 1）
        tenant_id = user_info['tenant_id'] or 1
        
        result = UserService.create_user(db, tenant_id, data)
        
        # 只有登录用户创建时才记录操作日志
        if user_info['user_id']:
            LogService.add_operation_log(db, tenant_id, user_info['user_id'], 
                                        user_info['login_name'], "系统管理", "POST", 
                                        "/api/admin/user", str(data.model_dump()), 1, 
                                        "创建用户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="创建成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.put("/{user_id}", summary="更新用户", response_model=UserResponse)
async def update_user(request: Request, user_id: int, data: UserUpdate, 
                     db: Session = Depends(get_db)):
    """更新用户接口"""
    try:
        user_info = request.state.user_info
        result = UserService.update_user(db, user_id, data)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/user/{user_id}", str(data.model_dump()), 1, 
                                    "更新用户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="更新成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    """删除用户接口"""
    try:
        user_info = request.state.user_info
        result = UserService.delete_user(db, user_id)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "DELETE", 
                                    f"/api/admin/user/{user_id}", "", 1, 
                                    "删除用户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="删除成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.put("/{user_id}/reset-password", summary="重置密码")
async def reset_password(request: Request, user_id: int, data: ResetPasswordRequest, 
                        db: Session = Depends(get_db)):
    """重置密码接口"""
    try:
        user_info = request.state.user_info
        UserService.reset_password(db, user_id, data)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/user/{user_id}/reset-password", str(data.model_dump()), 1, 
                                    "重置密码成功", request.client.host if request.client else "unknown")
        
        return success_response(message="密码重置成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.put("/{user_id}/unlock", summary="解锁用户")
async def unlock_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    """解锁用户接口"""
    try:
        user_info = request.state.user_info
        result = UserService.unlock_user(db, user_id)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/user/{user_id}/unlock", "", 1, 
                                    "解锁用户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="解锁成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.post("/{user_id}/grant-role", summary="分配角色")
async def grant_role(request: Request, user_id: int, data: GrantRoleRequest, 
                    db: Session = Depends(get_db)):
    """给用户分配角色接口"""
    try:
        user_info = request.state.user_info
        result = UserService.grant_role(db, user_info['tenant_id'], user_id, data)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "POST", 
                                    f"/api/admin/user/{user_id}/grant-role", str(data.model_dump()), 1, 
                                    "分配角色成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="分配成功")
    except Exception as e:
        return error_response(5000, str(e))

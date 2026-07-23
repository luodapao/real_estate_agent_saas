"""
登录模块路由
"""
from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
from core.db_base import get_db
from admin.service.user_service import UserService
from admin.service.log_service import LogService
from admin.schemas.user_schemas import (
    LoginRequest, LoginResponse, ChangePasswordRequest,
    RefreshTokenRequest
)
from config.exception import success_response, error_response
from config.constants import LOGIN_TYPE


router = APIRouter(tags=["登录模块"])


@router.post("/login", summary="用户登录", response_model=LoginResponse)
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录接口"""
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
    """修改密码接口"""
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
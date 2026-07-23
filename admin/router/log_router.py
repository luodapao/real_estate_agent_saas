"""
日志管理路由
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from core.db_base import get_db
from admin.service.log_service import LogService
from config.exception import success_response, error_response

router = APIRouter(prefix="/api/admin/log", tags=["日志管理"])


@router.get("/login", summary="分页查询登录日志")
async def get_login_log_list(request: Request, user_id: Optional[int] = None, 
                            login_name: Optional[str] = None, status: Optional[int] = None, 
                            start_time: Optional[str] = None, end_time: Optional[str] = None,
                            page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    """分页查询登录日志接口"""
    try:
        user_info = request.state.user_info
        result = LogService.get_login_log_list(db, user_info['tenant_id'], user_id, login_name, 
                                             status, start_time, end_time, page, size)
        return success_response(data=result)
    except Exception as e:
        return error_response(str(e))


@router.get("/operation", summary="分页查询操作日志")
async def get_operation_log_list(request: Request, user_id: Optional[int] = None, 
                                user_name: Optional[str] = None, module: Optional[str] = None,
                                status: Optional[int] = None, start_time: Optional[str] = None, 
                                end_time: Optional[str] = None, page: int = 1, size: int = 10, 
                                db: Session = Depends(get_db)):
    """分页查询操作日志接口"""
    try:
        user_info = request.state.user_info
        result = LogService.get_operation_log_list(db, user_info['tenant_id'], user_id, user_name, 
                                                 module, status, start_time, end_time, page, size)
        return success_response(data=result)
    except Exception as e:
        return error_response(str(e))
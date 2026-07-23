"""
角色管理路由
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from core.db_base import get_db
from admin.service.role_service import RoleService
from admin.service.log_service import LogService
from admin.schemas.role_schemas import (
    RoleCreate, RoleUpdate, RoleResponse, RoleListResponse
)
from config.exception import success_response, error_response

router = APIRouter(prefix="/role", tags=["角色管理"])


@router.get("/{role_id}", summary="查询角色详情", response_model=RoleResponse)
async def get_role(role_id: int, db: Session = Depends(get_db)):
    """查询角色详情接口"""
    try:
        result = RoleService.get_role(db, role_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@router.get("/", summary="分页查询角色列表")
async def get_role_list(request: Request, role_name: Optional[str] = None, 
                       status: Optional[int] = None, page: int = 1, size: int = 10, 
                       db: Session = Depends(get_db)):
    """分页查询角色列表接口"""
    try:
        user_info = request.state.user_info
        result = RoleService.get_role_list(db, user_info['tenant_id'], role_name, status, page, size)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@router.post("/", summary="创建角色", response_model=RoleResponse)
async def create_role(request: Request, data: RoleCreate, db: Session = Depends(get_db)):
    """创建角色接口"""
    try:
        user_info = request.state.user_info
        result = RoleService.create_role(db, user_info['tenant_id'], data)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "POST", 
                                    "/api/admin/role", str(data.model_dump()), 1, 
                                    "创建角色成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="创建成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.put("/{role_id}", summary="更新角色", response_model=RoleResponse)
async def update_role(request: Request, role_id: int, data: RoleUpdate, 
                     db: Session = Depends(get_db)):
    """更新角色接口"""
    try:
        user_info = request.state.user_info
        result = RoleService.update_role(db, role_id, data)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/role/{role_id}", str(data.model_dump()), 1, 
                                    "更新角色成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="更新成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.delete("/{role_id}", summary="删除角色")
async def delete_role(request: Request, role_id: int, db: Session = Depends(get_db)):
    """删除角色接口"""
    try:
        user_info = request.state.user_info
        result = RoleService.delete_role(db, role_id)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "DELETE", 
                                    f"/api/admin/role/{role_id}", "", 1, 
                                    "删除角色成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="删除成功")
    except Exception as e:
        return error_response(5000, str(e))

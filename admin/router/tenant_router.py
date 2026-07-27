"""
租户管理路由
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from core.db_base import get_db
from admin.service.tenant_service import TenantService
from admin.service.log_service import LogService
from admin.schemas.tenant_schemas import (
    TenantCreate, TenantUpdate, TenantResponse, TenantListResponse
)
from config.exception import success_response, error_response
from config.constants import CODE, MESSAGE

router = APIRouter(prefix="/api/admin/tenant", tags=["租户管理"])


def check_system_admin(user_info: dict):
    """检查是否为系统管理员（tenant_id=0 表示系统管理员）"""
    if user_info.get('tenant_id') != 0:
        raise PermissionError(MESSAGE['PERMISSION_DENIED'])


@router.get("/{tenant_id}", summary="查询租户详情", response_model=TenantResponse)
async def get_tenant(request: Request, tenant_id: int, db: Session = Depends(get_db)):
    """查询租户详情接口（仅系统管理员）"""
    try:
        user_info = request.state.user_info
        check_system_admin(user_info)
        
        result = TenantService.get_tenant(db, tenant_id)
        return success_response(data=result)
    except PermissionError as e:
        return error_response(CODE['PERMISSION_DENIED'], str(e))
    except Exception as e:
        return error_response(5000, str(e))


@router.get("/", summary="分页查询租户列表", response_model=TenantListResponse)
async def get_tenant_list(request: Request, tenant_name: Optional[str] = None, 
                         status: Optional[int] = None, page: int = 1, size: int = 10, 
                         db: Session = Depends(get_db)):
    """分页查询租户列表接口（仅系统管理员）"""
    try:
        user_info = request.state.user_info
        check_system_admin(user_info)
        
        result = TenantService.get_tenant_list(db, tenant_name, status, page, size)
        return success_response(data=result)
    except PermissionError as e:
        return error_response(CODE['PERMISSION_DENIED'], str(e))
    except Exception as e:
        return error_response(5000, str(e))


@router.post("/", summary="创建租户", response_model=TenantResponse)
async def create_tenant(request: Request, data: TenantCreate, db: Session = Depends(get_db)):
    """创建租户接口（仅系统管理员）"""
    try:
        user_info = request.state.user_info
        check_system_admin(user_info)
        
        result = TenantService.create_tenant(db, data)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "POST", 
                                    "/api/admin/tenant", str(data.model_dump()), 1, 
                                    "创建租户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="创建成功")
    except PermissionError as e:
        return error_response(CODE['PERMISSION_DENIED'], str(e))
    except Exception as e:
        return error_response(5000, str(e))


@router.put("/{tenant_id}", summary="更新租户", response_model=TenantResponse)
async def update_tenant(request: Request, tenant_id: int, data: TenantUpdate, 
                       db: Session = Depends(get_db)):
    """更新租户接口（仅系统管理员）"""
    try:
        user_info = request.state.user_info
        check_system_admin(user_info)
        
        result = TenantService.update_tenant(db, tenant_id, data)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/tenant/{tenant_id}", str(data.model_dump()), 1, 
                                    "更新租户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="更新成功")
    except PermissionError as e:
        return error_response(CODE['PERMISSION_DENIED'], str(e))
    except Exception as e:
        return error_response(5000, str(e))


@router.delete("/{tenant_id}", summary="删除租户")
async def delete_tenant(request: Request, tenant_id: int, db: Session = Depends(get_db)):
    """删除租户接口（仅系统管理员）"""
    try:
        user_info = request.state.user_info
        check_system_admin(user_info)
        
        result = TenantService.delete_tenant(db, tenant_id)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "DELETE", 
                                    f"/api/admin/tenant/{tenant_id}", "", 1, 
                                    "删除租户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="删除成功")
    except PermissionError as e:
        return error_response(CODE['PERMISSION_DENIED'], str(e))
    except Exception as e:
        return error_response(5000, str(e))


@router.put("/{tenant_id}/enable", summary="启用租户", response_model=TenantResponse)
async def enable_tenant(request: Request, tenant_id: int, db: Session = Depends(get_db)):
    """启用租户接口（仅系统管理员）"""
    try:
        user_info = request.state.user_info
        check_system_admin(user_info)
        
        result = TenantService.enable_tenant(db, tenant_id)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/tenant/{tenant_id}/enable", "", 1, 
                                    "启用租户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="启用成功")
    except PermissionError as e:
        return error_response(CODE['PERMISSION_DENIED'], str(e))
    except Exception as e:
        return error_response(5000, str(e))


@router.put("/{tenant_id}/disable", summary="禁用租户", response_model=TenantResponse)
async def disable_tenant(request: Request, tenant_id: int, db: Session = Depends(get_db)):
    """禁用租户接口（仅系统管理员）"""
    try:
        user_info = request.state.user_info
        check_system_admin(user_info)
        
        result = TenantService.disable_tenant(db, tenant_id)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/tenant/{tenant_id}/disable", "", 1, 
                                    "禁用租户成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="禁用成功")
    except PermissionError as e:
        return error_response(CODE['PERMISSION_DENIED'], str(e))
    except Exception as e:
        return error_response(5000, str(e))
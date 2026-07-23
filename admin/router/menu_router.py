"""
菜单管理路由
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from core.db_base import get_db
from admin.service.menu_service import MenuService
from admin.service.log_service import LogService
from admin.schemas.menu_schemas import (
    MenuCreate, MenuUpdate, MenuResponse, MenuListResponse,
    MenuTreeResponse, GrantMenuRequest
)
from config.exception import success_response, error_response

router = APIRouter(prefix="/api/admin/menu", tags=["菜单管理"])


@router.get("/{menu_id}", summary="查询菜单详情", response_model=MenuResponse)
async def get_menu(menu_id: int, db: Session = Depends(get_db)):
    """查询菜单详情接口"""
    try:
        result = MenuService.get_menu(db, menu_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@router.get("/", summary="查询菜单列表", response_model=MenuListResponse)
async def get_menu_list(request: Request, menu_name: Optional[str] = None, 
                       menu_type: Optional[int] = None, status: Optional[int] = None, 
                       db: Session = Depends(get_db)):
    """查询菜单列表接口"""
    try:
        user_info = request.state.user_info
        result = MenuService.get_menu_list(db, user_info['tenant_id'], menu_name, menu_type, status)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@router.get("/tree", summary="获取菜单树")
async def get_menu_tree(request: Request, db: Session = Depends(get_db)):
    """获取菜单树结构接口"""
    try:
        user_info = request.state.user_info
        result = MenuService.get_menu_tree(db, user_info['tenant_id'])
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@router.post("/", summary="创建菜单", response_model=MenuResponse)
async def create_menu(request: Request, data: MenuCreate, db: Session = Depends(get_db)):
    """创建菜单接口"""
    try:
        user_info = request.state.user_info
        result = MenuService.create_menu(db, user_info['tenant_id'], data)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "POST", 
                                    "/api/admin/menu", str(data.model_dump()), 1, 
                                    "创建菜单成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="创建成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.put("/{menu_id}", summary="更新菜单", response_model=MenuResponse)
async def update_menu(request: Request, menu_id: int, data: MenuUpdate, 
                     db: Session = Depends(get_db)):
    """更新菜单接口"""
    try:
        user_info = request.state.user_info
        result = MenuService.update_menu(db, menu_id, data)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/menu/{menu_id}", str(data.model_dump()), 1, 
                                    "更新菜单成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="更新成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.delete("/{menu_id}", summary="删除菜单")
async def delete_menu(request: Request, menu_id: int, db: Session = Depends(get_db)):
    """删除菜单接口"""
    try:
        user_info = request.state.user_info
        result = MenuService.delete_menu(db, menu_id)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "DELETE", 
                                    f"/api/admin/menu/{menu_id}", "", 1, 
                                    "删除菜单成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="删除成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.post("/role/{role_id}/grant", summary="角色授权")
async def grant_menu_to_role(request: Request, role_id: int, data: GrantMenuRequest, 
                            db: Session = Depends(get_db)):
    """给角色分配菜单权限接口"""
    try:
        user_info = request.state.user_info
        MenuService.grant_menu_to_role(db, user_info['tenant_id'], role_id, data.menu_ids)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "POST", 
                                    f"/api/admin/menu/role/{role_id}/grant", str(data.model_dump()), 1, 
                                    "角色授权成功", request.client.host if request.client else "unknown")
        
        return success_response(message="授权成功")
    except Exception as e:
        return error_response(5000, str(e))
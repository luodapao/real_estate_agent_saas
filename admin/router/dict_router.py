"""
数据字典路由
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from core.db_base import get_db
from admin.service.dict_service import DictService
from admin.service.log_service import LogService
from admin.schemas.dict_schemas import (
    DictItemCreate, DictItemUpdate, DictItemResponse
)
from config.exception import success_response, error_response

router = APIRouter(prefix="/api/admin/dict", tags=["数据字典"])


@router.get("/{dict_id}", summary="查询字典详情", response_model=DictItemResponse)
async def get_dict(dict_id: int, db: Session = Depends(get_db)):
    """查询字典详情接口"""
    try:
        result = DictService.get_dict(db, dict_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@router.get("/type/{dict_type}", summary="根据类型查询字典")
async def get_dict_by_type(request: Request, dict_type: str, db: Session = Depends(get_db)):
    """根据字典类型查询字典列表接口"""
    try:
        user_info = request.state.user_info
        result = DictService.get_dict_by_type(db, user_info['tenant_id'], dict_type)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@router.get("/", summary="分页查询字典列表")
async def get_dict_list(request: Request, dict_type: Optional[str] = None, 
                       dict_label: Optional[str] = None, status: Optional[int] = None, 
                       page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    """分页查询字典列表接口"""
    try:
        user_info = request.state.user_info
        result = DictService.get_dict_list(db, user_info['tenant_id'], dict_type, dict_label, status, page, size)
        return success_response(data=result)
    except Exception as e:
        return error_response(5000, str(e))


@router.post("/", summary="创建字典", response_model=DictItemResponse)
async def create_dict(request: Request, data: DictItemCreate, db: Session = Depends(get_db)):
    """创建字典接口"""
    try:
        user_info = request.state.user_info
        result = DictService.create_dict(db, user_info['tenant_id'], data)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "POST", 
                                    "/api/admin/dict", str(data.model_dump()), 1, 
                                    "创建字典成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="创建成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.put("/{dict_id}", summary="更新字典", response_model=DictItemResponse)
async def update_dict(request: Request, dict_id: int, data: DictItemUpdate, 
                     db: Session = Depends(get_db)):
    """更新字典接口"""
    try:
        user_info = request.state.user_info
        result = DictService.update_dict(db, dict_id, data)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "PUT", 
                                    f"/api/admin/dict/{dict_id}", str(data.model_dump()), 1, 
                                    "更新字典成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="更新成功")
    except Exception as e:
        return error_response(5000, str(e))


@router.delete("/{dict_id}", summary="删除字典")
async def delete_dict(request: Request, dict_id: int, db: Session = Depends(get_db)):
    """删除字典接口"""
    try:
        user_info = request.state.user_info
        result = DictService.delete_dict(db, dict_id)
        
        # 记录操作日志
        LogService.add_operation_log(db, user_info['tenant_id'], user_info['user_id'], 
                                    user_info['login_name'], "系统管理", "DELETE", 
                                    f"/api/admin/dict/{dict_id}", "", 1, 
                                    "删除字典成功", request.client.host if request.client else "unknown")
        
        return success_response(data=result, message="删除成功")
    except Exception as e:
        return error_response(5000, str(e))
﻿"""
房地产SaaS财务管理系统 - 财务审计追溯模块路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from core.db_base import get_finance_db
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from finance.service.audit_service import AuditService
from finance.schemas.audit_schemas import (
    OperateLogCreate,
    OperateLogUpdate,
)
from finance.schemas.base_schemas import PageRequest

router = APIRouter(prefix="/audit", tags=["财务审计追溯"])


# ========== 财务操作审计日志接口 ==========

@router.post("/operate-log/create")
async def create_operate_log(
    data: OperateLogCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建财务操作审计日志"""
    try:
        result = AuditService.create_operate_log(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="操作审计日志创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/operate-log/list")
async def list_operate_logs(
    page: int = 1,
    page_size: int = 20,
    biz_module: Optional[int] = None,
    operate_type: Optional[int] = None,
    biz_type: Optional[int] = None,
    biz_id: Optional[int] = None,
    voucher_id: Optional[int] = None,
    operate_user_id: Optional[int] = None,
    operate_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取财务操作审计日志列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        filters = {}
        if biz_module:
            filters['biz_module'] = biz_module
        if operate_type:
            filters['operate_type'] = operate_type
        if biz_type:
            filters['biz_type'] = biz_type
        if biz_id:
            filters['biz_id'] = biz_id
        if voucher_id:
            filters['voucher_id'] = voucher_id
        if operate_user_id:
            filters['operate_user_id'] = operate_user_id
        if operate_status is not None:
            filters['operate_status'] = operate_status
        result = AuditService.list_operate_logs(db, current_user['tenant'], page_request, filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/operate-log/{id}")
async def get_operate_log(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取财务操作审计日志详情"""
    try:
        result = AuditService.get_operate_log(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "操作审计日志不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/operate-log/{id}")
async def update_operate_log(
    id: int,
    data: OperateLogUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新财务操作审计日志"""
    try:
        result = AuditService.update_operate_log(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="操作审计日志更新成功")
        return error_response(-1, "操作审计日志不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/operate-log/{id}")
async def delete_operate_log(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除财务操作审计日志"""
    try:
        success = AuditService.delete_operate_log(db, current_user['tenant'], id)
        if success:
            return success_response(message="操作审计日志删除成功")
        return error_response(-1, "操作审计日志不存在")
    except Exception as e:
        return error_response(-1, str(e))

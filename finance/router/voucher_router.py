"""
房地产SaaS财务管理系统 - 会计凭证模块路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from core.db_base import get_finance_db
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from finance.service.voucher_service import VoucherService
from finance.schemas.voucher_schemas import (
    VoucherCreate,
    VoucherUpdate,
    VoucherItemCreate,
    VoucherItemUpdate,
    VoucherAudit,
    VoucherRedFlush,
)
from finance.schemas.base_schemas import PageRequest

router = APIRouter(prefix="/voucher", tags=["会计凭证"])


# ========== 会计凭证主表接口 ==========

@router.post("/create")
async def create_voucher(
    data: VoucherCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建会计凭证"""
    try:
        result = VoucherService.create_voucher(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="会计凭证创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/audit")
async def audit_voucher(
    data: VoucherAudit,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """审核会计凭证"""
    try:
        result = VoucherService.audit_voucher(db, current_user['tenant'], data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="会计凭证审核完成")
        return error_response(-1, "会计凭证不存在或已作废/红冲")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/red-flush")
async def red_flush_voucher(
    data: VoucherRedFlush,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """红字冲销会计凭证"""
    try:
        result = VoucherService.red_flush_voucher(db, current_user['tenant'], data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="会计凭证红冲成功")
        return error_response(-1, "会计凭证不存在或已作废/红冲")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/list")
async def list_vouchers(
    page: int = 1,
    page_size: int = 20,
    voucher_type: Optional[int] = None,
    voucher_date: Optional[str] = None,
    voucher_status: Optional[int] = None,
    source_type: Optional[int] = None,
    is_red_flush: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取会计凭证列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        filters = {}
        if voucher_type:
            filters['voucher_type'] = voucher_type
        if voucher_date:
            filters['voucher_date'] = voucher_date
        if voucher_status:
            filters['voucher_status'] = voucher_status
        if source_type:
            filters['source_type'] = source_type
        if is_red_flush is not None:
            filters['is_red_flush'] = is_red_flush
        result = VoucherService.list_vouchers(db, current_user['tenant'], page_request, filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/{id}")
async def get_voucher(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取会计凭证详情"""
    try:
        result = VoucherService.get_voucher(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "会计凭证不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/{id}/with-items")
async def get_voucher_with_items(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取会计凭证及明细"""
    try:
        result = VoucherService.get_voucher_with_items(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "会计凭证不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/{id}")
async def update_voucher(
    id: int,
    data: VoucherUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新会计凭证"""
    try:
        result = VoucherService.update_voucher(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="会计凭证更新成功")
        return error_response(-1, "会计凭证不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/{id}")
async def delete_voucher(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除会计凭证"""
    try:
        success = VoucherService.delete_voucher(db, current_user['tenant'], id)
        if success:
            return success_response(message="会计凭证删除成功")
        return error_response(-1, "会计凭证不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 凭证明细接口 ==========

@router.post("/item/create")
async def create_voucher_item(
    data: VoucherItemCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建凭证明细"""
    try:
        result = VoucherService.create_voucher_item(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="凭证明细创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/item/list")
async def list_voucher_items(
    page: int = 1,
    page_size: int = 20,
    voucher_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    subject_type: Optional[int] = None,
    project_id: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取凭证明细列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        filters = {}
        if voucher_id:
            filters['voucher_id'] = voucher_id
        if subject_id:
            filters['subject_id'] = subject_id
        if subject_type:
            filters['subject_type'] = subject_type
        if project_id:
            filters['project_id'] = project_id
        result = VoucherService.list_voucher_items(db, current_user['tenant'], page_request, filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/item/{id}")
async def get_voucher_item(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取凭证明细详情"""
    try:
        result = VoucherService.get_voucher_item(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "凭证明细不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/item/{id}")
async def update_voucher_item(
    id: int,
    data: VoucherItemUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新凭证明细"""
    try:
        result = VoucherService.update_voucher_item(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="凭证明细更新成功")
        return error_response(-1, "凭证明细不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/item/{id}")
async def delete_voucher_item(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除凭证明细"""
    try:
        success = VoucherService.delete_voucher_item(db, current_user['tenant'], id)
        if success:
            return success_response(message="凭证明细删除成功")
        return error_response(-1, "凭证明细不存在")
    except Exception as e:
        return error_response(-1, str(e))

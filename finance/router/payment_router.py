﻿"""
房地产SaaS财务管理系统 - 房款收支模块路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from core.db_base import get_finance_db
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from finance.service.payment_service import PaymentService
from finance.schemas.payment_schemas import (
    InstallmentPlanCreate,
    InstallmentPlanUpdate,
    PriceDiffCreate,
    PriceDiffUpdate,
    ReceiptRecordCreate,
    ReceiptRecordUpdate,
    RefundRecordCreate,
    RefundRecordUpdate,
    DepositAccountCreate,
    DepositAccountUpdate,
)
from finance.schemas.base_schemas import PageRequest

router = APIRouter(prefix="/payment", tags=["房款收支"])


# ========== 分期回款计划接口 ==========

@router.post("/installment/create")
async def create_installment_plan(
    data: InstallmentPlanCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建分期回款计划"""
    try:
        result = PaymentService.create_installment_plan(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result, message="分期回款计划创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/installment/list")
async def list_installment_plans(
    page: int = 1,
    page_size: int = 20,
    contract_id: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取分期回款计划列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = PaymentService.list_installment_plans(db, current_user['tenant'], page_request)
        return success_response(data={
            'total': result.total,
            'page': result.page,
            'page_size': result.size,
            'items': [item.model_dump(mode='json') for item in result.data]
        })
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/installment/{id}")
async def get_installment_plan(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取分期回款计划详情"""
    try:
        result = PaymentService.get_installment_plan(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "分期回款计划不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/installment/{id}")
async def update_installment_plan(
    id: int,
    data: InstallmentPlanUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新分期回款计划"""
    try:
        result = PaymentService.update_installment_plan(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="分期回款计划更新成功")
        return error_response(-1, "分期回款计划不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/installment/{id}")
async def delete_installment_plan(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除分期回款计划"""
    try:
        success = PaymentService.delete_installment_plan(db, current_user['tenant'], id)
        if success:
            return success_response(message="分期回款计划删除成功")
        return error_response(-1, "分期回款计划不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 面积差价调整接口 ==========

@router.post("/adjustment/create")
async def create_area_price_adjustment(
    data: PriceDiffCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建面积差价调整"""
    try:
        result = PaymentService.create_price_diff(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="面积差价调整创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/adjustment/list")
async def list_area_price_adjustments(
    page: int = 1,
    page_size: int = 20,
    contract_id: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取面积差价调整列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = PaymentService.list_area_price_adjustments(db, current_user['tenant'], page_request)
        return success_response(data={
            'total': result.total,
            'page': result.page,
            'page_size': result.size,
            'items': [item.model_dump(mode='json') for item in result.data]
        })
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/adjustment/{id}")
async def get_area_price_adjustment(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取面积差价调整详情"""
    try:
        result = PaymentService.get_area_price_adjustment(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "面积差价调整不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/adjustment/{id}")
async def update_area_price_adjustment(
    id: int,
    data: PriceDiffUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新面积差价调整"""
    try:
        result = PaymentService.update_area_price_adjustment(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="面积差价调整更新成功")
        return error_response(-1, "面积差价调整不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/adjustment/{id}")
async def delete_area_price_adjustment(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除面积差价调整"""
    try:
        success = PaymentService.delete_area_price_adjustment(db, current_user['tenant'], id)
        if success:
            return success_response(message="面积差价调整删除成功")
        return error_response(-1, "面积差价调整不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 收款记录接口 ==========

@router.post("/receipt/create")
async def create_receipt_record(
    data: ReceiptRecordCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建收款记录"""
    try:
        result = PaymentService.create_receipt_record(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="收款记录创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/receipt/list")
async def list_receipt_records(
    page: int = 1,
    page_size: int = 20,
    contract_id: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取收款记录列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = PaymentService.list_receipt_records(db, current_user['tenant'], page_request)
        return success_response(data={
            'total': result.total,
            'page': result.page,
            'page_size': result.size,
            'items': [item.model_dump(mode='json') for item in result.data]
        })
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/receipt/{id}")
async def get_receipt_record(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取收款记录详情"""
    try:
        result = PaymentService.get_receipt_record(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "收款记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/receipt/{id}")
async def update_receipt_record(
    id: int,
    data: ReceiptRecordUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新收款记录"""
    try:
        result = PaymentService.update_receipt_record(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="收款记录更新成功")
        return error_response(-1, "收款记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/receipt/{id}")
async def delete_receipt_record(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除收款记录"""
    try:
        success = PaymentService.delete_receipt_record(db, current_user['tenant'], id)
        if success:
            return success_response(message="收款记录删除成功")
        return error_response(-1, "收款记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 退款记录接口 ==========

@router.post("/refund/create")
async def create_refund_record(
    data: RefundRecordCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建退款记录"""
    try:
        result = PaymentService.create_refund_record(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="退款记录创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/refund/list")
async def list_refund_records(
    page: int = 1,
    page_size: int = 20,
    contract_id: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取退款记录列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = PaymentService.list_refund_records(db, current_user['tenant'], page_request)
        return success_response(data={
            'total': result.total,
            'page': result.page,
            'page_size': result.size,
            'items': [item.model_dump(mode='json') for item in result.data]
        })
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/refund/{id}")
async def get_refund_record(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取退款记录详情"""
    try:
        result = PaymentService.get_refund_record(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "退款记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/refund/{id}")
async def update_refund_record(
    id: int,
    data: RefundRecordUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新退款记录"""
    try:
        result = PaymentService.update_refund_record(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="退款记录更新成功")
        return error_response(-1, "退款记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/refund/{id}")
async def delete_refund_record(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除退款记录"""
    try:
        success = PaymentService.delete_refund_record(db, current_user['tenant'], id)
        if success:
            return success_response(message="退款记录删除成功")
        return error_response(-1, "退款记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 认筹定金台账接口 ==========

@router.post("/deposit/create")
async def create_deposit_ledger(
    data: DepositAccountCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建认筹定金台账"""
    try:
        result = PaymentService.create_deposit_ledger(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="认筹定金台账创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/deposit/list")
async def list_deposit_ledgers(
    page: int = 1,
    page_size: int = 20,
    customer_name: Optional[str] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取认筹定金台账列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = PaymentService.list_deposit_ledgers(db, current_user['tenant'], page_request)
        return success_response(data={
            'total': result.total,
            'page': result.page,
            'page_size': result.size,
            'items': [item.model_dump(mode='json') for item in result.data]
        })
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/deposit/{id}")
async def get_deposit_ledger(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取认筹定金台账详情"""
    try:
        result = PaymentService.get_deposit_ledger(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "认筹定金台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/deposit/{id}")
async def update_deposit_ledger(
    id: int,
    data: DepositAccountUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新认筹定金台账"""
    try:
        result = PaymentService.update_deposit_ledger(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="认筹定金台账更新成功")
        return error_response(-1, "认筹定金台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/deposit/{id}")
async def delete_deposit_ledger(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除认筹定金台账"""
    try:
        success = PaymentService.delete_deposit_ledger(db, current_user['tenant'], id)
        if success:
            return success_response(message="认筹定金台账删除成功")
        return error_response(-1, "认筹定金台账不存在")
    except Exception as e:
        return error_response(-1, str(e))

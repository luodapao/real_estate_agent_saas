"""
房地产SaaS财务管理系统 - 应收应付往来台账模块路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from core.db_base import get_finance_db
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from finance.service.ar_ap_service import ArApService
from finance.schemas.ar_ap_schemas import (
    AccountReceivableCreate,
    AccountReceivableUpdate,
    AccountPayableCreate,
    AccountPayableUpdate,
    AdvancePayCreate,
    AdvancePayUpdate,
    OtherLoanCreate,
    OtherLoanUpdate,
)
from finance.schemas.base_schemas import PageRequest

router = APIRouter(prefix="/ar-ap", tags=["应收应付往来台账"])


# ========== 客户应收台账接口 ==========

@router.post("/receivable/create")
async def create_account_receivable(
    data: AccountReceivableCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建客户应收台账"""
    try:
        result = ArApService.create_account_receivable(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="客户应收台账创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/receivable/list")
async def list_account_receivables(
    page: int = 1,
    page_size: int = 20,
    customer_id: Optional[int] = None,
    project_id: Optional[int] = None,
    building_id: Optional[int] = None,
    account_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取客户应收台账列表"""
    try:
        page_request = PageRequest(page=page, size=page_size)
        filters = {}
        if customer_id:
            filters['customer_id'] = customer_id
        if project_id:
            filters['project_id'] = project_id
        if building_id:
            filters['building_id'] = building_id
        if account_status:
            filters['account_status'] = account_status
        result = ArApService.list_account_receivables(db, current_user['tenant'], page_request, filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/receivable/{id}")
async def get_account_receivable(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取客户应收台账详情"""
    try:
        result = ArApService.get_account_receivable(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "客户应收台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/receivable/{id}")
async def update_account_receivable(
    id: int,
    data: AccountReceivableUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新客户应收台账"""
    try:
        result = ArApService.update_account_receivable(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="客户应收台账更新成功")
        return error_response(-1, "客户应收台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/receivable/{id}")
async def delete_account_receivable(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除客户应收台账"""
    try:
        success = ArApService.delete_account_receivable(db, current_user['tenant'], id)
        if success:
            return success_response(message="客户应收台账删除成功")
        return error_response(-1, "客户应收台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 供应商应付台账接口 ==========

@router.post("/payable/create")
async def create_account_payable(
    data: AccountPayableCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建供应商应付台账"""
    try:
        result = ArApService.create_account_payable(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="供应商应付台账创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/payable/list")
async def list_account_payables(
    page: int = 1,
    page_size: int = 20,
    supplier_id: Optional[int] = None,
    project_id: Optional[int] = None,
    payable_status: Optional[int] = None,
    supplier_type: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取供应商应付台账列表"""
    try:
        page_request = PageRequest(page=page, size=page_size)
        filters = {}
        if supplier_id:
            filters['supplier_id'] = supplier_id
        if project_id:
            filters['project_id'] = project_id
        if payable_status:
            filters['payable_status'] = payable_status
        if supplier_type:
            filters['supplier_type'] = supplier_type
        result = ArApService.list_account_payables(db, current_user['tenant'], page_request, filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/payable/{id}")
async def get_account_payable(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取供应商应付台账详情"""
    try:
        result = ArApService.get_account_payable(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "供应商应付台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/payable/{id}")
async def update_account_payable(
    id: int,
    data: AccountPayableUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新供应商应付台账"""
    try:
        result = ArApService.update_account_payable(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="供应商应付台账更新成功")
        return error_response(-1, "供应商应付台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/payable/{id}")
async def delete_account_payable(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除供应商应付台账"""
    try:
        success = ArApService.delete_account_payable(db, current_user['tenant'], id)
        if success:
            return success_response(message="供应商应付台账删除成功")
        return error_response(-1, "供应商应付台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 预付款台账接口 ==========

@router.post("/prepayment/create")
async def create_advance_pay(
    data: AdvancePayCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建预付款台账"""
    try:
        result = ArApService.create_advance_pay(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="预付款台账创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/prepayment/list")
async def list_advance_pays(
    page: int = 1,
    page_size: int = 20,
    supplier_id: Optional[int] = None,
    project_id: Optional[int] = None,
    advance_status: Optional[int] = None,
    advance_type: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取预付款台账列表"""
    try:
        page_request = PageRequest(page=page, size=page_size)
        filters = {}
        if supplier_id:
            filters['supplier_id'] = supplier_id
        if project_id:
            filters['project_id'] = project_id
        if advance_status:
            filters['advance_status'] = advance_status
        if advance_type:
            filters['advance_type'] = advance_type
        result = ArApService.list_advance_pays(db, current_user['tenant'], page_request, filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/prepayment/{id}")
async def get_advance_pay(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取预付款台账详情"""
    try:
        result = ArApService.get_advance_pay(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "预付款台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/prepayment/{id}")
async def update_advance_pay(
    id: int,
    data: AdvancePayUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新预付款台账"""
    try:
        result = ArApService.update_advance_pay(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="预付款台账更新成功")
        return error_response(-1, "预付款台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/prepayment/{id}")
async def delete_advance_pay(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除预付款台账"""
    try:
        success = ArApService.delete_advance_pay(db, current_user['tenant'], id)
        if success:
            return success_response(message="预付款台账删除成功")
        return error_response(-1, "预付款台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 其他往来款台账接口 ==========

@router.post("/other-loan/create")
async def create_other_loan(
    data: OtherLoanCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建其他往来款台账"""
    try:
        result = ArApService.create_other_loan(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="其他往来款台账创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/other-loan/list")
async def list_other_loans(
    page: int = 1,
    page_size: int = 20,
    counterparty_id: Optional[int] = None,
    project_id: Optional[int] = None,
    loan_type: Optional[int] = None,
    loan_direction: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取其他往来款台账列表"""
    try:
        page_request = PageRequest(page=page, size=page_size)
        filters = {}
        if counterparty_id:
            filters['counterparty_id'] = counterparty_id
        if project_id:
            filters['project_id'] = project_id
        if loan_type:
            filters['loan_type'] = loan_type
        if loan_direction:
            filters['loan_direction'] = loan_direction
        result = ArApService.list_other_loans(db, current_user['tenant'], page_request, filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/other-loan/{id}")
async def get_other_loan(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取其他往来款台账详情"""
    try:
        result = ArApService.get_other_loan(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "其他往来款台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/other-loan/{id}")
async def update_other_loan(
    id: int,
    data: OtherLoanUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新其他往来款台账"""
    try:
        result = ArApService.update_other_loan(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="其他往来款台账更新成功")
        return error_response(-1, "其他往来款台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/other-loan/{id}")
async def delete_other_loan(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除其他往来款台账"""
    try:
        success = ArApService.delete_other_loan(db, current_user['tenant'], id)
        if success:
            return success_response(message="其他往来款台账删除成功")
        return error_response(-1, "其他往来款台账不存在")
    except Exception as e:
        return error_response(-1, str(e))

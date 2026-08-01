"""
房地产SaaS销售管理系统 - 认购签约交易模块路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from core.db_base import get_sale_db as get_db
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from sale.service.transaction_service import TransactionService, LoanService, ReceiptService

router = APIRouter(prefix="/transaction", tags=["认购签约交易"])


# ========== 认购管理接口 ==========

@router.post("/subscribe/create")
async def create_subscribe(
    subscribe_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建认购单"""
    try:
        service = TransactionService(db, current_user['tenant'])
        result = service.create_subscribe(subscribe_data, current_user['user_id'])
        return success_response(data=result, message="认购单创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/subscribe/list")
async def get_subscribes_list(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    subscribe_status: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取认购单列表"""
    try:
        service = TransactionService(db, current_user['tenant'])
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if customer_id:
            filters['customer_id'] = customer_id
        if subscribe_status is not None:
            filters['subscribe_status'] = subscribe_status
        
        result = service.get_subscribes_list(page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/subscribe/detail/{subscribe_id}")
async def get_subscribe_detail(
    subscribe_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取认购单详情"""
    try:
        service = TransactionService(db, current_user['tenant'])
        detail = service.get_subscribe_detail(subscribe_id)
        return success_response(data=detail)
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/subscribe/update/{subscribe_id}")
async def update_subscribe(
    subscribe_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新认购单"""
    try:
        service = TransactionService(db, current_user['tenant'])
        subscribe = service.update_subscribe(subscribe_id, update_data, current_user['user_id'])
        return success_response(data={
            "subscribe_id": subscribe.subscribe_id,
            "subscribe_no": subscribe.subscribe_no
        }, message="认购单更新成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/subscribe/cancel/{subscribe_id}")
async def cancel_subscribe(
    subscribe_id: int,
    cancel_reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """取消认购单"""
    try:
        service = TransactionService(db, current_user['tenant'])
        service.cancel_subscribe(subscribe_id, cancel_reason, current_user['user_id'])
        return success_response(message="认购单取消成功")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 签约管理接口 ==========

@router.post("/contract/create/{subscribe_id}")
async def create_contract(
    subscribe_id: int,
    contract_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建签约合同"""
    try:
        service = TransactionService(db, current_user['tenant'])
        contract_data['subscribe_id'] = subscribe_id
        result = service.create_contract(contract_data, current_user['user_id'])
        return success_response(data=result, message="签约合同创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/contract/list")
async def get_contracts_list(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    contract_status: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取签约合同列表"""
    try:
        service = TransactionService(db, current_user['tenant'])
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if customer_id:
            filters['customer_id'] = customer_id
        if contract_status is not None:
            filters['contract_status'] = contract_status
        
        result = service.get_contracts_list(page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/contract/detail/{contract_id}")
async def get_contract_detail(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取签约合同详情"""
    try:
        service = TransactionService(db, current_user['tenant'])
        detail = service.get_contract_detail(contract_id)
        return success_response(data=detail)
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/contract/update/{contract_id}")
async def update_contract(
    contract_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新签约合同"""
    try:
        service = TransactionService(db, current_user['tenant'])
        contract = service.update_contract(contract_id, update_data, current_user['user_id'])
        return success_response(data={
            "contract_id": contract.contract_id,
            "contract_no": contract.contract_no
        }, message="签约合同更新成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/contract/record/{contract_id}")
async def record_contract(
    contract_id: int,
    record_date: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """合同备案"""
    try:
        service = TransactionService(db, current_user['tenant'])
        service.record_contract(contract_id, record_date, current_user['user_id'])
        return success_response(message="合同备案成功")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 回款管理接口 ==========

@router.post("/payment/create")
async def create_payment(
    payment_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建回款记录"""
    try:
        service = TransactionService(db, current_user['tenant'])
        result = service.create_payment(payment_data, current_user['user_id'])
        return success_response(data=result, message="回款记录创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/payment/list")
async def get_payments_list(
    contract_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取回款记录列表"""
    try:
        service = TransactionService(db, current_user['tenant'])
        result = service.get_payments_list(contract_id, page, page_size)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/payment/update/{payment_id}")
async def update_payment(
    payment_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新回款记录"""
    try:
        service = TransactionService(db, current_user['tenant'])
        payment = service.update_payment(payment_id, update_data, current_user['user_id'])
        return success_response(data={
            "payment_id": payment.payment_id,
            "payment_no": payment.payment_no
        }, message="回款记录更新成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/payment/confirm/{payment_id}")
async def confirm_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """确认回款"""
    try:
        service = TransactionService(db, current_user['tenant'])
        service.confirm_payment(payment_id, current_user['user_id'])
        return success_response(message="回款确认成功")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 贷款管理接口 ==========

@router.post("/loan/create")
async def create_loan(
    loan_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建贷款记录"""
    try:
        service = LoanService(db, current_user['tenant'])
        result = service.create_loan(loan_data, current_user['user_id'])
        return success_response(data=result, message="贷款记录创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/loan/list")
async def get_loans_list(
    contract_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取贷款记录列表"""
    try:
        service = LoanService(db, current_user['tenant'])
        result = service.get_loans_list(contract_id, page, page_size)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/loan/update/{loan_id}")
async def update_loan(
    loan_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新贷款记录"""
    try:
        service = LoanService(db, current_user['tenant'])
        loan = service.update_loan(loan_id, update_data, current_user['user_id'])
        return success_response(data={
            "loan_id": loan.loan_id
        }, message="贷款记录更新成功")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 发票管理接口 ==========

@router.post("/receipt/create")
async def create_receipt(
    receipt_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建发票记录"""
    try:
        service = ReceiptService(db, current_user['tenant'])
        result = service.create_receipt(receipt_data, current_user['user_id'])
        return success_response(data=result, message="发票记录创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/receipt/list")
async def get_receipts_list(
    contract_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取发票记录列表"""
    try:
        service = ReceiptService(db, current_user['tenant'])
        result = service.get_receipts_list(contract_id, page, page_size)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/receipt/update/{receipt_id}")
async def update_receipt(
    receipt_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新发票记录"""
    try:
        service = ReceiptService(db, current_user['tenant'])
        receipt = service.update_receipt(receipt_id, update_data, current_user['user_id'])
        return success_response(data={
            "receipt_id": receipt.receipt_id,
            "receipt_no": receipt.receipt_no
        }, message="发票记录更新成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/receipt/status/{receipt_id}")
async def update_receipt_status(
    receipt_id: int,
    new_status: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新发票状态"""
    try:
        service = ReceiptService(db, current_user['tenant'])
        result = service.update_receipt_status(receipt_id, new_status, current_user['user_id'])
        return success_response(data={
            "receipt_id": receipt_id,
            "new_status": new_status
        }, message="发票状态更新成功")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 交易综合查询接口 ==========

@router.get("/transaction/list")
async def get_transaction_list(
    page: int = 1,
    page_size: int = 20,
    filters: Optional[dict] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取交易综合列表"""
    try:
        service = TransactionService(db, current_user['tenant'])
        result = service.get_transaction_list(page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))

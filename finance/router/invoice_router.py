"""
房地产SaaS财务管理系统 - 票据税务合规模块路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from core.db_base import get_finance_db
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from finance.service.invoice_service import InvoiceService
from finance.schemas.invoice_schemas import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceRedCreate,
    InvoiceRedUpdate,
    ReceiptCreate,
    ReceiptUpdate,
    MaintenanceFundCreate,
    MaintenanceFundUpdate,
    TaxDeclareCreate,
    TaxDeclareUpdate,
)
from finance.schemas.base_schemas import PageRequest

router = APIRouter(prefix="/invoice", tags=["票据税务合规"])


# ========== 蓝字发票接口 ==========

@router.post("/blue/create")
async def create_blue_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建蓝字发票"""
    try:
        result = InvoiceService.create_invoice(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="蓝字发票创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/blue/list")
async def list_blue_invoices(
    page: int = 1,
    page_size: int = 20,
    contract_id: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取蓝字发票列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = InvoiceService.list_invoices(db, current_user['tenant'], page_request)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/blue/{id}")
async def get_blue_invoice(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取蓝字发票详情"""
    try:
        result = InvoiceService.get_invoice(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "蓝字发票不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/blue/{id}")
async def update_blue_invoice(
    id: int,
    data: InvoiceUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新蓝字发票"""
    try:
        result = InvoiceService.update_invoice(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="蓝字发票更新成功")
        return error_response(-1, "蓝字发票不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/blue/{id}")
async def delete_blue_invoice(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除蓝字发票"""
    try:
        success = InvoiceService.delete_invoice(db, current_user['tenant'], id)
        if success:
            return success_response(message="蓝字发票删除成功")
        return error_response(-1, "蓝字发票不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 红字发票接口 ==========

@router.post("/red/create")
async def create_red_invoice(
    data: InvoiceRedCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建红字发票"""
    try:
        result = InvoiceService.create_invoice_red(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="红字发票创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/red/list")
async def list_red_invoices(
    page: int = 1,
    page_size: int = 20,
    original_invoice_id: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取红字发票列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = InvoiceService.list_invoice_reds(db, current_user['tenant'], page_request)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/red/{id}")
async def get_red_invoice(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取红字发票详情"""
    try:
        result = InvoiceService.get_invoice_red(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "红字发票不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/red/{id}")
async def update_red_invoice(
    id: int,
    data: InvoiceRedUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新红字发票"""
    try:
        result = InvoiceService.update_invoice_red(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="红字发票更新成功")
        return error_response(-1, "红字发票不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/red/{id}")
async def delete_red_invoice(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除红字发票"""
    try:
        success = InvoiceService.delete_invoice_red(db, current_user['tenant'], id)
        if success:
            return success_response(message="红字发票删除成功")
        return error_response(-1, "红字发票不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 内部收据接口 ==========

@router.post("/receipt/create")
async def create_internal_receipt(
    data: ReceiptCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建内部收据"""
    try:
        result = InvoiceService.create_receipt(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="内部收据创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/receipt/list")
async def list_internal_receipts(
    page: int = 1,
    page_size: int = 20,
    contract_id: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取内部收据列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = InvoiceService.list_receipts(db, current_user['tenant'], page_request)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/receipt/{id}")
async def get_internal_receipt(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取内部收据详情"""
    try:
        result = InvoiceService.get_receipt(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "内部收据不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/receipt/{id}")
async def update_internal_receipt(
    id: int,
    data: ReceiptUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新内部收据"""
    try:
        result = InvoiceService.update_receipt(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="内部收据更新成功")
        return error_response(-1, "内部收据不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/receipt/{id}")
async def delete_internal_receipt(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除内部收据"""
    try:
        success = InvoiceService.delete_receipt(db, current_user['tenant'], id)
        if success:
            return success_response(message="内部收据删除成功")
        return error_response(-1, "内部收据不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 维修基金台账接口 ==========

@router.post("/maintenance-fund/create")
async def create_maintenance_fund_ledger(
    data: MaintenanceFundCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建维修基金台账"""
    try:
        result = InvoiceService.create_maintenance_fund(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="维修基金台账创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/maintenance-fund/list")
async def list_maintenance_fund_ledgers(
    page: int = 1,
    page_size: int = 20,
    contract_id: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取维修基金台账列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = InvoiceService.list_maintenance_funds(db, current_user['tenant'], page_request)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/maintenance-fund/{id}")
async def get_maintenance_fund_ledger(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取维修基金台账详情"""
    try:
        result = InvoiceService.get_maintenance_fund(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "维修基金台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/maintenance-fund/{id}")
async def update_maintenance_fund_ledger(
    id: int,
    data: MaintenanceFundUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新维修基金台账"""
    try:
        result = InvoiceService.update_maintenance_fund(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="维修基金台账更新成功")
        return error_response(-1, "维修基金台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/maintenance-fund/{id}")
async def delete_maintenance_fund_ledger(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除维修基金台账"""
    try:
        result = InvoiceService.delete_maintenance_fund(db, current_user['tenant'], id)
        if result:
            return success_response(message="维修基金台账删除成功")
        return error_response(-1, "维修基金台账不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 税务申报记录接口 ==========

@router.post("/tax-declaration/create")
async def create_tax_declaration_record(
    data: TaxDeclareCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建税务申报记录"""
    try:
        result = InvoiceService.create_tax_declare(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="税务申报记录创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/tax-declaration/list")
async def list_tax_declaration_records(
    page: int = 1,
    page_size: int = 20,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取税务申报记录列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = InvoiceService.list_tax_declares(db, current_user['tenant'], page_request)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/tax-declaration/{id}")
async def get_tax_declaration_record(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取税务申报记录详情"""
    try:
        result = InvoiceService.get_tax_declare(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "税务申报记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/tax-declaration/{id}")
async def update_tax_declaration_record(
    id: int,
    data: TaxDeclareUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新税务申报记录"""
    try:
        result = InvoiceService.update_tax_declare(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="税务申报记录更新成功")
        return error_response(-1, "税务申报记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/tax-declaration/{id}")
async def delete_tax_declaration_record(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除税务申报记录"""
    try:
        result = InvoiceService.delete_tax_declare(db, current_user['tenant'], id)
        if result:
            return success_response(message="税务申报记录删除成功")
        return error_response(-1, "税务申报记录不存在")
    except Exception as e:
        return error_response(-1, str(e))

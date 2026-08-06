"""
房地产SaaS财务管理系统 - 佣金支付模块路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from core.db_base import get_finance_db
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from finance.service.commission_service import (
    CommissionPayService,
    CommissionDeductService,
    SalesCommissionService,
    SalesBonusPayService
)
from finance.schemas.commission_schemas import (
    CommissionPayCreate, CommissionPayUpdate,
    CommissionDeductCreate, CommissionDeductUpdate,
    SalesCommissionCreate, SalesCommissionUpdate,
    SalesBonusPayCreate, SalesBonusPayUpdate
)
from finance.schemas.base_schemas import PageRequest

router = APIRouter(prefix="/commission", tags=["佣金支付"])


# ========== 佣金付款单接口 ==========

@router.post("/pay/create")
async def create_commission_pay(
    data: CommissionPayCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建佣金付款单"""
    try:
        result = CommissionPayService.create(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="佣金付款单创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/pay/list")
async def list_commission_pay(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    audit_status: Optional[int] = None,
    pay_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取佣金付款单列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = CommissionPayService.list(db, current_user['tenant'], page_request, project_id, channel_id, audit_status, pay_status)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/pay/{id}")
async def get_commission_pay(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取佣金付款单详情"""
    try:
        result = CommissionPayService.get_by_id(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "佣金付款单不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/pay/{id}")
async def update_commission_pay(
    id: int,
    data: CommissionPayUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新佣金付款单"""
    try:
        result = CommissionPayService.update(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="佣金付款单更新成功")
        return error_response(-1, "佣金付款单不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/pay/{id}")
async def delete_commission_pay(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除佣金付款单"""
    try:
        success = CommissionPayService.delete(db, current_user['tenant'], id)
        if success:
            return success_response(message="佣金付款单删除成功")
        return error_response(-1, "佣金付款单不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 扣款明细接口 ==========

@router.post("/deduct/create")
async def create_commission_deduct(
    data: CommissionDeductCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建扣款明细"""
    try:
        result = CommissionDeductService.create(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="扣款明细创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/deduct/list")
async def list_commission_deduct(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    deduct_type: Optional[int] = None,
    deduct_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取扣款明细列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = CommissionDeductService.list(db, current_user['tenant'], page_request, project_id, channel_id, deduct_type, deduct_status)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/deduct/{id}")
async def get_commission_deduct(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取扣款明细详情"""
    try:
        result = CommissionDeductService.get_by_id(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "扣款明细不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/deduct/{id}")
async def update_commission_deduct(
    id: int,
    data: CommissionDeductUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新扣款明细"""
    try:
        result = CommissionDeductService.update(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="扣款明细更新成功")
        return error_response(-1, "扣款明细不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/deduct/{id}")
async def delete_commission_deduct(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除扣款明细"""
    try:
        success = CommissionDeductService.delete(db, current_user['tenant'], id)
        if success:
            return success_response(message="扣款明细删除成功")
        return error_response(-1, "扣款明细不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 销售提成支付接口 ==========

@router.post("/sales/create")
async def create_sales_commission(
    data: SalesCommissionCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建销售提成支付"""
    try:
        result = SalesCommissionService.create(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="销售提成支付创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/sales/list")
async def list_sales_commission(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    commission_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取销售提成支付列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = SalesCommissionService.list(db, current_user['tenant'], page_request, project_id, employee_id, commission_status)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/sales/{id}")
async def get_sales_commission(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取销售提成支付详情"""
    try:
        result = SalesCommissionService.get_by_id(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "销售提成支付不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/sales/{id}")
async def update_sales_commission(
    id: int,
    data: SalesCommissionUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新销售提成支付"""
    try:
        result = SalesCommissionService.update(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="销售提成支付更新成功")
        return error_response(-1, "销售提成支付不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/sales/{id}")
async def delete_sales_commission(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除销售提成支付"""
    try:
        success = SalesCommissionService.delete(db, current_user['tenant'], id)
        if success:
            return success_response(message="销售提成支付删除成功")
        return error_response(-1, "销售提成支付不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 内部销售提成付款单接口 ==========

@router.post("/bonus/create")
async def create_sales_bonus_pay(
    data: SalesBonusPayCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建内部销售提成付款单"""
    try:
        result = SalesBonusPayService.create(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="内部销售提成付款单创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/bonus/list")
async def list_sales_bonus_pay(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    staff_id: Optional[int] = None,
    audit_status: Optional[int] = None,
    pay_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取内部销售提成付款单列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        result = SalesBonusPayService.list(db, current_user['tenant'], page_request, project_id, staff_id, audit_status, pay_status)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/bonus/{id}")
async def get_sales_bonus_pay(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取内部销售提成付款单详情"""
    try:
        result = SalesBonusPayService.get_by_id(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "内部销售提成付款单不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/bonus/{id}")
async def update_sales_bonus_pay(
    id: int,
    data: SalesBonusPayUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新内部销售提成付款单"""
    try:
        result = SalesBonusPayService.update(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="内部销售提成付款单更新成功")
        return error_response(-1, "内部销售提成付款单不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/bonus/{id}")
async def delete_sales_bonus_pay(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除内部销售提成付款单"""
    try:
        success = SalesBonusPayService.delete(db, current_user['tenant'], id)
        if success:
            return success_response(message="内部销售提成付款单删除成功")
        return error_response(-1, "内部销售提成付款单不存在")
    except Exception as e:
        return error_response(-1, str(e))

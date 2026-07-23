﻿"""
房地产SaaS财务管理系统 - 资金对账模块路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from core.db_base import get_finance_db
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from finance.service.reconciliation_service import ReconciliationService
from finance.schemas.reconciliation_schemas import (
    BankCheckCreate,
    BankCheckUpdate,
    BankCheckMatch,
    BankCheckFinish,
    DailyCashAccountCreate,
    DailyCashAccountUpdate,
    DailyCashAccountAudit,
    ChannelReconcileCreate,
    ChannelReconcileUpdate,
    ChannelReconcileConfirm,
)
from finance.schemas.base_schemas import PageRequest

router = APIRouter(prefix="/reconciliation", tags=["资金对账"])


# ========== 银行对账记录接口 ==========

@router.post("/bank/create")
async def create_bank_check(
    data: BankCheckCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建银行对账记录"""
    try:
        result = ReconciliationService.create_bank_check(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="银行对账记录创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/bank/match")
async def auto_match_bank_check(
    data: BankCheckMatch,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """自动匹配银行对账记录"""
    try:
        result = ReconciliationService.auto_match_bank_check(db, current_user['tenant'], data)
        return success_response(data=result, message="自动匹配完成")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/bank/finish")
async def finish_bank_check(
    data: BankCheckFinish,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """完成银行对账"""
    try:
        result = ReconciliationService.finish_bank_check(db, current_user['tenant'], data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="银行对账完成")
        return error_response(-1, "银行对账记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/bank/list")
async def list_bank_checks(
    page: int = 1,
    page_size: int = 20,
    account_id: Optional[int] = None,
    check_date: Optional[date] = None,
    bank_flow_type: Optional[int] = None,
    relate_biz_type: Optional[int] = None,
    check_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取银行对账记录列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        filters = {}
        if account_id:
            filters['account_id'] = account_id
        if check_date:
            filters['check_date'] = check_date
        if bank_flow_type:
            filters['bank_flow_type'] = bank_flow_type
        if relate_biz_type:
            filters['relate_biz_type'] = relate_biz_type
        if check_status:
            filters['check_status'] = check_status
        result = ReconciliationService.list_bank_checks(db, current_user['tenant'], page_request, filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/bank/{id}")
async def get_bank_check(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取银行对账记录详情"""
    try:
        result = ReconciliationService.get_bank_check(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "银行对账记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/bank/{id}")
async def update_bank_check(
    id: int,
    data: BankCheckUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新银行对账记录"""
    try:
        result = ReconciliationService.update_bank_check(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="银行对账记录更新成功")
        return error_response(-1, "银行对账记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/bank/{id}")
async def delete_bank_check(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除银行对账记录"""
    try:
        success = ReconciliationService.delete_bank_check(db, current_user['tenant'], id)
        if success:
            return success_response(message="银行对账记录删除成功")
        return error_response(-1, "银行对账记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 每日资金轧账记录接口 ==========

@router.post("/daily/create")
async def create_daily_cash_account(
    data: DailyCashAccountCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建每日资金轧账记录"""
    try:
        result = ReconciliationService.create_daily_cash_account(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="每日资金轧账记录创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/daily/audit")
async def audit_daily_cash_account(
    data: DailyCashAccountAudit,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """审核每日资金轧账记录"""
    try:
        result = ReconciliationService.audit_daily_cash_account(db, current_user['tenant'], data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="每日资金轧账审核完成")
        return error_response(-1, "每日资金轧账记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/daily/list")
async def list_daily_cash_accounts(
    page: int = 1,
    page_size: int = 20,
    account_id: Optional[int] = None,
    project_id: Optional[int] = None,
    account_date: Optional[date] = None,
    account_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取每日资金轧账记录列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        filters = {}
        if account_id:
            filters['account_id'] = account_id
        if project_id:
            filters['project_id'] = project_id
        if account_date:
            filters['account_date'] = account_date
        if account_status:
            filters['account_status'] = account_status
        result = ReconciliationService.list_daily_cash_accounts(db, current_user['tenant'], page_request, filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/daily/{id}")
async def get_daily_cash_account(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取每日资金轧账记录详情"""
    try:
        result = ReconciliationService.get_daily_cash_account(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "每日资金轧账记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/daily/{id}")
async def update_daily_cash_account(
    id: int,
    data: DailyCashAccountUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新每日资金轧账记录"""
    try:
        result = ReconciliationService.update_daily_cash_account(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="每日资金轧账记录更新成功")
        return error_response(-1, "每日资金轧账记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/daily/{id}")
async def delete_daily_cash_account(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除每日资金轧账记录"""
    try:
        success = ReconciliationService.delete_daily_cash_account(db, current_user['tenant'], id)
        if success:
            return success_response(message="每日资金轧账记录删除成功")
        return error_response(-1, "每日资金轧账记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 渠道月度对账记录接口 ==========

@router.post("/channel/create")
async def create_channel_reconcile(
    data: ChannelReconcileCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建渠道月度对账记录"""
    try:
        result = ReconciliationService.create_channel_reconcile(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="渠道月度对账记录创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/channel/confirm")
async def confirm_channel_reconcile(
    data: ChannelReconcileConfirm,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """确认渠道月度对账"""
    try:
        result = ReconciliationService.confirm_channel_reconcile(db, current_user['tenant'], data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="渠道月度对账确认成功")
        return error_response(-1, "渠道月度对账记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/channel/list")
async def list_channel_reconciles(
    page: int = 1,
    page_size: int = 20,
    channel_id: Optional[int] = None,
    project_id: Optional[int] = None,
    reconcile_month: Optional[str] = None,
    reconcile_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取渠道月度对账记录列表"""
    try:
        page_request = PageRequest(page=page, page_size=page_size)
        filters = {}
        if channel_id:
            filters['channel_id'] = channel_id
        if project_id:
            filters['project_id'] = project_id
        if reconcile_month:
            filters['reconcile_month'] = reconcile_month
        if reconcile_status:
            filters['reconcile_status'] = reconcile_status
        result = ReconciliationService.list_channel_reconciles(db, current_user['tenant'], page_request, filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/channel/{id}")
async def get_channel_reconcile(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取渠道月度对账记录详情"""
    try:
        result = ReconciliationService.get_channel_reconcile(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "渠道月度对账记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/channel/{id}")
async def update_channel_reconcile(
    id: int,
    data: ChannelReconcileUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新渠道月度对账记录"""
    try:
        result = ReconciliationService.update_channel_reconcile(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="渠道月度对账记录更新成功")
        return error_response(-1, "渠道月度对账记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/channel/{id}")
async def delete_channel_reconcile(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除渠道月度对账记录"""
    try:
        success = ReconciliationService.delete_channel_reconcile(db, current_user['tenant'], id)
        if success:
            return success_response(message="渠道月度对账记录删除成功")
        return error_response(-1, "渠道月度对账记录不存在")
    except Exception as e:
        return error_response(-1, str(e))


"""
房地产SaaS财务管理系统 - 财务统计报表模块路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from core.db_base import get_finance_db
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from finance.service.report_service import ReportService
from finance.schemas.report_schemas import (
    CashFlowCreate,
    CashFlowUpdate,
    ReceivableStatCreate,
    ReceivableStatUpdate,
    TaxStatCreate,
    TaxStatUpdate,
    CommissionStatCreate,
    CommissionStatUpdate,
    CashFlowStatementCreate,
    CashFlowStatementUpdate,
    ProfitStatementCreate,
    ProfitStatementUpdate,
    BalanceSheetCreate,
    BalanceSheetUpdate,
    FinancialReportCreate,
    FinancialReportUpdate,
)

router = APIRouter(prefix="/report", tags=["财务统计报表"])


# ========== 现金流统计接口 ==========

@router.post("/cash-flow-stat/create")
async def create_cash_flow_stat(
    data: CashFlowCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建现金流统计"""
    try:
        result = ReportService.create_cash_flow(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="现金流统计创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/cash-flow-stat/list")
async def list_cash_flow_stats(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    stat_month: Optional[str] = None,
    stat_type: Optional[int] = None,
    stat_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取现金流统计列表"""
    try:
        filters = {
            'page': page,
            'page_size': page_size,
            'project_id': project_id,
            'stat_month': stat_month,
            'stat_type': stat_type,
            'stat_status': stat_status
        }
        result = ReportService.list_cash_flows(db, current_user['tenant'], filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/cash-flow-stat/{id}")
async def get_cash_flow_stat(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取现金流统计详情"""
    try:
        result = ReportService.get_cash_flow(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "现金流统计不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/cash-flow-stat/{id}")
async def update_cash_flow_stat(
    id: int,
    data: CashFlowUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新现金流统计"""
    try:
        result = ReportService.update_cash_flow(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="现金流统计更新成功")
        return error_response(-1, "现金流统计不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/cash-flow-stat/{id}")
async def delete_cash_flow_stat(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除现金流统计"""
    try:
        success = ReportService.delete_cash_flow(db, current_user['tenant'], id)
        if success:
            return success_response(message="现金流统计删除成功")
        return error_response(-1, "现金流统计不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 应收款统计接口 ==========

@router.post("/receivable-stat/create")
async def create_receivable_stat(
    data: ReceivableStatCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建应收款统计"""
    try:
        result = ReportService.create_receivable_stat(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="应收款统计创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/receivable-stat/list")
async def list_receivable_stats(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    stat_month: Optional[str] = None,
    stat_type: Optional[int] = None,
    stat_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取应收款统计列表"""
    try:
        filters = {
            'page': page,
            'page_size': page_size,
            'project_id': project_id,
            'stat_month': stat_month,
            'stat_type': stat_type,
            'stat_status': stat_status
        }
        result = ReportService.list_receivable_stats(db, current_user['tenant'], filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/receivable-stat/{id}")
async def get_receivable_stat(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取应收款统计详情"""
    try:
        result = ReportService.get_receivable_stat(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "应收款统计不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/receivable-stat/{id}")
async def update_receivable_stat(
    id: int,
    data: ReceivableStatUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新应收款统计"""
    try:
        result = ReportService.update_receivable_stat(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="应收款统计更新成功")
        return error_response(-1, "应收款统计不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/receivable-stat/{id}")
async def delete_receivable_stat(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除应收款统计"""
    try:
        success = ReportService.delete_receivable_stat(db, current_user['tenant'], id)
        if success:
            return success_response(message="应收款统计删除成功")
        return error_response(-1, "应收款统计不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 税务统计接口 ==========

@router.post("/tax-stat/create")
async def create_tax_stat(
    data: TaxStatCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建税务统计"""
    try:
        result = ReportService.create_tax_stat(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="税务统计创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/tax-stat/list")
async def list_tax_stats(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    stat_month: Optional[str] = None,
    stat_year: Optional[str] = None,
    declared_status: Optional[int] = None,
    stat_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取税务统计列表"""
    try:
        filters = {
            'page': page,
            'page_size': page_size,
            'project_id': project_id,
            'stat_month': stat_month,
            'stat_year': stat_year,
            'declared_status': declared_status,
            'stat_status': stat_status
        }
        result = ReportService.list_tax_stats(db, current_user['tenant'], filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/tax-stat/{id}")
async def get_tax_stat(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取税务统计详情"""
    try:
        result = ReportService.get_tax_stat(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "税务统计不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/tax-stat/{id}")
async def update_tax_stat(
    id: int,
    data: TaxStatUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新税务统计"""
    try:
        result = ReportService.update_tax_stat(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="税务统计更新成功")
        return error_response(-1, "税务统计不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/tax-stat/{id}")
async def delete_tax_stat(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除税务统计"""
    try:
        success = ReportService.delete_tax_stat(db, current_user['tenant'], id)
        if success:
            return success_response(message="税务统计删除成功")
        return error_response(-1, "税务统计不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 佣金统计接口 ==========

@router.post("/commission-stat/create")
async def create_commission_stat(
    data: CommissionStatCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建佣金统计"""
    try:
        result = ReportService.create_commission_stat(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="佣金统计创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/commission-stat/list")
async def list_commission_stats(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    channel_type: Optional[int] = None,
    stat_month: Optional[str] = None,
    stat_year: Optional[str] = None,
    stat_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取佣金统计列表"""
    try:
        filters = {
            'page': page,
            'page_size': page_size,
            'project_id': project_id,
            'channel_id': channel_id,
            'channel_type': channel_type,
            'stat_month': stat_month,
            'stat_year': stat_year,
            'stat_status': stat_status
        }
        result = ReportService.list_commission_stats(db, current_user['tenant'], filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/commission-stat/{id}")
async def get_commission_stat(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取佣金统计详情"""
    try:
        result = ReportService.get_commission_stat(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "佣金统计不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/commission-stat/{id}")
async def update_commission_stat(
    id: int,
    data: CommissionStatUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新佣金统计"""
    try:
        result = ReportService.update_commission_stat(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="佣金统计更新成功")
        return error_response(-1, "佣金统计不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/commission-stat/{id}")
async def delete_commission_stat(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除佣金统计"""
    try:
        success = ReportService.delete_commission_stat(db, current_user['tenant'], id)
        if success:
            return success_response(message="佣金统计删除成功")
        return error_response(-1, "佣金统计不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 现金流量表接口 ==========

@router.post("/cash-flow/create")
async def create_cash_flow_statement(
    data: CashFlowStatementCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建现金流量表"""
    try:
        result = ReportService.create_cash_flow_statement(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="现金流量表创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/cash-flow/list")
async def list_cash_flow_statements(
    page: int = 1,
    page_size: int = 20,
    report_period: Optional[str] = None,
    report_type: Optional[int] = None,
    report_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取现金流量表列表"""
    try:
        filters = {
            'page': page,
            'page_size': page_size,
            'report_period': report_period,
            'report_type': report_type,
            'report_status': report_status
        }
        result = ReportService.list_cash_flow_statements(db, current_user['tenant'], filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/cash-flow/{id}")
async def get_cash_flow_statement(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取现金流量表详情"""
    try:
        result = ReportService.get_cash_flow_statement(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "现金流量表不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/cash-flow/{id}")
async def update_cash_flow_statement(
    id: int,
    data: CashFlowStatementUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新现金流量表"""
    try:
        result = ReportService.update_cash_flow_statement(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="现金流量表更新成功")
        return error_response(-1, "现金流量表不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/cash-flow/{id}")
async def delete_cash_flow_statement(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除现金流量表"""
    try:
        success = ReportService.delete_cash_flow_statement(db, current_user['tenant'], id)
        if success:
            return success_response(message="现金流量表删除成功")
        return error_response(-1, "现金流量表不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 利润表接口 ==========

@router.post("/profit/create")
async def create_profit_statement(
    data: ProfitStatementCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建利润表"""
    try:
        result = ReportService.create_profit_statement(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="利润表创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/profit/list")
async def list_profit_statements(
    page: int = 1,
    page_size: int = 20,
    report_period: Optional[str] = None,
    report_type: Optional[int] = None,
    report_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取利润表列表"""
    try:
        filters = {
            'page': page,
            'page_size': page_size,
            'report_period': report_period,
            'report_type': report_type,
            'report_status': report_status
        }
        result = ReportService.list_profit_statements(db, current_user['tenant'], filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/profit/{id}")
async def get_profit_statement(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取利润表详情"""
    try:
        result = ReportService.get_profit_statement(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "利润表不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/profit/{id}")
async def update_profit_statement(
    id: int,
    data: ProfitStatementUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新利润表"""
    try:
        result = ReportService.update_profit_statement(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="利润表更新成功")
        return error_response(-1, "利润表不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/profit/{id}")
async def delete_profit_statement(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除利润表"""
    try:
        success = ReportService.delete_profit_statement(db, current_user['tenant'], id)
        if success:
            return success_response(message="利润表删除成功")
        return error_response(-1, "利润表不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 资产负债表接口 ==========

@router.post("/balance/create")
async def create_balance_sheet(
    data: BalanceSheetCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建资产负债表"""
    try:
        result = ReportService.create_balance_sheet(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="资产负债表创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/balance/list")
async def list_balance_sheets(
    page: int = 1,
    page_size: int = 20,
    report_period: Optional[str] = None,
    report_type: Optional[int] = None,
    report_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取资产负债表列表"""
    try:
        filters = {
            'page': page,
            'page_size': page_size,
            'report_period': report_period,
            'report_type': report_type,
            'report_status': report_status
        }
        result = ReportService.list_balance_sheets(db, current_user['tenant'], filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/balance/{id}")
async def get_balance_sheet(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取资产负债表详情"""
    try:
        result = ReportService.get_balance_sheet(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "资产负债表不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/balance/{id}")
async def update_balance_sheet(
    id: int,
    data: BalanceSheetUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新资产负债表"""
    try:
        result = ReportService.update_balance_sheet(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="资产负债表更新成功")
        return error_response(-1, "资产负债表不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/balance/{id}")
async def delete_balance_sheet(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除资产负债表"""
    try:
        success = ReportService.delete_balance_sheet(db, current_user['tenant'], id)
        if success:
            return success_response(message="资产负债表删除成功")
        return error_response(-1, "资产负债表不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 财务报表主表接口 ==========

@router.post("/financial/create")
async def create_financial_report(
    data: FinancialReportCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建财务报表主表"""
    try:
        result = ReportService.create_financial_report(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="财务报表主表创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/financial/list")
async def list_financial_reports(
    page: int = 1,
    page_size: int = 20,
    report_period: Optional[str] = None,
    report_type: Optional[int] = None,
    report_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取财务报表主表列表"""
    try:
        filters = {
            'page': page,
            'page_size': page_size,
            'report_period': report_period,
            'report_type': report_type,
            'report_status': report_status
        }
        result = ReportService.list_financial_reports(db, current_user['tenant'], filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/financial/{id}")
async def get_financial_report(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取财务报表主表详情"""
    try:
        result = ReportService.get_financial_report(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "财务报表主表不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/financial/{id}")
async def update_financial_report(
    id: int,
    data: FinancialReportUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新财务报表主表"""
    try:
        result = ReportService.update_financial_report(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="财务报表主表更新成功")
        return error_response(-1, "财务报表主表不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/financial/{id}")
async def delete_financial_report(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除财务报表主表"""
    try:
        success = ReportService.delete_financial_report(db, current_user['tenant'], id)
        if success:
            return success_response(message="财务报表主表删除成功")
        return error_response(-1, "财务报表主表不存在")
    except Exception as e:
        return error_response(-1, str(e))

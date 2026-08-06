"""
房地产SaaS财务管理系统 - 财务统计报表服务层
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from ..dao import (
    FinCashFlowDAO,
    FinReceivableStatDAO,
    FinTaxStatDAO,
    FinCommissionStatDAO,
    FinCashFlowStatementDAO,
    FinProfitStatementDAO,
    FinBalanceSheetDAO,
    FinFinancialReportDAO,
)
from ..model.finance_models import (
    FinCashFlowStatement,
    FinProfitStatement,
    FinBalanceSheet,
    FinFinancialReport,
)
from ..schemas.report_schemas import (
    CashFlowCreate,
    CashFlowUpdate,
    CashFlowResponse,
    ReceivableStatCreate,
    ReceivableStatUpdate,
    ReceivableStatResponse,
    TaxStatCreate,
    TaxStatUpdate,
    TaxStatResponse,
    CommissionStatCreate,
    CommissionStatUpdate,
    CommissionStatResponse,
    CashFlowStatementCreate,
    CashFlowStatementUpdate,
    CashFlowStatementResponse,
    ProfitStatementCreate,
    ProfitStatementUpdate,
    ProfitStatementResponse,
    BalanceSheetCreate,
    BalanceSheetUpdate,
    BalanceSheetResponse,
    FinancialReportCreate,
    FinancialReportUpdate,
    FinancialReportResponse,
)
from ..schemas.base_schemas import PageRequest, PageResponse


class ReportService:
    """财务统计报表服务类"""

    @staticmethod
    def _generate_doc_no(db: Session, tenant: str, prefix: str) -> str:
        """
        生成单据编号（私有方法）
        :param db: 数据库会话
        :param tenant: 租户编码
        :param prefix: 编号前缀（LLR:现金流量表, LR:利润表, FZ:负债表, CB:财报）
        :return: 生成的单据编号
        """
        date_str = datetime.now().strftime("%Y%m%d")
        max_no = 0
        pattern = f"{prefix}{date_str}%"

        if prefix == "LLR":
            result = db.query(func.max(FinCashFlowStatement.statement_no)).filter(
                FinCashFlowStatement.tenant == tenant,
                FinCashFlowStatement.statement_no.like(pattern)
            ).scalar()
        elif prefix == "LR":
            result = db.query(func.max(FinProfitStatement.statement_no)).filter(
                FinProfitStatement.tenant == tenant,
                FinProfitStatement.statement_no.like(pattern)
            ).scalar()
        elif prefix == "FZ":
            result = db.query(func.max(FinBalanceSheet.statement_no)).filter(
                FinBalanceSheet.tenant == tenant,
                FinBalanceSheet.statement_no.like(pattern)
            ).scalar()
        elif prefix == "CB":
            result = db.query(func.max(FinFinancialReport.report_no)).filter(
                FinFinancialReport.tenant == tenant,
                FinFinancialReport.report_no.like(pattern)
            ).scalar()

        if result:
            seq_str = result[-4:]
            max_no = int(seq_str) + 1

        seq_str = str(max_no).zfill(4)
        return f"{prefix}{date_str}{seq_str}"

    @staticmethod
    def create_cash_flow(db: Session, tenant: str, data: CashFlowCreate, create_user_id: int = 1) -> CashFlowResponse:
        """创建现金流统计"""
        data_dict = data.model_dump()
        if not data_dict.get('stat_batch'):
            data_dict['stat_batch'] = ReportService._generate_doc_no(db, tenant, "TXJ")
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinCashFlowDAO.create(db, tenant, data_dict)
        return CashFlowResponse.from_orm(entity)

    @staticmethod
    def get_cash_flow(db: Session, tenant: str, id: int) -> Optional[CashFlowResponse]:
        """获取现金流统计详情"""
        entity = FinCashFlowDAO.get_by_id(db, tenant, id)
        return CashFlowResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_cash_flow(db: Session, tenant: str, id: int, data: CashFlowUpdate) -> Optional[CashFlowResponse]:
        """更新现金流统计"""
        entity = FinCashFlowDAO.update(db, tenant, id, data.model_dump(exclude_unset=True))
        return CashFlowResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_cash_flow(db: Session, tenant: str, id: int) -> bool:
        """删除现金流统计"""
        return FinCashFlowDAO.delete(db, tenant, id)

    @staticmethod
    def list_cash_flows(db: Session, tenant: str, filters: Optional[dict] = None) -> PageResponse[CashFlowResponse]:
        """查询现金流统计列表"""
        total, items = FinCashFlowDAO.list(db, tenant, filters)
        page = filters.get('page', 1) if filters else 1
        page_size = filters.get('page_size', 10) if filters else 10
        return PageResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[CashFlowResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_receivable_stat(db: Session, tenant: str, data: ReceivableStatCreate, create_user_id: int = 1) -> ReceivableStatResponse:
        """创建应收款统计"""
        data_dict = data.model_dump()
        if not data_dict.get('stat_batch'):
            data_dict['stat_batch'] = ReportService._generate_doc_no(db, tenant, "YSK")
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinReceivableStatDAO.create(db, tenant, data_dict)
        return ReceivableStatResponse.from_orm(entity)

    @staticmethod
    def get_receivable_stat(db: Session, tenant: str, id: int) -> Optional[ReceivableStatResponse]:
        """获取应收款统计详情"""
        entity = FinReceivableStatDAO.get_by_id(db, tenant, id)
        return ReceivableStatResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_receivable_stat(db: Session, tenant: str, id: int, data: ReceivableStatUpdate) -> Optional[ReceivableStatResponse]:
        """更新应收款统计"""
        entity = FinReceivableStatDAO.update(db, tenant, id, data.model_dump(exclude_unset=True))
        return ReceivableStatResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_receivable_stat(db: Session, tenant: str, id: int) -> bool:
        """删除应收款统计"""
        return FinReceivableStatDAO.delete(db, tenant, id)

    @staticmethod
    def list_receivable_stats(db: Session, tenant: str, filters: Optional[dict] = None) -> PageResponse[ReceivableStatResponse]:
        """查询应收款统计列表"""
        total, items = FinReceivableStatDAO.list(db, tenant, filters)
        page = filters.get('page', 1) if filters else 1
        page_size = filters.get('page_size', 10) if filters else 10
        return PageResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[ReceivableStatResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_tax_stat(db: Session, tenant: str, data: TaxStatCreate, create_user_id: int = 1) -> TaxStatResponse:
        """创建税务统计"""
        data_dict = data.model_dump()
        if not data_dict.get('stat_batch'):
            data_dict['stat_batch'] = ReportService._generate_doc_no(db, tenant, "SW")
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinTaxStatDAO.create(db, tenant, data_dict)
        return TaxStatResponse.from_orm(entity)

    @staticmethod
    def get_tax_stat(db: Session, tenant: str, id: int) -> Optional[TaxStatResponse]:
        """获取税务统计详情"""
        entity = FinTaxStatDAO.get_by_id(db, tenant, id)
        return TaxStatResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_tax_stat(db: Session, tenant: str, id: int, data: TaxStatUpdate) -> Optional[TaxStatResponse]:
        """更新税务统计"""
        entity = FinTaxStatDAO.update(db, tenant, id, data.model_dump(exclude_unset=True))
        return TaxStatResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_tax_stat(db: Session, tenant: str, id: int) -> bool:
        """删除税务统计"""
        return FinTaxStatDAO.delete(db, tenant, id)

    @staticmethod
    def list_tax_stats(db: Session, tenant: str, filters: Optional[dict] = None) -> PageResponse[TaxStatResponse]:
        """查询税务统计列表"""
        total, items = FinTaxStatDAO.list(db, tenant, filters)
        page = filters.get('page', 1) if filters else 1
        page_size = filters.get('page_size', 10) if filters else 10
        return PageResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[TaxStatResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_commission_stat(db: Session, tenant: str, data: CommissionStatCreate, create_user_id: int = 1) -> CommissionStatResponse:
        """创建佣金统计"""
        data_dict = data.model_dump()
        if not data_dict.get('stat_batch'):
            data_dict['stat_batch'] = ReportService._generate_doc_no(db, tenant, "YJ")
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinCommissionStatDAO.create(db, tenant, data_dict)
        return CommissionStatResponse.from_orm(entity)

    @staticmethod
    def get_commission_stat(db: Session, tenant: str, id: int) -> Optional[CommissionStatResponse]:
        """获取佣金统计详情"""
        entity = FinCommissionStatDAO.get_by_id(db, tenant, id)
        return CommissionStatResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_commission_stat(db: Session, tenant: str, id: int, data: CommissionStatUpdate) -> Optional[CommissionStatResponse]:
        """更新佣金统计"""
        entity = FinCommissionStatDAO.update(db, tenant, id, data.model_dump(exclude_unset=True))
        return CommissionStatResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_commission_stat(db: Session, tenant: str, id: int) -> bool:
        """删除佣金统计"""
        return FinCommissionStatDAO.delete(db, tenant, id)

    @staticmethod
    def list_commission_stats(db: Session, tenant: str, filters: Optional[dict] = None) -> PageResponse[CommissionStatResponse]:
        """查询佣金统计列表"""
        total, items = FinCommissionStatDAO.list(db, tenant, filters)
        page = filters.get('page', 1) if filters else 1
        page_size = filters.get('page_size', 10) if filters else 10
        return PageResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[CommissionStatResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_cash_flow_statement(db: Session, tenant: str, data: CashFlowStatementCreate, create_user_id: int = 1) -> CashFlowStatementResponse:
        """创建现金流量表"""
        data_dict = data.model_dump()
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinCashFlowStatementDAO.create(db, tenant, data_dict)
        return CashFlowStatementResponse.from_orm(entity)

    @staticmethod
    def get_cash_flow_statement(db: Session, tenant: str, id: int) -> Optional[CashFlowStatementResponse]:
        """获取现金流量表详情"""
        entity = FinCashFlowStatementDAO.get_by_id(db, tenant, id)
        return CashFlowStatementResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_cash_flow_statement(db: Session, tenant: str, id: int, data: CashFlowStatementUpdate) -> Optional[CashFlowStatementResponse]:
        """更新现金流量表"""
        entity = FinCashFlowStatementDAO.update(db, tenant, id, data.model_dump(exclude_unset=True))
        return CashFlowStatementResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_cash_flow_statement(db: Session, tenant: str, id: int) -> bool:
        """删除现金流量表"""
        return FinCashFlowStatementDAO.delete(db, tenant, id)

    @staticmethod
    def list_cash_flow_statements(db: Session, tenant: str, filters: Optional[dict] = None) -> PageResponse[CashFlowStatementResponse]:
        """查询现金流量表列表"""
        total, items = FinCashFlowStatementDAO.list(db, tenant, filters)
        page = filters.get('page', 1) if filters else 1
        page_size = filters.get('page_size', 10) if filters else 10
        return PageResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[CashFlowStatementResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_profit_statement(db: Session, tenant: str, data: ProfitStatementCreate, create_user_id: int = 1) -> ProfitStatementResponse:
        """创建利润表"""
        data_dict = data.model_dump()
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinProfitStatementDAO.create(db, tenant, data_dict)
        return ProfitStatementResponse.from_orm(entity)

    @staticmethod
    def get_profit_statement(db: Session, tenant: str, id: int) -> Optional[ProfitStatementResponse]:
        """获取利润表详情"""
        entity = FinProfitStatementDAO.get_by_id(db, tenant, id)
        return ProfitStatementResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_profit_statement(db: Session, tenant: str, id: int, data: ProfitStatementUpdate) -> Optional[ProfitStatementResponse]:
        """更新利润表"""
        entity = FinProfitStatementDAO.update(db, tenant, id, data.model_dump(exclude_unset=True))
        return ProfitStatementResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_profit_statement(db: Session, tenant: str, id: int) -> bool:
        """删除利润表"""
        return FinProfitStatementDAO.delete(db, tenant, id)

    @staticmethod
    def list_profit_statements(db: Session, tenant: str, filters: Optional[dict] = None) -> PageResponse[ProfitStatementResponse]:
        """查询利润表列表"""
        total, items = FinProfitStatementDAO.list(db, tenant, filters)
        page = filters.get('page', 1) if filters else 1
        page_size = filters.get('page_size', 10) if filters else 10
        return PageResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[ProfitStatementResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_balance_sheet(db: Session, tenant: str, data: BalanceSheetCreate, create_user_id: int = 1) -> BalanceSheetResponse:
        """创建资产负债表"""
        data_dict = data.model_dump()
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinBalanceSheetDAO.create(db, tenant, data_dict)
        return BalanceSheetResponse.from_orm(entity)

    @staticmethod
    def get_balance_sheet(db: Session, tenant: str, id: int) -> Optional[BalanceSheetResponse]:
        """获取资产负债表详情"""
        entity = FinBalanceSheetDAO.get_by_id(db, tenant, id)
        return BalanceSheetResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_balance_sheet(db: Session, tenant: str, id: int, data: BalanceSheetUpdate) -> Optional[BalanceSheetResponse]:
        """更新资产负债表"""
        entity = FinBalanceSheetDAO.update(db, tenant, id, data.model_dump(exclude_unset=True))
        return BalanceSheetResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_balance_sheet(db: Session, tenant: str, id: int) -> bool:
        """删除资产负债表"""
        return FinBalanceSheetDAO.delete(db, tenant, id)

    @staticmethod
    def list_balance_sheets(db: Session, tenant: str, filters: Optional[dict] = None) -> PageResponse[BalanceSheetResponse]:
        """查询资产负债表列表"""
        total, items = FinBalanceSheetDAO.list(db, tenant, filters)
        page = filters.get('page', 1) if filters else 1
        page_size = filters.get('page_size', 10) if filters else 10
        return PageResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[BalanceSheetResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_financial_report(db: Session, tenant: str, data: FinancialReportCreate, create_user_id: int = 1) -> FinancialReportResponse:
        """创建财务报表主表"""
        data_dict = data.model_dump()
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinFinancialReportDAO.create(db, tenant, data_dict)
        return FinancialReportResponse.from_orm(entity)

    @staticmethod
    def get_financial_report(db: Session, tenant: str, id: int) -> Optional[FinancialReportResponse]:
        """获取财务报表主表详情"""
        entity = FinFinancialReportDAO.get_by_id(db, tenant, id)
        return FinancialReportResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_financial_report(db: Session, tenant: str, id: int, data: FinancialReportUpdate) -> Optional[FinancialReportResponse]:
        """更新财务报表主表"""
        entity = FinFinancialReportDAO.update(db, tenant, id, data.model_dump(exclude_unset=True))
        return FinancialReportResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_financial_report(db: Session, tenant: str, id: int) -> bool:
        """删除财务报表主表"""
        return FinFinancialReportDAO.delete(db, tenant, id)

    @staticmethod
    def list_financial_reports(db: Session, tenant: str, filters: Optional[dict] = None) -> PageResponse[FinancialReportResponse]:
        """查询财务报表主表列表"""
        total, items = FinFinancialReportDAO.list(db, tenant, filters)
        page = filters.get('page', 1) if filters else 1
        page_size = filters.get('page_size', 10) if filters else 10
        return PageResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[FinancialReportResponse.from_orm(item) for item in items]
        )

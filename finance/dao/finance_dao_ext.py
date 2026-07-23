"""
房地产SaaS财务管理系统 - 数据访问层（DAO）扩展
包含佣金支付、项目成本、应收应付往来台账、资金对账、会计凭证、财务审计追溯和财务统计报表模块
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from finance.model.finance_models import (
    # 佣金支付模块
    FinCommissionPay, FinCommissionDeduct, FinSalesCommission, FinSalesBonusPay,
    # 项目成本模块
    FinCostExpense, FinExpenseReimbursement, FinCostPay, FinAdCost, FinProjectEngCost,
    # 应收应付往来台账模块
    FinAccountReceivable, FinAccountPayable, FinAdvancePay, FinOtherLoan,
    # 资金对账模块
    FinBankCheck, FinDailyCashAccount, FinChannelReconcile,
    # 会计凭证模块
    FinVoucher, FinVoucherItem,
    # 财务审计追溯模块
    FinOperateLog, FinDataChangeLog,
    # 财务统计报表模块
    FinCashFlow, FinReceivableStat, FinTaxStat, FinCommissionStat,
    FinCashFlowStatement, FinProfitStatement, FinBalanceSheet, FinFinancialReport
)


# ==================== 佣金支付模块 ====================

class FinCommissionPayDAO:
    """佣金付款单表数据访问对象"""
    
    @staticmethod
    def create(db: Session, data: dict) -> FinCommissionPay:
        record = FinCommissionPay(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinCommissionPay]:
        return db.query(FinCommissionPay).filter(
            and_(
                FinCommissionPay.id == id,
                FinCommissionPay.tenant == tenant,
                FinCommissionPay.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_pay_no(db: Session, tenant: str, pay_no: str) -> Optional[FinCommissionPay]:
        return db.query(FinCommissionPay).filter(
            and_(
                FinCommissionPay.pay_no == pay_no,
                FinCommissionPay.tenant == tenant,
                FinCommissionPay.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant: str, page: int = 1, page_size: int = 20, **filters) -> tuple:
        query = db.query(FinCommissionPay).filter(
            and_(
                FinCommissionPay.tenant == tenant,
                FinCommissionPay.is_del == 0
            )
        )
        if filters.get('project_id'):
            query = query.filter(FinCommissionPay.project_id == filters['project_id'])
        if filters.get('channel_id'):
            query = query.filter(FinCommissionPay.channel_id == filters['channel_id'])
        if filters.get('audit_status'):
            query = query.filter(FinCommissionPay.audit_status == filters['audit_status'])
        if filters.get('pay_status'):
            query = query.filter(FinCommissionPay.pay_status == filters['pay_status'])
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinCommissionPay]:
        record = db.query(FinCommissionPay).filter(
            and_(
                FinCommissionPay.id == id,
                FinCommissionPay.tenant == tenant,
                FinCommissionPay.is_del == 0
            )
        ).first()
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
        return record
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = db.query(FinCommissionPay).filter(
            and_(
                FinCommissionPay.id == id,
                FinCommissionPay.tenant == tenant,
                FinCommissionPay.is_del == 0
            )
        ).first()
        if record:
            record.is_del = 1
            record.update_time = datetime.now()
            record.version += 1
            db.commit()
            return True
        return False


class FinCommissionDeductDAO:
    """佣金扣款明细表数据访问对象"""
    
    @staticmethod
    def create(db: Session, data: dict) -> FinCommissionDeduct:
        record = FinCommissionDeduct(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinCommissionDeduct]:
        return db.query(FinCommissionDeduct).filter(
            and_(
                FinCommissionDeduct.id == id,
                FinCommissionDeduct.tenant == tenant,
                FinCommissionDeduct.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_pay_id(db: Session, tenant: str, pay_id: int) -> List[FinCommissionDeduct]:
        return db.query(FinCommissionDeduct).filter(
            and_(
                FinCommissionDeduct.commission_pay_id == pay_id,
                FinCommissionDeduct.tenant == tenant,
                FinCommissionDeduct.is_del == 0
            )
        ).all()
    
    @staticmethod
    def list(db: Session, tenant: str, page: int = 1, page_size: int = 20, **filters) -> tuple:
        query = db.query(FinCommissionDeduct).filter(
            and_(
                FinCommissionDeduct.tenant == tenant,
                FinCommissionDeduct.is_del == 0
            )
        )
        if filters.get('project_id'):
            query = query.filter(FinCommissionDeduct.project_id == filters['project_id'])
        if filters.get('channel_id'):
            query = query.filter(FinCommissionDeduct.channel_id == filters['channel_id'])
        if filters.get('deduct_type'):
            query = query.filter(FinCommissionDeduct.deduct_type == filters['deduct_type'])
        if filters.get('deduct_status'):
            query = query.filter(FinCommissionDeduct.deduct_status == filters['deduct_status'])
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinCommissionDeduct]:
        record = db.query(FinCommissionDeduct).filter(
            and_(
                FinCommissionDeduct.id == id,
                FinCommissionDeduct.tenant == tenant,
                FinCommissionDeduct.is_del == 0
            )
        ).first()
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
        return record
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = db.query(FinCommissionDeduct).filter(
            and_(
                FinCommissionDeduct.id == id,
                FinCommissionDeduct.tenant == tenant,
                FinCommissionDeduct.is_del == 0
            )
        ).first()
        if record:
            record.is_del = 1
            record.update_time = datetime.now()
            record.version += 1
            db.commit()
            return True
        return False


class FinSalesCommissionDAO:
    """销售提成支付表数据访问对象"""
    
    @staticmethod
    def create(db: Session, data: dict) -> FinSalesCommission:
        record = FinSalesCommission(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinSalesCommission]:
        return db.query(FinSalesCommission).filter(
            and_(
                FinSalesCommission.id == id,
                FinSalesCommission.tenant == tenant,
                FinSalesCommission.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_order_id(db: Session, tenant: str, order_id: int) -> Optional[FinSalesCommission]:
        return db.query(FinSalesCommission).filter(
            and_(
                FinSalesCommission.order_id == order_id,
                FinSalesCommission.tenant == tenant,
                FinSalesCommission.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant: str, page: int = 1, page_size: int = 20, **filters) -> tuple:
        query = db.query(FinSalesCommission).filter(
            and_(
                FinSalesCommission.tenant == tenant,
                FinSalesCommission.is_del == 0
            )
        )
        if filters.get('project_id'):
            query = query.filter(FinSalesCommission.project_id == filters['project_id'])
        if filters.get('employee_id'):
            query = query.filter(FinSalesCommission.employee_id == filters['employee_id'])
        if filters.get('commission_status'):
            query = query.filter(FinSalesCommission.commission_status == filters['commission_status'])
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinSalesCommission]:
        record = db.query(FinSalesCommission).filter(
            and_(
                FinSalesCommission.id == id,
                FinSalesCommission.tenant == tenant,
                FinSalesCommission.is_del == 0
            )
        ).first()
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
        return record
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = db.query(FinSalesCommission).filter(
            and_(
                FinSalesCommission.id == id,
                FinSalesCommission.tenant == tenant,
                FinSalesCommission.is_del == 0
            )
        ).first()
        if record:
            record.is_del = 1
            record.update_time = datetime.now()
            record.version += 1
            db.commit()
            return True
        return False


class FinSalesBonusPayDAO:
    """销售奖金支付表数据访问对象"""
    
    @staticmethod
    def create(db: Session, data: dict) -> FinSalesBonusPay:
        record = FinSalesBonusPay(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinSalesBonusPay]:
        return db.query(FinSalesBonusPay).filter(
            and_(
                FinSalesBonusPay.id == id,
                FinSalesBonusPay.tenant == tenant,
                FinSalesBonusPay.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_bonus_no(db: Session, tenant: str, bonus_no: str) -> Optional[FinSalesBonusPay]:
        return db.query(FinSalesBonusPay).filter(
            and_(
                FinSalesBonusPay.bonus_no == bonus_no,
                FinSalesBonusPay.tenant == tenant,
                FinSalesBonusPay.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant: str, page: int = 1, page_size: int = 20, **filters) -> tuple:
        query = db.query(FinSalesBonusPay).filter(
            and_(
                FinSalesBonusPay.tenant == tenant,
                FinSalesBonusPay.is_del == 0
            )
        )
        if filters.get('project_id'):
            query = query.filter(FinSalesBonusPay.project_id == filters['project_id'])
        if filters.get('employee_id'):
            query = query.filter(FinSalesBonusPay.employee_id == filters['employee_id'])
        if filters.get('bonus_type'):
            query = query.filter(FinSalesBonusPay.bonus_type == filters['bonus_type'])
        if filters.get('bonus_status'):
            query = query.filter(FinSalesBonusPay.bonus_status == filters['bonus_status'])
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinSalesBonusPay]:
        record = db.query(FinSalesBonusPay).filter(
            and_(
                FinSalesBonusPay.id == id,
                FinSalesBonusPay.tenant == tenant,
                FinSalesBonusPay.is_del == 0
            )
        ).first()
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
        return record
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = db.query(FinSalesBonusPay).filter(
            and_(
                FinSalesBonusPay.id == id,
                FinSalesBonusPay.tenant == tenant,
                FinSalesBonusPay.is_del == 0
            )
        ).first()
        if record:
            record.is_del = 1
            record.update_time = datetime.now()
            record.version += 1
            db.commit()
            return True
        return False


# ==================== 项目成本模块 ====================

class FinCostExpenseDAO:
    """通用费用申请表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: int, data: dict) -> FinCostExpense:
        record = FinCostExpense(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int, id: int) -> Optional[FinCostExpense]:
        return db.query(FinCostExpense).filter(
            and_(
                FinCostExpense.id == id,
                FinCostExpense.tenant == tenant_id,
                FinCostExpense.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_expense_no(db: Session, tenant_id: int, expense_no: str) -> Optional[FinCostExpense]:
        return db.query(FinCostExpense).filter(
            and_(
                FinCostExpense.expense_no == expense_no,
                FinCostExpense.tenant == tenant_id,
                FinCostExpense.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: int, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinCostExpense).filter(
            and_(
                FinCostExpense.tenant == tenant_id,
                FinCostExpense.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinCostExpense.project_id == filters['project_id'])
            if filters.get('apply_user_id'):
                query = query.filter(FinCostExpense.apply_user_id == filters['apply_user_id'])
            if filters.get('expense_type'):
                query = query.filter(FinCostExpense.expense_type == filters['expense_type'])
            if filters.get('audit_status'):
                query = query.filter(FinCostExpense.audit_status == filters['audit_status'])
            if filters.get('page') and filters.get('size'):
                skip = (filters['page'] - 1) * filters['size']
                total = query.count()
                items = query.offset(skip).limit(filters['size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: int, id: int, update_data: dict) -> Optional[FinCostExpense]:
        record = FinCostExpenseDAO.get_by_id(db, tenant_id, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant_id: int, id: int) -> bool:
        record = FinCostExpenseDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinExpenseReimbursementDAO:
    """费用报销单表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: int, data: dict) -> FinExpenseReimbursement:
        record = FinExpenseReimbursement(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int, id: int) -> Optional[FinExpenseReimbursement]:
        return db.query(FinExpenseReimbursement).filter(
            and_(
                FinExpenseReimbursement.id == id,
                FinExpenseReimbursement.tenant == tenant_id,
                FinExpenseReimbursement.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_reimburse_no(db: Session, tenant_id: int, reimburse_no: str) -> Optional[FinExpenseReimbursement]:
        return db.query(FinExpenseReimbursement).filter(
            and_(
                FinExpenseReimbursement.reimburse_no == reimburse_no,
                FinExpenseReimbursement.tenant == tenant_id,
                FinExpenseReimbursement.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: int, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinExpenseReimbursement).filter(
            and_(
                FinExpenseReimbursement.tenant == tenant_id,
                FinExpenseReimbursement.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinExpenseReimbursement.project_id == filters['project_id'])
            if filters.get('employee_id'):
                query = query.filter(FinExpenseReimbursement.employee_id == filters['employee_id'])
            if filters.get('expense_type'):
                query = query.filter(FinExpenseReimbursement.expense_type == filters['expense_type'])
            if filters.get('audit_status'):
                query = query.filter(FinExpenseReimbursement.audit_status == filters['audit_status'])
            if filters.get('page') and filters.get('size'):
                skip = (filters['page'] - 1) * filters['size']
                total = query.count()
                items = query.offset(skip).limit(filters['size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: int, id: int, update_data: dict) -> Optional[FinExpenseReimbursement]:
        record = FinExpenseReimbursementDAO.get_by_id(db, tenant_id, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant_id: int, id: int) -> bool:
        record = FinExpenseReimbursementDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinCostPayDAO:
    """费用付款单表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: int, data: dict) -> FinCostPay:
        record = FinCostPay(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int, id: int) -> Optional[FinCostPay]:
        return db.query(FinCostPay).filter(
            and_(
                FinCostPay.id == id,
                FinCostPay.tenant == tenant_id,
                FinCostPay.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_pay_no(db: Session, tenant_id: int, pay_no: str) -> Optional[FinCostPay]:
        return db.query(FinCostPay).filter(
            and_(
                FinCostPay.pay_no == pay_no,
                FinCostPay.tenant == tenant_id,
                FinCostPay.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: int, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinCostPay).filter(
            and_(
                FinCostPay.tenant == tenant_id,
                FinCostPay.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinCostPay.project_id == filters['project_id'])
            if filters.get('pay_target_type'):
                query = query.filter(FinCostPay.pay_target_type == filters['pay_target_type'])
            if filters.get('audit_status'):
                query = query.filter(FinCostPay.audit_status == filters['audit_status'])
            if filters.get('pay_status'):
                query = query.filter(FinCostPay.pay_status == filters['pay_status'])
            if filters.get('page') and filters.get('size'):
                skip = (filters['page'] - 1) * filters['size']
                total = query.count()
                items = query.offset(skip).limit(filters['size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: int, id: int, update_data: dict) -> Optional[FinCostPay]:
        record = FinCostPayDAO.get_by_id(db, tenant_id, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant_id: int, id: int) -> bool:
        record = FinCostPayDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinAdCostDAO:
    """广告推广成本专项台账数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: int, data: dict) -> FinAdCost:
        record = FinAdCost(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int, id: int) -> Optional[FinAdCost]:
        return db.query(FinAdCost).filter(
            and_(
                FinAdCost.id == id,
                FinAdCost.tenant == tenant_id,
                FinAdCost.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_cost_no(db: Session, tenant_id: int, cost_no: str) -> Optional[FinAdCost]:
        return db.query(FinAdCost).filter(
            and_(
                FinAdCost.cost_no == cost_no,
                FinAdCost.tenant == tenant_id,
                FinAdCost.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: int, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinAdCost).filter(
            and_(
                FinAdCost.tenant == tenant_id,
                FinAdCost.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinAdCost.project_id == filters['project_id'])
            if filters.get('supplier_id'):
                query = query.filter(FinAdCost.supplier_id == filters['supplier_id'])
            if filters.get('ad_type'):
                query = query.filter(FinAdCost.ad_type == filters['ad_type'])
            if filters.get('cost_status'):
                query = query.filter(FinAdCost.cost_status == filters['cost_status'])
            if filters.get('page') and filters.get('size'):
                skip = (filters['page'] - 1) * filters['size']
                total = query.count()
                items = query.offset(skip).limit(filters['size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: int, id: int, update_data: dict) -> Optional[FinAdCost]:
        record = FinAdCostDAO.get_by_id(db, tenant_id, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant_id: int, id: int) -> bool:
        record = FinAdCostDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinProjectEngCostDAO:
    """工程建设成本专项台账数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: int, data: dict) -> FinProjectEngCost:
        record = FinProjectEngCost(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int, id: int) -> Optional[FinProjectEngCost]:
        return db.query(FinProjectEngCost).filter(
            and_(
                FinProjectEngCost.id == id,
                FinProjectEngCost.tenant == tenant_id,
                FinProjectEngCost.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_cost_no(db: Session, tenant_id: int, cost_no: str) -> Optional[FinProjectEngCost]:
        return db.query(FinProjectEngCost).filter(
            and_(
                FinProjectEngCost.cost_no == cost_no,
                FinProjectEngCost.tenant == tenant_id,
                FinProjectEngCost.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: int, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinProjectEngCost).filter(
            and_(
                FinProjectEngCost.tenant == tenant_id,
                FinProjectEngCost.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinProjectEngCost.project_id == filters['project_id'])
            if filters.get('building_id'):
                query = query.filter(FinProjectEngCost.building_id == filters['building_id'])
            if filters.get('supplier_id'):
                query = query.filter(FinProjectEngCost.supplier_id == filters['supplier_id'])
            if filters.get('eng_type'):
                query = query.filter(FinProjectEngCost.eng_type == filters['eng_type'])
            if filters.get('cost_status'):
                query = query.filter(FinProjectEngCost.cost_status == filters['cost_status'])
            if filters.get('page') and filters.get('size'):
                skip = (filters['page'] - 1) * filters['size']
                total = query.count()
                items = query.offset(skip).limit(filters['size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: int, id: int, update_data: dict) -> Optional[FinProjectEngCost]:
        record = FinProjectEngCostDAO.get_by_id(db, tenant_id, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant_id: int, id: int) -> bool:
        record = FinProjectEngCostDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


# ==================== 应收应付往来台账模块 ====================

class FinAccountReceivableDAO:
    """客户应收台账表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: str, data: dict) -> FinAccountReceivable:
        record = FinAccountReceivable(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: str, id: int) -> Optional[FinAccountReceivable]:
        return db.query(FinAccountReceivable).filter(
            and_(
                FinAccountReceivable.id == id,
                FinAccountReceivable.tenant == tenant_id,
                FinAccountReceivable.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_house_contract(db: Session, tenant_id: str, house_id: int, contract_id: int) -> Optional[FinAccountReceivable]:
        return db.query(FinAccountReceivable).filter(
            and_(
                FinAccountReceivable.house_id == house_id,
                FinAccountReceivable.contract_id == contract_id,
                FinAccountReceivable.tenant == tenant_id,
                FinAccountReceivable.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinAccountReceivable).filter(
            and_(
                FinAccountReceivable.tenant == tenant_id,
                FinAccountReceivable.is_del == 0
            )
        )
        if filters:
            if filters.get('customer_id'):
                query = query.filter(FinAccountReceivable.customer_id == filters['customer_id'])
            if filters.get('project_id'):
                query = query.filter(FinAccountReceivable.project_id == filters['project_id'])
            if filters.get('building_id'):
                query = query.filter(FinAccountReceivable.building_id == filters['building_id'])
            if filters.get('account_status'):
                query = query.filter(FinAccountReceivable.account_status == filters['account_status'])
            if filters.get('page') and filters.get('size'):
                skip = (filters['page'] - 1) * filters['size']
                total = query.count()
                items = query.offset(skip).limit(filters['size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: str, id: int, update_data: dict) -> Optional[FinAccountReceivable]:
        record = FinAccountReceivableDAO.get_by_id(db, tenant_id, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant_id: str, id: int) -> bool:
        record = FinAccountReceivableDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinAccountPayableDAO:
    """供应商应付台账表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: str, data: dict) -> FinAccountPayable:
        record = FinAccountPayable(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: str, id: int) -> Optional[FinAccountPayable]:
        return db.query(FinAccountPayable).filter(
            and_(
                FinAccountPayable.id == id,
                FinAccountPayable.tenant == tenant_id,
                FinAccountPayable.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_payable_no(db: Session, tenant_id: str, payable_no: str) -> Optional[FinAccountPayable]:
        return db.query(FinAccountPayable).filter(
            and_(
                FinAccountPayable.payable_no == payable_no,
                FinAccountPayable.tenant == tenant_id,
                FinAccountPayable.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinAccountPayable).filter(
            and_(
                FinAccountPayable.tenant == tenant_id,
                FinAccountPayable.is_del == 0
            )
        )
        if filters:
            if filters.get('supplier_id'):
                query = query.filter(FinAccountPayable.supplier_id == filters['supplier_id'])
            if filters.get('project_id'):
                query = query.filter(FinAccountPayable.project_id == filters['project_id'])
            if filters.get('payable_status'):
                query = query.filter(FinAccountPayable.payable_status == filters['payable_status'])
            if filters.get('supplier_type'):
                query = query.filter(FinAccountPayable.supplier_type == filters['supplier_type'])
            if filters.get('page') and filters.get('size'):
                skip = (filters['page'] - 1) * filters['size']
                total = query.count()
                items = query.offset(skip).limit(filters['size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: str, id: int, update_data: dict) -> Optional[FinAccountPayable]:
        record = FinAccountPayableDAO.get_by_id(db, tenant_id, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant_id: str, id: int) -> bool:
        record = FinAccountPayableDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinAdvancePayDAO:
    """预付款台账表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: str, data: dict) -> FinAdvancePay:
        record = FinAdvancePay(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: str, id: int) -> Optional[FinAdvancePay]:
        return db.query(FinAdvancePay).filter(
            and_(
                FinAdvancePay.id == id,
                FinAdvancePay.tenant == tenant_id,
                FinAdvancePay.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_advance_no(db: Session, tenant_id: str, advance_no: str) -> Optional[FinAdvancePay]:
        return db.query(FinAdvancePay).filter(
            and_(
                FinAdvancePay.advance_no == advance_no,
                FinAdvancePay.tenant == tenant_id,
                FinAdvancePay.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinAdvancePay).filter(
            and_(
                FinAdvancePay.tenant == tenant_id,
                FinAdvancePay.is_del == 0
            )
        )
        if filters:
            if filters.get('supplier_id'):
                query = query.filter(FinAdvancePay.supplier_id == filters['supplier_id'])
            if filters.get('project_id'):
                query = query.filter(FinAdvancePay.project_id == filters['project_id'])
            if filters.get('advance_status'):
                query = query.filter(FinAdvancePay.advance_status == filters['advance_status'])
            if filters.get('advance_type'):
                query = query.filter(FinAdvancePay.advance_type == filters['advance_type'])
            if filters.get('page') and filters.get('size'):
                skip = (filters['page'] - 1) * filters['size']
                total = query.count()
                items = query.offset(skip).limit(filters['size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: str, id: int, update_data: dict) -> Optional[FinAdvancePay]:
        record = FinAdvancePayDAO.get_by_id(db, tenant_id, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant_id: str, id: int) -> bool:
        record = FinAdvancePayDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinOtherLoanDAO:
    """其他往来款台账表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: str, data: dict) -> FinOtherLoan:
        record = FinOtherLoan(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: str, id: int) -> Optional[FinOtherLoan]:
        return db.query(FinOtherLoan).filter(
            and_(
                FinOtherLoan.id == id,
                FinOtherLoan.tenant == tenant_id,
                FinOtherLoan.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_loan_no(db: Session, tenant_id: str, loan_no: str) -> Optional[FinOtherLoan]:
        return db.query(FinOtherLoan).filter(
            and_(
                FinOtherLoan.loan_no == loan_no,
                FinOtherLoan.tenant == tenant_id,
                FinOtherLoan.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinOtherLoan).filter(
            and_(
                FinOtherLoan.tenant == tenant_id,
                FinOtherLoan.is_del == 0
            )
        )
        if filters:
            if filters.get('counterparty_id'):
                query = query.filter(FinOtherLoan.counterparty_id == filters['counterparty_id'])
            if filters.get('project_id'):
                query = query.filter(FinOtherLoan.project_id == filters['project_id'])
            if filters.get('loan_type'):
                query = query.filter(FinOtherLoan.loan_type == filters['loan_type'])
            if filters.get('loan_direction'):
                query = query.filter(FinOtherLoan.loan_direction == filters['loan_direction'])
            if filters.get('page') and filters.get('size'):
                skip = (filters['page'] - 1) * filters['size']
                total = query.count()
                items = query.offset(skip).limit(filters['size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: str, id: int, update_data: dict) -> Optional[FinOtherLoan]:
        record = FinOtherLoanDAO.get_by_id(db, tenant_id, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant_id: str, id: int) -> bool:
        record = FinOtherLoanDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


# ==================== 资金对账模块 ====================

class FinBankCheckDAO:
    """银行对账记录表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinBankCheck:
        record = FinBankCheck(**data)
        record.tenant = tenant
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinBankCheck]:
        return db.query(FinBankCheck).filter(
            and_(
                FinBankCheck.id == id,
                FinBankCheck.tenant == tenant,
                FinBankCheck.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_check_no(db: Session, tenant: str, check_no: str) -> Optional[FinBankCheck]:
        return db.query(FinBankCheck).filter(
            and_(
                FinBankCheck.check_no == check_no,
                FinBankCheck.tenant == tenant,
                FinBankCheck.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_flow_no(db: Session, tenant: str, bank_flow_no: str) -> Optional[FinBankCheck]:
        return db.query(FinBankCheck).filter(
            and_(
                FinBankCheck.bank_flow_no == bank_flow_no,
                FinBankCheck.tenant == tenant,
                FinBankCheck.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinBankCheck).filter(
            and_(
                FinBankCheck.tenant == tenant,
                FinBankCheck.is_del == 0
            )
        )
        if filters:
            if filters.get('account_id'):
                query = query.filter(FinBankCheck.account_id == filters['account_id'])
            if filters.get('check_date'):
                query = query.filter(FinBankCheck.check_date == filters['check_date'])
            if filters.get('bank_flow_type'):
                query = query.filter(FinBankCheck.bank_flow_type == filters['bank_flow_type'])
            if filters.get('relate_biz_type'):
                query = query.filter(FinBankCheck.relate_biz_type == filters['relate_biz_type'])
            if filters.get('check_status'):
                query = query.filter(FinBankCheck.check_status == filters['check_status'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinBankCheck]:
        record = FinBankCheckDAO.get_by_id(db, tenant, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = FinBankCheckDAO.get_by_id(db, tenant, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False

    @staticmethod
    def get_statistics(db: Session, tenant: str, account_id: int = None, check_date: date = None) -> dict:
        """获取银行对账统计信息"""
        query = db.query(
            FinBankCheck.check_status,
            func.count(FinBankCheck.id).label('count'),
            func.sum(FinBankCheck.bank_amount).label('total_amount'),
            func.sum(FinBankCheck.diff_amount).label('total_diff')
        ).filter(
            and_(
                FinBankCheck.tenant == tenant,
                FinBankCheck.is_del == 0
            )
        )
        if account_id:
            query = query.filter(FinBankCheck.account_id == account_id)
        if check_date:
            query = query.filter(FinBankCheck.check_date == check_date)
        query = query.group_by(FinBankCheck.check_status)

        results = query.all()
        statistics = {
            'total_count': 0,
            'total_amount': Decimal('0'),
            'total_diff': Decimal('0'),
            'status_detail': {}
        }
        for row in results:
            status = row[0]
            count = row[1] or 0
            amount = row[2] or Decimal('0')
            diff = row[3] or Decimal('0')
            statistics['total_count'] += count
            statistics['total_amount'] += amount
            statistics['total_diff'] += diff
            statistics['status_detail'][status] = {
                'count': count,
                'amount': amount,
                'diff': diff
            }
        return statistics

    @staticmethod
    def get_account_statistics(db: Session, tenant: str) -> List[dict]:
        """按银行账户统计对账情况"""
        query = db.query(
            FinBankCheck.account_id,
            FinBankCheck.account_name,
            func.count(FinBankCheck.id).label('count'),
            func.sum(FinBankCheck.bank_amount).label('total_amount'),
            func.sum(FinBankCheck.diff_amount).label('total_diff'),
            func.sum(func.case([(FinBankCheck.check_status == 1, 1)], else_=0)).label('unmatched_count'),
            func.sum(func.case([(FinBankCheck.check_status == 3, 1)], else_=0)).label('diff_count')
        ).filter(
            and_(
                FinBankCheck.tenant == tenant,
                FinBankCheck.is_del == 0
            )
        ).group_by(FinBankCheck.account_id, FinBankCheck.account_name)

        results = query.all()
        return [{
            'account_id': row[0],
            'account_name': row[1],
            'total_count': row[2] or 0,
            'total_amount': row[3] or Decimal('0'),
            'total_diff': row[4] or Decimal('0'),
            'unmatched_count': row[5] or 0,
            'diff_count': row[6] or 0
        } for row in results]


class FinDailyCashAccountDAO:
    """每日资金轧账表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinDailyCashAccount:
        record = FinDailyCashAccount(**data)
        record.tenant = tenant
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinDailyCashAccount]:
        return db.query(FinDailyCashAccount).filter(
            and_(
                FinDailyCashAccount.id == id,
                FinDailyCashAccount.tenant == tenant,
                FinDailyCashAccount.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_account_date(db: Session, tenant: str, account_date: datetime, account_id: int = None) -> Optional[FinDailyCashAccount]:
        query = db.query(FinDailyCashAccount).filter(
            and_(
                FinDailyCashAccount.account_date == account_date,
                FinDailyCashAccount.tenant == tenant,
                FinDailyCashAccount.is_del == 0
            )
        )
        if account_id:
            query = query.filter(FinDailyCashAccount.account_id == account_id)
        return query.first()
    
    @staticmethod
    def list(db: Session, tenant: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinDailyCashAccount).filter(
            and_(
                FinDailyCashAccount.tenant == tenant,
                FinDailyCashAccount.is_del == 0
            )
        )
        if filters:
            if filters.get('account_id'):
                query = query.filter(FinDailyCashAccount.account_id == filters['account_id'])
            if filters.get('project_id'):
                query = query.filter(FinDailyCashAccount.project_id == filters['project_id'])
            if filters.get('account_date'):
                query = query.filter(FinDailyCashAccount.account_date == filters['account_date'])
            if filters.get('account_status'):
                query = query.filter(FinDailyCashAccount.account_status == filters['account_status'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinDailyCashAccount]:
        record = FinDailyCashAccountDAO.get_by_id(db, tenant, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = FinDailyCashAccountDAO.get_by_id(db, tenant, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False

    @staticmethod
    def get_statistics(db: Session, tenant: str, account_date: date = None) -> dict:
        """获取每日资金轧账统计信息"""
        query = db.query(
            FinDailyCashAccount.account_status,
            func.count(FinDailyCashAccount.id).label('count'),
            func.sum(FinDailyCashAccount.total_receipt).label('total_receipt'),
            func.sum(FinDailyCashAccount.total_pay).label('total_pay'),
            func.sum(FinDailyCashAccount.balance_diff).label('total_diff')
        ).filter(
            and_(
                FinDailyCashAccount.tenant == tenant,
                FinDailyCashAccount.is_del == 0
            )
        )
        if account_date:
            query = query.filter(FinDailyCashAccount.account_date == account_date)
        query = query.group_by(FinDailyCashAccount.account_status)

        results = query.all()
        statistics = {
            'total_count': 0,
            'total_receipt': Decimal('0'),
            'total_pay': Decimal('0'),
            'total_diff': Decimal('0'),
            'status_detail': {}
        }
        for row in results:
            status = row[0]
            count = row[1] or 0
            receipt = row[2] or Decimal('0')
            pay = row[3] or Decimal('0')
            diff = row[4] or Decimal('0')
            statistics['total_count'] += count
            statistics['total_receipt'] += receipt
            statistics['total_pay'] += pay
            statistics['total_diff'] += diff
            statistics['status_detail'][status] = {
                'count': count,
                'receipt': receipt,
                'pay': pay,
                'diff': diff
            }
        return statistics

    @staticmethod
    def get_monthly_summary(db: Session, tenant: str, account_id: int = None) -> List[dict]:
        """获取月度资金汇总"""
        query = db.query(
            func.date_trunc('month', FinDailyCashAccount.account_date).label('month'),
            func.sum(FinDailyCashAccount.total_receipt).label('total_receipt'),
            func.sum(FinDailyCashAccount.total_refund).label('total_refund'),
            func.sum(FinDailyCashAccount.total_pay).label('total_pay'),
            func.sum(FinDailyCashAccount.balance_diff).label('total_diff')
        ).filter(
            and_(
                FinDailyCashAccount.tenant == tenant,
                FinDailyCashAccount.is_del == 0
            )
        )
        if account_id:
            query = query.filter(FinDailyCashAccount.account_id == account_id)
        query = query.group_by(func.date_trunc('month', FinDailyCashAccount.account_date))
        query = query.order_by(func.date_trunc('month', FinDailyCashAccount.account_date))

        results = query.all()
        return [{
            'month': row[0],
            'total_receipt': row[1] or Decimal('0'),
            'total_refund': row[2] or Decimal('0'),
            'total_pay': row[3] or Decimal('0'),
            'total_diff': row[4] or Decimal('0')
        } for row in results]


class FinChannelReconcileDAO:
    """渠道月度对账表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinChannelReconcile:
        record = FinChannelReconcile(**data)
        record.tenant = tenant
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinChannelReconcile]:
        return db.query(FinChannelReconcile).filter(
            and_(
                FinChannelReconcile.id == id,
                FinChannelReconcile.tenant == tenant,
                FinChannelReconcile.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_reconcile_no(db: Session, tenant: str, reconcile_no: str) -> Optional[FinChannelReconcile]:
        return db.query(FinChannelReconcile).filter(
            and_(
                FinChannelReconcile.reconcile_no == reconcile_no,
                FinChannelReconcile.tenant == tenant,
                FinChannelReconcile.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_channel_month(db: Session, tenant: str, channel_id: int, reconcile_month: str) -> Optional[FinChannelReconcile]:
        return db.query(FinChannelReconcile).filter(
            and_(
                FinChannelReconcile.channel_id == channel_id,
                FinChannelReconcile.reconcile_month == reconcile_month,
                FinChannelReconcile.tenant == tenant,
                FinChannelReconcile.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinChannelReconcile).filter(
            and_(
                FinChannelReconcile.tenant == tenant,
                FinChannelReconcile.is_del == 0
            )
        )
        if filters:
            if filters.get('channel_id'):
                query = query.filter(FinChannelReconcile.channel_id == filters['channel_id'])
            if filters.get('project_id'):
                query = query.filter(FinChannelReconcile.project_id == filters['project_id'])
            if filters.get('reconcile_month'):
                query = query.filter(FinChannelReconcile.reconcile_month == filters['reconcile_month'])
            if filters.get('reconcile_status'):
                query = query.filter(FinChannelReconcile.reconcile_status == filters['reconcile_status'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinChannelReconcile]:
        record = FinChannelReconcileDAO.get_by_id(db, tenant, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = FinChannelReconcileDAO.get_by_id(db, tenant, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False

    @staticmethod
    def get_statistics(db: Session, tenant: str, reconcile_month: str = None, project_id: int = None) -> dict:
        """获取渠道月度对账统计信息"""
        query = db.query(
            FinChannelReconcile.reconcile_status,
            func.count(FinChannelReconcile.id).label('count'),
            func.sum(FinChannelReconcile.channel_amount).label('channel_amount'),
            func.sum(FinChannelReconcile.system_amount).label('system_amount'),
            func.sum(FinChannelReconcile.diff_amount).label('total_diff')
        ).filter(
            and_(
                FinChannelReconcile.tenant == tenant,
                FinChannelReconcile.is_del == 0
            )
        )
        if reconcile_month:
            query = query.filter(FinChannelReconcile.reconcile_month == reconcile_month)
        if project_id:
            query = query.filter(FinChannelReconcile.project_id == project_id)
        query = query.group_by(FinChannelReconcile.reconcile_status)

        results = query.all()
        statistics = {
            'total_count': 0,
            'channel_amount': Decimal('0'),
            'system_amount': Decimal('0'),
            'total_diff': Decimal('0'),
            'status_detail': {}
        }
        for row in results:
            status = row[0]
            count = row[1] or 0
            channel = row[2] or Decimal('0')
            system = row[3] or Decimal('0')
            diff = row[4] or Decimal('0')
            statistics['total_count'] += count
            statistics['channel_amount'] += channel
            statistics['system_amount'] += system
            statistics['total_diff'] += diff
            statistics['status_detail'][status] = {
                'count': count,
                'channel_amount': channel,
                'system_amount': system,
                'diff': diff
            }
        return statistics

    @staticmethod
    def get_channel_statistics(db: Session, tenant: str) -> List[dict]:
        """按渠道统计对账情况"""
        query = db.query(
            FinChannelReconcile.channel_id,
            FinChannelReconcile.channel_name,
            func.count(FinChannelReconcile.id).label('count'),
            func.sum(FinChannelReconcile.channel_amount).label('channel_amount'),
            func.sum(FinChannelReconcile.system_amount).label('system_amount'),
            func.sum(FinChannelReconcile.diff_amount).label('total_diff'),
            func.sum(func.case([(FinChannelReconcile.reconcile_status == 1, 1)], else_=0)).label('pending_count'),
            func.sum(func.case([(FinChannelReconcile.reconcile_status == 3, 1)], else_=0)).label('diff_count')
        ).filter(
            and_(
                FinChannelReconcile.tenant == tenant,
                FinChannelReconcile.is_del == 0
            )
        ).group_by(FinChannelReconcile.channel_id, FinChannelReconcile.channel_name)

        results = query.all()
        return [{
            'channel_id': row[0],
            'channel_name': row[1],
            'total_count': row[2] or 0,
            'channel_amount': row[3] or Decimal('0'),
            'system_amount': row[4] or Decimal('0'),
            'total_diff': row[5] or Decimal('0'),
            'pending_count': row[6] or 0,
            'diff_count': row[7] or 0
        } for row in results]


# ==================== 会计凭证模块 ====================

class FinVoucherDAO:
    """会计凭证主表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinVoucher:
        record = FinVoucher(**data)
        record.tenant = tenant
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinVoucher]:
        return db.query(FinVoucher).filter(
            and_(
                FinVoucher.id == id,
                FinVoucher.tenant == tenant,
                FinVoucher.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_voucher_no(db: Session, tenant: str, voucher_no: str) -> Optional[FinVoucher]:
        return db.query(FinVoucher).filter(
            and_(
                FinVoucher.voucher_no == voucher_no,
                FinVoucher.tenant == tenant,
                FinVoucher.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinVoucher).filter(
            and_(
                FinVoucher.tenant == tenant,
                FinVoucher.is_del == 0
            )
        )
        if filters:
            if filters.get('voucher_type'):
                query = query.filter(FinVoucher.voucher_type == filters['voucher_type'])
            if filters.get('voucher_date'):
                query = query.filter(FinVoucher.voucher_date == filters['voucher_date'])
            if filters.get('voucher_status'):
                query = query.filter(FinVoucher.voucher_status == filters['voucher_status'])
            if filters.get('source_type'):
                query = query.filter(FinVoucher.source_type == filters['source_type'])
            if filters.get('is_red_flush'):
                query = query.filter(FinVoucher.is_red_flush == filters['is_red_flush'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinVoucher]:
        record = FinVoucherDAO.get_by_id(db, tenant, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = FinVoucherDAO.get_by_id(db, tenant, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinVoucherItemDAO:
    """会计凭证明细表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinVoucherItem:
        record = FinVoucherItem(**data)
        record.tenant = tenant
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinVoucherItem]:
        return db.query(FinVoucherItem).filter(
            and_(
                FinVoucherItem.id == id,
                FinVoucherItem.tenant == tenant,
                FinVoucherItem.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_voucher_id(db: Session, tenant: str, voucher_id: int) -> List[FinVoucherItem]:
        return db.query(FinVoucherItem).filter(
            and_(
                FinVoucherItem.voucher_id == voucher_id,
                FinVoucherItem.tenant == tenant,
                FinVoucherItem.is_del == 0
            )
        ).order_by(FinVoucherItem.item_sort).all()
    
    @staticmethod
    def bulk_create(db: Session, tenant: str, details: List[dict]) -> List[FinVoucherItem]:
        records = []
        for d in details:
            record = FinVoucherItem(**d)
            record.tenant = tenant
            records.append(record)
        db.add_all(records)
        db.commit()
        return records
    
    @staticmethod
    def list(db: Session, tenant: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinVoucherItem).filter(
            and_(
                FinVoucherItem.tenant == tenant,
                FinVoucherItem.is_del == 0
            )
        )
        if filters:
            if filters.get('voucher_id'):
                query = query.filter(FinVoucherItem.voucher_id == filters['voucher_id'])
            if filters.get('subject_id'):
                query = query.filter(FinVoucherItem.subject_id == filters['subject_id'])
            if filters.get('subject_type'):
                query = query.filter(FinVoucherItem.subject_type == filters['subject_type'])
            if filters.get('project_id'):
                query = query.filter(FinVoucherItem.project_id == filters['project_id'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinVoucherItem]:
        record = FinVoucherItemDAO.get_by_id(db, tenant, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = FinVoucherItemDAO.get_by_id(db, tenant, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


# ==================== 财务审计追溯模块 ====================

class FinFinanceAuditDAO:
    """财务审计记录表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinOperateLog:
        data['tenant'] = tenant
        record = FinOperateLog(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinOperateLog]:
        return db.query(FinOperateLog).filter(
            and_(
                FinOperateLog.id == id,
                FinOperateLog.tenant == tenant,
                FinOperateLog.is_del == 0
            )
        ).first()
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinOperateLog]:
        record = db.query(FinOperateLog).filter(
            and_(
                FinOperateLog.id == id,
                FinOperateLog.tenant == tenant,
                FinOperateLog.is_del == 0
            )
        ).first()
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            db.commit()
            db.refresh(record)
        return record
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = db.query(FinOperateLog).filter(
            and_(
                FinOperateLog.id == id,
                FinOperateLog.tenant == tenant,
                FinOperateLog.is_del == 0
            )
        ).first()
        if record:
            record.is_del = 1
            db.commit()
            return True
        return False
    
    @staticmethod
    def list(db: Session, tenant: str, params: dict) -> tuple:
        query = db.query(FinOperateLog).filter(
            and_(
                FinOperateLog.tenant == tenant,
                FinOperateLog.is_del == 0
            )
        )
        page = params.get('page', 1)
        page_size = params.get('page_size', 10)
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return total, items


class FinOperationLogDAO:
    """操作日志表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinOperateLog:
        data['tenant'] = tenant
        record = FinOperateLog(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinOperateLog]:
        return db.query(FinOperateLog).filter(
            and_(
                FinOperateLog.id == id,
                FinOperateLog.tenant == tenant,
                FinOperateLog.is_del == 0
            )
        ).first()
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinOperateLog]:
        record = db.query(FinOperateLog).filter(
            and_(
                FinOperateLog.id == id,
                FinOperateLog.tenant == tenant,
                FinOperateLog.is_del == 0
            )
        ).first()
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            db.commit()
            db.refresh(record)
        return record
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = db.query(FinOperateLog).filter(
            and_(
                FinOperateLog.id == id,
                FinOperateLog.tenant == tenant,
                FinOperateLog.is_del == 0
            )
        ).first()
        if record:
            record.is_del = 1
            db.commit()
            return True
        return False
    
    @staticmethod
    def list(db: Session, tenant: str, params: dict) -> tuple:
        query = db.query(FinOperateLog).filter(
            and_(
                FinOperateLog.tenant == tenant,
                FinOperateLog.is_del == 0
            )
        )
        page = params.get('page', 1)
        page_size = params.get('page_size', 10)
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return total, items


# ==================== 财务统计报表模块 ====================

class FinCashFlowDAO:
    """现金流统计表数据访问对象"""
    
    @staticmethod
    def create(db: Session, data: dict) -> FinCashFlow:
        record = FinCashFlow(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, id: int, tenant: str) -> Optional[FinCashFlow]:
        return db.query(FinCashFlow).filter(
            and_(
                FinCashFlow.id == id,
                FinCashFlow.tenant == tenant,
                FinCashFlow.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_list(db: Session, tenant: str, skip: int = 0, limit: int = 100, 
                 filters: Optional[Dict] = None) -> List[FinCashFlow]:
        query = db.query(FinCashFlow).filter(
            and_(
                FinCashFlow.tenant == tenant,
                FinCashFlow.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinCashFlow.project_id == filters['project_id'])
            if filters.get('year_month'):
                query = query.filter(FinCashFlow.year_month == filters['year_month'])
        return query.order_by(FinCashFlow.year_month).offset(skip).limit(limit).all()


class FinReceivableStatDAO:
    """应收账款统计表数据访问对象"""
    
    @staticmethod
    def create(db: Session, data: dict) -> FinReceivableStat:
        record = FinReceivableStat(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, id: int, tenant: str) -> Optional[FinReceivableStat]:
        return db.query(FinReceivableStat).filter(
            and_(
                FinReceivableStat.id == id,
                FinReceivableStat.tenant == tenant,
                FinReceivableStat.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_list(db: Session, tenant: str, skip: int = 0, limit: int = 100, 
                 filters: Optional[Dict] = None) -> List[FinReceivableStat]:
        query = db.query(FinReceivableStat).filter(
            and_(
                FinReceivableStat.tenant == tenant,
                FinReceivableStat.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinReceivableStat.project_id == filters['project_id'])
            if filters.get('year_month'):
                query = query.filter(FinReceivableStat.year_month == filters['year_month'])
        return query.order_by(FinReceivableStat.year_month).offset(skip).limit(limit).all()


class FinTaxStatDAO:
    """税务统计表数据访问对象"""
    
    @staticmethod
    def create(db: Session, data: dict) -> FinTaxStat:
        record = FinTaxStat(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, id: int, tenant: str) -> Optional[FinTaxStat]:
        return db.query(FinTaxStat).filter(
            and_(
                FinTaxStat.id == id,
                FinTaxStat.tenant == tenant,
                FinTaxStat.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_list(db: Session, tenant: str, skip: int = 0, limit: int = 100, 
                 filters: Optional[Dict] = None) -> List[FinTaxStat]:
        query = db.query(FinTaxStat).filter(
            and_(
                FinTaxStat.tenant == tenant,
                FinTaxStat.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinTaxStat.project_id == filters['project_id'])
            if filters.get('year_month'):
                query = query.filter(FinTaxStat.year_month == filters['year_month'])
            if filters.get('tax_type'):
                query = query.filter(FinTaxStat.tax_type == filters['tax_type'])
        return query.order_by(FinTaxStat.year_month).offset(skip).limit(limit).all()


class FinCommissionStatDAO:
    """佣金统计表数据访问对象"""
    
    @staticmethod
    def create(db: Session, data: dict) -> FinCommissionStat:
        record = FinCommissionStat(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, id: int, tenant: str) -> Optional[FinCommissionStat]:
        return db.query(FinCommissionStat).filter(
            and_(
                FinCommissionStat.id == id,
                FinCommissionStat.tenant == tenant,
                FinCommissionStat.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_list(db: Session, tenant: str, skip: int = 0, limit: int = 100, 
                 filters: Optional[Dict] = None) -> List[FinCommissionStat]:
        query = db.query(FinCommissionStat).filter(
            and_(
                FinCommissionStat.tenant == tenant,
                FinCommissionStat.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinCommissionStat.project_id == filters['project_id'])
            if filters.get('year_month'):
                query = query.filter(FinCommissionStat.year_month == filters['year_month'])
        return query.order_by(FinCommissionStat.year_month).offset(skip).limit(limit).all()


class FinOperateLogDAO:
    """财务操作审计日志表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinOperateLog:
        data['tenant'] = tenant
        record = FinOperateLog(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinOperateLog]:
        return db.query(FinOperateLog).filter(
            and_(
                FinOperateLog.id == id,
                FinOperateLog.tenant == tenant,
                FinOperateLog.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_operate_no(db: Session, tenant: str, operate_no: str) -> Optional[FinOperateLog]:
        return db.query(FinOperateLog).filter(
            and_(
                FinOperateLog.operate_no == operate_no,
                FinOperateLog.tenant == tenant,
                FinOperateLog.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinOperateLog).filter(
            and_(
                FinOperateLog.tenant == tenant,
                FinOperateLog.is_del == 0
            )
        )
        if filters:
            if filters.get('biz_module'):
                query = query.filter(FinOperateLog.biz_module == filters['biz_module'])
            if filters.get('operate_type'):
                query = query.filter(FinOperateLog.operate_type == filters['operate_type'])
            if filters.get('biz_type'):
                query = query.filter(FinOperateLog.biz_type == filters['biz_type'])
            if filters.get('biz_id'):
                query = query.filter(FinOperateLog.biz_id == filters['biz_id'])
            if filters.get('voucher_id'):
                query = query.filter(FinOperateLog.voucher_id == filters['voucher_id'])
            if filters.get('operate_user_id'):
                query = query.filter(FinOperateLog.operate_user_id == filters['operate_user_id'])
            if filters.get('operate_status'):
                query = query.filter(FinOperateLog.operate_status == filters['operate_status'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinOperateLog]:
        record = FinOperateLogDAO.get_by_id(db, tenant, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = FinOperateLogDAO.get_by_id(db, tenant, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinDataChangeLogDAO:
    """数据变更记录表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinDataChangeLog:
        data['tenant'] = tenant
        record = FinDataChangeLog(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinDataChangeLog]:
        return db.query(FinDataChangeLog).filter(
            and_(
                FinDataChangeLog.id == id,
                FinDataChangeLog.tenant == tenant,
                FinDataChangeLog.is_del == 0
            )
        ).first()
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinDataChangeLog]:
        record = db.query(FinDataChangeLog).filter(
            and_(
                FinDataChangeLog.id == id,
                FinDataChangeLog.tenant == tenant,
                FinDataChangeLog.is_del == 0
            )
        ).first()
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            db.commit()
            db.refresh(record)
        return record
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = db.query(FinDataChangeLog).filter(
            and_(
                FinDataChangeLog.id == id,
                FinDataChangeLog.tenant == tenant,
                FinDataChangeLog.is_del == 0
            )
        ).first()
        if record:
            record.is_del = 1
            db.commit()
            return True
        return False
    
    @staticmethod
    def list(db: Session, tenant: str, params: dict) -> tuple:
        query = db.query(FinDataChangeLog).filter(
            and_(
                FinDataChangeLog.tenant == tenant,
                FinDataChangeLog.is_del == 0
            )
        )
        page = params.get('page', 1)
        page_size = params.get('page_size', 10)
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return total, items


# ==================== 财务统计报表模块 ====================

class FinCashFlowDAO:
    """现金流统计表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinCashFlow:
        data['tenant'] = tenant
        record = FinCashFlow(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinCashFlow]:
        return db.query(FinCashFlow).filter(
            and_(
                FinCashFlow.id == id,
                FinCashFlow.tenant == tenant,
                FinCashFlow.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinCashFlow).filter(
            and_(
                FinCashFlow.tenant == tenant,
                FinCashFlow.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinCashFlow.project_id == filters['project_id'])
            if filters.get('stat_month'):
                query = query.filter(FinCashFlow.stat_month == filters['stat_month'])
            if filters.get('stat_type'):
                query = query.filter(FinCashFlow.stat_type == filters['stat_type'])
            if filters.get('stat_status'):
                query = query.filter(FinCashFlow.stat_status == filters['stat_status'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinCashFlow]:
        record = FinCashFlowDAO.get_by_id(db, tenant, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = FinCashFlowDAO.get_by_id(db, tenant, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinReceivableStatDAO:
    """应收款统计表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinReceivableStat:
        data['tenant'] = tenant
        record = FinReceivableStat(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinReceivableStat]:
        return db.query(FinReceivableStat).filter(
            and_(
                FinReceivableStat.id == id,
                FinReceivableStat.tenant == tenant,
                FinReceivableStat.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinReceivableStat).filter(
            and_(
                FinReceivableStat.tenant == tenant,
                FinReceivableStat.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinReceivableStat.project_id == filters['project_id'])
            if filters.get('stat_month'):
                query = query.filter(FinReceivableStat.stat_month == filters['stat_month'])
            if filters.get('stat_type'):
                query = query.filter(FinReceivableStat.stat_type == filters['stat_type'])
            if filters.get('stat_status'):
                query = query.filter(FinReceivableStat.stat_status == filters['stat_status'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinReceivableStat]:
        record = FinReceivableStatDAO.get_by_id(db, tenant, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = FinReceivableStatDAO.get_by_id(db, tenant, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinTaxStatDAO:
    """税务统计表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinTaxStat:
        data['tenant'] = tenant
        record = FinTaxStat(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinTaxStat]:
        return db.query(FinTaxStat).filter(
            and_(
                FinTaxStat.id == id,
                FinTaxStat.tenant == tenant,
                FinTaxStat.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinTaxStat).filter(
            and_(
                FinTaxStat.tenant == tenant,
                FinTaxStat.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinTaxStat.project_id == filters['project_id'])
            if filters.get('stat_month'):
                query = query.filter(FinTaxStat.stat_month == filters['stat_month'])
            if filters.get('stat_year'):
                query = query.filter(FinTaxStat.stat_year == filters['stat_year'])
            if filters.get('declared_status'):
                query = query.filter(FinTaxStat.declared_status == filters['declared_status'])
            if filters.get('stat_status'):
                query = query.filter(FinTaxStat.stat_status == filters['stat_status'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinTaxStat]:
        record = FinTaxStatDAO.get_by_id(db, tenant, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = FinTaxStatDAO.get_by_id(db, tenant, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinCommissionStatDAO:
    """佣金统计表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinCommissionStat:
        data['tenant'] = tenant
        record = FinCommissionStat(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinCommissionStat]:
        return db.query(FinCommissionStat).filter(
            and_(
                FinCommissionStat.id == id,
                FinCommissionStat.tenant == tenant,
                FinCommissionStat.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinCommissionStat).filter(
            and_(
                FinCommissionStat.tenant == tenant,
                FinCommissionStat.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinCommissionStat.project_id == filters['project_id'])
            if filters.get('channel_id'):
                query = query.filter(FinCommissionStat.channel_id == filters['channel_id'])
            if filters.get('channel_type'):
                query = query.filter(FinCommissionStat.channel_type == filters['channel_type'])
            if filters.get('stat_month'):
                query = query.filter(FinCommissionStat.stat_month == filters['stat_month'])
            if filters.get('stat_year'):
                query = query.filter(FinCommissionStat.stat_year == filters['stat_year'])
            if filters.get('stat_status'):
                query = query.filter(FinCommissionStat.stat_status == filters['stat_status'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinCommissionStat]:
        record = FinCommissionStatDAO.get_by_id(db, tenant, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = FinCommissionStatDAO.get_by_id(db, tenant, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


# ==================== 财务报表模块 ====================

class FinCashFlowStatementDAO:
    """现金流量表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinCashFlowStatement:
        data['tenant'] = tenant
        record = FinCashFlowStatement(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinCashFlowStatement]:
        return db.query(FinCashFlowStatement).filter(
            and_(
                FinCashFlowStatement.id == id,
                FinCashFlowStatement.tenant == tenant,
                FinCashFlowStatement.is_del == 0
            )
        ).first()
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinCashFlowStatement]:
        record = FinCashFlowStatementDAO.get_by_id(db, tenant, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = FinCashFlowStatementDAO.get_by_id(db, tenant, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False
    
    @staticmethod
    def list(db: Session, tenant: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinCashFlowStatement).filter(
            and_(
                FinCashFlowStatement.tenant == tenant,
                FinCashFlowStatement.is_del == 0
            )
        )
        if filters:
            if filters.get('report_period'):
                query = query.filter(FinCashFlowStatement.report_period == filters['report_period'])
            if filters.get('report_type'):
                query = query.filter(FinCashFlowStatement.report_type == filters['report_type'])
            if filters.get('report_status'):
                query = query.filter(FinCashFlowStatement.report_status == filters['report_status'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items


class FinProfitStatementDAO:
    """利润表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinProfitStatement:
        data['tenant'] = tenant
        record = FinProfitStatement(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinProfitStatement]:
        return db.query(FinProfitStatement).filter(
            and_(
                FinProfitStatement.id == id,
                FinProfitStatement.tenant == tenant,
                FinProfitStatement.is_del == 0
            )
        ).first()
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinProfitStatement]:
        record = FinProfitStatementDAO.get_by_id(db, tenant, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = FinProfitStatementDAO.get_by_id(db, tenant, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False
    
    @staticmethod
    def list(db: Session, tenant: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinProfitStatement).filter(
            and_(
                FinProfitStatement.tenant == tenant,
                FinProfitStatement.is_del == 0
            )
        )
        if filters:
            if filters.get('report_period'):
                query = query.filter(FinProfitStatement.report_period == filters['report_period'])
            if filters.get('report_type'):
                query = query.filter(FinProfitStatement.report_type == filters['report_type'])
            if filters.get('report_status'):
                query = query.filter(FinProfitStatement.report_status == filters['report_status'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items


class FinBalanceSheetDAO:
    """资产负债表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinBalanceSheet:
        data['tenant'] = tenant
        record = FinBalanceSheet(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinBalanceSheet]:
        return db.query(FinBalanceSheet).filter(
            and_(
                FinBalanceSheet.id == id,
                FinBalanceSheet.tenant == tenant,
                FinBalanceSheet.is_del == 0
            )
        ).first()
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinBalanceSheet]:
        record = FinBalanceSheetDAO.get_by_id(db, tenant, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = FinBalanceSheetDAO.get_by_id(db, tenant, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False
    
    @staticmethod
    def list(db: Session, tenant: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinBalanceSheet).filter(
            and_(
                FinBalanceSheet.tenant == tenant,
                FinBalanceSheet.is_del == 0
            )
        )
        if filters:
            if filters.get('report_period'):
                query = query.filter(FinBalanceSheet.report_period == filters['report_period'])
            if filters.get('report_type'):
                query = query.filter(FinBalanceSheet.report_type == filters['report_type'])
            if filters.get('report_status'):
                query = query.filter(FinBalanceSheet.report_status == filters['report_status'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items


class FinFinancialReportDAO:
    """财务报表主表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant: str, data: dict) -> FinFinancialReport:
        data['tenant'] = tenant
        record = FinFinancialReport(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant: str, id: int) -> Optional[FinFinancialReport]:
        return db.query(FinFinancialReport).filter(
            and_(
                FinFinancialReport.id == id,
                FinFinancialReport.tenant == tenant,
                FinFinancialReport.is_del == 0
            )
        ).first()
    
    @staticmethod
    def update(db: Session, tenant: str, id: int, update_data: dict) -> Optional[FinFinancialReport]:
        record = FinFinancialReportDAO.get_by_id(db, tenant, id)
        if record:
            for key, value in update_data.items():
                setattr(record, key, value)
            record.version += 1
            db.commit()
            db.refresh(record)
            return record
        return None
    
    @staticmethod
    def delete(db: Session, tenant: str, id: int) -> bool:
        record = FinFinancialReportDAO.get_by_id(db, tenant, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False
    
    @staticmethod
    def list(db: Session, tenant: str, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinFinancialReport).filter(
            and_(
                FinFinancialReport.tenant == tenant,
                FinFinancialReport.is_del == 0
            )
        )
        if filters:
            if filters.get('report_period'):
                query = query.filter(FinFinancialReport.report_period == filters['report_period'])
            if filters.get('report_type'):
                query = query.filter(FinFinancialReport.report_type == filters['report_type'])
            if filters.get('report_status'):
                query = query.filter(FinFinancialReport.status == filters['report_status'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
"""
房地产SaaS财务管理系统 - 数据访问层（DAO）
所有业务表的CRUD操作
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from finance.model.finance_models import (
    # 财务基础档案模块
    FinProjectFinConfig, FinAccount, FinSubject, FinTaxRate, FinBankInfo, FinDiscountRule,
    # 房款收支模块
    FinInstallmentPlan, FinPriceDiff, FinReceiptRecord, FinRefundRecord, FinDepositAccount,
    # 票据税务合规模块
    FinInvoice, FinInvoiceRed, FinReceipt, FinMaintainFund, FinTaxDeclare,
    # 佣金支付模块
    FinCommissionPay, FinCommissionDeduct, FinSalesCommission,
    # 项目成本模块
    FinExpenseReimbursement, FinCostPay, FinAdCost, FinProjectEngCost,
    # 应收应付往来台账模块
    FinAccountReceivable, FinAccountPayable, FinAdvancePay, FinOtherLoan,
    # 资金对账模块
    FinBankCheck, FinDailyCashAccount, FinChannelReconcile,
    # 会计凭证模块
    FinVoucher, FinVoucherItem,
    # 财务审计追溯模块
    FinOperateLog,
    # 财务统计报表模块
    FinCashFlow, FinReceivableStat, FinTaxStat, FinCommissionStat
)


# ==================== 财务基础档案模块 ====================

class FinProjectFinConfigDAO:
    """项目财务配置表数据访问对象"""
    
    @staticmethod
    def create(db: Session, data: dict) -> FinProjectFinConfig:
        record = FinProjectFinConfig(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, id: int, tenant: str) -> Optional[FinProjectFinConfig]:
        return db.query(FinProjectFinConfig).filter(
            and_(
                FinProjectFinConfig.id == id,
                FinProjectFinConfig.tenant == tenant,
                FinProjectFinConfig.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_project_id(db: Session, project_id: int, tenant: str) -> Optional[FinProjectFinConfig]:
        return db.query(FinProjectFinConfig).filter(
            and_(
                FinProjectFinConfig.project_id == project_id,
                FinProjectFinConfig.tenant == tenant,
                FinProjectFinConfig.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_list(db: Session, tenant: str, skip: int = 0, limit: int = 100, 
                 filters: Optional[Dict] = None) -> List[FinProjectFinConfig]:
        query = db.query(FinProjectFinConfig).filter(
            and_(
                FinProjectFinConfig.tenant == tenant,
                FinProjectFinConfig.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinProjectFinConfig.project_id == filters['project_id'])
            if filters.get('project_name'):
                query = query.filter(FinProjectFinConfig.project_name.like(f"%{filters['project_name']}%"))
            if filters.get('calc_mode'):
                query = query.filter(FinProjectFinConfig.calc_mode == filters['calc_mode'])
            if filters.get('is_active') is not None:
                query = query.filter(FinProjectFinConfig.is_active == filters['is_active'])
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, record: FinProjectFinConfig, update_data: dict) -> FinProjectFinConfig:
        for key, value in update_data.items():
            setattr(record, key, value)
        record.version += 1
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def delete(db: Session, id: int, tenant: str) -> bool:
        record = FinProjectFinConfigDAO.get_by_id(db, id, tenant)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinAccountDAO:
    """账户表数据访问对象"""
    
    @staticmethod
    def create(db: Session, data: dict) -> FinAccount:
        record = FinAccount(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, id: int, tenant: str) -> Optional[FinAccount]:
        return db.query(FinAccount).filter(
            and_(
                FinAccount.id == id,
                FinAccount.tenant == tenant,
                FinAccount.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_code(db: Session, account_code: str, tenant: str) -> Optional[FinAccount]:
        return db.query(FinAccount).filter(
            and_(
                FinAccount.account_code == account_code,
                FinAccount.tenant == tenant,
                FinAccount.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_list(db: Session, tenant: str, skip: int = 0, limit: int = 100, 
                 filters: Optional[Dict] = None) -> List[FinAccount]:
        query = db.query(FinAccount).filter(
            and_(
                FinAccount.tenant == tenant,
                FinAccount.is_del == 0
            )
        )
        if filters:
            if filters.get('account_name'):
                query = query.filter(FinAccount.account_name.like(f"%{filters['account_name']}%"))
            if filters.get('account_type'):
                query = query.filter(FinAccount.account_type == filters['account_type'])
            if filters.get('account_holder'):
                query = query.filter(FinAccount.account_holder.like(f"%{filters['account_holder']}%"))
            if filters.get('mobile'):
                query = query.filter(FinAccount.mobile.like(f"%{filters['mobile']}%"))
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, record: FinAccount, update_data: dict) -> FinAccount:
        for key, value in update_data.items():
            setattr(record, key, value)
        record.version += 1
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def delete(db: Session, id: int, tenant: str) -> bool:
        record = FinAccountDAO.get_by_id(db, id, tenant)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinSubjectDAO:
    """科目表数据访问对象"""
    
    @staticmethod
    def create(db: Session, data: dict) -> FinSubject:
        record = FinSubject(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, id: int, tenant: str) -> Optional[FinSubject]:
        return db.query(FinSubject).filter(
            and_(
                FinSubject.id == id,
                FinSubject.tenant == tenant,
                FinSubject.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_code(db: Session, subject_code: str, tenant: str) -> Optional[FinSubject]:
        return db.query(FinSubject).filter(
            and_(
                FinSubject.subject_code == subject_code,
                FinSubject.tenant == tenant,
                FinSubject.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_list(db: Session, tenant: str, skip: int = 0, limit: int = 100, 
                 filters: Optional[Dict] = None) -> List[FinSubject]:
        query = db.query(FinSubject).filter(
            and_(
                FinSubject.tenant == tenant,
                FinSubject.is_del == 0
            )
        )
        if filters:
            if filters.get('subject_name'):
                query = query.filter(FinSubject.subject_name.like(f"%{filters['subject_name']}%"))
            if filters.get('subject_type'):
                query = query.filter(FinSubject.subject_type == filters['subject_type'])
            if filters.get('account_id'):
                query = query.filter(FinSubject.account_id == filters['account_id'])
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, record: FinSubject, update_data: dict) -> FinSubject:
        for key, value in update_data.items():
            setattr(record, key, value)
        record.version += 1
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def delete(db: Session, id: int, tenant: str) -> bool:
        record = FinSubjectDAO.get_by_id(db, id, tenant)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinTaxRateDAO:
    """税率配置表数据访问对象"""
    
    @staticmethod
    def create(db: Session, data: dict) -> FinTaxRate:
        record = FinTaxRate(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, id: int, tenant: str) -> Optional[FinTaxRate]:
        return db.query(FinTaxRate).filter(
            and_(
                FinTaxRate.id == id,
                FinTaxRate.tenant == tenant,
                FinTaxRate.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_tax_type(db: Session, tax_type: str, tenant: str) -> Optional[FinTaxRate]:
        return db.query(FinTaxRate).filter(
            and_(
                FinTaxRate.tax_type == tax_type,
                FinTaxRate.tenant == tenant,
                FinTaxRate.is_del == 0,
                FinTaxRate.is_active == 1
            )
        ).first()
    
    @staticmethod
    def get_list(db: Session, tenant: str, skip: int = 0, limit: int = 100, 
                 filters: Optional[Dict] = None) -> List[FinTaxRate]:
        query = db.query(FinTaxRate).filter(
            and_(
                FinTaxRate.tenant == tenant,
                FinTaxRate.is_del == 0
            )
        )
        if filters:
            if filters.get('tax_type'):
                query = query.filter(FinTaxRate.tax_type == filters['tax_type'])
            if filters.get('is_active') is not None:
                query = query.filter(FinTaxRate.is_active == filters['is_active'])
            if filters.get('calc_mode'):
                query = query.filter(FinTaxRate.calc_mode == filters['calc_mode'])
            if filters.get('bind_subject_id'):
                query = query.filter(FinTaxRate.bind_subject_id == filters['bind_subject_id'])
            if filters.get('biz_scope'):
                query = query.filter(FinTaxRate.biz_scope.like(f"%{filters['biz_scope']}%"))
            if filters.get('create_user_id'):
                query = query.filter(FinTaxRate.create_user_id == filters['create_user_id'])
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, record: FinTaxRate, update_data: dict) -> FinTaxRate:
        for key, value in update_data.items():
            setattr(record, key, value)
        record.version += 1
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def delete(db: Session, id: int, tenant: str) -> bool:
        record = FinTaxRateDAO.get_by_id(db, id, tenant)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinBankInfoDAO:
    """银行信息表数据访问对象"""
    
    @staticmethod
    def create(db: Session, data: dict) -> FinBankInfo:
        record = FinBankInfo(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, id: int, tenant: str) -> Optional[FinBankInfo]:
        return db.query(FinBankInfo).filter(
            and_(
                FinBankInfo.id == id,
                FinBankInfo.tenant == tenant,
                FinBankInfo.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_list(db: Session, tenant: str, skip: int = 0, limit: int = 100, 
                 filters: Optional[Dict] = None) -> List[FinBankInfo]:
        query = db.query(FinBankInfo).filter(
            and_(
                FinBankInfo.tenant == tenant,
                FinBankInfo.is_del == 0
            )
        )
        if filters:
            if filters.get('bank_name'):
                query = query.filter(FinBankInfo.bank_name.like(f"%{filters['bank_name']}%"))
            if filters.get('account_name'):
                query = query.filter(FinBankInfo.account_name.like(f"%{filters['account_name']}%"))
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, record: FinBankInfo, update_data: dict) -> FinBankInfo:
        for key, value in update_data.items():
            setattr(record, key, value)
        record.version += 1
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def delete(db: Session, id: int, tenant: str) -> bool:
        record = FinBankInfoDAO.get_by_id(db, id, tenant)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinDiscountRuleDAO:
    """优惠规则配置表数据访问对象"""
    
    @staticmethod
    def create(db: Session, data: dict) -> FinDiscountRule:
        record = FinDiscountRule(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, id: int, tenant: str) -> Optional[FinDiscountRule]:
        return db.query(FinDiscountRule).filter(
            and_(
                FinDiscountRule.id == id,
                FinDiscountRule.tenant == tenant,
                FinDiscountRule.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_list(db: Session, tenant: str, skip: int = 0, limit: int = 100, 
                 filters: Optional[Dict] = None) -> List[FinDiscountRule]:
        query = db.query(FinDiscountRule).filter(
            and_(
                FinDiscountRule.tenant == tenant,
                FinDiscountRule.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinDiscountRule.project_id == filters['project_id'])
            if filters.get('rule_type'):
                query = query.filter(FinDiscountRule.rule_type == filters['rule_type'])
            if filters.get('is_active') is not None:
                query = query.filter(FinDiscountRule.is_active == filters['is_active'])
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, record: FinDiscountRule, update_data: dict) -> FinDiscountRule:
        for key, value in update_data.items():
            setattr(record, key, value)
        record.version += 1
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def delete(db: Session, id: int, tenant: str) -> bool:
        record = FinDiscountRuleDAO.get_by_id(db, id, tenant)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


# ==================== 房款收支模块 ====================

class FinInstallmentPlanDAO:
    """分期回款计划表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: int, data: dict) -> FinInstallmentPlan:
        record = FinInstallmentPlan(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int, id: int) -> Optional[FinInstallmentPlan]:
        return db.query(FinInstallmentPlan).filter(
            and_(
                FinInstallmentPlan.id == id,
                FinInstallmentPlan.tenant == tenant_id,
                FinInstallmentPlan.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_order_id(db: Session, tenant_id: int, order_id: int) -> List[FinInstallmentPlan]:
        return db.query(FinInstallmentPlan).filter(
            and_(
                FinInstallmentPlan.order_id == order_id,
                FinInstallmentPlan.tenant == tenant_id,
                FinInstallmentPlan.is_del == 0
            )
        ).order_by(FinInstallmentPlan.installment_no).all()
    
    @staticmethod
    def list(db: Session, tenant_id: int, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinInstallmentPlan).filter(
            and_(
                FinInstallmentPlan.tenant == tenant_id,
                FinInstallmentPlan.is_del == 0
            )
        )
        if filters:
            if filters.get('customer_id'):
                query = query.filter(FinInstallmentPlan.customer_id == filters['customer_id'])
            if filters.get('plan_status'):
                query = query.filter(FinInstallmentPlan.plan_status == filters['plan_status'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: int, id: int, update_data: dict) -> Optional[FinInstallmentPlan]:
        record = FinInstallmentPlanDAO.get_by_id(db, tenant_id, id)
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
        record = FinInstallmentPlanDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinPriceDiffDAO:
    """面积差价记录表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: int, data: dict) -> FinPriceDiff:
        record = FinPriceDiff(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int, id: int) -> Optional[FinPriceDiff]:
        return db.query(FinPriceDiff).filter(
            and_(
                FinPriceDiff.id == id,
                FinPriceDiff.tenant == tenant_id,
                FinPriceDiff.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_order_id(db: Session, tenant_id: int, order_id: int) -> List[FinPriceDiff]:
        return db.query(FinPriceDiff).filter(
            and_(
                FinPriceDiff.order_id == order_id,
                FinPriceDiff.tenant == tenant_id,
                FinPriceDiff.is_del == 0
            )
        ).order_by(FinPriceDiff.created_at.desc()).all()
    
    @staticmethod
    def list(db: Session, tenant_id: int, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinPriceDiff).filter(
            and_(
                FinPriceDiff.tenant == tenant_id,
                FinPriceDiff.is_del == 0
            )
        )
        if filters:
            if filters.get('customer_id'):
                query = query.filter(FinPriceDiff.customer_id == filters['customer_id'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: int, id: int, update_data: dict) -> Optional[FinPriceDiff]:
        record = FinPriceDiffDAO.get_by_id(db, tenant_id, id)
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
        record = FinPriceDiffDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinReceiptRecordDAO:
    """收款记录表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: int, data: dict) -> FinReceiptRecord:
        record = FinReceiptRecord(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int, id: int) -> Optional[FinReceiptRecord]:
        return db.query(FinReceiptRecord).filter(
            and_(
                FinReceiptRecord.id == id,
                FinReceiptRecord.tenant == tenant_id,
                FinReceiptRecord.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_receipt_no(db: Session, tenant_id: int, receipt_no: str) -> Optional[FinReceiptRecord]:
        return db.query(FinReceiptRecord).filter(
            and_(
                FinReceiptRecord.receipt_no == receipt_no,
                FinReceiptRecord.tenant == tenant_id,
                FinReceiptRecord.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: int, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinReceiptRecord).filter(
            and_(
                FinReceiptRecord.tenant == tenant_id,
                FinReceiptRecord.is_del == 0
            )
        )
        if filters:
            if filters.get('order_id'):
                query = query.filter(FinReceiptRecord.order_id == filters['order_id'])
            if filters.get('customer_id'):
                query = query.filter(FinReceiptRecord.customer_id == filters['customer_id'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: int, id: int, update_data: dict) -> Optional[FinReceiptRecord]:
        record = FinReceiptRecordDAO.get_by_id(db, tenant_id, id)
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
        record = FinReceiptRecordDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinRefundRecordDAO:
    """退款记录表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: int, data: dict) -> FinRefundRecord:
        record = FinRefundRecord(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int, id: int) -> Optional[FinRefundRecord]:
        return db.query(FinRefundRecord).filter(
            and_(
                FinRefundRecord.id == id,
                FinRefundRecord.tenant == tenant_id,
                FinRefundRecord.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_refund_no(db: Session, tenant_id: int, refund_no: str) -> Optional[FinRefundRecord]:
        return db.query(FinRefundRecord).filter(
            and_(
                FinRefundRecord.refund_no == refund_no,
                FinRefundRecord.tenant == tenant_id,
                FinRefundRecord.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: int, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinRefundRecord).filter(
            and_(
                FinRefundRecord.tenant == tenant_id,
                FinRefundRecord.is_del == 0
            )
        )
        if filters:
            if filters.get('order_id'):
                query = query.filter(FinRefundRecord.order_id == filters['order_id'])
            if filters.get('customer_id'):
                query = query.filter(FinRefundRecord.customer_id == filters['customer_id'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: int, id: int, update_data: dict) -> Optional[FinRefundRecord]:
        record = FinRefundRecordDAO.get_by_id(db, tenant_id, id)
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
        record = FinRefundRecordDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinDepositAccountDAO:
    """保证金账户表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: int, data: dict) -> FinDepositAccount:
        record = FinDepositAccount(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int, id: int) -> Optional[FinDepositAccount]:
        return db.query(FinDepositAccount).filter(
            and_(
                FinDepositAccount.id == id,
                FinDepositAccount.tenant == tenant_id,
                FinDepositAccount.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_customer_id(db: Session, tenant_id: int, customer_id: int) -> Optional[FinDepositAccount]:
        return db.query(FinDepositAccount).filter(
            and_(
                FinDepositAccount.customer_id == customer_id,
                FinDepositAccount.tenant == tenant_id,
                FinDepositAccount.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: int, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinDepositAccount).filter(
            and_(
                FinDepositAccount.tenant == tenant_id,
                FinDepositAccount.is_del == 0
            )
        )
        if filters:
            if filters.get('customer_id'):
                query = query.filter(FinDepositAccount.customer_id == filters['customer_id'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: int, id: int, update_data: dict) -> Optional[FinDepositAccount]:
        record = FinDepositAccountDAO.get_by_id(db, tenant_id, id)
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
        record = FinDepositAccountDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


# ==================== 票据税务合规模块 ====================

class FinInvoiceDAO:
    """蓝字发票主表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: int, data: dict) -> FinInvoice:
        record = FinInvoice(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int, id: int) -> Optional[FinInvoice]:
        return db.query(FinInvoice).filter(
            and_(
                FinInvoice.id == id,
                FinInvoice.tenant == tenant_id,
                FinInvoice.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_invoice_no(db: Session, tenant_id: int, invoice_no: str) -> Optional[FinInvoice]:
        return db.query(FinInvoice).filter(
            and_(
                FinInvoice.invoice_no == invoice_no,
                FinInvoice.tenant == tenant_id,
                FinInvoice.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: int, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinInvoice).filter(
            and_(
                FinInvoice.tenant == tenant_id,
                FinInvoice.is_del == 0
            )
        )
        if filters:
            if filters.get('order_id'):
                query = query.filter(FinInvoice.order_id == filters['order_id'])
            if filters.get('invoice_type'):
                query = query.filter(FinInvoice.invoice_type == filters['invoice_type'])
            if filters.get('invoice_status'):
                query = query.filter(FinInvoice.invoice_status == filters['invoice_status'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: int, id: int, update_data: dict) -> Optional[FinInvoice]:
        record = FinInvoiceDAO.get_by_id(db, tenant_id, id)
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
        record = FinInvoiceDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinInvoiceRedDAO:
    """红字冲销发票表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: int, data: dict) -> FinInvoiceRed:
        record = FinInvoiceRed(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int, id: int) -> Optional[FinInvoiceRed]:
        return db.query(FinInvoiceRed).filter(
            and_(
                FinInvoiceRed.id == id,
                FinInvoiceRed.tenant == tenant_id,
                FinInvoiceRed.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_original_no(db: Session, tenant_id: int, original_invoice_no: str) -> List[FinInvoiceRed]:
        return db.query(FinInvoiceRed).filter(
            and_(
                FinInvoiceRed.original_invoice_no == original_invoice_no,
                FinInvoiceRed.tenant == tenant_id,
                FinInvoiceRed.is_del == 0
            )
        ).all()
    
    @staticmethod
    def list(db: Session, tenant_id: int, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinInvoiceRed).filter(
            and_(
                FinInvoiceRed.tenant == tenant_id,
                FinInvoiceRed.is_del == 0
            )
        )
        if filters:
            if filters.get('order_id'):
                query = query.filter(FinInvoiceRed.order_id == filters['order_id'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: int, id: int, update_data: dict) -> Optional[FinInvoiceRed]:
        record = FinInvoiceRedDAO.get_by_id(db, tenant_id, id)
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
        record = FinInvoiceRedDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinReceiptDAO:
    """内部收据表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: int, data: dict) -> FinReceipt:
        record = FinReceipt(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int, id: int) -> Optional[FinReceipt]:
        return db.query(FinReceipt).filter(
            and_(
                FinReceipt.id == id,
                FinReceipt.tenant == tenant_id,
                FinReceipt.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_receipt_no(db: Session, tenant_id: int, receipt_no: str) -> Optional[FinReceipt]:
        return db.query(FinReceipt).filter(
            and_(
                FinReceipt.receipt_no == receipt_no,
                FinReceipt.tenant == tenant_id,
                FinReceipt.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: int, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinReceipt).filter(
            and_(
                FinReceipt.tenant == tenant_id,
                FinReceipt.is_del == 0
            )
        )
        if filters:
            if filters.get('customer_id'):
                query = query.filter(FinReceipt.customer_id == filters['customer_id'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: int, id: int, update_data: dict) -> Optional[FinReceipt]:
        record = FinReceiptDAO.get_by_id(db, tenant_id, id)
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
        record = FinReceiptDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinMaintainFundDAO:
    """维修基金台账表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: int, data: dict) -> FinMaintainFund:
        record = FinMaintainFund(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int, id: int) -> Optional[FinMaintainFund]:
        return db.query(FinMaintainFund).filter(
            and_(
                FinMaintainFund.id == id,
                FinMaintainFund.tenant == tenant_id,
                FinMaintainFund.is_del == 0
            )
        ).first()
    
    @staticmethod
    def get_by_order_id(db: Session, tenant_id: int, order_id: int) -> Optional[FinMaintainFund]:
        return db.query(FinMaintainFund).filter(
            and_(
                FinMaintainFund.order_id == order_id,
                FinMaintainFund.tenant == tenant_id,
                FinMaintainFund.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: int, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinMaintainFund).filter(
            and_(
                FinMaintainFund.tenant == tenant_id,
                FinMaintainFund.is_del == 0
            )
        )
        if filters:
            if filters.get('project_id'):
                query = query.filter(FinMaintainFund.project_id == filters['project_id'])
            if filters.get('paid_status'):
                query = query.filter(FinMaintainFund.paid_status == filters['paid_status'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: int, id: int, update_data: dict) -> Optional[FinMaintainFund]:
        record = FinMaintainFundDAO.get_by_id(db, tenant_id, id)
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
        record = FinMaintainFundDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False


class FinTaxDeclareDAO:
    """税务申报记录表数据访问对象"""
    
    @staticmethod
    def create(db: Session, tenant_id: int, data: dict) -> FinTaxDeclare:
        record = FinTaxDeclare(**data)
        record.tenant = tenant_id
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int, id: int) -> Optional[FinTaxDeclare]:
        return db.query(FinTaxDeclare).filter(
            and_(
                FinTaxDeclare.id == id,
                FinTaxDeclare.tenant == tenant_id,
                FinTaxDeclare.is_del == 0
            )
        ).first()
    
    @staticmethod
    def list(db: Session, tenant_id: int, filters: Optional[Dict] = None) -> tuple:
        query = db.query(FinTaxDeclare).filter(
            and_(
                FinTaxDeclare.tenant == tenant_id,
                FinTaxDeclare.is_del == 0
            )
        )
        if filters:
            if filters.get('declare_month'):
                query = query.filter(FinTaxDeclare.declare_month == filters['declare_month'])
            if filters.get('page') and filters.get('page_size'):
                skip = (filters['page'] - 1) * filters['page_size']
                total = query.count()
                items = query.offset(skip).limit(filters['page_size']).all()
                return total, items
        total = query.count()
        items = query.all()
        return total, items
    
    @staticmethod
    def update(db: Session, tenant_id: int, id: int, update_data: dict) -> Optional[FinTaxDeclare]:
        record = FinTaxDeclareDAO.get_by_id(db, tenant_id, id)
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
        record = FinTaxDeclareDAO.get_by_id(db, tenant_id, id)
        if record:
            record.is_del = 1
            record.version += 1
            db.commit()
            return True
        return False
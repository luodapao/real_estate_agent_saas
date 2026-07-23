﻿"""
房地产SaaS财务管理系统 - 资金对账服务层
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal

from ..dao.finance_dao_ext import (
    FinBankCheckDAO,
    FinDailyCashAccountDAO,
    FinChannelReconcileDAO,
)
from ..schemas.reconciliation_schemas import (
    BankCheckCreate,
    BankCheckUpdate,
    BankCheckMatch,
    BankCheckFinish,
    BankCheckResponse,
    DailyCashAccountCreate,
    DailyCashAccountUpdate,
    DailyCashAccountAudit,
    DailyCashAccountResponse,
    ChannelReconcileCreate,
    ChannelReconcileUpdate,
    ChannelReconcileConfirm,
    ChannelReconcileResponse,
)
from ..schemas.base_schemas import PageRequest, PageResponse


class ReconciliationService:
    """资金对账服务类"""

    @staticmethod
    def _generate_doc_no(db: Session, tenant: str, prefix: str) -> str:
        """
        生成单据编号（私有方法）
        :param db: 数据库会话
        :param tenant: 租户编码
        :param prefix: 编号前缀（DZ:银行对账, QD:渠道对账）
        :return: 生成的单据编号
        """
        date_str = datetime.now().strftime("%Y%m%d")
        max_no = 0

        if prefix == "DZ":
            result = db.execute(
                "SELECT MAX(check_no) FROM fin_bank_check WHERE tenant = :tenant AND check_no LIKE :pattern",
                {"tenant": tenant, "pattern": f"{prefix}{date_str}%"}
            ).scalar()
        elif prefix == "QD":
            result = db.execute(
                "SELECT MAX(reconcile_no) FROM fin_channel_reconcile WHERE tenant = :tenant AND reconcile_no LIKE :pattern",
                {"tenant": tenant, "pattern": f"{prefix}{date_str}%"}
            ).scalar()

        if result:
            seq_str = result[-4:]
            max_no = int(seq_str) + 1

        seq_str = str(max_no).zfill(4)
        return f"{prefix}{date_str}{seq_str}"

    # ==================== 银行对账记录 ====================

    @staticmethod
    def _calculate_bank_check_diff(bank_amount: Decimal, system_amount: Decimal) -> Decimal:
        """计算银行对账差异金额"""
        return bank_amount - system_amount

    @staticmethod
    def _determine_bank_check_status(diff_amount: Decimal, check_status: int = None) -> int:
        """根据差异金额确定对账状态"""
        if check_status == 4 or check_status == 5:
            return check_status
        if diff_amount == Decimal('0'):
            return 2
        return 3

    @staticmethod
    def create_bank_check(db: Session, tenant: str, data: BankCheckCreate, create_user_id: int = 1) -> BankCheckResponse:
        """创建银行对账记录"""
        data_dict = data.model_dump()
        data_dict['tenant'] = tenant
        if not data_dict.get('check_no'):
            data_dict['check_no'] = ReconciliationService._generate_doc_no(db, tenant, "DZ")
        data_dict['system_amount'] = data_dict.get('system_amount', Decimal('0'))
        data_dict['diff_amount'] = ReconciliationService._calculate_bank_check_diff(
            data_dict['bank_amount'],
            data_dict['system_amount']
        )
        if 'check_status' not in data_dict or data_dict['check_status'] == 1:
            data_dict['check_status'] = ReconciliationService._determine_bank_check_status(
                data_dict['diff_amount']
            )
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinBankCheckDAO.create(db, tenant, data_dict)
        return BankCheckResponse.from_orm(entity)

    @staticmethod
    def get_bank_check(db: Session, tenant: str, id: int) -> Optional[BankCheckResponse]:
        """获取银行对账记录详情"""
        entity = FinBankCheckDAO.get_by_id(db, tenant, id)
        return BankCheckResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_bank_check(db: Session, tenant: str, id: int, data: BankCheckUpdate) -> Optional[BankCheckResponse]:
        """更新银行对账记录"""
        update_data = data.model_dump(exclude_unset=True)
        if 'system_amount' in update_data:
            entity = FinBankCheckDAO.get_by_id(db, tenant, id)
            if entity:
                update_data['diff_amount'] = ReconciliationService._calculate_bank_check_diff(
                    entity.bank_amount,
                    update_data['system_amount']
                )
                if 'check_status' not in update_data:
                    update_data['check_status'] = ReconciliationService._determine_bank_check_status(
                        update_data['diff_amount'],
                        entity.check_status
                    )
        entity = FinBankCheckDAO.update(db, tenant, id, update_data)
        return BankCheckResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_bank_check(db: Session, tenant: str, id: int) -> bool:
        """删除银行对账记录"""
        return FinBankCheckDAO.delete(db, tenant, id)

    @staticmethod
    def list_bank_checks(db: Session, tenant: str, page_request: PageRequest, filters: Optional[dict] = None) -> PageResponse[BankCheckResponse]:
        """分页查询银行对账记录列表"""
        query_filters = filters or {}
        query_filters['page'] = page_request.page
        query_filters['page_size'] = page_request.page_size
        total, items = FinBankCheckDAO.list(db, tenant, query_filters)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[BankCheckResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def auto_match_bank_check(db: Session, tenant: str, data: BankCheckMatch) -> dict:
        """自动匹配银行对账记录"""
        filters = {}
        if data.account_id:
            filters['account_id'] = data.account_id
        if data.check_date:
            filters['check_date'] = data.check_date
        filters['check_status'] = 1
        filters['page'] = 1
        filters['page_size'] = 10000

        total, items = FinBankCheckDAO.list(db, tenant, filters)
        matched_count = 0
        unmatched_count = 0

        for item in items:
            if abs(item.bank_amount) <= data.amount_tolerance:
                update_data = {
                    'system_amount': item.bank_amount,
                    'check_status': 2,
                    'check_finish_time': datetime.now()
                }
                update_data['diff_amount'] = ReconciliationService._calculate_bank_check_diff(
                    item.bank_amount,
                    update_data['system_amount']
                )
                FinBankCheckDAO.update(db, tenant, item.id, update_data)
                matched_count += 1
            else:
                unmatched_count += 1

        return {
            'total_count': total,
            'matched_count': matched_count,
            'unmatched_count': unmatched_count
        }

    @staticmethod
    def finish_bank_check(db: Session, tenant: str, data: BankCheckFinish) -> Optional[BankCheckResponse]:
        """完成银行对账"""
        entity = FinBankCheckDAO.get_by_id(db, tenant, data.id)
        if not entity:
            return None

        update_data = {
            'system_amount': data.system_amount,
            'relate_biz_type': data.relate_biz_type,
            'check_user_id': data.check_user_id,
            'check_finish_time': datetime.now()
        }

        if data.relate_biz_id:
            update_data['relate_biz_id'] = data.relate_biz_id
        if data.relate_biz_no:
            update_data['relate_biz_no'] = data.relate_biz_no
        if data.diff_reason:
            update_data['diff_reason'] = data.diff_reason
        if data.solve_remark:
            update_data['solve_remark'] = data.solve_remark

        update_data['diff_amount'] = ReconciliationService._calculate_bank_check_diff(
            entity.bank_amount,
            data.system_amount
        )
        update_data['check_status'] = ReconciliationService._determine_bank_check_status(
            update_data['diff_amount']
        )

        entity = FinBankCheckDAO.update(db, tenant, data.id, update_data)
        return BankCheckResponse.from_orm(entity) if entity else None

    # ==================== 每日资金轧账 ====================

    @staticmethod
    def _calculate_daily_cash_ending(beginning_balance: Decimal, total_receipt: Decimal, 
                                      total_refund: Decimal, total_pay: Decimal) -> Decimal:
        """计算当日系统期末余额"""
        return beginning_balance + total_receipt - total_refund - total_pay

    @staticmethod
    def _calculate_daily_cash_diff(ending_balance: Decimal, bank_ending_balance: Decimal) -> Decimal:
        """计算账实余额差异"""
        return ending_balance - bank_ending_balance

    @staticmethod
    def _validate_daily_cash_receipt(house_receipt: Decimal, other_receipt: Decimal, 
                                      total_receipt: Decimal) -> Decimal:
        """验证收款总额"""
        calculated_total = house_receipt + other_receipt
        if total_receipt != calculated_total:
            return calculated_total
        return total_receipt

    @staticmethod
    def _validate_daily_cash_pay(commission_pay: Decimal, cost_pay: Decimal, 
                                  other_pay: Decimal, total_pay: Decimal) -> Decimal:
        """验证付款总额"""
        calculated_total = commission_pay + cost_pay + other_pay
        if total_pay != calculated_total:
            return calculated_total
        return total_pay

    @staticmethod
    def _determine_daily_cash_status(balance_diff: Decimal, account_status: int = None) -> int:
        """根据余额差异确定轧账状态"""
        if account_status == 4 or account_status == 5:
            return account_status
        if balance_diff == Decimal('0'):
            return 2
        return 3

    @staticmethod
    def create_daily_cash_account(db: Session, tenant: str, data: DailyCashAccountCreate, create_user_id: int = 1) -> DailyCashAccountResponse:
        """创建每日资金轧账记录"""
        data_dict = data.model_dump()
        data_dict['tenant'] = tenant
        
        data_dict['total_receipt'] = ReconciliationService._validate_daily_cash_receipt(
            data_dict.get('house_receipt', Decimal('0')),
            data_dict.get('other_receipt', Decimal('0')),
            data_dict.get('total_receipt', Decimal('0'))
        )
        
        data_dict['total_pay'] = ReconciliationService._validate_daily_cash_pay(
            data_dict.get('commission_pay', Decimal('0')),
            data_dict.get('cost_pay', Decimal('0')),
            data_dict.get('other_pay', Decimal('0')),
            data_dict.get('total_pay', Decimal('0'))
        )
        
        data_dict['ending_balance'] = ReconciliationService._calculate_daily_cash_ending(
            data_dict.get('beginning_balance', Decimal('0')),
            data_dict.get('total_receipt', Decimal('0')),
            data_dict.get('total_refund', Decimal('0')),
            data_dict.get('total_pay', Decimal('0'))
        )
        
        data_dict['balance_diff'] = ReconciliationService._calculate_daily_cash_diff(
            data_dict['ending_balance'],
            data_dict.get('bank_ending_balance', Decimal('0'))
        )
        
        if 'account_status' not in data_dict or data_dict['account_status'] == 1:
            data_dict['account_status'] = ReconciliationService._determine_daily_cash_status(
                data_dict['balance_diff']
            )
        
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinDailyCashAccountDAO.create(db, tenant, data_dict)
        return DailyCashAccountResponse.from_orm(entity)

    @staticmethod
    def get_daily_cash_account(db: Session, tenant: str, id: int) -> Optional[DailyCashAccountResponse]:
        """获取每日资金轧账记录详情"""
        entity = FinDailyCashAccountDAO.get_by_id(db, tenant, id)
        return DailyCashAccountResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_daily_cash_account(db: Session, tenant: str, id: int, data: DailyCashAccountUpdate) -> Optional[DailyCashAccountResponse]:
        """更新每日资金轧账记录"""
        update_data = data.model_dump(exclude_unset=True)
        entity = FinDailyCashAccountDAO.get_by_id(db, tenant, id)
        
        if entity and (
            'house_receipt' in update_data or 'other_receipt' in update_data or
            'commission_pay' in update_data or 'cost_pay' in update_data or 'other_pay' in update_data or
            'total_receipt' in update_data or 'total_refund' in update_data or 'total_pay' in update_data or
            'beginning_balance' in update_data or 'bank_ending_balance' in update_data
        ):
            house_receipt = update_data.get('house_receipt', entity.house_receipt)
            other_receipt = update_data.get('other_receipt', entity.other_receipt)
            total_receipt = update_data.get('total_receipt', entity.total_receipt)
            
            commission_pay = update_data.get('commission_pay', entity.commission_pay)
            cost_pay = update_data.get('cost_pay', entity.cost_pay)
            other_pay = update_data.get('other_pay', entity.other_pay)
            total_pay = update_data.get('total_pay', entity.total_pay)
            
            total_refund = update_data.get('total_refund', entity.total_refund)
            beginning_balance = update_data.get('beginning_balance', entity.beginning_balance)
            bank_ending_balance = update_data.get('bank_ending_balance', entity.bank_ending_balance)
            
            update_data['total_receipt'] = ReconciliationService._validate_daily_cash_receipt(
                house_receipt, other_receipt, total_receipt
            )
            update_data['total_pay'] = ReconciliationService._validate_daily_cash_pay(
                commission_pay, cost_pay, other_pay, total_pay
            )
            update_data['ending_balance'] = ReconciliationService._calculate_daily_cash_ending(
                beginning_balance, update_data['total_receipt'], total_refund, update_data['total_pay']
            )
            update_data['balance_diff'] = ReconciliationService._calculate_daily_cash_diff(
                update_data['ending_balance'], bank_ending_balance
            )
            
            if 'account_status' not in update_data:
                update_data['account_status'] = ReconciliationService._determine_daily_cash_status(
                    update_data['balance_diff'], entity.account_status
                )
        
        entity = FinDailyCashAccountDAO.update(db, tenant, id, update_data)
        return DailyCashAccountResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_daily_cash_account(db: Session, tenant: str, id: int) -> bool:
        """删除每日资金轧账记录"""
        return FinDailyCashAccountDAO.delete(db, tenant, id)

    @staticmethod
    def list_daily_cash_accounts(db: Session, tenant: str, page_request: PageRequest, filters: Optional[dict] = None) -> PageResponse[DailyCashAccountResponse]:
        """分页查询每日资金轧账记录列表"""
        query_filters = filters or {}
        query_filters['page'] = page_request.page
        query_filters['page_size'] = page_request.page_size
        total, items = FinDailyCashAccountDAO.list(db, tenant, query_filters)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[DailyCashAccountResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def audit_daily_cash_account(db: Session, tenant: str, data: DailyCashAccountAudit) -> Optional[DailyCashAccountResponse]:
        """审核每日资金轧账记录"""
        entity = FinDailyCashAccountDAO.get_by_id(db, tenant, data.id)
        if not entity:
            return None

        update_data = {
            'audit_user_id': data.audit_user_id,
            'audit_time': datetime.now(),
            'account_status': data.audit_status
        }
        
        if data.diff_remark:
            update_data['diff_remark'] = data.diff_remark
        
        entity = FinDailyCashAccountDAO.update(db, tenant, data.id, update_data)
        return DailyCashAccountResponse.from_orm(entity) if entity else None

    # ==================== 渠道月度对账 ====================

    @staticmethod
    def _calculate_channel_diff(channel_amount: Decimal, system_amount: Decimal, 
                                 deduct_amount: Decimal) -> Decimal:
        """计算渠道对账差异金额"""
        return channel_amount - system_amount - deduct_amount

    @staticmethod
    def _determine_channel_status(diff_amount: Decimal, reconcile_status: int = None) -> int:
        """根据差异金额确定渠道对账状态"""
        if reconcile_status == 4 or reconcile_status == 5:
            return reconcile_status
        if diff_amount == Decimal('0'):
            return 2
        return 3

    @staticmethod
    def create_channel_reconcile(db: Session, tenant: str, data: ChannelReconcileCreate, create_user_id: int = 1) -> ChannelReconcileResponse:
        """创建渠道月度对账记录"""
        data_dict = data.model_dump()
        data_dict['tenant'] = tenant
        if not data_dict.get('reconcile_no'):
            data_dict['reconcile_no'] = ReconciliationService._generate_doc_no(db, tenant, "QD")
        
        data_dict['diff_amount'] = ReconciliationService._calculate_channel_diff(
            data_dict.get('channel_amount', Decimal('0')),
            data_dict.get('system_amount', Decimal('0')),
            data_dict.get('deduct_amount', Decimal('0'))
        )
        
        if 'reconcile_status' not in data_dict or data_dict['reconcile_status'] == 1:
            data_dict['reconcile_status'] = ReconciliationService._determine_channel_status(
                data_dict['diff_amount']
            )
        
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinChannelReconcileDAO.create(db, tenant, data_dict)
        return ChannelReconcileResponse.from_orm(entity)

    @staticmethod
    def get_channel_reconcile(db: Session, tenant: str, id: int) -> Optional[ChannelReconcileResponse]:
        """获取渠道月度对账记录详情"""
        entity = FinChannelReconcileDAO.get_by_id(db, tenant, id)
        return ChannelReconcileResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_channel_reconcile(db: Session, tenant: str, id: int, data: ChannelReconcileUpdate) -> Optional[ChannelReconcileResponse]:
        """更新渠道月度对账记录"""
        update_data = data.model_dump(exclude_unset=True)
        entity = FinChannelReconcileDAO.get_by_id(db, tenant, id)
        
        if entity and (
            'channel_amount' in update_data or 'system_amount' in update_data or 
            'deduct_amount' in update_data
        ):
            channel_amount = update_data.get('channel_amount', entity.channel_amount)
            system_amount = update_data.get('system_amount', entity.system_amount)
            deduct_amount = update_data.get('deduct_amount', entity.deduct_amount)
            
            update_data['diff_amount'] = ReconciliationService._calculate_channel_diff(
                channel_amount, system_amount, deduct_amount
            )
            
            if 'reconcile_status' not in update_data:
                update_data['reconcile_status'] = ReconciliationService._determine_channel_status(
                    update_data['diff_amount'], entity.reconcile_status
                )
        
        entity = FinChannelReconcileDAO.update(db, tenant, id, update_data)
        return ChannelReconcileResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_channel_reconcile(db: Session, tenant: str, id: int) -> bool:
        """删除渠道月度对账记录"""
        return FinChannelReconcileDAO.delete(db, tenant, id)

    @staticmethod
    def list_channel_reconciles(db: Session, tenant: str, page_request: PageRequest, filters: Optional[dict] = None) -> PageResponse[ChannelReconcileResponse]:
        """分页查询渠道月度对账记录列表"""
        query_filters = filters or {}
        query_filters['page'] = page_request.page
        query_filters['page_size'] = page_request.page_size
        total, items = FinChannelReconcileDAO.list(db, tenant, query_filters)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[ChannelReconcileResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def confirm_channel_reconcile(db: Session, tenant: str, data: ChannelReconcileConfirm) -> Optional[ChannelReconcileResponse]:
        """确认渠道月度对账"""
        entity = FinChannelReconcileDAO.get_by_id(db, tenant, data.id)
        if not entity:
            return None

        update_data = {
            'reconcile_user_id': data.reconcile_user_id,
            'reconcile_status': data.confirm_status,
            'reconcile_time': datetime.now()
        }
        
        if data.diff_reason:
            update_data['diff_reason'] = data.diff_reason
        if data.solve_plan:
            update_data['solve_plan'] = data.solve_plan
        
        entity = FinChannelReconcileDAO.update(db, tenant, data.id, update_data)
        return ChannelReconcileResponse.from_orm(entity) if entity else None


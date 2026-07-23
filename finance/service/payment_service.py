﻿"""
房地产SaaS财务管理系统 - 房款收支服务层
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from ..dao import (
    FinInstallmentPlanDAO,
    FinPriceDiffDAO,
    FinReceiptRecordDAO,
    FinRefundRecordDAO,
    FinDepositAccountDAO,
)
from ..schemas.payment_schemas import (
    InstallmentPlanCreate,
    InstallmentPlanUpdate,
    InstallmentPlanResponse,
    PriceDiffCreate,
    PriceDiffUpdate,
    PriceDiffResponse,
    ReceiptRecordCreate,
    ReceiptRecordUpdate,
    ReceiptRecordResponse,
    RefundRecordCreate,
    RefundRecordUpdate,
    RefundRecordResponse,
    DepositAccountCreate,
    DepositAccountUpdate,
    DepositAccountResponse,
)
from ..schemas.base_schemas import PageRequest, PageResponse


class PaymentService:
    """房款收支服务类"""

    @staticmethod
    def _generate_doc_no(db: Session, tenant_id: int, prefix: str) -> str:
        """
        生成单据编号（私有方法）
        :param db: 数据库会话
        :param tenant_id: 租户ID
        :param prefix: 编号前缀（FQ:分期, CJ:差价, SK:收款, TK:退款, DJ:定金）
        :return: 生成的单据编号
        """
        # 获取当前日期（格式：YYYYMMDD）
        date_str = datetime.now().strftime("%Y%m%d")
        
        # 查询当天最大编号
        max_no = 0
        if prefix == "FQ":
            result = db.execute(
                text("SELECT MAX(plan_no) FROM fin_installment_plan WHERE tenant = :tenant AND plan_no LIKE :pattern"),
                {"tenant": tenant_id, "pattern": f"{prefix}{date_str}%"}
            ).scalar()
        elif prefix == "CJ":
            result = db.execute(
                text("SELECT MAX(diff_no) FROM fin_price_diff WHERE tenant = :tenant AND diff_no LIKE :pattern"),
                {"tenant": tenant_id, "pattern": f"{prefix}{date_str}%"}
            ).scalar()
        elif prefix == "SK":
            result = db.execute(
                text("SELECT MAX(receipt_no) FROM fin_receipt_record WHERE tenant = :tenant AND receipt_no LIKE :pattern"),
                {"tenant": tenant_id, "pattern": f"{prefix}{date_str}%"}
            ).scalar()
        elif prefix == "TK":
            result = db.execute(
                text("SELECT MAX(refund_no) FROM fin_refund_record WHERE tenant = :tenant AND refund_no LIKE :pattern"),
                {"tenant": tenant_id, "pattern": f"{prefix}{date_str}%"}
            ).scalar()
        elif prefix == "DJ":
            result = db.execute(
                text("SELECT MAX(deposit_no) FROM fin_deposit_account WHERE tenant = :tenant AND deposit_no LIKE :pattern"),
                {"tenant": tenant_id, "pattern": f"{prefix}{date_str}%"}
            ).scalar()
        
        if result:
            # 提取序列号部分并加1
            seq_str = result[-4:]
            max_no = int(seq_str) + 1
        
        # 生成4位序列号（不足补0）
        seq_str = str(max_no).zfill(4)
        
        return f"{prefix}{date_str}{seq_str}"

    @staticmethod
    def create_installment_plan(db: Session, tenant_id: int, data: InstallmentPlanCreate, create_user_id: int = 1) -> dict:
        """创建分期回款计划"""
        plan_no = PaymentService._generate_doc_no(db, tenant_id, "FQ")
        data_dict = {
            'plan_no': plan_no,
            'project_id': data.project_id,
            'project_name': '测试项目',
            'house_id': 1,
            'house_no': '1-1-101',
            'customer_id': data.customer_id,
            'customer_name': '测试客户',
            'contract_id': 1,
            'project_fin_config_id': 1,
            'tax_tpl_id': 1,
            'calc_mode': 1,
            'income_subject_id': 1,
            'total_period': data.installment_count,
            'period_no': 1,
            'due_date': data.first_payment_date,
            'period_untax_amt': data.down_payment_untax_amt,
            'period_vat': data.down_payment_tax,
            'period_maintain': 0,
            'period_total': data.down_payment_amount,
            'received_amount': 0,
            'unpaid_amount': data.down_payment_amount,
            'create_user_id': create_user_id,
            'update_user_id': create_user_id,
        }
        entity = FinInstallmentPlanDAO.create(db, tenant_id, data_dict)
        entity_dict = entity.__dict__.copy()
        entity_dict.pop('_sa_instance_state', None)
        return entity_dict

    @staticmethod
    def get_installment_plan(db: Session, tenant_id: int, id: int) -> Optional[InstallmentPlanResponse]:
        """获取分期回款计划详情"""
        entity = FinInstallmentPlanDAO.get_by_id(db, tenant_id, id)
        return InstallmentPlanResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_installment_plan(db: Session, tenant_id: int, id: int, data: InstallmentPlanUpdate) -> Optional[InstallmentPlanResponse]:
        """更新分期回款计划"""
        entity = FinInstallmentPlanDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return InstallmentPlanResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_installment_plan(db: Session, tenant_id: int, id: int) -> bool:
        """删除分期回款计划"""
        return FinInstallmentPlanDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_installment_plans(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[InstallmentPlanResponse]:
        """分页查询分期回款计划列表"""
        total, items = FinInstallmentPlanDAO.list(db, tenant_id, page_request.model_dump())
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[InstallmentPlanResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_price_diff(db: Session, tenant_id: int, data: PriceDiffCreate, create_user_id: int = 1) -> PriceDiffResponse:
        """创建面积差价调整记录"""
        diff_no = PaymentService._generate_doc_no(db, tenant_id, "CJ")
        data_dict = {
            'diff_no': diff_no,
            'project_id': 1,
            'project_name': '测试项目',
            'house_id': data.house_id,
            'house_no': '1-1-101',
            'contract_id': 1,
            'customer_id': data.customer_id,
            'customer_name': '测试客户',
            'project_fin_config_id': 1,
            'tax_tpl_id': 1,
            'calc_mode': 1,
            'income_subject_id': 1,
            'predict_area': data.original_area,
            'actual_area': data.actual_area,
            'diff_area': data.area_diff,
            'unit_price': data.unit_price,
            'diff_untax_amt': data.diff_untax_amt,
            'diff_vat': data.diff_tax,
            'diff_total': data.diff_total_amt,
            'diff_type': 1 if data.diff_type == '补收' else 2,
            'create_user_id': create_user_id,
            'update_user_id': create_user_id,
        }
        entity = FinPriceDiffDAO.create(db, tenant_id, data_dict)
        return PriceDiffResponse.from_orm(entity)

    @staticmethod
    def get_area_price_adjustment(db: Session, tenant_id: int, id: int) -> Optional[PriceDiffResponse]:
        """获取面积差价调整详情"""
        entity = FinPriceDiffDAO.get_by_id(db, tenant_id, id)
        return PriceDiffResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_area_price_adjustment(db: Session, tenant_id: int, id: int, data: PriceDiffUpdate) -> Optional[PriceDiffResponse]:
        """更新面积差价调整"""
        entity = FinPriceDiffDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return PriceDiffResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_area_price_adjustment(db: Session, tenant_id: int, id: int) -> bool:
        """删除面积差价调整"""
        return FinPriceDiffDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_area_price_adjustments(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[PriceDiffResponse]:
        """分页查询面积差价调整列表"""
        total, items = FinPriceDiffDAO.list(db, tenant_id, page_request.model_dump())
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[PriceDiffResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_receipt_record(db: Session, tenant_id: int, data: ReceiptRecordCreate, create_user_id: int = 1) -> ReceiptRecordResponse:
        """创建收款记录"""
        receipt_no = PaymentService._generate_doc_no(db, tenant_id, "SK")
        receipt_type_map = {'定金': 1, '首付': 2, '分期': 3, '面积补差': 4, '车位款': 5, '储藏室款': 6, '其他': 7}
        pay_way_map = {'现金': 1, '转账': 2, '微信': 3, '支付宝': 4, '刷卡': 5, '按揭': 6, '银行汇票': 7}
        data_dict = {
            'receipt_no': receipt_no,
            'project_id': data.project_id,
            'project_name': '测试项目',
            'house_id': 1,
            'house_no': '1-1-101',
            'contract_id': 1,
            'customer_id': data.customer_id,
            'customer_name': '测试客户',
            'account_id': data.account_id,
            'account_name': '测试账户',
            'account_type': 1,
            'project_fin_config_id': 1,
            'tax_tpl_id': 1,
            'income_subject_id': 1,
            'receipt_date': datetime.now(),
            'receipt_type': receipt_type_map.get(data.receipt_type, 7),
            'pay_way': pay_way_map.get(data.payment_method, 2),
            'payer_name': data.payer_name or '测试付款人',
            'payer_account': data.bank_account_no or '',
            'receipt_amount': data.receipt_total_amt,
            'untax_principal': data.receipt_untax_amt,
            'tax_amount': data.receipt_tax,
            'maintain_amount': data.receipt_agency_fee,
            'other_fee_amount': 0,
            'order_id': data.order_id,
            'create_user_id': create_user_id,
            'update_user_id': create_user_id,
        }
        entity = FinReceiptRecordDAO.create(db, tenant_id, data_dict)
        return ReceiptRecordResponse.from_orm(entity)

    @staticmethod
    def get_receipt_record(db: Session, tenant_id: int, id: int) -> Optional[ReceiptRecordResponse]:
        """获取收款记录详情"""
        entity = FinReceiptRecordDAO.get_by_id(db, tenant_id, id)
        return ReceiptRecordResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_receipt_record(db: Session, tenant_id: int, id: int, data: ReceiptRecordUpdate) -> Optional[ReceiptRecordResponse]:
        """更新收款记录"""
        entity = FinReceiptRecordDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return ReceiptRecordResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_receipt_record(db: Session, tenant_id: int, id: int) -> bool:
        """删除收款记录"""
        return FinReceiptRecordDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_receipt_records(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[ReceiptRecordResponse]:
        """分页查询收款记录列表"""
        total, items = FinReceiptRecordDAO.list(db, tenant_id, page_request.model_dump())
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[ReceiptRecordResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_refund_record(db: Session, tenant_id: int, data: RefundRecordCreate, create_user_id: int = 1) -> RefundRecordResponse:
        """创建退款记录"""
        refund_no = PaymentService._generate_doc_no(db, tenant_id, "TK")
        refund_type_map = {'退房退款': 1, '其他': 2}
        data_dict = {
            'refund_no': refund_no,
            'project_id': data.project_id,
            'project_name': '测试项目',
            'house_id': 1,
            'house_no': '1-1-101',
            'contract_id': 1,
            'customer_id': data.customer_id,
            'customer_name': '测试客户',
            'account_id': data.account_id,
            'account_name': '测试账户',
            'account_use_type': 1,
            'project_fin_config_id': 1,
            'tax_tpl_id': 1,
            'income_subject_id': 1,
            'refund_apply_date': datetime.now(),
            'refund_type': refund_type_map.get(data.refund_type, 2),
            'total_refund_amount': data.refund_total_amt,
            'untax_refund_principal': data.untax_refund_principal,
            'refund_tax': data.refund_tax,
            'refund_maintain': 0,
            'refund_other_fee': 0,
            'deduct_commission': 0,
            'deduct_forfeit': 0,
            'real_pay_amount': data.refund_total_amt,
            'remark': data.refund_reason,
            'source_receipt_id': 1,
            'refund_payer_name': '测试客户',
            'refund_bank_name': '测试银行',
            'refund_bank_account': '6222021234567890123',
            'create_user_id': create_user_id,
            'update_user_id': create_user_id,
        }
        entity = FinRefundRecordDAO.create(db, tenant_id, data_dict)
        return RefundRecordResponse.from_orm(entity)

    @staticmethod
    def get_refund_record(db: Session, tenant_id: int, id: int) -> Optional[RefundRecordResponse]:
        """获取退款记录详情"""
        entity = FinRefundRecordDAO.get_by_id(db, tenant_id, id)
        return RefundRecordResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_refund_record(db: Session, tenant_id: int, id: int, data: RefundRecordUpdate) -> Optional[RefundRecordResponse]:
        """更新退款记录"""
        update_data = data.model_dump(exclude_unset=True)
        if 'refund_amount' in update_data:
            update_data['total_refund_amount'] = update_data.pop('refund_amount')
        entity = FinRefundRecordDAO.update(db, tenant_id, id, update_data)
        return RefundRecordResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_refund_record(db: Session, tenant_id: int, id: int) -> bool:
        """删除退款记录"""
        return FinRefundRecordDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_refund_records(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[RefundRecordResponse]:
        """分页查询退款记录列表"""
        total, items = FinRefundRecordDAO.list(db, tenant_id, page_request.model_dump())
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[RefundRecordResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_deposit_ledger(db: Session, tenant_id: int, data: DepositAccountCreate, create_user_id: int = 1) -> DepositAccountResponse:
        """创建定金台账"""
        deposit_no = PaymentService._generate_doc_no(db, tenant_id, "DJ")
        pay_way_map = {'现金': 1, '银行卡': 2, '微信': 3, '支付宝': 4, 'POS': 5, '银行转账': 6}
        deposit_type_map = {'认筹金': 1, '定金': 2}
        data_dict = {
            'deposit_no': deposit_no,
            'project_id': data.project_id,
            'project_name': '测试项目',
            'customer_id': data.customer_id,
            'customer_name': '测试客户',
            'account_id': data.account_id,
            'account_name': '测试账户',
            'account_use_type': 1,
            'project_fin_config_id': 1,
            'tax_tpl_id': 1,
            'deposit_subject_id': 1,
            'pay_time': datetime.now(),
            'pay_way': pay_way_map.get(data.payment_method, 2),
            'payer_name': '测试付款人',
            'deposit_type': deposit_type_map.get(data.deposit_type, 1),
            'deposit_total_amt': getattr(data, 'deposit_total_amt', getattr(data, 'deposit_amount', 0)),
            'deposit_untax_amt': data.deposit_untax_amt,
            'deposit_tax': data.deposit_tax,
            'other_fee': 0,
            'create_user_id': create_user_id,
            'update_user_id': create_user_id,
        }
        entity = FinDepositAccountDAO.create(db, tenant_id, data_dict)
        return DepositAccountResponse.from_orm(entity)

    @staticmethod
    def get_deposit_ledger(db: Session, tenant_id: int, id: int) -> Optional[DepositAccountResponse]:
        """获取认籌定金台账详情"""
        entity = FinDepositAccountDAO.get_by_id(db, tenant_id, id)
        return DepositAccountResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_deposit_ledger(db: Session, tenant_id: int, id: int, data: DepositAccountUpdate) -> Optional[DepositAccountResponse]:
        """更新认籌定金台账"""
        update_data = data.model_dump(exclude_unset=True)
        if 'deposit_amount' in update_data:
            update_data['deposit_total_amt'] = update_data.pop('deposit_amount')
        entity = FinDepositAccountDAO.update(db, tenant_id, id, update_data)
        return DepositAccountResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_deposit_ledger(db: Session, tenant_id: int, id: int) -> bool:
        """删除认籌定金台账"""
        return FinDepositAccountDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_deposit_ledgers(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[DepositAccountResponse]:
        """分页查询认籌定金台账列表"""
        total, items = FinDepositAccountDAO.list(db, tenant_id, page_request.model_dump())
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[DepositAccountResponse.from_orm(item) for item in items]
        )

﻿"""
房地产SaaS财务管理系统 - 应收应付往来台账服务层
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from ..dao import (
    FinAccountReceivableDAO,
    FinAccountPayableDAO,
    FinAdvancePayDAO,
    FinOtherLoanDAO,
)
from ..model.finance_models import (
    FinAccountReceivable,
    FinAccountPayable,
    FinAdvancePay,
    FinOtherLoan,
)
from ..schemas.ar_ap_schemas import (
    AccountReceivableCreate,
    AccountReceivableUpdate,
    AccountReceivableResponse,
    AccountPayableCreate,
    AccountPayableUpdate,
    AccountPayableResponse,
    AdvancePayCreate,
    AdvancePayUpdate,
    AdvancePayResponse,
    OtherLoanCreate,
    OtherLoanUpdate,
    OtherLoanResponse,
)
from ..schemas.base_schemas import PageRequest, PageResponse


class ArApService:
    """应收应付往来台账服务类"""

    @staticmethod
    def _generate_doc_no(db: Session, tenant_id: str, prefix: str) -> str:
        """
        生成单据编号（私有方法）
        :param db: 数据库会话
        :param tenant_id: 租户ID
        :param prefix: 编号前缀（YS:应收, YF:应付, YFUK:预付, WL:往来）
        :return: 生成的单据编号
        """
        date_str = datetime.now().strftime("%Y%m%d")
        
        max_no = 0
        if prefix == "YS":
            result = db.query(func.max(FinAccountReceivable.id)).filter(FinAccountReceivable.tenant == tenant_id).scalar()
        elif prefix == "YF":
            result = db.query(func.max(FinAccountPayable.id)).filter(FinAccountPayable.tenant == tenant_id).scalar()
        elif prefix == "YFUK":
            result = db.query(func.max(FinAdvancePay.id)).filter(FinAdvancePay.tenant == tenant_id).scalar()
        elif prefix == "WL":
            result = db.query(func.max(FinOtherLoan.id)).filter(FinOtherLoan.tenant == tenant_id).scalar()
        
        if result:
            max_no = int(result) + 1
        
        seq_str = str(max_no).zfill(4)
        
        return f"{prefix}{date_str}{seq_str}"

    @staticmethod
    def create_account_receivable(db: Session, tenant_id: str, data: AccountReceivableCreate, create_user_id: int = 1) -> AccountReceivableResponse:
        """创建客户应收台账"""
        data_dict = data.model_dump()
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinAccountReceivableDAO.create(db, tenant_id, data_dict)
        return AccountReceivableResponse.from_orm(entity)

    @staticmethod
    def get_account_receivable(db: Session, tenant_id: str, id: int) -> Optional[AccountReceivableResponse]:
        """获取客户应收台账详情"""
        entity = FinAccountReceivableDAO.get_by_id(db, tenant_id, id)
        return AccountReceivableResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_account_receivable(db: Session, tenant_id: str, id: int, data: AccountReceivableUpdate) -> Optional[AccountReceivableResponse]:
        """更新客户应收台账"""
        entity = FinAccountReceivableDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return AccountReceivableResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_account_receivable(db: Session, tenant_id: str, id: int) -> bool:
        """删除客户应收台账"""
        return FinAccountReceivableDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_account_receivables(db: Session, tenant_id: str, page_request: PageRequest, filters: Optional[dict] = None) -> PageResponse[AccountReceivableResponse]:
        """分页查询客户应收台账列表"""
        query_params = page_request.model_dump()
        if filters:
            query_params.update(filters)
        total, items = FinAccountReceivableDAO.list(db, tenant_id, query_params)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.size,
            items=[AccountReceivableResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_account_payable(db: Session, tenant_id: str, data: AccountPayableCreate, create_user_id: int = 1) -> AccountPayableResponse:
        """创建供应商应付台账"""
        payable_no = ArApService._generate_doc_no(db, tenant_id, "YF")
        data_dict = data.model_dump()
        data_dict['payable_no'] = payable_no
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinAccountPayableDAO.create(db, tenant_id, data_dict)
        return AccountPayableResponse.from_orm(entity)

    @staticmethod
    def get_account_payable(db: Session, tenant_id: str, id: int) -> Optional[AccountPayableResponse]:
        """获取供应商应付台账详情"""
        entity = FinAccountPayableDAO.get_by_id(db, tenant_id, id)
        return AccountPayableResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_account_payable(db: Session, tenant_id: str, id: int, data: AccountPayableUpdate) -> Optional[AccountPayableResponse]:
        """更新供应商应付台账"""
        entity = FinAccountPayableDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return AccountPayableResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_account_payable(db: Session, tenant_id: str, id: int) -> bool:
        """删除供应商应付台账"""
        return FinAccountPayableDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_account_payables(db: Session, tenant_id: str, page_request: PageRequest, filters: Optional[dict] = None) -> PageResponse[AccountPayableResponse]:
        """分页查询供应商应付台账列表"""
        query_params = page_request.model_dump()
        if filters:
            query_params.update(filters)
        total, items = FinAccountPayableDAO.list(db, tenant_id, query_params)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.size,
            items=[AccountPayableResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_advance_pay(db: Session, tenant_id: str, data: AdvancePayCreate, create_user_id: int = 1) -> AdvancePayResponse:
        """创建预付款台账"""
        advance_no = ArApService._generate_doc_no(db, tenant_id, "YFUK")
        data_dict = data.model_dump()
        data_dict['advance_no'] = advance_no
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinAdvancePayDAO.create(db, tenant_id, data_dict)
        return AdvancePayResponse.from_orm(entity)

    @staticmethod
    def get_advance_pay(db: Session, tenant_id: str, id: int) -> Optional[AdvancePayResponse]:
        """获取预付款台账详情"""
        entity = FinAdvancePayDAO.get_by_id(db, tenant_id, id)
        return AdvancePayResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_advance_pay(db: Session, tenant_id: str, id: int, data: AdvancePayUpdate) -> Optional[AdvancePayResponse]:
        """更新预付款台账"""
        entity = FinAdvancePayDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return AdvancePayResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_advance_pay(db: Session, tenant_id: str, id: int) -> bool:
        """删除预付款台账"""
        return FinAdvancePayDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_advance_pays(db: Session, tenant_id: str, page_request: PageRequest, filters: Optional[dict] = None) -> PageResponse[AdvancePayResponse]:
        """分页查询预付款台账列表"""
        query_params = page_request.model_dump()
        if filters:
            query_params.update(filters)
        total, items = FinAdvancePayDAO.list(db, tenant_id, query_params)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.size,
            items=[AdvancePayResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_other_loan(db: Session, tenant_id: str, data: OtherLoanCreate, create_user_id: int = 1) -> OtherLoanResponse:
        """创建其他往来款台账"""
        loan_no = ArApService._generate_doc_no(db, tenant_id, "WL")
        data_dict = data.model_dump()
        data_dict['loan_no'] = loan_no
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinOtherLoanDAO.create(db, tenant_id, data_dict)
        return OtherLoanResponse.from_orm(entity)

    @staticmethod
    def get_other_loan(db: Session, tenant_id: str, id: int) -> Optional[OtherLoanResponse]:
        """获取其他往来款台账详情"""
        entity = FinOtherLoanDAO.get_by_id(db, tenant_id, id)
        return OtherLoanResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_other_loan(db: Session, tenant_id: str, id: int, data: OtherLoanUpdate) -> Optional[OtherLoanResponse]:
        """更新其他往来款台账"""
        entity = FinOtherLoanDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return OtherLoanResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_other_loan(db: Session, tenant_id: str, id: int) -> bool:
        """删除其他往来款台账"""
        return FinOtherLoanDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_other_loans(db: Session, tenant_id: str, page_request: PageRequest, filters: Optional[dict] = None) -> PageResponse[OtherLoanResponse]:
        """分页查询其他往来款台账列表"""
        query_params = page_request.model_dump()
        if filters:
            query_params.update(filters)
        total, items = FinOtherLoanDAO.list(db, tenant_id, query_params)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.size,
            items=[OtherLoanResponse.from_orm(item) for item in items]
        )


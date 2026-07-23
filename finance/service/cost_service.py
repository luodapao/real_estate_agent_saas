﻿"""
房地产SaaS财务管理系统 - 项目成本服务层
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..dao import (
    FinCostExpenseDAO,
    FinExpenseReimbursementDAO,
    FinCostPayDAO,
    FinAdCostDAO,
    FinProjectEngCostDAO,
)
from ..schemas.cost_schemas import (
    CostExpenseCreate,
    CostExpenseUpdate,
    CostExpenseResponse,
    ExpenseReimbursementCreate,
    ExpenseReimbursementUpdate,
    ExpenseReimbursementResponse,
    CostPayCreate,
    CostPayUpdate,
    CostPayResponse,
    AdCostCreate,
    AdCostUpdate,
    AdCostResponse,
    ProjectEngCostCreate,
    ProjectEngCostUpdate,
    ProjectEngCostResponse,
)
from ..schemas.base_schemas import PageRequest, PageResponse


class CostService:
    """项目成本服务类"""

    @staticmethod
    def _generate_doc_no(db: Session, tenant_id: int, prefix: str) -> str:
        """
        生成单据编号（私有方法）
        :param db: 数据库会话
        :param tenant_id: 租户ID
        :param prefix: 编号前缀（FYSQ:费用申请, BX:报销, FK:付款, GGCB:广告成本, GC:工程成本）
        :return: 生成的单据编号
        """
        date_str = datetime.now().strftime("%Y%m%d")

        max_no = 0
        if prefix == "FYSQ":
            result = db.execute(
                "SELECT MAX(expense_no) FROM fin_cost_expense WHERE tenant = :tenant_id AND expense_no LIKE :pattern",
                {"tenant_id": tenant_id, "pattern": f"{prefix}{date_str}%"}
            ).scalar()
        elif prefix == "BX":
            result = db.execute(
                "SELECT MAX(reimburse_no) FROM fin_expense_reimbursement WHERE tenant = :tenant_id AND reimburse_no LIKE :pattern",
                {"tenant_id": tenant_id, "pattern": f"{prefix}{date_str}%"}
            ).scalar()
        elif prefix == "FK":
            result = db.execute(
                "SELECT MAX(pay_no) FROM fin_cost_pay WHERE tenant = :tenant_id AND pay_no LIKE :pattern",
                {"tenant_id": tenant_id, "pattern": f"{prefix}{date_str}%"}
            ).scalar()
        elif prefix == "GGCB":
            result = db.execute(
                "SELECT MAX(cost_no) FROM fin_ad_cost WHERE tenant = :tenant_id AND cost_no LIKE :pattern",
                {"tenant_id": tenant_id, "pattern": f"{prefix}{date_str}%"}
            ).scalar()
        elif prefix == "GC":
            result = db.execute(
                "SELECT MAX(cost_no) FROM fin_project_eng_cost WHERE tenant = :tenant_id AND cost_no LIKE :pattern",
                {"tenant_id": tenant_id, "pattern": f"{prefix}{date_str}%"}
            ).scalar()

        if result:
            seq_str = result[-4:]
            max_no = int(seq_str) + 1

        seq_str = str(max_no).zfill(4)

        return f"{prefix}{date_str}{seq_str}"

    # ========== 通用费用申请（事前审批） ==========

    @staticmethod
    def create_cost_expense(db: Session, tenant_id: int, data: CostExpenseCreate, create_user_id: int = 1) -> CostExpenseResponse:
        """创建通用费用申请"""
        expense_no = CostService._generate_doc_no(db, tenant_id, "FYSQ")
        data_dict = data.model_dump()
        data_dict['expense_no'] = expense_no
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinCostExpenseDAO.create(db, tenant_id, data_dict)
        return CostExpenseResponse.from_orm(entity)

    @staticmethod
    def get_cost_expense(db: Session, tenant_id: int, id: int) -> Optional[CostExpenseResponse]:
        """获取通用费用申请详情"""
        entity = FinCostExpenseDAO.get_by_id(db, tenant_id, id)
        return CostExpenseResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_cost_expense(db: Session, tenant_id: int, id: int, data: CostExpenseUpdate) -> Optional[CostExpenseResponse]:
        """更新通用费用申请"""
        entity = FinCostExpenseDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return CostExpenseResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_cost_expense(db: Session, tenant_id: int, id: int) -> bool:
        """删除通用费用申请"""
        return FinCostExpenseDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_cost_expenses(db: Session, tenant_id: int, page_request: PageRequest, filters: Optional[dict] = None) -> PageResponse[CostExpenseResponse]:
        """分页查询通用费用申请列表"""
        query_params = page_request.model_dump()
        if filters:
            query_params.update(filters)
        total, items = FinCostExpenseDAO.list(db, tenant_id, query_params)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.size,
            items=[CostExpenseResponse.from_orm(item) for item in items]
        )

    # ========== 费用报销（事后核销） ==========

    @staticmethod
    def create_expense_reimbursement(db: Session, tenant_id: int, data: ExpenseReimbursementCreate, create_user_id: int = 1) -> ExpenseReimbursementResponse:
        """创建费用报销"""
        reimburse_no = CostService._generate_doc_no(db, tenant_id, "BX")
        data_dict = data.model_dump()
        data_dict['reimburse_no'] = reimburse_no
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinExpenseReimbursementDAO.create(db, tenant_id, data_dict)
        return ExpenseReimbursementResponse.from_orm(entity)

    @staticmethod
    def get_expense_reimbursement(db: Session, tenant_id: int, id: int) -> Optional[ExpenseReimbursementResponse]:
        """获取费用报销详情"""
        entity = FinExpenseReimbursementDAO.get_by_id(db, tenant_id, id)
        return ExpenseReimbursementResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_expense_reimbursement(db: Session, tenant_id: int, id: int, data: ExpenseReimbursementUpdate) -> Optional[ExpenseReimbursementResponse]:
        """更新费用报销"""
        entity = FinExpenseReimbursementDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return ExpenseReimbursementResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_expense_reimbursement(db: Session, tenant_id: int, id: int) -> bool:
        """删除费用报销"""
        return FinExpenseReimbursementDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_expense_reimbursements(db: Session, tenant_id: int, page_request: PageRequest, filters: Optional[dict] = None) -> PageResponse[ExpenseReimbursementResponse]:
        """分页查询费用报销列表"""
        query_params = page_request.model_dump()
        if filters:
            query_params.update(filters)
        total, items = FinExpenseReimbursementDAO.list(db, tenant_id, query_params)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.size,
            items=[ExpenseReimbursementResponse.from_orm(item) for item in items]
        )

    # ========== 费用付款（资金执行层） ==========

    @staticmethod
    def create_cost_pay(db: Session, tenant_id: int, data: CostPayCreate, create_user_id: int = 1) -> CostPayResponse:
        """创建费用付款"""
        pay_no = CostService._generate_doc_no(db, tenant_id, "FK")
        data_dict = data.model_dump()
        data_dict['pay_no'] = pay_no
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinCostPayDAO.create(db, tenant_id, data_dict)
        return CostPayResponse.from_orm(entity)

    @staticmethod
    def get_cost_pay(db: Session, tenant_id: int, id: int) -> Optional[CostPayResponse]:
        """获取费用付款详情"""
        entity = FinCostPayDAO.get_by_id(db, tenant_id, id)
        return CostPayResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_cost_pay(db: Session, tenant_id: int, id: int, data: CostPayUpdate) -> Optional[CostPayResponse]:
        """更新费用付款"""
        entity = FinCostPayDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return CostPayResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_cost_pay(db: Session, tenant_id: int, id: int) -> bool:
        """删除费用付款"""
        return FinCostPayDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_cost_pays(db: Session, tenant_id: int, page_request: PageRequest, filters: Optional[dict] = None) -> PageResponse[CostPayResponse]:
        """分页查询费用付款列表"""
        query_params = page_request.model_dump()
        if filters:
            query_params.update(filters)
        total, items = FinCostPayDAO.list(db, tenant_id, query_params)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.size,
            items=[CostPayResponse.from_orm(item) for item in items]
        )

    # ========== 广告推广成本 ==========

    @staticmethod
    def create_ad_cost(db: Session, tenant_id: int, data: AdCostCreate, create_user_id: int = 1) -> AdCostResponse:
        """创建广告推广成本"""
        cost_no = CostService._generate_doc_no(db, tenant_id, "GGCB")
        data_dict = data.model_dump()
        data_dict['cost_no'] = cost_no
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinAdCostDAO.create(db, tenant_id, data_dict)
        return AdCostResponse.from_orm(entity)

    @staticmethod
    def get_ad_cost(db: Session, tenant_id: int, id: int) -> Optional[AdCostResponse]:
        """获取广告推广成本详情"""
        entity = FinAdCostDAO.get_by_id(db, tenant_id, id)
        return AdCostResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_ad_cost(db: Session, tenant_id: int, id: int, data: AdCostUpdate) -> Optional[AdCostResponse]:
        """更新广告推广成本"""
        entity = FinAdCostDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return AdCostResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_ad_cost(db: Session, tenant_id: int, id: int) -> bool:
        """删除广告推广成本"""
        return FinAdCostDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_ad_costs(db: Session, tenant_id: int, page_request: PageRequest, filters: Optional[dict] = None) -> PageResponse[AdCostResponse]:
        """分页查询广告推广成本列表"""
        query_params = page_request.model_dump()
        if filters:
            query_params.update(filters)
        total, items = FinAdCostDAO.list(db, tenant_id, query_params)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.size,
            items=[AdCostResponse.from_orm(item) for item in items]
        )

    # ========== 工程建设成本 ==========

    @staticmethod
    def create_project_eng_cost(db: Session, tenant_id: int, data: ProjectEngCostCreate, create_user_id: int = 1) -> ProjectEngCostResponse:
        """创建工程建设成本"""
        cost_no = CostService._generate_doc_no(db, tenant_id, "GC")
        data_dict = data.model_dump()
        data_dict['cost_no'] = cost_no
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinProjectEngCostDAO.create(db, tenant_id, data_dict)
        return ProjectEngCostResponse.from_orm(entity)

    @staticmethod
    def get_project_eng_cost(db: Session, tenant_id: int, id: int) -> Optional[ProjectEngCostResponse]:
        """获取工程建设成本详情"""
        entity = FinProjectEngCostDAO.get_by_id(db, tenant_id, id)
        return ProjectEngCostResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_project_eng_cost(db: Session, tenant_id: int, id: int, data: ProjectEngCostUpdate) -> Optional[ProjectEngCostResponse]:
        """更新工程建设成本"""
        entity = FinProjectEngCostDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return ProjectEngCostResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_project_eng_cost(db: Session, tenant_id: int, id: int) -> bool:
        """删除工程建设成本"""
        return FinProjectEngCostDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_project_eng_costs(db: Session, tenant_id: int, page_request: PageRequest, filters: Optional[dict] = None) -> PageResponse[ProjectEngCostResponse]:
        """分页查询工程建设成本列表"""
        query_params = page_request.model_dump()
        if filters:
            query_params.update(filters)
        total, items = FinProjectEngCostDAO.list(db, tenant_id, query_params)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.size,
            items=[ProjectEngCostResponse.from_orm(item) for item in items]
        )

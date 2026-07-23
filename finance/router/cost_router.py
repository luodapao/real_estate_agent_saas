﻿"""
房地产SaaS财务管理系统 - 项目成本模块路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from core.db_base import get_finance_db
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from finance.service.cost_service import CostService
from finance.schemas.cost_schemas import (
    CostExpenseCreate,
    CostExpenseUpdate,
    ExpenseReimbursementCreate,
    ExpenseReimbursementUpdate,
    CostPayCreate,
    CostPayUpdate,
    AdCostCreate,
    AdCostUpdate,
    ProjectEngCostCreate,
    ProjectEngCostUpdate,
)
from finance.schemas.base_schemas import PageRequest

router = APIRouter(prefix="/cost", tags=["项目成本"])


# ========== 通用费用申请（事前审批）接口 ==========

@router.post("/expense/create")
async def create_cost_expense(
    data: CostExpenseCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建通用费用申请"""
    try:
        result = CostService.create_cost_expense(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="费用申请创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/expense/list")
async def list_cost_expenses(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    expense_type: Optional[int] = None,
    audit_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取通用费用申请列表"""
    try:
        page_request = PageRequest(page=page, size=page_size)
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if expense_type:
            filters['expense_type'] = expense_type
        if audit_status:
            filters['audit_status'] = audit_status
        result = CostService.list_cost_expenses(db, current_user['tenant'], page_request, filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/expense/{id}")
async def get_cost_expense(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取通用费用申请详情"""
    try:
        result = CostService.get_cost_expense(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "费用申请不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/expense/{id}")
async def update_cost_expense(
    id: int,
    data: CostExpenseUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新通用费用申请"""
    try:
        result = CostService.update_cost_expense(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="费用申请更新成功")
        return error_response(-1, "费用申请不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/expense/{id}")
async def delete_cost_expense(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除通用费用申请"""
    try:
        success = CostService.delete_cost_expense(db, current_user['tenant'], id)
        if success:
            return success_response(message="费用申请删除成功")
        return error_response(-1, "费用申请不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 费用报销（事后核销）接口 ==========

@router.post("/reimbursement/create")
async def create_expense_reimbursement(
    data: ExpenseReimbursementCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建费用报销"""
    try:
        result = CostService.create_expense_reimbursement(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="费用报销创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/reimbursement/list")
async def list_expense_reimbursements(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    expense_type: Optional[int] = None,
    audit_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取费用报销列表"""
    try:
        page_request = PageRequest(page=page, size=page_size)
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if employee_id:
            filters['employee_id'] = employee_id
        if expense_type:
            filters['expense_type'] = expense_type
        if audit_status:
            filters['audit_status'] = audit_status
        result = CostService.list_expense_reimbursements(db, current_user['tenant'], page_request, filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/reimbursement/{id}")
async def get_expense_reimbursement(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取费用报销详情"""
    try:
        result = CostService.get_expense_reimbursement(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "费用报销不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/reimbursement/{id}")
async def update_expense_reimbursement(
    id: int,
    data: ExpenseReimbursementUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新费用报销"""
    try:
        result = CostService.update_expense_reimbursement(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="费用报销更新成功")
        return error_response(-1, "费用报销不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/reimbursement/{id}")
async def delete_expense_reimbursement(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除费用报销"""
    try:
        success = CostService.delete_expense_reimbursement(db, current_user['tenant'], id)
        if success:
            return success_response(message="费用报销删除成功")
        return error_response(-1, "费用报销不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 费用付款（资金执行层）接口 ==========

@router.post("/payment/create")
async def create_cost_payment(
    data: CostPayCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建费用付款"""
    try:
        result = CostService.create_cost_pay(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="费用付款创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/payment/list")
async def list_cost_payments(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    pay_target_type: Optional[int] = None,
    audit_status: Optional[int] = None,
    pay_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取费用付款列表"""
    try:
        page_request = PageRequest(page=page, size=page_size)
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if pay_target_type:
            filters['pay_target_type'] = pay_target_type
        if audit_status:
            filters['audit_status'] = audit_status
        if pay_status:
            filters['pay_status'] = pay_status
        result = CostService.list_cost_pays(db, current_user['tenant'], page_request, filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/payment/{id}")
async def get_cost_payment(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取费用付款详情"""
    try:
        result = CostService.get_cost_pay(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "费用付款不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/payment/{id}")
async def update_cost_payment(
    id: int,
    data: CostPayUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新费用付款"""
    try:
        result = CostService.update_cost_pay(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="费用付款更新成功")
        return error_response(-1, "费用付款不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/payment/{id}")
async def delete_cost_payment(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除费用付款"""
    try:
        success = CostService.delete_cost_pay(db, current_user['tenant'], id)
        if success:
            return success_response(message="费用付款删除成功")
        return error_response(-1, "费用付款不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 广告推广成本接口 ==========

@router.post("/advertising/create")
async def create_advertising_cost(
    data: AdCostCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建广告推广成本"""
    try:
        result = CostService.create_ad_cost(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="广告推广成本创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/advertising/list")
async def list_advertising_costs(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    ad_type: Optional[int] = None,
    cost_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取广告推广成本列表"""
    try:
        page_request = PageRequest(page=page, size=page_size)
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if supplier_id:
            filters['supplier_id'] = supplier_id
        if ad_type:
            filters['ad_type'] = ad_type
        if cost_status:
            filters['cost_status'] = cost_status
        result = CostService.list_ad_costs(db, current_user['tenant'], page_request, filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/advertising/{id}")
async def get_advertising_cost(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取广告推广成本详情"""
    try:
        result = CostService.get_ad_cost(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "广告推广成本不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/advertising/{id}")
async def update_advertising_cost(
    id: int,
    data: AdCostUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新广告推广成本"""
    try:
        result = CostService.update_ad_cost(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="广告推广成本更新成功")
        return error_response(-1, "广告推广成本不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/advertising/{id}")
async def delete_advertising_cost(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除广告推广成本"""
    try:
        success = CostService.delete_ad_cost(db, current_user['tenant'], id)
        if success:
            return success_response(message="广告推广成本删除成功")
        return error_response(-1, "广告推广成本不存在")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 工程建设成本接口 ==========

@router.post("/engineering/create")
async def create_engineering_cost(
    data: ProjectEngCostCreate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """创建工程建设成本"""
    try:
        result = CostService.create_project_eng_cost(db, current_user['tenant'], data, current_user['user_id'])
        return success_response(data=result.model_dump(mode='json'), message="工程建设成本创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/engineering/list")
async def list_engineering_costs(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    building_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    eng_type: Optional[int] = None,
    cost_status: Optional[int] = None,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取工程建设成本列表"""
    try:
        page_request = PageRequest(page=page, size=page_size)
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if building_id:
            filters['building_id'] = building_id
        if supplier_id:
            filters['supplier_id'] = supplier_id
        if eng_type:
            filters['eng_type'] = eng_type
        if cost_status:
            filters['cost_status'] = cost_status
        result = CostService.list_project_eng_costs(db, current_user['tenant'], page_request, filters)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/engineering/{id}")
async def get_engineering_cost(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """获取工程建设成本详情"""
    try:
        result = CostService.get_project_eng_cost(db, current_user['tenant'], id)
        if result:
            return success_response(data=result.model_dump(mode='json'))
        return error_response(-1, "工程建设成本不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/engineering/{id}")
async def update_engineering_cost(
    id: int,
    data: ProjectEngCostUpdate,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """更新工程建设成本"""
    try:
        result = CostService.update_project_eng_cost(db, current_user['tenant'], id, data)
        if result:
            return success_response(data=result.model_dump(mode='json'), message="工程建设成本更新成功")
        return error_response(-1, "工程建设成本不存在")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/engineering/{id}")
async def delete_engineering_cost(
    id: int,
    db: Session = Depends(get_finance_db),
    current_user = Depends(get_current_user)
):
    """删除工程建设成本"""
    try:
        success = CostService.delete_project_eng_cost(db, current_user['tenant'], id)
        if success:
            return success_response(message="工程建设成本删除成功")
        return error_response(-1, "工程建设成本不存在")
    except Exception as e:
        return error_response(-1, str(e))

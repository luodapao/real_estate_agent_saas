"""
房地产SaaS销售管理系统 - 客户全生命周期管理模块路由
"""

from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Optional, List

from core.db_base import get_sale_db as get_db
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from sale.service.customer_service import CustomerService, ReportVisitService, FollowService, SeaCustomerService
from sale.schemas.customer_schemas import (
    VisitConfirmRequest, FollowCreate, CustomerTransferRequest, SeaCustomerRequest
)

router = APIRouter(prefix="/customer", tags=["客户管理"])


# ========== 客户档案接口 ==========

@router.post("/create")
async def create_customer(
    customer_data: dict,
    tags: Optional[List[str]] = None,
    demands: Optional[List[dict]] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建客户"""
    try:
        service = CustomerService(db, current_user['tenant'])
        customer = service.create_customer(customer_data, tags, demands, current_user['user_id'])
        return success_response(data={
            "customer_id": customer.customer_id,
            "customer_name": customer.customer_name,
            "mobile": customer.mobile
        }, message="客户创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/list")
async def get_customers_list(
    page: int = 1,
    page_size: int = 20,
    customer_name: Optional[str] = None,
    mobile: Optional[str] = None,
    customer_status: Optional[int] = None,
    belong_user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取客户列表"""
    try:
        service = CustomerService(db, current_user['tenant'])
        filters = {}
        if customer_name:
            filters['customer_name'] = customer_name
        if mobile:
            filters['mobile'] = mobile
        if customer_status is not None:
            filters['customer_status'] = customer_status
        if belong_user_id:
            filters['belong_user_id'] = belong_user_id
        
        result = service.get_customers_list(page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/detail/{customer_id}")
async def get_customer_detail(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取客户详情"""
    try:
        service = CustomerService(db, current_user['tenant'])
        detail = service.get_customer_detail(customer_id)
        return success_response(data=detail)
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/update/{customer_id}")
async def update_customer(
    customer_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新客户"""
    try:
        service = CustomerService(db, current_user['tenant'])
        customer = service.update_customer(customer_id, update_data, current_user['user_id'])
        return success_response(data={
            "customer_id": customer.customer_id,
            "customer_name": customer.customer_name
        }, message="客户更新成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.delete("/delete/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除客户"""
    try:
        service = CustomerService(db, current_user['tenant'])
        service.delete_customer(customer_id, current_user['user_id'])
        return success_response(message="客户删除成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/transfer")
async def transfer_customer(
    transfer_data: CustomerTransferRequest = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """转移客户归属"""
    try:
        service = CustomerService(db, current_user['tenant'])
        service.transfer_customer(transfer_data.customer_id, transfer_data.target_user_id, current_user['user_id'])
        return success_response(message="客户转移成功")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 报备与到访接口 ==========

@router.post("/report/create")
async def create_report_visit(
    report_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建报备（入参：customer_name, mobile, project_id，channel_id， broker_id）"""
    try:
        service = ReportVisitService(db, current_user['tenant']) # 可能存在一个外部渠道如何获取多个项目的租户id问题
        report = service.create_report(report_data, current_user['user_id'])
        return success_response(data={
            "report_id": report.report_id,
            "report_no": report.report_no
        }, message="报备创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/report/list")
async def get_reports_list(
    page: int = 1,
    page_size: int = 20,
    customer_id: Optional[int] = None,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取报备列表"""
    try:
        service = ReportVisitService(db, current_user['tenant'])
        filters = {}
        if customer_id:
            filters['customer_id'] = customer_id
        if project_id:
            filters['project_id'] = project_id
        
        result = service.get_reports_list(page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/visit/confirm/{report_id}")
async def confirm_visit(
    report_id: int,
    visit_data: VisitConfirmRequest = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """确认到访"""
    try:
        service = ReportVisitService(db, current_user['tenant'])
        visit = service.confirm_visit(report_id, visit_data.model_dump(), current_user['user_id'])
        return success_response(data={
            "visit_id": visit.visit_id,
            "visit_time": visit.visit_time.isoformat() if visit.visit_time else None
        }, message="到访确认成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/visit/list")
async def get_visits_list(
    page: int = 1,
    page_size: int = 20,
    customer_id: Optional[int] = None,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取到访列表"""
    try:
        service = ReportVisitService(db, current_user['tenant'])
        filters = {}
        if customer_id:
            filters['customer_id'] = customer_id
        if project_id:
            filters['project_id'] = project_id
        
        result = service.get_visits_list(page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


# ========== 跟进记录接口 ==========

@router.post("/follow/create")
async def create_follow(
    follow_data: FollowCreate = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建跟进记录"""
    try:
        service = FollowService(db, current_user['tenant'])
        follow_dict = follow_data.model_dump()
        # 将 follow_method 映射到 service 层需要的字段
        follow_dict['follow_method'] = follow_dict.pop('follow_method', None)
        follow = service.create_follow(follow_dict, False, current_user['user_id'])
        return success_response(data={
            "follow_id": follow.follow_id,
            "follow_time": follow.follow_time.isoformat() if follow.follow_time else None
        }, message="跟进记录创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/follow/list")
async def get_follows_list(
    customer_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取跟进记录列表"""
    try:
        service = FollowService(db, current_user['tenant'])
        filters = {'customer_id': customer_id}
        result = service.get_follows_list(page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


# ========== 公海客户接口 ==========

@router.post("/sea/add")
async def add_customer_to_sea(
    sea_data: SeaCustomerRequest = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """添加客户到公海"""
    try:
        service = SeaCustomerService(db, current_user['tenant'])
        service.add_customer_to_sea(sea_data.customer_id, current_user['user_id'])
        return success_response(message="客户已添加到公海")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/sea/pick")
async def pick_customer_from_sea(
    sea_data: SeaCustomerRequest = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """从公海认领客户"""
    try:
        service = SeaCustomerService(db, current_user['tenant'])
        service.pick_customer_from_sea(sea_data.customer_id, current_user['user_id'])
        return success_response(message="客户认领成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/sea/list")
async def get_sea_customers_list(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取公海客户列表"""
    try:
        service = SeaCustomerService(db, current_user['tenant'])
        result = service.get_sea_customers_list(page, page_size)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))

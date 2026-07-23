"""
房地产SaaS销售管理系统 - 销售业绩与考核模块路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from core.db_base import get_db
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from sale.service.performance_service import (
    TeamService, PerformanceTargetService, PerformanceService, SalesCommissionService
)

router = APIRouter(prefix="/performance", tags=["销售业绩与考核"])


# ========== 销售团队管理接口 ==========

@router.post("/team/create")
async def create_team(
    team_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建销售团队"""
    try:
        service = TeamService(db, current_user['tenant'])
        team = service.create_team(team_data, current_user['user_id'])
        return success_response(data={
            "team_id": team.team_id,
            "team_code": team.team_code,
            "team_name": team.team_name
        }, message="销售团队创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/team/list")
async def get_teams_list(
    page: int = 1,
    page_size: int = 20,
    team_name: Optional[str] = None,
    team_level: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取销售团队列表"""
    try:
        service = TeamService(db, current_user['tenant'])
        filters = {}
        if team_name:
            filters['team_name'] = team_name
        if team_level is not None:
            filters['team_level'] = team_level
        
        result = service.get_teams_list(page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/team/detail/{team_id}")
async def get_team_detail(
    team_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取销售团队详情"""
    try:
        service = TeamService(db, current_user['tenant'])
        detail = service.get_team_detail(team_id)
        return success_response(data=detail)
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/team/update/{team_id}")
async def update_team(
    team_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新销售团队"""
    try:
        service = TeamService(db, current_user['tenant'])
        team = service.update_team(team_id, update_data, current_user['user_id'])
        return success_response(data={
            "team_id": team.team_id,
            "team_name": team.team_name
        }, message="销售团队更新成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/team/dissolve/{team_id}")
async def dissolve_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """解散销售团队"""
    try:
        service = TeamService(db, current_user['tenant'])
        service.dissolve_team(team_id, current_user['user_id'])
        return success_response(message="销售团队解散成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/team/member/add")
async def add_team_member(
    member_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """添加团队成员"""
    try:
        service = TeamService(db, current_user['tenant'])
        member = service.add_team_member(
            team_id=member_data['team_id'],
            user_id=member_data['user_id'],
            member_role=member_data.get('member_role', 'member'),
            operator_id=current_user['user_id']
        )
        return success_response(data={
            "member_id": member.member_id,
            "team_id": member.team_id,
            "user_id": member.user_id,
            "member_role": member.member_role
        }, message="团队成员添加成功")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 业绩目标管理接口 ==========

@router.post("/target/create")
async def create_target(
    target_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建业绩目标"""
    try:
        service = PerformanceTargetService(db, current_user['tenant'])
        target = service.create_target(target_data, current_user['user_id'])
        return success_response(data={
            "target_id": target.target_id,
            "target_type": target.target_type
        }, message="业绩目标创建成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/target/list")
async def get_targets_list(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    target_type: Optional[str] = None,
    target_status: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取业绩目标列表"""
    try:
        service = PerformanceTargetService(db, current_user['tenant'])
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if target_type:
            filters['target_type'] = target_type
        if target_status is not None:
            filters['target_status'] = target_status
        
        result = service.get_targets_list(page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.put("/target/update/{target_id}")
async def update_target(
    target_id: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新业绩目标"""
    try:
        service = PerformanceTargetService(db, current_user['tenant'])
        target = service.update_target(target_id, update_data, current_user['user_id'])
        return success_response(data={
            "target_id": target.target_id,
            "target_type": target.target_type
        }, message="业绩目标更新成功")
    except Exception as e:
        return error_response(-1, str(e))


# ========== 销售业绩统计接口 ==========

@router.get("/personal")
async def get_personal_performance(
    user_id: int,
    project_id: int,
    time_type: str = "month",
    time_value: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取个人销售业绩"""
    try:
        service = PerformanceService(db, current_user['tenant'])
        result = service.get_personal_performance(user_id, project_id, time_type, time_value)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/team")
async def get_team_performance(
    team_id: int,
    project_id: int,
    time_type: str = "month",
    time_value: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取团队销售业绩"""
    try:
        service = PerformanceService(db, current_user['tenant'])
        result = service.get_team_performance(team_id, project_id, time_type, time_value)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


# ========== 销售提成管理接口 ==========

@router.post("/sales/commission/calculate/{contract_id}")
async def calculate_sales_commission(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """计算销售提成"""
    try:
        service = SalesCommissionService(db, current_user['tenant'])
        result = service.calculate_sales_commission(contract_id, current_user['user_id'])
        return success_response(data=result, message="销售提成计算成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.get("/sales/commission/list")
async def get_commissions_list(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    sale_user_id: Optional[int] = None,
    commission_status: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取销售提成列表"""
    try:
        service = SalesCommissionService(db, current_user['tenant'])
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if sale_user_id:
            filters['sale_user_id'] = sale_user_id
        if commission_status is not None:
            filters['commission_status'] = commission_status
        
        result = service.get_commissions_list(page, page_size, filters)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/sales/commission/audit/{commission_id}")
async def audit_sales_commission(
    commission_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """审核销售提成"""
    try:
        service = SalesCommissionService(db, current_user['tenant'])
        service.audit_sales_commission(commission_id, current_user['user_id'], current_user['user_id'])
        return success_response(message="销售提成审核成功")
    except Exception as e:
        return error_response(-1, str(e))


@router.post("/sales/commission/freeze/{commission_id}")
async def freeze_sales_commission(
    commission_id: int,
    freeze_reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """冻结销售提成"""
    try:
        service = SalesCommissionService(db, current_user['tenant'])
        service.freeze_sales_commission(commission_id, freeze_reason, current_user['user_id'])
        return success_response(message="销售提成冻结成功")
    except Exception as e:
        return error_response(-1, str(e))

"""
房地产SaaS销售管理系统 - 数据统计报表模块路由
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.db_base import get_db
from core.auth_middleware import get_current_user
from config.exception import success_response, error_response

from sale.service.statistics_service import StatisticsService

router = APIRouter(prefix="/statistics", tags=["数据统计报表"])


# ========== 项目总览统计接口 ==========

@router.get("/overview/{project_id}")
async def get_overview_statistics(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取项目总览统计（首页大屏）"""
    try:
        service = StatisticsService(db, current_user['tenant'])
        result = service.get_overview_statistics(project_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


# ========== 项目维度统计接口 ==========

@router.get("/project")
async def get_project_statistics(
    project_id: int,
    time_type: str = "month",
    time_value: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取项目维度统计"""
    try:
        service = StatisticsService(db, current_user['tenant'])
        result = service.get_project_statistics(project_id, time_type, time_value)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


# ========== 个人维度统计接口 ==========

@router.get("/personal")
async def get_personal_statistics(
    user_id: int,
    project_id: int,
    time_type: str = "month",
    time_value: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取个人维度统计"""
    try:
        service = StatisticsService(db, current_user['tenant'])
        result = service.get_personal_statistics(user_id, project_id, time_type, time_value)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


# ========== 团队维度统计接口 ==========

@router.get("/team")
async def get_team_statistics(
    team_id: int,
    project_id: int,
    time_type: str = "month",
    time_value: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取团队维度统计"""
    try:
        service = StatisticsService(db, current_user['tenant'])
        result = service.get_team_statistics(team_id, project_id, time_type, time_value)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


# ========== 渠道维度统计接口 ==========

@router.get("/channel")
async def get_channel_statistics(
    channel_id: int,
    project_id: int,
    time_type: str = "month",
    time_value: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取渠道维度统计"""
    try:
        service = StatisticsService(db, current_user['tenant'])
        result = service.get_channel_statistics(channel_id, project_id, time_type, time_value)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))


# ========== 自定义时段统计接口 ==========

@router.get("/custom")
async def get_custom_statistics(
    project_id: int,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取自定义时段统计"""
    try:
        service = StatisticsService(db, current_user['tenant'])
        result = service.get_custom_statistics(project_id, start_date, end_date)
        return success_response(data=result)
    except Exception as e:
        return error_response(-1, str(e))

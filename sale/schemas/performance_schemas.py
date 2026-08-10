"""
房地产SaaS销售管理系统 - 销售业绩与考核模块数据模型
"""

from pydantic import BaseModel, Field
from common.schemas.response import ORMBaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ========== 销售团队管理模型 ==========

class TeamCreate(BaseModel):
    """创建销售团队请求模型"""
    team_code: str = Field(..., description="团队编码", max_length=50)
    team_name: str = Field(..., description="团队名称", max_length=100)
    parent_team_id: Optional[int] = Field(None, description="父团队ID")
    leader_id: Optional[int] = Field(None, description="团队负责人ID")
    team_level: Optional[int] = Field(1, description="团队层级")
    team_status: Optional[int] = Field(1, description="团队状态（1：正常 2：冻结 3：解散）")


class TeamUpdate(BaseModel):
    """更新销售团队请求模型"""
    team_name: Optional[str] = Field(None, description="团队名称", max_length=100)
    leader_id: Optional[int] = Field(None, description="团队负责人ID")
    team_status: Optional[int] = Field(None, description="团队状态")


class TeamResponse(ORMBaseModel):
    """销售团队响应模型"""
    team_id: int
    team_code: str
    team_name: str
    parent_team_id: Optional[int]
    parent_team_name: Optional[str]
    leader_id: Optional[int]
    leader_name: Optional[str]
    team_level: int
    member_count: int
    team_status: int
    status: int
    create_time: Optional[datetime]
    update_time: Optional[datetime]


class TeamDetailResponse(ORMBaseModel):
    """销售团队详情响应模型"""
    team_id: int
    team_code: str
    team_name: str
    parent_team_id: Optional[int]
    leader_id: Optional[int]
    leader_name: Optional[str]
    team_level: int
    member_count: int
    team_status: int
    status: int
    sub_teams: List[dict]
    performance: dict
    create_time: Optional[datetime]
    update_time: Optional[datetime]


# ========== 业绩目标管理模型 ==========

class PerformanceTargetCreate(BaseModel):
    """创建业绩目标请求模型"""
    project_id: int = Field(..., description="楼盘ID")
    target_type: str = Field(..., description="目标类型（个人/团队）", max_length=20)
    target_user_id: Optional[int] = Field(None, description="目标用户ID（个人目标时必填）")
    target_team_id: Optional[int] = Field(None, description="目标团队ID（团队目标时必填）")
    time_type: str = Field(..., description="时间类型（年/季/月/周/日/自定义）", max_length=20)
    time_value: Optional[str] = Field(None, description="时间值（如2024-01、2024-Q1等）")
    target_amount: Decimal = Field(..., description="目标金额", ge=0)
    target_sets: Optional[int] = Field(None, description="目标套数")
    target_status: Optional[int] = Field(1, description="目标状态（1：进行中 2：已完成 3：已作废）")


class PerformanceTargetUpdate(BaseModel):
    """更新业绩目标请求模型"""
    target_amount: Optional[Decimal] = Field(None, description="目标金额", ge=0)
    target_sets: Optional[int] = Field(None, description="目标套数")
    target_status: Optional[int] = Field(None, description="目标状态")


class PerformanceTargetResponse(ORMBaseModel):
    """业绩目标响应模型"""
    target_id: int
    project_id: int
    project_name: str
    target_type: str
    target_user_id: Optional[int]
    target_user_name: Optional[str]
    target_team_id: Optional[int]
    target_team_name: Optional[str]
    time_type: str
    time_value: Optional[str]
    target_amount: Decimal
    target_sets: Optional[int]
    target_status: int
    status: int
    create_time: Optional[datetime]
    update_time: Optional[datetime]


# ========== 销售业绩统计模型 ==========

class PersonalPerformanceResponse(ORMBaseModel):
    """个人销售业绩响应模型"""
    user_id: int
    user_name: str
    project_id: int
    project_name: str
    time_type: str
    time_value: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    visit_count: int
    subscribe_sets: int
    subscribe_amount: Decimal
    contract_sets: int
    contract_amount: Decimal
    payment_amount: Decimal
    customer_count: int
    target_amount: Decimal
    target_sets: int
    completion_rate: float


class TeamPerformanceResponse(ORMBaseModel):
    """团队销售业绩响应模型"""
    team_id: int
    team_name: str
    project_id: int
    project_name: str
    time_type: str
    time_value: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    visit_count: int
    subscribe_sets: int
    subscribe_amount: Decimal
    contract_sets: int
    contract_amount: Decimal
    payment_amount: Decimal
    member_count: int
    target_amount: Decimal
    completion_rate: float


# ========== 销售提成管理模型 ==========

class SalesCommissionResponse(ORMBaseModel):
    """销售提成响应模型"""
    commission_id: int
    commission_no: str
    project_id: int
    project_name: str
    contract_id: int
    contract_no: str
    sale_user_id: int
    sale_user_name: str
    sale_team_id: Optional[int]
    sale_team_name: Optional[str]
    commission_amount: Decimal
    commission_rate: float
    base_amount: Decimal
    commission_status: int
    audit_user_id: Optional[int]
    audit_user_name: Optional[str]
    audit_time: Optional[datetime]
    pay_time: Optional[datetime]
    freeze_reason: Optional[str]
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]


class SalesCommissionListResponse(ORMBaseModel):
    """销售提成列表响应模型"""
    total: int
    page: int
    page_size: int
    pages: int
    data: List[SalesCommissionResponse]


class SalesCommissionFreezeRequest(BaseModel):
    """冻结销售提成请求模型"""
    commission_id: int = Field(..., description="提成ID")
    freeze_reason: str = Field(..., description="冻结原因")


class SalesCommissionCalculateResponse(ORMBaseModel):
    """销售提成计算响应模型"""
    commission_id: int
    commission_no: str
    contract_id: int
    contract_no: str
    sale_user_id: int
    sale_user_name: str
    commission_amount: Decimal
    commission_rate: float
    base_amount: Decimal
    commission_status: int
    message: str


class PerformanceRankingResponse(ORMBaseModel):
    """业绩排行响应模型"""
    rank: int
    user_id: int
    user_name: str
    team_name: Optional[str]
    project_id: int
    project_name: str
    contract_sets: int
    contract_amount: Decimal
    payment_amount: Decimal


class TeamRankingResponse(ORMBaseModel):
    """团队业绩排行响应模型"""
    rank: int
    team_id: int
    team_name: str
    project_id: int
    project_name: str
    member_count: int
    contract_sets: int
    contract_amount: Decimal
    payment_amount: Decimal
    avg_amount: Decimal
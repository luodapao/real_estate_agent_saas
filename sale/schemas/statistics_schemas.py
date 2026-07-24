"""
房地产SaaS销售管理系统 - 数据统计报表模块数据模型
"""

from pydantic import BaseModel, Field\nfrom common.schemas.response import ORMBaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ========== 项目总览统计模型 ==========

class OverviewStatisticsResponse(ORMBaseModel):
    """项目总览统计响应模型"""
    project_id: int
    project_name: str
    today: dict
    total: dict


class TodayStatistics(BaseModel):
    """今日统计数据模型"""
    visit_count: int
    subscribe_sets: int
    subscribe_amount: Decimal
    contract_sets: int
    contract_amount: Decimal
    payment_amount: Decimal
    date: str


class TotalStatistics(BaseModel):
    """累计统计数据模型"""
    visit_count: int
    subscribe_sets: int
    subscribe_amount: Decimal
    contract_sets: int
    contract_amount: Decimal
    payment_amount: Decimal
    signed_unpaid_amount: Decimal


# ========== 项目维度统计模型 ==========

class ProjectStatisticsResponse(ORMBaseModel):
    """项目维度统计响应模型"""
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
    signed_unpaid_amount: Decimal
    visit_to_contract_rate: float
    contract_to_payment_rate: float


# ========== 个人维度统计模型 ==========

class PersonalStatisticsResponse(ORMBaseModel):
    """个人维度统计响应模型"""
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
    visit_to_contract_rate: float


# ========== 团队维度统计模型 ==========

class TeamStatisticsResponse(ORMBaseModel):
    """团队维度统计响应模型"""
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


# ========== 渠道维度统计模型 ==========

class ChannelStatisticsResponse(ORMBaseModel):
    """渠道维度统计响应模型"""
    channel_id: int
    channel_name: str
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


# ========== 自定义时段统计模型 ==========

class CustomStatisticsRequest(BaseModel):
    """自定义时段统计请求模型"""
    project_id: int = Field(..., description="楼盘ID")
    start_date: str = Field(..., description="开始日期（YYYY-MM-DD）")
    end_date: str = Field(..., description="结束日期（YYYY-MM-DD）")


class CustomStatisticsResponse(ORMBaseModel):
    """自定义时段统计响应模型"""
    project_id: int
    project_name: str
    time_type: str
    start_date: str
    end_date: str
    visit_count: int
    subscribe_sets: int
    subscribe_amount: Decimal
    contract_sets: int
    contract_amount: Decimal
    payment_amount: Decimal
    signed_unpaid_amount: Decimal


# ========== 时间范围配置模型 ==========

class TimeRangeConfig(BaseModel):
    """时间范围配置模型"""
    time_type: str = Field(..., description="时间类型（total/year/quarter/month/week/day/custom）")
    time_value: Optional[str] = Field(None, description="时间值（如2024-01、2024-Q1等）")


# ========== 统计报表综合响应模型 ==========

class StatisticsReportResponse(ORMBaseModel):
    """统计报表综合响应模型"""
    project_id: int
    project_name: str
    time_type: str
    time_value: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    dimensions: dict
    charts_data: dict


class DimensionStatistics(BaseModel):
    """维度统计数据模型"""
    name: str
    label: str
    value: int
    amount: Decimal
    rate: float


class ChartData(BaseModel):
    """图表数据模型"""
    chart_type: str
    chart_name: str
    x_axis: List[str]
    y_axis: List[float]
    series: List[dict]


# ========== 销售漏斗模型 ==========

class SalesFunnelResponse(ORMBaseModel):
    """销售漏斗响应模型"""
    project_id: int
    project_name: str
    time_type: str
    time_value: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    stages: List[dict]


class FunnelStage(BaseModel):
    """漏斗阶段模型"""
    stage_name: str
    stage_order: int
    count: int
    rate: float
    amount: Optional[Decimal]


# ========== 客户转化分析模型 ==========

class CustomerConversionResponse(ORMBaseModel):
    """客户转化分析响应模型"""
    project_id: int
    project_name: str
    time_type: str
    time_value: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    total_customers: int
    visit_customers: int
    subscribe_customers: int
    contract_customers: int
    visit_rate: float
    subscribe_rate: float
    contract_rate: float


# ========== 回款分析模型 ==========

class PaymentAnalysisResponse(ORMBaseModel):
    """回款分析响应模型"""
    project_id: int
    project_name: str
    time_type: str
    time_value: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    total_contract_amount: Decimal
    total_payment_amount: Decimal
    pending_payment_amount: Decimal
    payment_rate: float
    overdue_payment_amount: Decimal
    payment_trend: List[dict]


class PaymentTrend(BaseModel):
    """回款趋势模型"""
    date: str
    contract_amount: Decimal
    payment_amount: Decimal
    pending_amount: Decimal


# ========== 房源销控统计模型 ==========

class HouseControlStatisticsResponse(ORMBaseModel):
    """房源销控统计响应模型"""
    project_id: int
    project_name: str
    total_houses: int
    available_houses: int
    sold_houses: int
    locked_houses: int
    reserved_houses: int
    available_rate: float
    sold_rate: float
    building_distribution: List[dict]
    room_type_distribution: List[dict]


class BuildingDistribution(BaseModel):
    """楼栋分布模型"""
    building_id: int
    building_name: str
    total_houses: int
    sold_houses: int
    available_houses: int


class RoomTypeDistribution(BaseModel):
    """户型分布模型"""
    room_type: str
    total_houses: int
    sold_houses: int
    available_houses: int
    sold_rate: float


# ========== 渠道业绩排行模型 ==========

class ChannelPerformanceRankingResponse(ORMBaseModel):
    """渠道业绩排行响应模型"""
    project_id: int
    project_name: str
    time_type: str
    time_value: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    ranking: List[dict]


class ChannelRanking(BaseModel):
    """渠道排行模型"""
    rank: int
    channel_id: int
    channel_name: str
    visit_count: int
    contract_sets: int
    contract_amount: Decimal
    payment_amount: Decimal
"""
房地产SaaS销售管理系统 - 客户全生命周期管理模块数据模型
"""

from pydantic import BaseModel, Field
from common.schemas.response import ORMBaseModel
from typing import Optional, List
from datetime import datetime


# ========== 客户档案模型 ==========

class CustomerCreate(BaseModel):
    """创建客户请求模型"""
    customer_name: str = Field(..., description="客户姓名", max_length=50)
    mobile: str = Field(..., description="手机号", max_length=20)
    gender: Optional[int] = Field(1, description="性别（1：男 2：女 3：未知）")
    id_card: Optional[str] = Field(None, description="身份证号", max_length=20)
    province: Optional[str] = Field(None, description="省份", max_length=50)
    city: Optional[str] = Field(None, description="城市", max_length=50)
    district: Optional[str] = Field(None, description="区县", max_length=50)
    address: Optional[str] = Field(None, description="详细地址", max_length=200)
    customer_status: Optional[int] = Field(1, description="客户状态（1：潜客 2：意向 3：认购 4：签约 5：成交 6：无效）")
    customer_source: Optional[str] = Field("自然到访", description="客户来源", max_length=50)
    belong_sale_user_id: Optional[int] = Field(None, description="归属销售ID")
    remark: Optional[str] = Field(None, description="备注")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    demands: Optional[List[dict]] = Field(None, description="购房需求列表")


class CustomerUpdate(BaseModel):
    """更新客户请求模型"""
    customer_name: Optional[str] = Field(None, description="客户姓名", max_length=50)
    gender: Optional[int] = Field(None, description="性别")
    id_card: Optional[str] = Field(None, description="身份证号", max_length=20)
    province: Optional[str] = Field(None, description="省份", max_length=50)
    city: Optional[str] = Field(None, description="城市", max_length=50)
    district: Optional[str] = Field(None, description="区县", max_length=50)
    address: Optional[str] = Field(None, description="详细地址", max_length=200)
    customer_status: Optional[int] = Field(None, description="客户状态")
    customer_source: Optional[str] = Field(None, description="客户来源", max_length=50)
    belong_sale_user_id: Optional[int] = Field(None, description="归属销售ID")
    remark: Optional[str] = Field(None, description="备注")


class CustomerResponse(ORMBaseModel):
    """客户响应模型"""
    customer_id: int
    customer_code: str
    customer_name: str
    mobile: str
    gender: Optional[int]
    id_card: Optional[str]
    province: Optional[str]
    city: Optional[str]
    district: Optional[str]
    address: Optional[str]
    customer_status: int
    customer_source: Optional[str]
    belong_sale_user_id: Optional[int]
    belong_user_name: Optional[str]
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]
    tags: Optional[List[dict]]
    demands: Optional[List[dict]]


class CustomerTransferRequest(BaseModel):
    """转移客户请求模型"""
    customer_id: int = Field(..., description="客户ID")
    target_user_id: int = Field(..., description="目标销售ID")


# ========== 报备模型 ==========

class ReportCreate(BaseModel):
    """创建报备请求模型"""
    customer_id: int = Field(..., description="客户ID")
    project_id: int = Field(..., description="楼盘ID")
    report_time: Optional[str] = Field(None, description="报备时间")
    plan_visit_time: Optional[str] = Field(None, description="预计到访时间")
    report_source: Optional[str] = Field("渠道报备", description="报备来源")
    broker_id: Optional[int] = Field(None, description="经纪人ID")
    channel_id: Optional[int] = Field(None, description="渠道公司ID")
    remark: Optional[str] = Field(None, description="备注")


class ReportResponse(ORMBaseModel):
    """报备响应模型"""
    report_id: int
    report_no: str
    customer_id: int
    customer_name: str
    customer_mobile: str
    project_id: int
    project_name: str
    report_time: Optional[datetime]
    plan_visit_time: Optional[datetime]
    report_status: int
    report_source: Optional[str]
    broker_id: Optional[int]
    channel_id: Optional[int]
    remark: Optional[str]
    create_time: Optional[datetime]


# ========== 到访模型 ==========

class VisitConfirmRequest(BaseModel):
    """确认到访请求模型"""
    visit_time: Optional[str] = Field(None, description="到访时间")
    visit_type: Optional[str] = Field("首次到访", description="到访类型（首次到访/多次到访）")
    sale_user_id: Optional[int] = Field(None, description="接待销售ID")


class VisitResponse(ORMBaseModel):
    """到访响应模型"""
    visit_id: int
    tenant: str
    customer_id: int
    project_id: int
    report_id: Optional[int]
    sale_user_id: Optional[int]
    visit_time: Optional[datetime]
    visit_type: Optional[str]
    reception_score: Optional[float]
    protect_expire_time: Optional[datetime]
    visit_status: int
    status: int
    create_time: Optional[datetime]
    update_time: Optional[datetime]


# ========== 跟进记录模型 ==========

class FollowCreate(BaseModel):
    """创建跟进记录请求模型"""
    customer_id: int = Field(..., description="客户ID")
    follow_method: str = Field(..., description="跟进方式（电话/微信/面谈/短信）")
    follow_time: Optional[str] = Field(None, description="跟进时间")
    follow_content: str = Field(..., description="跟进内容")
    customer_intention: Optional[str] = Field(None, description="客户意向度")
    next_follow_time: Optional[str] = Field(None, description="下次跟进时间")


class FollowResponse(ORMBaseModel):
    """跟进记录响应模型"""
    follow_id: int
    tenant: str
    customer_id: int
    follow_user_id: Optional[int]
    follow_method: str
    follow_time: Optional[datetime]
    follow_content: str
    customer_intention: Optional[str]
    next_follow_time: Optional[datetime]
    follow_status: int
    status: int
    create_time: Optional[datetime]
    update_time: Optional[datetime]


# ========== 公海客户模型 ==========

class SeaCustomerRequest(BaseModel):
    """公海客户操作请求模型"""
    customer_id: int = Field(..., description="客户ID")


class SeaCustomerResponse(ORMBaseModel):
    """公海客户响应模型"""
    customer_id: int
    customer_code: str
    customer_name: str
    mobile: str
    customer_status: int
    customer_source: Optional[str]
    sea_time: Optional[datetime]
    add_time: Optional[datetime]
    last_follow_time: Optional[datetime]
    remark: Optional[str]
    create_time: Optional[datetime]


class CustomerDetailResponse(ORMBaseModel):
    """客户详情响应模型"""
    customer_id: int
    customer_code: str
    customer_name: str
    mobile: str
    gender: Optional[int]
    id_card: Optional[str]
    province: Optional[str]
    city: Optional[str]
    district: Optional[str]
    address: Optional[str]
    customer_status: int
    customer_source: Optional[str]
    belong_sale_user_id: Optional[int]
    belong_user_name: Optional[str]
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]
    tags: Optional[List[dict]]
    demands: Optional[List[dict]]
    reports: Optional[List[dict]]
    visits: Optional[List[dict]]
    follows: Optional[List[dict]]
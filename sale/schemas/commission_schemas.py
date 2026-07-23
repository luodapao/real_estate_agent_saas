"""
房地产SaaS销售管理系统 - 分销渠道与佣金模块数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ========== 渠道公司管理模型 ==========

class ChannelCreate(BaseModel):
    """创建渠道公司请求模型"""
    channel_code: str = Field(..., description="渠道编码", max_length=50)
    channel_name: str = Field(..., description="渠道名称", max_length=100)
    contact_person: str = Field(..., description="联系人", max_length=50)
    contact_mobile: str = Field(..., description="联系电话", max_length=20)
    channel_level: Optional[str] = Field("一级渠道", description="渠道等级")
    province: Optional[str] = Field(None, description="省份", max_length=50)
    city: Optional[str] = Field(None, description="城市", max_length=50)
    district: Optional[str] = Field(None, description="区县", max_length=50)
    address: Optional[str] = Field(None, description="详细地址", max_length=200)
    start_date: Optional[str] = Field(None, description="合作开始日期")
    end_date: Optional[str] = Field(None, description="合作结束日期")
    cooperation_status: Optional[int] = Field(1, description="合作状态（1：合作中 2：已终止）")
    remark: Optional[str] = Field(None, description="备注")


class ChannelUpdate(BaseModel):
    """更新渠道公司请求模型"""
    channel_name: Optional[str] = Field(None, description="渠道名称", max_length=100)
    contact_person: Optional[str] = Field(None, description="联系人", max_length=50)
    contact_mobile: Optional[str] = Field(None, description="联系电话", max_length=20)
    channel_level: Optional[str] = Field(None, description="渠道等级")
    address: Optional[str] = Field(None, description="详细地址", max_length=200)
    end_date: Optional[str] = Field(None, description="合作结束日期")
    cooperation_status: Optional[int] = Field(None, description="合作状态")
    remark: Optional[str] = Field(None, description="备注")


class ChannelResponse(BaseModel):
    """渠道公司响应模型"""
    channel_id: int
    channel_code: str
    channel_name: str
    contact_person: str
    contact_mobile: str
    channel_level: Optional[str]
    province: Optional[str]
    city: Optional[str]
    district: Optional[str]
    address: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    cooperation_status: int
    status: int
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]


# ========== 经纪人管理模型 ==========

class BrokerCreate(BaseModel):
    """创建经纪人请求模型"""
    channel_id: int = Field(..., description="渠道公司ID")
    broker_code: str = Field(..., description="经纪人编码", max_length=50)
    broker_name: str = Field(..., description="经纪人姓名", max_length=50)
    mobile: str = Field(..., description="手机号", max_length=20)
    id_card: Optional[str] = Field(None, description="身份证号", max_length=20)
    gender: Optional[int] = Field(1, description="性别（1：男 2：女）")
    broker_level: Optional[str] = Field("普通经纪人", description="经纪人等级")
    commission_rate: Optional[float] = Field(None, description="佣金比例（%）")
    work_status: Optional[int] = Field(1, description="工作状态（1：在职 2：离职）")
    entry_date: Optional[str] = Field(None, description="入职日期")
    remark: Optional[str] = Field(None, description="备注")


class BrokerUpdate(BaseModel):
    """更新经纪人请求模型"""
    broker_name: Optional[str] = Field(None, description="经纪人姓名", max_length=50)
    mobile: Optional[str] = Field(None, description="手机号", max_length=20)
    id_card: Optional[str] = Field(None, description="身份证号", max_length=20)
    gender: Optional[int] = Field(None, description="性别")
    broker_level: Optional[str] = Field(None, description="经纪人等级")
    commission_rate: Optional[float] = Field(None, description="佣金比例（%）")
    work_status: Optional[int] = Field(None, description="工作状态")
    remark: Optional[str] = Field(None, description="备注")


class BrokerResponse(BaseModel):
    """经纪人响应模型"""
    broker_id: int
    channel_id: int
    channel_name: Optional[str]
    broker_code: str
    broker_name: str
    mobile: str
    id_card: Optional[str]
    gender: Optional[int]
    broker_level: Optional[str]
    commission_rate: Optional[float]
    work_status: int
    entry_date: Optional[datetime]
    quit_date: Optional[datetime]
    status: int
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]


# ========== 佣金规则管理模型 ==========

class CommissionRuleCreate(BaseModel):
    """创建佣金规则请求模型"""
    project_id: Optional[int] = Field(None, description="楼盘ID（如果为空则表示全局规则）")
    room_type: Optional[str] = Field(None, description="户型", max_length=20)
    commission_rate: Optional[float] = Field(None, description="佣金比例（%）", ge=0)
    commission_amount: Optional[Decimal] = Field(None, description="固定佣金金额（元）", ge=0)
    rule_level: Optional[int] = Field(1, description="规则级别（优先级）")
    rule_status: Optional[int] = Field(1, description="规则状态（1：启用 0：停用）")
    effective_date: Optional[str] = Field(None, description="生效日期")
    expire_date: Optional[str] = Field(None, description="失效日期")
    remark: Optional[str] = Field(None, description="备注")


class CommissionRuleUpdate(BaseModel):
    """更新佣金规则请求模型"""
    room_type: Optional[str] = Field(None, description="户型", max_length=20)
    commission_rate: Optional[float] = Field(None, description="佣金比例（%）", ge=0)
    commission_amount: Optional[Decimal] = Field(None, description="固定佣金金额（元）", ge=0)
    rule_level: Optional[int] = Field(None, description="规则级别")
    rule_status: Optional[int] = Field(None, description="规则状态")
    effective_date: Optional[str] = Field(None, description="生效日期")
    expire_date: Optional[str] = Field(None, description="失效日期")
    remark: Optional[str] = Field(None, description="备注")


class CommissionRuleResponse(BaseModel):
    """佣金规则响应模型"""
    rule_id: int
    project_id: Optional[int]
    project_name: Optional[str]
    rule_type: str
    room_type: Optional[str]
    commission_rate: Optional[float]
    commission_amount: Optional[Decimal]
    rule_level: int
    rule_status: int
    effective_date: Optional[datetime]
    expire_date: Optional[datetime]
    status: int
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]


# ========== 佣金结算管理模型 ==========

class CommissionBillResponse(BaseModel):
    """佣金结算单响应模型"""
    bill_id: int
    bill_no: str
    project_id: int
    project_name: str
    channel_id: int
    channel_name: str
    broker_id: int
    broker_name: str
    contract_id: int
    contract_no: str
    bill_amount: Decimal
    bill_status: int
    audit_user_id: Optional[int]
    audit_user_name: Optional[str]
    audit_time: Optional[datetime]
    pay_time: Optional[datetime]
    freeze_reason: Optional[str]
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]


class CommissionBillListResponse(BaseModel):
    """佣金结算单列表响应模型"""
    total: int
    page: int
    page_size: int
    pages: int
    data: List[CommissionBillResponse]


class CommissionBillFreezeRequest(BaseModel):
    """冻结佣金结算单请求模型"""
    bill_id: int = Field(..., description="佣金结算单ID")
    freeze_reason: str = Field(..., description="冻结原因")


class ChannelDetailResponse(BaseModel):
    """渠道公司详情响应模型"""
    channel_id: int
    channel_code: str
    channel_name: str
    contact_person: str
    contact_mobile: str
    channel_level: Optional[str]
    province: Optional[str]
    city: Optional[str]
    district: Optional[str]
    address: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    cooperation_status: int
    status: int
    brokers: List[dict]
    statistics: dict
    create_time: Optional[datetime]
    update_time: Optional[datetime]


class BrokerDetailResponse(BaseModel):
    """经纪人详情响应模型"""
    broker_id: int
    channel_id: int
    broker_code: str
    broker_name: str
    mobile: str
    id_card: Optional[str]
    gender: Optional[int]
    broker_level: Optional[str]
    commission_rate: Optional[float]
    work_status: int
    entry_date: Optional[datetime]
    quit_date: Optional[datetime]
    status: int
    channel: Optional[dict]
    statistics: dict
    create_time: Optional[datetime]
    update_time: Optional[datetime]
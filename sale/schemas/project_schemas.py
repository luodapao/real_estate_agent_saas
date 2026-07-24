"""
房地产SaaS销售管理系统 - 楼盘销控模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field\nfrom common.schemas.response import ORMBaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ========== 楼盘管理模型 ==========

class ProjectCreate(BaseModel):
    """创建楼盘请求模型"""
    project_code: str = Field(..., description="楼盘编码", max_length=50)
    project_name: str = Field(..., description="楼盘名称", max_length=100)
    developer: str = Field(..., description="开发商", max_length=100)
    province: str = Field(..., description="省份", max_length=50)
    city: str = Field(..., description="城市", max_length=50)
    district: str = Field(..., description="区县", max_length=50)
    address: str = Field(..., description="详细地址", max_length=200)
    project_type: Optional[str] = Field(None, description="楼盘类型（住宅/商业/综合体）", max_length=20)
    project_status: Optional[int] = Field(1, description="项目状态（1：在售 2：售罄 3：停售）")
    project_image: Optional[str] = Field(None, description="项目图片URL")
    description: Optional[str] = Field(None, description="项目描述")
    sale_hotline: Optional[str] = Field(None, description="销售热线", max_length=20)
    opening_date: Optional[str] = Field(None, description="开盘日期")


class ProjectUpdate(BaseModel):
    """更新楼盘请求模型"""
    project_name: Optional[str] = Field(None, description="楼盘名称", max_length=100)
    developer: Optional[str] = Field(None, description="开发商", max_length=100)
    address: Optional[str] = Field(None, description="详细地址", max_length=200)
    project_type: Optional[str] = Field(None, description="楼盘类型", max_length=20)
    project_status: Optional[int] = Field(None, description="项目状态")
    project_image: Optional[str] = Field(None, description="项目图片URL")
    description: Optional[str] = Field(None, description="项目描述")
    sale_hotline: Optional[str] = Field(None, description="销售热线", max_length=20)
    opening_date: Optional[str] = Field(None, description="开盘日期")


class ProjectResponse(ORMBaseModel):
    """楼盘响应模型"""
    project_id: int
    project_code: str
    project_name: str
    developer: str
    province: str
    city: str
    district: str
    address: str
    project_type: Optional[str]
    project_status: int
    project_image: Optional[str]
    description: Optional[str]
    sale_hotline: Optional[str]
    opening_date: Optional[datetime]
    create_time: Optional[datetime]
    update_time: Optional[datetime]


# ========== 楼栋管理模型 ==========

class BuildingCreate(BaseModel):
    """创建楼栋请求模型"""
    project_id: int = Field(..., description="楼盘ID")
    building_code: str = Field(..., description="楼栋编码", max_length=50)
    building_name: str = Field(..., description="楼栋名称", max_length=100)
    building_type: Optional[str] = Field("高层", description="楼栋类型（高层/多层/洋房/别墅）")
    floor_count: Optional[int] = Field(None, description="楼层数")
    unit_per_floor: Optional[int] = Field(None, description="每层单元数")
    building_status: Optional[int] = Field(1, description="楼栋状态（1：在售 2：售罄 3：停售）")
    description: Optional[str] = Field(None, description="楼栋描述")


class BuildingUpdate(BaseModel):
    """更新楼栋请求模型"""
    building_name: Optional[str] = Field(None, description="楼栋名称", max_length=100)
    building_type: Optional[str] = Field(None, description="楼栋类型")
    floor_count: Optional[int] = Field(None, description="楼层数")
    unit_per_floor: Optional[int] = Field(None, description="每层单元数")
    building_status: Optional[int] = Field(None, description="楼栋状态")
    description: Optional[str] = Field(None, description="楼栋描述")


class BuildingResponse(ORMBaseModel):
    """楼栋响应模型"""
    building_id: int
    project_id: int
    building_code: str
    building_name: str
    building_type: Optional[str]
    floor_count: Optional[int]
    unit_per_floor: Optional[int]
    building_status: int
    description: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]


# ========== 单元管理模型 ==========

class UnitCreate(BaseModel):
    """创建单元请求模型"""
    building_id: int = Field(..., description="楼栋ID")
    unit_code: str = Field(..., description="单元编码", max_length=50)
    unit_name: str = Field(..., description="单元名称", max_length=50)
    floor_count: Optional[int] = Field(None, description="楼层数")
    unit_status: Optional[int] = Field(1, description="单元状态")


class UnitUpdate(BaseModel):
    """更新单元请求模型"""
    unit_name: Optional[str] = Field(None, description="单元名称", max_length=50)
    floor_count: Optional[int] = Field(None, description="楼层数")
    unit_status: Optional[int] = Field(None, description="单元状态")


class UnitResponse(ORMBaseModel):
    """单元响应模型"""
    unit_id: int
    building_id: int
    unit_code: str
    unit_name: str
    floor_count: Optional[int]
    unit_status: int
    create_time: Optional[datetime]
    update_time: Optional[datetime]


# ========== 房源管理模型 ==========

class HouseCreate(BaseModel):
    """创建房源请求模型"""
    project_id: int = Field(..., description="楼盘ID")
    building_id: int = Field(..., description="楼栋ID")
    unit_id: Optional[int] = Field(None, description="单元ID")
    house_code: str = Field(..., description="房源编码", max_length=50)
    house_name: str = Field(..., description="房源名称", max_length=100)
    floor: int = Field(..., description="楼层")
    room_type: str = Field(..., description="户型", max_length=20)
    building_area: Decimal = Field(..., description="建筑面积", ge=0)
    use_area: Optional[Decimal] = Field(None, description="使用面积", ge=0)
    price: Decimal = Field(..., description="单价（元/㎡）", ge=0)
    total_price: Optional[Decimal] = Field(None, description="总价（元）", ge=0)
    house_status: Optional[int] = Field(1, description="房源状态（1：可售 2：已售 3：锁定 4：预定 5：停售）")
    house_type: Optional[str] = Field("住宅", description="房源类型（住宅/商业/车位）")
    orientation: Optional[str] = Field(None, description="朝向", max_length=10)
    decoration: Optional[str] = Field(None, description="装修情况", max_length=20)
    room_num: Optional[int] = Field(None, description="室数")
    hall_num: Optional[int] = Field(None, description="厅数")
    toilet_num: Optional[int] = Field(None, description="卫数")
    description: Optional[str] = Field(None, description="房源描述")
    remark: Optional[str] = Field(None, description="备注")


class HouseUpdate(BaseModel):
    """更新房源请求模型"""
    house_name: Optional[str] = Field(None, description="房源名称", max_length=100)
    price: Optional[Decimal] = Field(None, description="单价（元/㎡）", ge=0)
    total_price: Optional[Decimal] = Field(None, description="总价（元）", ge=0)
    house_status: Optional[int] = Field(None, description="房源状态")
    orientation: Optional[str] = Field(None, description="朝向", max_length=10)
    decoration: Optional[str] = Field(None, description="装修情况", max_length=20)
    description: Optional[str] = Field(None, description="房源描述")
    remark: Optional[str] = Field(None, description="备注")


class HouseResponse(ORMBaseModel):
    """房源响应模型"""
    house_id: int
    project_id: int
    building_id: int
    unit_id: Optional[int]
    house_code: str
    house_name: str
    floor: int
    room_type: str
    building_area: Decimal
    use_area: Optional[Decimal]
    price: Decimal
    total_price: Optional[Decimal]
    house_status: int
    house_type: Optional[str]
    orientation: Optional[str]
    decoration: Optional[str]
    room_num: Optional[int]
    hall_num: Optional[int]
    toilet_num: Optional[int]
    description: Optional[str]
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]


class HouseLockRequest(BaseModel):
    """锁定房源请求模型"""
    house_id: int = Field(..., description="房源ID")
    customer_id: int = Field(..., description="客户ID")
    expire_minutes: Optional[int] = Field(30, description="过期时间（分钟）")


class HouseControlPanelResponse(ORMBaseModel):
    """销控面板响应模型"""
    project_id: int
    total_houses: int
    sold_count: int
    available_count: int
    locked_count: int
    reserved_count: int
    building_stats: List[dict]
    room_type_stats: List[dict]


# ========== 项目规则管理模型 ==========

class ProjectRuleCreate(BaseModel):
    """创建项目规则请求模型"""
    project_id: Optional[int] = Field(None, description="楼盘ID（为空表示全局规则）")
    rule_key: str = Field(..., description="规则键：visit_protect_days（到访保护期天数）/ report_protect_days（报备保护期天数）", max_length=50)
    rule_value: int = Field(..., description="规则值（天数）", ge=0)
    rule_desc: Optional[str] = Field(None, description="规则描述", max_length=255)
    rule_status: Optional[int] = Field(1, description="规则状态：1-启用 2-停用")


class ProjectRuleUpdate(BaseModel):
    """更新项目规则请求模型"""
    rule_value: Optional[int] = Field(None, description="规则值（天数）", ge=0)
    rule_desc: Optional[str] = Field(None, description="规则描述", max_length=255)
    rule_status: Optional[int] = Field(None, description="规则状态：1-启用 2-停用")


class ProjectRuleResponse(ORMBaseModel):
    """项目规则响应模型"""
    rule_id: int
    project_id: Optional[int]
    rule_key: str
    rule_value: int
    rule_desc: Optional[str]
    rule_status: int
    create_time: Optional[datetime]
    update_time: Optional[datetime]
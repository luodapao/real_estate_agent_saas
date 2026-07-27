"""
后台管理系统 - 字典管理模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from common.schemas.response import ORMBaseModel


# ========== 字典类型模型 ==========

class DictTypeCreate(BaseModel):
    """创建字典类型请求模型"""
    dict_name: str = Field(..., description="字典名称", max_length=100)
    dict_code: str = Field(..., description="字典编码", max_length=50)
    status: Optional[int] = Field(1, description="状态：1-正常，2-禁用")
    remark: Optional[str] = Field(None, description="备注")


class DictTypeUpdate(BaseModel):
    """更新字典类型请求模型"""
    dict_name: Optional[str] = Field(None, description="字典名称", max_length=100)
    status: Optional[int] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")


class DictTypeResponse(ORMBaseModel):
    """字典类型响应模型"""
    dict_id: int = Field(..., description="字典类型ID")
    dict_name: str = Field(..., description="字典名称")
    dict_code: str = Field(..., description="字典编码")
    status: int = Field(..., description="状态")
    remark: Optional[str] = Field(None, description="备注")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


# ========== 字典项模型 ==========

class DictItemCreate(BaseModel):
    """创建字典项请求模型"""
    dict_type: str = Field(..., description="字典类型", max_length=50)
    dict_label: str = Field(..., description="字典标签", max_length=100)
    dict_value: str = Field(..., description="字典值", max_length=100)
    sort_order: Optional[int] = Field(0, description="排序号")
    status: Optional[int] = Field(1, description="状态：1-正常，2-禁用")
    remark: Optional[str] = Field(None, description="备注")


class DictItemUpdate(BaseModel):
    """更新字典项请求模型"""
    dict_label: Optional[str] = Field(None, description="字典标签", max_length=100)
    dict_value: Optional[str] = Field(None, description="字典值", max_length=100)
    sort_order: Optional[int] = Field(None, description="排序号")
    status: Optional[int] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")


class DictItemResponse(ORMBaseModel):
    """字典项响应模型"""
    item_id: int = Field(..., description="字典项ID")
    dict_id: int = Field(..., description="字典类型ID")
    dict_label: str = Field(..., description="字典标签")
    dict_value: str = Field(..., description="字典值")
    sort_order: int = Field(..., description="排序号")
    status: int = Field(..., description="状态")
    remark: Optional[str] = Field(None, description="备注")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class DictItemListResponse(BaseModel):
    """字典项列表响应模型"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    size: int = Field(..., description="每页数量")
    data: List[DictItemResponse] = Field(..., description="字典项列表")


class DictTypeListResponse(BaseModel):
    """字典类型列表响应模型"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    size: int = Field(..., description="每页数量")
    data: List[DictTypeResponse] = Field(..., description="字典类型列表")

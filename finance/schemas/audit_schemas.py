"""
房地产SaaS财务管理系统 - 财务审计追溯模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field\nfrom common.schemas.response import ORMBaseModel, field_validator
from typing import Optional
from datetime import datetime


# ========== 财务操作审计日志 ==========

class OperateLogCreate(BaseModel):
    """创建财务操作审计日志请求模型"""
    operate_no: Optional[str] = Field(None, description="审计日志唯一编号，租户唯一，不传则自动生成", max_length=64)
    operate_user_id: int = Field(..., description="操作人ID")
    operate_user_name: str = Field(..., description="操作人姓名冗余", max_length=50)
    operate_dept_id: Optional[int] = Field(None, description="操作人所属部门ID")
    operate_dept_name: Optional[str] = Field(None, description="操作人所属部门名称冗余", max_length=100)
    operate_ip: Optional[str] = Field(None, description="操作客户端IP地址", max_length=64)
    operate_mac: Optional[str] = Field(None, description="设备MAC地址", max_length=64)
    terminal_type: int = Field(1, description="操作终端：1PC端 2移动端 3后台管理端")
    request_url: Optional[str] = Field(None, description="操作请求接口地址", max_length=255)
    biz_module: int = Field(..., description="业务模块：1收款管理 2退款管理 3应付应收台账 4预付款管理 5其他往来款 6资金对账 7会计凭证 8佣金结算 9费用报销 10财务配置")
    operate_type: int = Field(..., description="操作类型：1新增 2修改 3删除 4审核 5反审核 6作废 7红冲 8结账 9反结账 10配置变更 11批量操作")
    biz_type: Optional[int] = Field(None, description="业务单据类型：1收款单 2退款单 3应付台账 4应收台账 5预付款单 6往来款单 7会计凭证 8渠道对账 9资金轧账")
    biz_id: Optional[int] = Field(None, description="关联业务单据主ID")
    biz_no: Optional[str] = Field(None, description="关联业务单据编号", max_length=64)
    voucher_id: Optional[int] = Field(None, description="关联会计凭证ID，凭证操作专属溯源")
    voucher_no: Optional[str] = Field(None, description="关联会计凭证编号", max_length=64)
    operate_summary: str = Field(..., description="操作简短摘要", max_length=255)
    operate_content: str = Field(..., description="操作详细描述、变更说明")
    old_data: Optional[str] = Field(None, description="操作前完整数据JSON快照")
    new_data: Optional[str] = Field(None, description="操作后完整数据JSON快照")
    operate_status: int = Field(1, description="操作结果状态：1操作成功 2操作失败 3部分成功")
    error_msg: Optional[str] = Field(None, description="操作失败异常信息、报错详情")

    @field_validator('terminal_type')
    def validate_terminal_type(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError('操作终端必须为1(PC端)、2(移动端)或3(后台管理端)')
        return v

    @field_validator('biz_module')
    def validate_biz_module(cls, v):
        if v not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            raise ValueError('业务模块必须为1-10之间的整数')
        return v

    @field_validator('operate_type')
    def validate_operate_type(cls, v):
        if v not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
            raise ValueError('操作类型必须为1-11之间的整数')
        return v

    @field_validator('biz_type')
    def validate_biz_type(cls, v):
        if v is not None and v not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            raise ValueError('业务单据类型必须为1-9之间的整数')
        return v

    @field_validator('operate_status')
    def validate_operate_status(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError('操作结果状态必须为1(成功)、2(失败)或3(部分成功)')
        return v


class OperateLogUpdate(BaseModel):
    """更新财务操作审计日志请求模型"""
    operate_user_id: Optional[int] = Field(None, description="操作人ID")
    operate_user_name: Optional[str] = Field(None, description="操作人姓名冗余", max_length=50)
    operate_dept_id: Optional[int] = Field(None, description="操作人所属部门ID")
    operate_dept_name: Optional[str] = Field(None, description="操作人所属部门名称冗余", max_length=100)
    operate_ip: Optional[str] = Field(None, description="操作客户端IP地址", max_length=64)
    operate_mac: Optional[str] = Field(None, description="设备MAC地址", max_length=64)
    terminal_type: Optional[int] = Field(None, description="操作终端")
    request_url: Optional[str] = Field(None, description="操作请求接口地址", max_length=255)
    biz_module: Optional[int] = Field(None, description="业务模块")
    operate_type: Optional[int] = Field(None, description="操作类型")
    biz_type: Optional[int] = Field(None, description="业务单据类型")
    biz_id: Optional[int] = Field(None, description="关联业务单据主ID")
    biz_no: Optional[str] = Field(None, description="关联业务单据编号", max_length=64)
    voucher_id: Optional[int] = Field(None, description="关联会计凭证ID")
    voucher_no: Optional[str] = Field(None, description="关联会计凭证编号", max_length=64)
    operate_summary: Optional[str] = Field(None, description="操作简短摘要", max_length=255)
    operate_content: Optional[str] = Field(None, description="操作详细描述、变更说明")
    old_data: Optional[str] = Field(None, description="操作前完整数据JSON快照")
    new_data: Optional[str] = Field(None, description="操作后完整数据JSON快照")
    operate_status: Optional[int] = Field(None, description="操作结果状态")
    error_msg: Optional[str] = Field(None, description="操作失败异常信息、报错详情")


class OperateLogResponse(ORMBaseModel):
    """财务操作审计日志响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    operate_no: str
    operate_user_id: int
    operate_user_name: str
    operate_dept_id: Optional[int]
    operate_dept_name: Optional[str]
    operate_ip: Optional[str]
    operate_mac: Optional[str]
    terminal_type: int
    request_url: Optional[str]
    biz_module: int
    operate_type: int
    biz_type: Optional[int]
    biz_id: Optional[int]
    biz_no: Optional[str]
    voucher_id: Optional[int]
    voucher_no: Optional[str]
    operate_summary: str
    operate_content: str
    old_data: Optional[str]
    new_data: Optional[str]
    operate_status: int
    error_msg: Optional[str]
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime
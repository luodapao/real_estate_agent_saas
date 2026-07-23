"""
房地产SaaS财务管理系统 - 会计凭证模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# ========== 会计凭证主表 ==========

class VoucherCreate(BaseModel):
    """创建会计凭证请求模型"""
    voucher_no: Optional[str] = Field(None, description="凭证编号，租户唯一，不传则自动生成", max_length=64)
    voucher_word: str = Field("记", description="凭证字：收/付/转/记", max_length=16)
    voucher_type: int = Field(..., description="凭证类型：1收款凭证 2付款凭证 3转账凭证")
    voucher_year: int = Field(..., description="会计年度")
    voucher_month: str = Field(..., description="会计月份", max_length=32)
    voucher_date: date = Field(..., description="凭证做账日期")
    attach_num: int = Field(0, description="附件张数")
    source_type: int = Field(..., description="来源类型：1收款 2退款 3销售佣金 4费用报销 5工程成本 6广告成本 7应收应付 8预付核销 9往来款 10手工录入")
    source_biz_id: int = Field(..., description="关联上游业务单据ID")
    source_biz_no: str = Field(..., description="关联上游业务单据编号", max_length=64)
    is_red_flush: int = Field(0, description="0正常凭证 1红字冲销凭证")
    red_flush_voucher_id: Optional[int] = Field(None, description="对应被红冲的原凭证ID")
    red_flush_reason: Optional[str] = Field(None, description="红冲作废原因说明")
    is_manual: int = Field(0, description="0系统自动生成 1财务手工录入")
    summary: str = Field(..., description="凭证总摘要", max_length=255)
    voucher_status: int = Field(1, description="凭证状态：1草稿 2已审核 3已结账 4已作废 5已红冲 6反结账")
    make_user_id: int = Field(..., description="制单人ID")
    audit_user_id: Optional[int] = Field(None, description="审核人ID")
    settle_user_id: Optional[int] = Field(None, description="月末结账人ID")
    voucher_file_url: Optional[str] = Field(None, description="凭证附件、单据扫描件、对账资料", max_length=1024)
    remark: Optional[str] = Field(None, description="凭证备注、特殊账务处理说明")

    @field_validator('voucher_type')
    def validate_voucher_type(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError('凭证类型必须为1(收款凭证)、2(付款凭证)或3(转账凭证)')
        return v

    @field_validator('source_type')
    def validate_source_type(cls, v):
        if v not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            raise ValueError('来源类型必须为1-10之间的整数')
        return v

    @field_validator('is_red_flush')
    def validate_is_red_flush(cls, v):
        if v not in [0, 1]:
            raise ValueError('is_red_flush必须为0或1')
        return v

    @field_validator('is_manual')
    def validate_is_manual(cls, v):
        if v not in [0, 1]:
            raise ValueError('is_manual必须为0或1')
        return v

    @field_validator('voucher_status')
    def validate_voucher_status(cls, v):
        if v not in [1, 2, 3, 4, 5, 6]:
            raise ValueError('凭证状态必须为1-6之间的整数')
        return v


class VoucherUpdate(BaseModel):
    """更新会计凭证请求模型"""
    voucher_word: Optional[str] = Field(None, description="凭证字：收/付/转/记", max_length=16)
    voucher_date: Optional[date] = Field(None, description="凭证做账日期")
    attach_num: Optional[int] = Field(None, description="附件张数")
    source_type: Optional[int] = Field(None, description="来源类型")
    source_biz_id: Optional[int] = Field(None, description="关联上游业务单据ID")
    source_biz_no: Optional[str] = Field(None, description="关联上游业务单据编号")
    is_red_flush: Optional[int] = Field(None, description="0正常凭证 1红字冲销凭证")
    red_flush_voucher_id: Optional[int] = Field(None, description="对应被红冲的原凭证ID")
    red_flush_reason: Optional[str] = Field(None, description="红冲作废原因说明")
    is_manual: Optional[int] = Field(None, description="0系统自动生成 1财务手工录入")
    summary: Optional[str] = Field(None, description="凭证总摘要", max_length=255)
    voucher_status: Optional[int] = Field(None, description="凭证状态")
    audit_user_id: Optional[int] = Field(None, description="审核人ID")
    audit_time: Optional[datetime] = Field(None, description="凭证审核时间")
    settle_user_id: Optional[int] = Field(None, description="月末结账人ID")
    settle_time: Optional[datetime] = Field(None, description="月末结账时间")
    voucher_file_url: Optional[str] = Field(None, description="凭证附件、单据扫描件、对账资料")
    remark: Optional[str] = Field(None, description="凭证备注、特殊账务处理说明")


class VoucherResponse(BaseModel):
    """会计凭证响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    voucher_no: str
    voucher_word: str
    voucher_type: int
    voucher_year: int
    voucher_month: str
    voucher_date: date
    attach_num: int
    source_type: int
    source_biz_id: int
    source_biz_no: str
    is_red_flush: int
    red_flush_voucher_id: Optional[int]
    red_flush_reason: Optional[str]
    is_manual: int
    summary: str
    voucher_status: int
    make_user_id: int
    audit_user_id: Optional[int]
    audit_time: Optional[datetime]
    settle_user_id: Optional[int]
    settle_time: Optional[datetime]
    voucher_file_url: Optional[str]
    remark: Optional[str]
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 凭证明细 ==========

class VoucherItemCreate(BaseModel):
    """创建凭证明细请求模型"""
    voucher_id: int = Field(..., description="关联凭证主表ID")
    subject_id: int = Field(..., description="会计科目ID")
    subject_code: str = Field(..., description="科目编码冗余", max_length=64)
    subject_name: str = Field(..., description="科目名称冗余", max_length=128)
    subject_type: int = Field(..., description="科目类型：1资产 2负债 3权益 4成本 5损益")
    borrow_amount: Decimal = Field(0, description="借方发生金额")
    lend_amount: Decimal = Field(0, description="贷方发生金额")
    original_currency: str = Field("CNY", description="原币币种", max_length=32)
    original_amount: Decimal = Field(0, description="原币金额")
    exchange_rate: Decimal = Field(1.0000, description="记账汇率")
    project_id: Optional[int] = Field(None, description="辅助核算-楼盘ID")
    project_name: Optional[str] = Field(None, description="楼盘名称冗余", max_length=128)
    building_id: Optional[int] = Field(None, description="辅助核算-楼栋ID")
    building_name: Optional[str] = Field(None, description="楼栋名称冗余", max_length=128)
    customer_id: Optional[int] = Field(None, description="辅助核算-购房客户ID")
    supplier_id: Optional[int] = Field(None, description="辅助核算-供应商ID")
    channel_id: Optional[int] = Field(None, description="辅助核算-分销渠道ID")
    staff_id: Optional[int] = Field(None, description="辅助核算-员工ID")
    dept_id: Optional[int] = Field(None, description="辅助核算-部门ID")
    item_summary: Optional[str] = Field(None, description="分录行明细摘要", max_length=255)
    item_sort: int = Field(0, description="分录行排序号")
    item_remark: Optional[str] = Field(None, description="分录明细备注、账务说明")

    @field_validator('subject_type')
    def validate_subject_type(cls, v):
        if v not in [1, 2, 3, 4, 5]:
            raise ValueError('科目类型必须为1(资产)、2(负债)、3(权益)、4(成本)或5(损益)')
        return v


class VoucherItemUpdate(BaseModel):
    """更新凭证明细请求模型"""
    subject_id: Optional[int] = Field(None, description="会计科目ID")
    subject_code: Optional[str] = Field(None, description="科目编码冗余", max_length=64)
    subject_name: Optional[str] = Field(None, description="科目名称冗余", max_length=128)
    subject_type: Optional[int] = Field(None, description="科目类型")
    borrow_amount: Optional[Decimal] = Field(None, description="借方发生金额")
    lend_amount: Optional[Decimal] = Field(None, description="贷方发生金额")
    original_currency: Optional[str] = Field(None, description="原币币种", max_length=32)
    original_amount: Optional[Decimal] = Field(None, description="原币金额")
    exchange_rate: Optional[Decimal] = Field(None, description="记账汇率")
    project_id: Optional[int] = Field(None, description="辅助核算-楼盘ID")
    project_name: Optional[str] = Field(None, description="楼盘名称冗余", max_length=128)
    building_id: Optional[int] = Field(None, description="辅助核算-楼栋ID")
    building_name: Optional[str] = Field(None, description="楼栋名称冗余", max_length=128)
    customer_id: Optional[int] = Field(None, description="辅助核算-购房客户ID")
    supplier_id: Optional[int] = Field(None, description="辅助核算-供应商ID")
    channel_id: Optional[int] = Field(None, description="辅助核算-分销渠道ID")
    staff_id: Optional[int] = Field(None, description="辅助核算-员工ID")
    dept_id: Optional[int] = Field(None, description="辅助核算-部门ID")
    item_summary: Optional[str] = Field(None, description="分录行明细摘要", max_length=255)
    item_sort: Optional[int] = Field(None, description="分录行排序号")
    item_remark: Optional[str] = Field(None, description="分录明细备注、账务说明")


class VoucherItemResponse(BaseModel):
    """凭证明细响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    voucher_id: int
    subject_id: int
    subject_code: str
    subject_name: str
    subject_type: int
    borrow_amount: Decimal
    lend_amount: Decimal
    original_currency: str
    original_amount: Decimal
    exchange_rate: Decimal
    project_id: Optional[int]
    project_name: Optional[str]
    building_id: Optional[int]
    building_name: Optional[str]
    customer_id: Optional[int]
    supplier_id: Optional[int]
    channel_id: Optional[int]
    staff_id: Optional[int]
    dept_id: Optional[int]
    item_summary: Optional[str]
    item_sort: int
    item_remark: Optional[str]
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 凭证审核与红冲 ==========

class VoucherAudit(BaseModel):
    """凭证审核请求模型"""
    id: int = Field(..., description="凭证ID")
    audit_user_id: int = Field(..., description="审核人ID")
    audit_status: int = Field(..., description="审核状态：2(已审核)或4(已作废)")

    @field_validator('audit_status')
    def validate_audit_status(cls, v):
        if v not in [2, 4]:
            raise ValueError('审核状态必须为2(已审核)或4(已作废)')
        return v


class VoucherRedFlush(BaseModel):
    """凭证红冲请求模型"""
    id: int = Field(..., description="凭证ID")
    red_flush_reason: str = Field(..., description="红冲原因说明")
    make_user_id: int = Field(..., description="制单人ID")


# ========== 凭证列表响应（含明细） ==========

class VoucherWithItemsResponse(BaseModel):
    """含明细的凭证响应模型"""
    voucher: VoucherResponse
    items: List[VoucherItemResponse]
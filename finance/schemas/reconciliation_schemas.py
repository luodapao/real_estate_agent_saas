"""
房地产SaaS财务管理系统 - 资金对账模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field, field_validator
from common.schemas.response import ORMBaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# ========== 银行对账记录 ==========

class BankCheckCreate(BaseModel):
    """创建银行对账记录请求模型"""
    check_no: Optional[str] = Field(None, description="银行对账单号，租户唯一，不传则自动生成", max_length=64)
    account_id: int = Field(..., description="银行账户ID")
    account_name: str = Field(..., description="银行账户名称", max_length=100)
    account_bank: Optional[str] = Field(None, description="开户银行", max_length=100)
    check_date: date = Field(..., description="对账所属日期")
    bank_flow_no: str = Field(..., description="银行官方流水号", max_length=64)
    bank_flow_type: int = Field(..., description="流水类型：1收款 2付款 3退款 4手续费")
    bank_trade_time: datetime = Field(..., description="银行交易发生时间")
    bank_amount: Decimal = Field(..., description="银行流水交易金额")
    relate_biz_type: int = Field(..., description="业务类型：1房款收款 2佣金付款 3费用报销 4工程付款 5渠道结算 6其他往来")
    relate_biz_id: Optional[int] = Field(None, description="关联系统业务单据ID")
    relate_biz_no: Optional[str] = Field(None, description="关联系统业务单据编号", max_length=64)
    voucher_no: Optional[str] = Field(None, description="对应财务凭证编号", max_length=64)
    check_status: int = Field(1, description="对账状态：1未匹配 2已匹配对账一致 3对账差异 4手动调平 5作废")
    check_user_id: Optional[int] = Field(None, description="对账操作人ID")
    create_user_id: int = Field(..., description="单据制单人ID")
    check_file_url: Optional[str] = Field(None, description="银行回单、对账调节表、差异处理附件", max_length=1024)
    remark: Optional[str] = Field(None, description="对账通用备注")

    @field_validator('bank_flow_type')
    def validate_bank_flow_type(cls, v):
        if v not in [1, 2, 3, 4]:
            raise ValueError('流水类型必须为1(收款)、2(付款)、3(退款)或4(手续费)')
        return v

    @field_validator('relate_biz_type')
    def validate_relate_biz_type(cls, v):
        if v not in [1, 2, 3, 4, 5, 6]:
            raise ValueError('业务类型必须为1(房款收款)、2(佣金付款)、3(费用报销)、4(工程付款)、5(渠道结算)或6(其他往来)')
        return v

    @field_validator('check_status')
    def validate_check_status(cls, v):
        if v not in [1, 2, 3, 4, 5]:
            raise ValueError('对账状态必须为1(未匹配)、2(已匹配对账一致)、3(对账差异)、4(手动调平)或5(作废)')
        return v


class BankCheckUpdate(BaseModel):
    """更新银行对账记录请求模型"""
    check_finish_time: Optional[datetime] = Field(None, description="对账完成时间")
    system_amount: Optional[Decimal] = Field(None, description="系统匹配业务金额")
    relate_biz_type: Optional[int] = Field(None, description="业务类型")
    relate_biz_id: Optional[int] = Field(None, description="关联系统业务单据ID")
    relate_biz_no: Optional[str] = Field(None, description="关联系统业务单据编号")
    voucher_no: Optional[str] = Field(None, description="对应财务凭证编号")
    check_status: Optional[int] = Field(None, description="对账状态")
    diff_reason: Optional[str] = Field(None, description="对账差异原因说明")
    solve_remark: Optional[str] = Field(None, description="差异处理方案、调平备注")
    check_user_id: Optional[int] = Field(None, description="对账操作人ID")
    check_file_url: Optional[str] = Field(None, description="银行回单、对账调节表、差异处理附件")
    remark: Optional[str] = Field(None, description="对账通用备注")


class BankCheckMatch(BaseModel):
    """银行对账自动匹配请求模型"""
    account_id: Optional[int] = Field(None, description="银行账户ID")
    check_date: Optional[date] = Field(None, description="对账日期")
    amount_tolerance: Decimal = Field(0.01, description="金额容差范围")


class BankCheckFinish(BaseModel):
    """银行对账完成请求模型"""
    id: int = Field(..., description="银行对账记录ID")
    system_amount: Decimal = Field(..., description="系统匹配业务金额")
    relate_biz_type: int = Field(..., description="业务类型")
    relate_biz_id: Optional[int] = Field(None, description="关联业务单据ID")
    relate_biz_no: Optional[str] = Field(None, description="关联业务单据编号")
    check_user_id: int = Field(..., description="对账操作人ID")
    diff_reason: Optional[str] = Field(None, description="差异原因")
    solve_remark: Optional[str] = Field(None, description="处理方案")


class BankCheckResponse(ORMBaseModel):
    """银行对账记录响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    check_no: str
    account_id: int
    account_name: str
    account_bank: Optional[str]
    check_date: date
    check_finish_time: Optional[datetime]
    bank_flow_no: str
    bank_flow_type: int
    bank_trade_time: datetime
    bank_amount: Decimal
    system_amount: Decimal
    diff_amount: Decimal
    relate_biz_type: int
    relate_biz_id: Optional[int]
    relate_biz_no: Optional[str]
    voucher_no: Optional[str]
    check_status: int
    diff_reason: Optional[str]
    solve_remark: Optional[str]
    check_user_id: Optional[int]
    create_user_id: int
    check_file_url: Optional[str]
    remark: Optional[str]
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 每日资金轧账 ==========

class DailyCashAccountCreate(BaseModel):
    """创建每日资金轧账请求模型"""
    account_id: int = Field(..., description="银行账户ID")
    account_name: str = Field(..., description="账户名称", max_length=100)
    project_id: Optional[int] = Field(None, description="楼盘ID")
    project_name: Optional[str] = Field(None, description="楼盘名称", max_length=128)
    account_date: date = Field(..., description="资金轧账日期")
    beginning_balance: Decimal = Field(0, description="当日期初账户余额")
    total_receipt: Decimal = Field(0, description="当日收款总额")
    house_receipt: Decimal = Field(0, description="当日房款收款")
    other_receipt: Decimal = Field(0, description="当日其他收款")
    total_refund: Decimal = Field(0, description="当日退款总额")
    house_refund: Decimal = Field(0, description="当日房款退款")
    total_pay: Decimal = Field(0, description="当日付款总额")
    commission_pay: Decimal = Field(0, description="当日佣金提成付款")
    cost_pay: Decimal = Field(0, description="当日费用/工程付款")
    other_pay: Decimal = Field(0, description="当日其他付款")
    bank_ending_balance: Decimal = Field(0, description="银行官方期末余额")
    account_status: int = Field(1, description="轧账状态：1未轧账 2轧账正常 3余额差异 4已审核归档 5作废重轧")
    create_user_id: int = Field(..., description="轧账制单人ID")
    voucher_no: Optional[str] = Field(None, description="日结汇总凭证编号", max_length=64)
    account_file_url: Optional[str] = Field(None, description="日结报表、对账表附件", max_length=1024)
    diff_remark: Optional[str] = Field(None, description="余额差异原因及处理说明")
    remark: Optional[str] = Field(None, description="轧账通用备注")

    @field_validator('account_status')
    def validate_account_status(cls, v):
        if v not in [1, 2, 3, 4, 5]:
            raise ValueError('轧账状态必须为1(未轧账)、2(轧账正常)、3(余额差异)、4(已审核归档)或5(作废重轧)')
        return v


class DailyCashAccountUpdate(BaseModel):
    """更新每日资金轧账请求模型"""
    total_receipt: Optional[Decimal] = Field(None, description="当日收款总额")
    house_receipt: Optional[Decimal] = Field(None, description="当日房款收款")
    other_receipt: Optional[Decimal] = Field(None, description="当日其他收款")
    total_refund: Optional[Decimal] = Field(None, description="当日退款总额")
    house_refund: Optional[Decimal] = Field(None, description="当日房款退款")
    total_pay: Optional[Decimal] = Field(None, description="当日付款总额")
    commission_pay: Optional[Decimal] = Field(None, description="当日佣金提成付款")
    cost_pay: Optional[Decimal] = Field(None, description="当日费用/工程付款")
    other_pay: Optional[Decimal] = Field(None, description="当日其他付款")
    bank_ending_balance: Optional[Decimal] = Field(None, description="银行官方期末余额")
    account_status: Optional[int] = Field(None, description="轧账状态")
    audit_user_id: Optional[int] = Field(None, description="资金审核人ID")
    audit_time: Optional[datetime] = Field(None, description="审核归档时间")
    voucher_no: Optional[str] = Field(None, description="日结汇总凭证编号")
    account_file_url: Optional[str] = Field(None, description="日结报表、对账表附件")
    diff_remark: Optional[str] = Field(None, description="余额差异原因及处理说明")
    remark: Optional[str] = Field(None, description="轧账通用备注")


class DailyCashAccountAudit(BaseModel):
    """每日资金轧账审核请求模型"""
    id: int = Field(..., description="轧账记录ID")
    audit_user_id: int = Field(..., description="审核人ID")
    audit_status: int = Field(..., description="审核结果：2(通过)或5(驳回)")
    diff_remark: Optional[str] = Field(None, description="审核意见/差异说明")

    @field_validator('audit_status')
    def validate_audit_status(cls, v):
        if v not in [2, 5]:
            raise ValueError('审核结果必须为2(通过)或5(驳回)')
        return v


class DailyCashAccountResponse(ORMBaseModel):
    """每日资金轧账响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    account_id: int
    account_name: str
    project_id: Optional[int]
    project_name: Optional[str]
    account_date: date
    beginning_balance: Decimal
    ending_balance: Decimal
    bank_ending_balance: Decimal
    balance_diff: Decimal
    total_receipt: Decimal
    house_receipt: Decimal
    other_receipt: Decimal
    total_refund: Decimal
    house_refund: Decimal
    total_pay: Decimal
    commission_pay: Decimal
    cost_pay: Decimal
    other_pay: Decimal
    account_status: int
    create_user_id: int
    audit_user_id: Optional[int]
    audit_time: Optional[datetime]
    voucher_no: Optional[str]
    account_file_url: Optional[str]
    diff_remark: Optional[str]
    remark: Optional[str]
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 渠道月度对账 ==========

class ChannelReconcileCreate(BaseModel):
    """创建渠道月度对账请求模型"""
    reconcile_no: Optional[str] = Field(None, description="渠道对账单号，租户唯一，不传则自动生成", max_length=64)
    project_id: int = Field(..., description="楼盘ID")
    project_name: str = Field(..., description="楼盘名称", max_length=128)
    building_scope: Optional[str] = Field(None, description="本次对账覆盖楼栋ID，逗号分隔", max_length=512)
    channel_id: int = Field(..., description="分销渠道ID")
    channel_name: str = Field(..., description="渠道名称", max_length=100)
    reconcile_month: str = Field(..., description="对账月份", max_length=32)
    settle_start: date = Field(..., description="对账周期起始日")
    settle_end: date = Field(..., description="对账周期截止日")
    channel_deal_num: int = Field(0, description="渠道申报成交套数")
    system_deal_num: int = Field(0, description="系统审核成交套数")
    refund_num: int = Field(0, description="周期内退房套数")
    channel_amount: Decimal = Field(0, description="渠道自主申报佣金金额")
    system_amount: Decimal = Field(0, description="系统核算合规佣金金额")
    deduct_amount: Decimal = Field(0, description="周期退房/违规扣减金额")
    commission_pay_id: Optional[int] = Field(None, description="关联渠道佣金付款单ID")
    voucher_no: Optional[str] = Field(None, description="对账结算凭证编号", max_length=64)
    reconcile_status: int = Field(1, description="对账状态：1待渠道确认 2已对账无差异 3对账存在差异 4差异已处理 5作废")
    reconcile_user_id: Optional[int] = Field(None, description="对账负责人ID")
    create_user_id: int = Field(..., description="制单人ID")
    diff_reason: Optional[str] = Field(None, description="金额/套数差异原因")
    solve_plan: Optional[str] = Field(None, description="差异调整方案、下期抵扣说明")
    reconcile_file_url: Optional[str] = Field(None, description="渠道对账表、结算明细、沟通回执附件", max_length=1024)
    remark: Optional[str] = Field(None, description="月度对账通用备注")

    @field_validator('reconcile_status')
    def validate_reconcile_status(cls, v):
        if v not in [1, 2, 3, 4, 5]:
            raise ValueError('对账状态必须为1(待渠道确认)、2(已对账无差异)、3(对账存在差异)、4(差异已处理)或5(作废)')
        return v


class ChannelReconcileUpdate(BaseModel):
    """更新渠道月度对账请求模型"""
    system_deal_num: Optional[int] = Field(None, description="系统审核成交套数")
    refund_num: Optional[int] = Field(None, description="周期内退房套数")
    system_amount: Optional[Decimal] = Field(None, description="系统核算合规佣金金额")
    deduct_amount: Optional[Decimal] = Field(None, description="周期退房/违规扣减金额")
    commission_pay_id: Optional[int] = Field(None, description="关联渠道佣金付款单ID")
    voucher_no: Optional[str] = Field(None, description="对账结算凭证编号")
    reconcile_status: Optional[int] = Field(None, description="对账状态")
    reconcile_user_id: Optional[int] = Field(None, description="对账负责人ID")
    reconcile_time: Optional[datetime] = Field(None, description="对账最终确认时间")
    diff_reason: Optional[str] = Field(None, description="金额/套数差异原因")
    solve_plan: Optional[str] = Field(None, description="差异调整方案、下期抵扣说明")
    reconcile_file_url: Optional[str] = Field(None, description="渠道对账表、结算明细、沟通回执附件")
    remark: Optional[str] = Field(None, description="月度对账通用备注")


class ChannelReconcileConfirm(BaseModel):
    """渠道对账确认请求模型"""
    id: int = Field(..., description="渠道对账记录ID")
    reconcile_user_id: int = Field(..., description="确认人ID")
    confirm_status: int = Field(..., description="确认状态：2(无差异)或3(有差异)")
    diff_reason: Optional[str] = Field(None, description="差异原因")
    solve_plan: Optional[str] = Field(None, description="解决方案")

    @field_validator('confirm_status')
    def validate_confirm_status(cls, v):
        if v not in [2, 3]:
            raise ValueError('确认状态必须为2(无差异)或3(有差异)')
        return v


class ChannelReconcileResponse(ORMBaseModel):
    """渠道月度对账响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    reconcile_no: str
    project_id: int
    project_name: str
    building_scope: Optional[str]
    channel_id: int
    channel_name: str
    reconcile_month: str
    settle_start: date
    settle_end: date
    channel_deal_num: int
    system_deal_num: int
    refund_num: int
    channel_amount: Decimal
    system_amount: Decimal
    deduct_amount: Decimal
    diff_amount: Decimal
    commission_pay_id: Optional[int]
    voucher_no: Optional[str]
    reconcile_status: int
    reconcile_user_id: Optional[int]
    create_user_id: int
    reconcile_time: Optional[datetime]
    diff_reason: Optional[str]
    solve_plan: Optional[str]
    reconcile_file_url: Optional[str]
    remark: Optional[str]
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime

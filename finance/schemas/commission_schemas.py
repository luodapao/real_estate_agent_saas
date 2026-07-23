"""
房地产SaaS财务管理系统 - 渠道佣金&内部提成支付模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# ========== 佣金付款单 ==========

class CommissionPayCreate(BaseModel):
    """创建佣金付款单请求模型"""
    pay_no: Optional[str] = Field(None, description="佣金付款单号，不传则自动生成", max_length=64)
    project_id: int = Field(..., description="楼盘ID")
    project_name: str = Field(..., description="楼盘名称", max_length=128)
    building_scope: Optional[str] = Field(None, description="结算覆盖楼栋ID，逗号分隔", max_length=512)
    channel_id: int = Field(..., description="分销渠道ID")
    channel_name: str = Field(..., description="渠道名称", max_length=100)
    bank_info_id: int = Field(..., description="渠道对公收款账户ID")
    project_fin_config_id: int = Field(..., description="楼盘财务配置ID")
    cost_subject_id: int = Field(..., description="营销费用成本科目ID")
    tax_tpl_id: int = Field(..., description="渠道服务费进项税率模板ID")
    pay_account_id: int = Field(..., description="我方付款账户ID")
    settle_cycle: str = Field(..., description="结算周期文本", max_length=32)
    settle_start: date = Field(..., description="结算周期起始日")
    settle_end: date = Field(..., description="结算周期截止日")
    settle_type: int = Field(..., description="结算类型：1按月结算 2按回款结算")
    refund_deduct_flag: int = Field(0, description="是否包含退房扣佣：0不含 1包含")
    total_commission_untax: Decimal = Field(..., description="应付佣金不含税总额")
    total_commission_tax: Decimal = Field(..., description="渠道服务费进项税额")
    total_commission: Decimal = Field(..., description="应付佣金含税总金额")
    deduct_amount: Decimal = Field(0, description="退房/违规扣减含税总额")
    actual_pay_untax: Decimal = Field(..., description="实付不含税佣金")
    actual_pay_tax: Decimal = Field(..., description="实付对应进项税额")
    actual_pay_amount: Decimal = Field(..., description="实际含税应付付款金额")
    pay_file_url: Optional[str] = Field(None, description="结算单附件URL", max_length=1024)
    remark: Optional[str] = Field(None, description="备注")
    create_user_id: int = Field(..., description="结算制单人ID")


class CommissionPayUpdate(BaseModel):
    """更新佣金付款单请求模型"""
    building_scope: Optional[str] = Field(None, description="结算覆盖楼栋ID", max_length=512)
    refund_deduct_flag: Optional[int] = Field(None, description="是否包含退房扣佣")
    deduct_amount: Optional[Decimal] = Field(None, description="扣减含税总额")
    actual_pay_untax: Optional[Decimal] = Field(None, description="实付不含税佣金")
    actual_pay_tax: Optional[Decimal] = Field(None, description="实付对应进项税额")
    actual_pay_amount: Optional[Decimal] = Field(None, description="实际含税应付付款金额")
    audit_status: Optional[int] = Field(None, description="审核状态：1待审核 2已通过 3已驳回 4作废")
    pay_status: Optional[int] = Field(None, description="付款状态：1待付款 2付款中 3付款完成 4付款失败退回")
    pay_time: Optional[datetime] = Field(None, description="银行实际付款出账时间")
    audit_user_id: Optional[int] = Field(None, description="财务审核人ID")
    pay_user_id: Optional[int] = Field(None, description="出纳付款操作人ID")
    bank_flow_id: Optional[int] = Field(None, description="付款对应银行流水ID")
    bank_flow_no: Optional[str] = Field(None, description="银行流水单号", max_length=64)
    voucher_no: Optional[str] = Field(None, description="营销费用财务凭证编号", max_length=64)
    pay_file_url: Optional[str] = Field(None, description="结算单附件URL", max_length=1024)
    remark: Optional[str] = Field(None, description="备注")


class CommissionPayResponse(BaseModel):
    """佣金付款单响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    pay_no: str
    project_id: int
    project_name: str
    building_scope: Optional[str]
    channel_id: int
    channel_name: str
    bank_info_id: int
    project_fin_config_id: int
    cost_subject_id: int
    tax_tpl_id: int
    pay_account_id: int
    settle_cycle: str
    settle_start: date
    settle_end: date
    settle_type: int
    refund_deduct_flag: int
    total_commission_untax: Decimal
    total_commission_tax: Decimal
    total_commission: Decimal
    deduct_amount: Decimal
    actual_pay_untax: Decimal
    actual_pay_tax: Decimal
    actual_pay_amount: Decimal
    audit_status: int
    pay_status: int
    pay_time: Optional[datetime]
    create_user_id: int
    audit_user_id: Optional[int]
    pay_user_id: Optional[int]
    bank_flow_id: Optional[int]
    bank_flow_no: Optional[str]
    voucher_no: Optional[str]
    pay_file_url: Optional[str]
    remark: Optional[str]
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 佣金扣罚记录 ==========

class CommissionDeductCreate(BaseModel):
    """创建佣金扣罚记录请求模型"""
    deduct_no: Optional[str] = Field(None, description="扣罚单号，不传则自动生成", max_length=64)
    project_id: int = Field(..., description="楼盘ID")
    project_name: str = Field(..., description="楼盘名称", max_length=128)
    building_id: int = Field(..., description="楼栋ID")
    building_name: str = Field(..., description="楼栋名称", max_length=60)
    house_id: int = Field(..., description="房源ID")
    house_no: str = Field(..., description="房号", max_length=60)
    contract_id: int = Field(..., description="对应退房购房合同ID")
    sales_user_id: int = Field(..., description="成交置业顾问员工ID")
    sales_user_name: str = Field(..., description="置业顾问姓名", max_length=80)
    channel_id: int = Field(..., description="分销渠道ID")
    channel_name: str = Field(..., description="渠道名称", max_length=100)
    commission_pay_id: Optional[int] = Field(None, description="归属佣金汇总付款单ID")
    deduct_type: int = Field(..., description="扣罚类型：1客户退房 2业绩不达标 3渠道违规罚款")
    relate_biz_type: int = Field(1, description="关联单据类型：1购房合同 2认购单")
    relate_biz_id: int = Field(..., description="关联业务单据ID")
    deduct_untax_amt: Decimal = Field(..., description="扣罚不含税佣金金额")
    deduct_tax_amt: Decimal = Field(..., description="对应进项税额转出金额")
    deduct_amount: Decimal = Field(..., description="扣罚含税总金额")
    remark: Optional[str] = Field(None, description="扣罚详细原因")
    create_user_id: int = Field(..., description="扣罚记录制单人ID")


class CommissionDeductUpdate(BaseModel):
    """更新佣金扣罚记录请求模型"""
    commission_pay_id: Optional[int] = Field(None, description="归属佣金汇总付款单ID")
    deduct_status: Optional[int] = Field(None, description="扣罚状态：1待确认 2已确认抵扣佣金付款单")
    remark: Optional[str] = Field(None, description="扣罚详细原因")


class CommissionDeductResponse(BaseModel):
    """佣金扣罚记录响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    deduct_no: str
    project_id: int
    project_name: str
    building_id: int
    building_name: str
    house_id: int
    house_no: str
    contract_id: int
    sales_user_id: int
    sales_user_name: str
    channel_id: int
    channel_name: str
    commission_pay_id: Optional[int]
    deduct_type: int
    relate_biz_type: int
    relate_biz_id: int
    deduct_untax_amt: Decimal
    deduct_tax_amt: Decimal
    deduct_amount: Decimal
    deduct_status: int
    create_user_id: int
    remark: Optional[str]
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 销售提成支付明细 ==========

class SalesCommissionCreate(BaseModel):
    """创建销售提成支付明细请求模型"""
    project_id: int = Field(..., description="楼盘ID")
    project_name: str = Field(..., description="楼盘名称", max_length=128)
    building_id: int = Field(..., description="楼栋ID")
    building_name: str = Field(..., description="楼栋名称", max_length=60)
    house_id: int = Field(..., description="房源ID")
    house_no: str = Field(..., description="房号", max_length=60)
    contract_id: int = Field(..., description="购房合同ID")
    order_id: int = Field(..., description="认购订单ID")
    employee_id: int = Field(..., description="成交销售员工ID")
    employee_name: str = Field(..., description="销售姓名", max_length=80)
    project_fin_config_id: int = Field(..., description="楼盘财务配置ID")
    cost_subject_id: int = Field(..., description="销售提成费用科目ID")
    commission_untax: Decimal = Field(..., description="提成不含税金额")
    commission_tax: Decimal = Field(0, description="提成对应个税/服务费税额")
    commission_amount: Decimal = Field(..., description="提成含税总金额")
    remark: Optional[str] = Field(None, description="提成计算规则备注")
    create_user_id: int = Field(..., description="提成计算制单人ID")


class SalesCommissionUpdate(BaseModel):
    """更新销售提成支付明细请求模型"""
    bonus_pay_id: Optional[int] = Field(None, description="归属月度提成汇总付款单ID")
    commission_status: Optional[int] = Field(None, description="提成状态：1待结算 2已汇总至付款单 3已完成代发支付")
    settle_time: Optional[datetime] = Field(None, description="提成汇总结算时间")
    pay_time: Optional[datetime] = Field(None, description="银行代发实际支付时间")
    remark: Optional[str] = Field(None, description="提成计算规则备注")


class SalesCommissionResponse(BaseModel):
    """销售提成支付明细响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    project_id: int
    project_name: str
    building_id: int
    building_name: str
    house_id: int
    house_no: str
    contract_id: int
    order_id: int
    employee_id: int
    employee_name: str
    project_fin_config_id: int
    cost_subject_id: int
    commission_untax: Decimal
    commission_tax: Decimal
    commission_amount: Decimal
    bonus_pay_id: Optional[int]
    commission_status: int
    settle_time: Optional[datetime]
    pay_time: Optional[datetime]
    create_user_id: int
    remark: Optional[str]
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 内部销售提成付款单 ==========

class SalesBonusPayCreate(BaseModel):
    """创建内部销售提成付款单请求模型"""
    pay_no: Optional[str] = Field(None, description="提成付款单号，不传则自动生成", max_length=64)
    project_id: int = Field(..., description="楼盘ID")
    project_name: str = Field(..., description="楼盘名称", max_length=128)
    building_scope: Optional[str] = Field(None, description="代发覆盖楼栋ID，逗号分隔", max_length=512)
    staff_id: int = Field(..., description="销售员工ID")
    staff_name: str = Field(..., description="员工姓名", max_length=80)
    project_fin_config_id: int = Field(..., description="楼盘财务配置ID")
    cost_subject_id: int = Field(..., description="销售提成费用科目ID")
    pay_account_id: int = Field(..., description="我方代发付款账户ID")
    settle_cycle: str = Field(..., description="结算周期文本", max_length=32)
    settle_start: date = Field(..., description="结算周期起始日")
    settle_end: date = Field(..., description="结算周期截止日")
    total_bonus_untax: Decimal = Field(..., description="应付提成不含税总额")
    total_bonus_tax: Decimal = Field(..., description="代扣个人所得税总额")
    total_bonus: Decimal = Field(..., description="应付提成含税总额")
    deduct_amount: Decimal = Field(0, description="扣款（迟到/违规）含税总额")
    actual_pay_untax: Decimal = Field(..., description="实发不含税提成")
    actual_pay_tax: Decimal = Field(..., description="实发对应代扣个税")
    actual_pay_amount: Decimal = Field(..., description="银行代发实际净额")
    remark: Optional[str] = Field(None, description="月度提成代发备注")
    create_user_id: int = Field(..., description="提成汇总制单人ID")


class SalesBonusPayUpdate(BaseModel):
    """更新内部销售提成付款单请求模型"""
    building_scope: Optional[str] = Field(None, description="代发覆盖楼栋ID", max_length=512)
    deduct_amount: Optional[Decimal] = Field(None, description="扣款含税总额")
    actual_pay_untax: Optional[Decimal] = Field(None, description="实发不含税提成")
    actual_pay_tax: Optional[Decimal] = Field(None, description="实发对应代扣个税")
    actual_pay_amount: Optional[Decimal] = Field(None, description="银行代发实际净额")
    audit_status: Optional[int] = Field(None, description="审核状态：1待审核 2已通过 3已驳回 4作废")
    pay_status: Optional[int] = Field(None, description="代发状态：1待代发 2付款中 3代发完成 4代发失败退回")
    pay_time: Optional[datetime] = Field(None, description="银行代发完成时间")
    audit_user_id: Optional[int] = Field(None, description="财务审核人ID")
    pay_user_id: Optional[int] = Field(None, description="出纳代发操作人ID")
    bank_flow_id: Optional[int] = Field(None, description="代发对应银行流水ID")
    bank_flow_no: Optional[str] = Field(None, description="银行流水单号", max_length=64)
    voucher_no: Optional[str] = Field(None, description="销售费用财务凭证编号", max_length=64)
    remark: Optional[str] = Field(None, description="月度提成代发备注")


class SalesBonusPayResponse(BaseModel):
    """内部销售提成付款单响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    pay_no: str
    project_id: int
    project_name: str
    building_scope: Optional[str]
    staff_id: int
    staff_name: str
    project_fin_config_id: int
    cost_subject_id: int
    pay_account_id: int
    settle_cycle: str
    settle_start: date
    settle_end: date
    total_bonus_untax: Decimal
    total_bonus_tax: Decimal
    total_bonus: Decimal
    deduct_amount: Decimal
    actual_pay_untax: Decimal
    actual_pay_tax: Decimal
    actual_pay_amount: Decimal
    audit_status: int
    pay_status: int
    pay_time: Optional[datetime]
    create_user_id: int
    audit_user_id: Optional[int]
    pay_user_id: Optional[int]
    bank_flow_id: Optional[int]
    bank_flow_no: Optional[str]
    voucher_no: Optional[str]
    remark: Optional[str]
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime
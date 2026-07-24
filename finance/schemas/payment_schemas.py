"""
房地产SaaS财务管理系统 - 房款收支核心模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field\nfrom common.schemas.response import ORMBaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ========== 分期回款计划 ==========

class InstallmentPlanCreate(BaseModel):
    """分期回款计划创建模型"""
    order_id: int = Field(..., description="销售订单ID")
    customer_id: int = Field(..., description="客户ID")
    project_id: int = Field(..., description="楼盘ID")
    contract_amount: Decimal = Field(..., description="合同金额")
    down_payment_ratio: Decimal = Field(..., description="首付比例")
    down_payment_amount: Decimal = Field(..., description="首付金额")
    down_payment_untax_amt: Decimal = Field(..., description="首付不含税金额")
    down_payment_tax: Decimal = Field(..., description="首付税额")
    loan_amount: Decimal = Field(..., description="贷款金额")
    installment_count: int = Field(..., description="分期付款次数")
    payment_cycle: str = Field(..., description="付款周期（月/季度/年）", max_length=20)
    first_payment_date: datetime = Field(..., description="首期付款日期")
    plan_no: Optional[str] = Field(default=None, description="分期计划编号（系统自动生成）")
    period_no: Optional[int] = Field(None, description="期数编号（系统自动生成）")


class InstallmentPlanUpdate(BaseModel):
    """更新分期回款计划请求模型"""
    down_payment_ratio: Optional[Decimal] = Field(None, description="首付比例")
    down_payment_amount: Optional[Decimal] = Field(None, description="首付金额")
    down_payment_untax_amt: Optional[Decimal] = Field(None, description="首付不含税金额")
    down_payment_tax: Optional[Decimal] = Field(None, description="首付税额")
    loan_amount: Optional[Decimal] = Field(None, description="贷款金额")
    installment_count: Optional[int] = Field(None, description="分期付款次数")
    payment_cycle: Optional[str] = Field(None, description="付款周期", max_length=20)
    first_payment_date: Optional[datetime] = Field(None, description="首期付款日期")


class InstallmentPlanResponse(ORMBaseModel):
    """分期回款计划响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    plan_no: str = Field(description="分期单据编号")
    project_id: int
    project_name: Optional[str] = Field(None, description="楼盘名称")
    house_id: int
    house_no: Optional[str] = Field(None, description="房号")
    customer_id: int
    customer_name: Optional[str] = Field(None, description="客户名称")
    contract_id: int = Field(description="合同ID")
    project_fin_config_id: int = Field(description="楼盘财务配置ID")
    tax_tpl_id: int = Field(description="计税税率模板ID")
    calc_mode: int = Field(description="计税模式")
    income_subject_id: int = Field(description="应收收入会计科目ID")
    discount_rule_id: Optional[int] = Field(None, description="分期适用优惠规则ID")
    receive_account_id: Optional[int] = Field(None, description="分期回款默认收款账户ID")
    installment_rule_json: Optional[str] = Field(None, description="分期规则快照JSON")
    total_period: int = Field(description="总期数")
    period_no: int = Field(description="当前期号")
    due_date: datetime = Field(description="到期日")
    period_untax_amt: Decimal = Field(description="本期应收不含税金额")
    period_vat: Decimal = Field(description="本期增值税")
    period_maintain: Decimal = Field(description="代收维修基金")
    period_total: Decimal = Field(description="本期应收总金额")
    received_amount: Decimal = Field(description="已收金额")
    unpaid_amount: Decimal = Field(description="未收金额")
    settle_time: Optional[datetime] = Field(None, description="结清完成时间")
    overdue_days: int = Field(description="逾期天数")
    overdue_rate: Decimal = Field(description="逾期罚息日利率")
    overdue_interest: Decimal = Field(description="累计逾期罚息总额")
    overdue_calc_flag: int = Field(description="是否开启自动计息")
    plan_status: int = Field(description="分期状态")
    offset_record_no: Optional[str] = Field(None, description="作废/冲销关联单据编号")
    remark: Optional[str] = Field(None, description="业务备注")
    settle_remark: Optional[str] = Field(None, description="结清备注")
    create_user_id: int = Field(description="制单人ID")
    update_user_id: Optional[int] = Field(None, description="最后修改人ID")
    audit_user_id: Optional[int] = Field(None, description="财务审核人ID")
    version: int = Field(description="乐观锁版本号")
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 面积差价调整 ==========

class PriceDiffCreate(BaseModel):
    """创建面积差价调整请求模型"""
    order_id: int = Field(..., description="销售订单ID")
    customer_id: int = Field(..., description="客户ID")
    house_id: int = Field(..., description="房源ID")
    original_area: Decimal = Field(..., description="原合同面积")
    actual_area: Decimal = Field(..., description="实测面积")
    area_diff: Decimal = Field(..., description="面积差异")
    unit_price: Decimal = Field(..., description="单价")
    diff_amount: Decimal = Field(..., description="差价金额")
    diff_untax_amt: Decimal = Field(..., description="差价不含税金额")
    diff_tax: Decimal = Field(..., description="差价税额")
    diff_total_amt: Decimal = Field(..., description="差价含税总金额")
    diff_type: str = Field(..., description="差价类型（补收/退还）")
    reason: Optional[str] = Field(None, description="调整原因")
    diff_no: Optional[str] = Field(default=None, description="差价调整编号（系统自动生成）")


class PriceDiffUpdate(BaseModel):
    """更新面积差价调整请求模型"""
    original_area: Optional[Decimal] = Field(None, description="原合同面积")
    actual_area: Optional[Decimal] = Field(None, description="实测面积")
    unit_price: Optional[Decimal] = Field(None, description="单价")
    diff_amount: Optional[Decimal] = Field(None, description="差价金额")
    diff_untax_amt: Optional[Decimal] = Field(None, description="差价不含税金额")
    diff_tax: Optional[Decimal] = Field(None, description="差价税额")
    diff_total_amt: Optional[Decimal] = Field(None, description="差价含税总金额")
    reason: Optional[str] = Field(None, description="调整原因")


class PriceDiffResponse(ORMBaseModel):
    """面积差价调整响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    diff_no: str
    project_id: int
    project_name: Optional[str] = Field(None, description="楼盘名称")
    house_id: int
    house_no: Optional[str] = Field(None, description="房号")
    contract_id: int = Field(description="合同ID")
    customer_id: int
    customer_name: Optional[str] = Field(None, description="客户名称")
    project_fin_config_id: int = Field(description="楼盘财务配置ID")
    tax_tpl_id: int = Field(description="差价计税税率模板ID")
    calc_mode: int = Field(description="计税模式")
    income_subject_id: int = Field(description="差价收入对应会计科目ID")
    discount_rule_id: Optional[int] = Field(None, description="差价适用优惠规则ID")
    predict_area: Decimal = Field(description="预测面积")
    actual_area: Decimal = Field(description="实测面积")
    diff_area: Decimal = Field(description="面积差额")
    unit_price: Decimal = Field(description="单价")
    diff_untax_amt: Decimal = Field(description="差价不含税金额")
    diff_vat: Decimal = Field(description="差价税额")
    diff_total: Decimal = Field(description="差价总金额")
    diff_type: int = Field(description="差价类型")
    adjust_commission: int = Field(description="是否同步调整渠道佣金")
    adjust_tax: int = Field(description="是否同步调整计税收入")
    survey_no: Optional[str] = Field(None, description="房产测绘报告编号")
    survey_org: Optional[str] = Field(None, description="测绘报告机构名称")
    survey_file_url: Optional[str] = Field(None, description="测绘报告附件链接")
    receipt_record_no: Optional[str] = Field(None, description="补差价关联收款单编号")
    refund_record_no: Optional[str] = Field(None, description="退差价关联退款单编号")
    audit_status: int = Field(description="审核状态")
    audit_time: Optional[datetime] = Field(None, description="审核完成时间")
    audit_user_id: Optional[int] = Field(None, description="审核人ID")
    create_user_id: int = Field(description="制单人ID")
    update_user_id: Optional[int] = Field(None, description="最后修改人ID")
    remark: Optional[str] = Field(None, description="调整说明")
    version: int = Field(description="乐观锁版本号")
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 收款记录 ==========

class ReceiptRecordCreate(BaseModel):
    """创建收款记录请求模型"""
    order_id: int = Field(..., description="销售订单ID")
    customer_id: int = Field(..., description="客户ID")
    project_id: int = Field(..., description="楼盘ID")
    receipt_type: str = Field(..., description="收款类型（定金/首付/分期/面积补差/车位款/储藏室款/其他）")
    receipt_amount: Decimal = Field(..., description="收款金额")
    receipt_untax_amt: Decimal = Field(..., description="收款不含税金额")
    receipt_tax: Decimal = Field(..., description="收款税额")
    receipt_total_amt: Decimal = Field(..., description="收款含税总金额")
    receipt_principal: Decimal = Field(..., description="不含税本金")
    receipt_agency_fee: Decimal = Field(..., description="代收款项")
    account_id: int = Field(..., description="收款账户ID")
    payment_method: str = Field(..., description="支付方式（现金/转账/微信/支付宝/POS刷卡/银行按揭/银行汇票）")
    bank_account_no: Optional[str] = Field(None, description="付款人银行账号", max_length=50)
    payer_name: Optional[str] = Field(None, description="付款人姓名", max_length=100)
    remark: Optional[str] = Field(None, description="备注")
    receipt_no: Optional[str] = Field(default=None, description="收据编号（系统自动生成）", max_length=50)


class ReceiptRecordUpdate(BaseModel):
    """更新收款记录请求模型"""
    receipt_no: Optional[str] = Field(None, description="收据编号", max_length=50)
    receipt_type: Optional[int] = Field(None, description="收款类型")
    receipt_amount: Optional[Decimal] = Field(None, description="收款金额")
    receipt_untax_amt: Optional[Decimal] = Field(None, description="收款不含税金额")
    receipt_tax: Optional[Decimal] = Field(None, description="收款税额")
    receipt_total_amt: Optional[Decimal] = Field(None, description="收款含税总金额")
    receipt_principal: Optional[Decimal] = Field(None, description="不含税本金")
    receipt_agency_fee: Optional[Decimal] = Field(None, description="代收款项")
    account_id: Optional[int] = Field(None, description="收款账户ID")
    payment_method: Optional[int] = Field(None, description="支付方式")
    bank_account_no: Optional[str] = Field(None, description="付款人银行账号", max_length=50)
    payer_name: Optional[str] = Field(None, description="付款人姓名", max_length=100)
    remark: Optional[str] = Field(None, description="备注")


class ReceiptRecordResponse(ORMBaseModel):
    """收款记录响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    receipt_no: str
    project_id: int
    project_name: Optional[str] = Field(None, description="楼盘名称")
    house_id: int = Field(description="房源ID")
    house_no: Optional[str] = Field(None, description="房号")
    contract_id: int = Field(description="合同ID")
    customer_id: int
    customer_name: Optional[str] = Field(None, description="客户名称")
    account_id: int
    account_name: Optional[str] = Field(None, description="账户名称")
    account_type: int = Field(description="账户类型")
    project_fin_config_id: int = Field(description="楼盘财务配置ID")
    tax_tpl_id: int = Field(description="收款计税税率模板ID")
    income_subject_id: int = Field(description="收款对应会计科目ID")
    receipt_date: datetime = Field(description="实际收款日期")
    receipt_type: int = Field(description="收款类型")
    pay_way: int = Field(description="支付方式")
    payer_name: Optional[str]
    payer_account: Optional[str]
    receipt_amount: Decimal = Field(description="实收总金额")
    untax_principal: Decimal = Field(description="不含税本金")
    tax_amount: Decimal = Field(description="税额")
    maintain_amount: Decimal = Field(description="代收维修基金")
    other_fee_amount: Decimal = Field(description="其他费用")
    deposit_account_id: Optional[int] = Field(None, description="抵扣首付的定金台账ID")
    installment_id: Optional[int] = Field(None, description="关联分期计划ID")
    diff_id: Optional[int] = Field(None, description="关联差价单据ID")
    order_id: Optional[int] = Field(None, description="关联认购单ID")
    discount_rule_id: Optional[int] = Field(None, description="收款适用优惠规则ID")
    verify_status: int = Field(description="对账状态")
    verify_time: Optional[datetime] = Field(None, description="对账完成时间")
    verify_user_id: Optional[int] = Field(None, description="对账操作人ID")
    bank_flow_id: Optional[int] = Field(None, description="关联银行流水ID")
    bank_flow_no: Optional[str] = Field(None, description="银行流水单号")
    reconcile_remark: Optional[str] = Field(None, description="对账差异说明")
    audit_status: int = Field(description="审核状态")
    audit_time: Optional[datetime] = Field(None, description="审核完成时间")
    audit_user_id: Optional[int] = Field(None, description="审核人ID")
    receipt_file_url: Optional[str] = Field(None, description="收款凭证附件链接")
    receipt_voucher_no: Optional[str] = Field(None, description="对应财务凭证编号")
    create_user_id: int = Field(description="制单人ID")
    update_user_id: Optional[int] = Field(None, description="最后修改人ID")
    operate_time: datetime = Field(description="收款操作时间")
    remark: Optional[str] = Field(None, description="收款备注")
    version: int = Field(description="乐观锁版本号")
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 退款记录 ==========

class RefundRecordCreate(BaseModel):
    """创建退款记录请求模型"""
    order_id: int = Field(..., description="销售订单ID")
    customer_id: int = Field(..., description="客户ID")
    project_id: int = Field(..., description="楼盘ID")
    refund_type: str = Field(..., description="退款类型（退房退款/其他）")
    refund_amount: Decimal = Field(..., description="退款金额")
    untax_refund_principal: Decimal = Field(..., description="不含税退款本金")
    refund_tax: Decimal = Field(..., description="退款税额")
    refund_total_amt: Decimal = Field(..., description="退款含税总金额")
    refund_agency_fee: Decimal = Field(..., description="代退款项")
    refund_reason: str = Field(..., description="退款原因")
    account_id: int = Field(..., description="退款账户ID")
    remark: Optional[str] = Field(None, description="备注")
    refund_no: Optional[str] = Field(default=None, description="退款编号（系统自动生成）", max_length=50)


class RefundRecordUpdate(BaseModel):
    """更新退款记录请求模型"""
    refund_no: Optional[str] = Field(None, description="退款编号", max_length=50)
    refund_type: Optional[int] = Field(None, description="退款类型")
    refund_amount: Optional[Decimal] = Field(None, description="退款金额")
    untax_refund_principal: Optional[Decimal] = Field(None, description="不含税退款本金")
    refund_tax: Optional[Decimal] = Field(None, description="退款税额")
    refund_total_amt: Optional[Decimal] = Field(None, description="退款含税总金额")
    refund_agency_fee: Optional[Decimal] = Field(None, description="代退款项")
    refund_reason: Optional[str] = Field(None, description="退款原因")
    account_id: Optional[int] = Field(None, description="退款账户ID")
    remark: Optional[str] = Field(None, description="备注")


class RefundRecordResponse(ORMBaseModel):
    """退款记录响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    refund_no: str
    customer_id: int
    customer_name: Optional[str] = Field(None, description="客户名称")
    project_id: int
    project_name: Optional[str] = Field(None, description="楼盘名称")
    contract_id: int = Field(description="合同ID")
    house_id: int = Field(description="房源ID")
    house_no: Optional[str] = Field(None, description="房号")
    refund_type: int = Field(description="退款类型")
    total_refund_amount: Decimal = Field(description="退款总金额")
    untax_refund_principal: Decimal = Field(description="不含税退款本金")
    refund_tax: Decimal = Field(description="退款税额")
    refund_maintain: Decimal = Field(description="退还维修基金")
    refund_other_fee: Decimal = Field(description="退还其他费用")
    deduct_commission: Decimal = Field(description="扣减佣金")
    deduct_forfeit: Decimal = Field(description="违约扣款")
    real_pay_amount: Decimal = Field(description="实际退款金额")
    remark: Optional[str] = Field(None, description="备注")
    account_id: int
    account_name: Optional[str] = Field(None, description="账户名称")
    account_use_type: int = Field(description="账户用途")
    audit_status: int = Field(description="审核状态")
    refund_exec_status: int = Field(description="执行状态")
    create_user_id: int = Field(description="制单人ID")
    update_user_id: Optional[int] = Field(None, description="最后修改人ID")
    is_del: int
    version: int = Field(description="乐观锁版本号")
    create_time: datetime
    update_time: datetime


# ========== 认筹定金台账 ==========

class DepositAccountCreate(BaseModel):
    """认筹定金台账创建模型"""
    customer_id: int = Field(..., description="客户ID")
    project_id: int = Field(..., description="楼盘ID")
    deposit_type: str = Field(..., description="定金类型（认筹金/购房定金）")
    deposit_total_amt: Decimal = Field(..., description="定金含税总金额")
    deposit_untax_amt: Decimal = Field(..., description="定金不含税金额")
    deposit_tax: Decimal = Field(..., description="定金税额")
    account_id: int = Field(..., description="账户ID")
    payment_method: str = Field(..., description="支付方式（现金/银行卡/微信/支付宝/POS/银行转账）")
    expire_date: Optional[datetime] = Field(None, description="有效期截止日期")
    remark: Optional[str] = Field(None, description="备注")
    deposit_no: Optional[str] = Field(default=None, description="定金编号（系统自动生成）", max_length=50)


class DepositAccountUpdate(BaseModel):
    """更新认筹定金台账请求模型"""
    deposit_total_amt: Optional[Decimal] = Field(None, description="定金含税总金额")
    deposit_untax_amt: Optional[Decimal] = Field(None, description="定金不含税金额")
    deposit_tax: Optional[Decimal] = Field(None, description="定金税额")
    expire_date: Optional[datetime] = Field(None, description="有效期截止日期")
    remark: Optional[str] = Field(None, description="备注")


class DepositAccountResponse(ORMBaseModel):
    """认筹定金台账响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    deposit_no: str
    customer_id: int
    customer_name: Optional[str] = Field(None, description="客户名称")
    project_id: int
    project_name: Optional[str] = Field(None, description="楼盘名称")
    house_id: Optional[int] = Field(None, description="房源ID")
    house_no: Optional[str] = Field(None, description="房号")
    deposit_type: int = Field(description="定金类型")
    deposit_total_amt: Decimal = Field(description="定金含税总金额")
    deposit_untax_amt: Decimal = Field(description="定金不含税金额")
    deposit_tax: Decimal = Field(description="定金税额")
    other_fee: Decimal = Field(description="其他费用")
    pay_time: datetime = Field(description="缴纳时间")
    pay_way: int = Field(description="支付方式")
    payer_name: str = Field(description="付款人姓名")
    payer_account: Optional[str] = Field(None, description="付款人账号")
    account_id: int
    account_name: Optional[str] = Field(None, description="账户名称")
    account_use_type: int = Field(description="账户用途")
    use_status: int = Field(description="使用状态")
    forfeit_amount: Decimal = Field(description="挞定金额")
    create_user_id: int = Field(description="制单人ID")
    update_user_id: Optional[int] = Field(None, description="最后修改人ID")
    is_del: int
    version: int = Field(description="乐观锁版本号")
    create_time: datetime
    update_time: datetime
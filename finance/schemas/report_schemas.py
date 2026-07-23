"""
房地产SaaS财务管理系统 - 财务统计报表模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


# ========== 现金流统计表 ==========

class CashFlowCreate(BaseModel):
    """现金流统计表创建请求模型"""
    project_id: int = Field(..., description="楼盘ID")
    project_name: str = Field(..., description="楼盘名称冗余", max_length=128)
    stat_date: date = Field(..., description="统计日期（日统计维度）")
    stat_month: str = Field(..., description="统计月份（YYYY-MM）", max_length=32)
    stat_type: int = Field(1, description="统计类型：1日统计 2月统计")
    total_receipt: Decimal = Field(0, description="收款总金额")
    house_receipt: Decimal = Field(0, description="房款销售收入")
    other_receipt: Decimal = Field(0, description="其他经营收款")
    total_refund: Decimal = Field(0, description="退款总金额")
    house_refund: Decimal = Field(0, description="房款退款金额")
    total_pay: Decimal = Field(0, description="付款总金额")
    commission_pay: Decimal = Field(0, description="渠道佣金支付金额")
    cost_pay: Decimal = Field(0, description="工程/营销费用支付")
    admin_pay: Decimal = Field(0, description="管理费用支付")
    other_pay: Decimal = Field(0, description="其他付款金额")
    operating_net_cash: Decimal = Field(0, description="经营活动净现金流")
    investing_net_cash: Decimal = Field(0, description="投资活动净现金流")
    financing_net_cash: Decimal = Field(0, description="筹资活动净现金流")
    net_cash_flow: Decimal = Field(0, description="当期总净现金流")
    stat_status: int = Field(1, description="1正常 2待重算 3数据异常")
    stat_batch: Optional[str] = Field(None, description="统计批次号，重算溯源", max_length=64)
    create_user_id: int = Field(..., description="统计生成人ID")

    @field_validator('stat_type')
    def validate_stat_type(cls, v):
        if v not in [1, 2]:
            raise ValueError('统计类型必须为1(日统计)或2(月统计)')
        return v

    @field_validator('stat_status')
    def validate_stat_status(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError('统计状态必须为1(正常)、2(待重算)或3(数据异常)')
        return v


class CashFlowUpdate(BaseModel):
    """现金流统计表更新请求模型"""
    stat_date: Optional[date] = Field(None, description="统计日期")
    stat_month: Optional[str] = Field(None, description="统计月份（YYYY-MM）", max_length=32)
    stat_type: Optional[int] = Field(None, description="统计类型")
    total_receipt: Optional[Decimal] = Field(None, description="收款总金额")
    house_receipt: Optional[Decimal] = Field(None, description="房款销售收入")
    other_receipt: Optional[Decimal] = Field(None, description="其他经营收款")
    total_refund: Optional[Decimal] = Field(None, description="退款总金额")
    house_refund: Optional[Decimal] = Field(None, description="房款退款金额")
    total_pay: Optional[Decimal] = Field(None, description="付款总金额")
    commission_pay: Optional[Decimal] = Field(None, description="渠道佣金支付金额")
    cost_pay: Optional[Decimal] = Field(None, description="工程/营销费用支付")
    admin_pay: Optional[Decimal] = Field(None, description="管理费用支付")
    other_pay: Optional[Decimal] = Field(None, description="其他付款金额")
    operating_net_cash: Optional[Decimal] = Field(None, description="经营活动净现金流")
    investing_net_cash: Optional[Decimal] = Field(None, description="投资活动净现金流")
    financing_net_cash: Optional[Decimal] = Field(None, description="筹资活动净现金流")
    net_cash_flow: Optional[Decimal] = Field(None, description="当期总净现金流")
    stat_status: Optional[int] = Field(None, description="统计状态")
    stat_batch: Optional[str] = Field(None, description="统计批次号", max_length=64)


class CashFlowResponse(BaseModel):
    """现金流统计表响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    project_id: int
    project_name: str
    stat_date: date
    stat_month: str
    stat_type: int
    total_receipt: Decimal
    house_receipt: Decimal
    other_receipt: Decimal
    total_refund: Decimal
    house_refund: Decimal
    total_pay: Decimal
    commission_pay: Decimal
    cost_pay: Decimal
    admin_pay: Decimal
    other_pay: Decimal
    operating_net_cash: Decimal
    investing_net_cash: Decimal
    financing_net_cash: Decimal
    net_cash_flow: Decimal
    stat_status: int
    stat_batch: Optional[str]
    create_user_id: int
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 应收款统计表 ==========

class ReceivableStatCreate(BaseModel):
    """应收款统计表创建请求模型"""
    project_id: int = Field(..., description="楼盘ID")
    project_name: str = Field(..., description="楼盘名称冗余", max_length=128)
    stat_date: date = Field(..., description="统计日期")
    stat_month: str = Field(..., description="统计月份（YYYY-MM）", max_length=32)
    stat_type: int = Field(1, description="统计类型：1日统计 2月统计")
    total_receivable: Decimal = Field(0, description="累计应收总额")
    current_period_receivable: Decimal = Field(0, description="当期新增应收")
    total_received: Decimal = Field(0, description="累计已收总额")
    current_period_received: Decimal = Field(0, description="当期回款金额")
    unpaid_amount: Decimal = Field(0, description="当前未收余额")
    overdue_amount: Decimal = Field(0, description="当前逾期总金额")
    overdue_count: int = Field(0, description="逾期单据笔数")
    max_overdue_days: int = Field(0, description="当期最大逾期天数")
    receive_rate: Decimal = Field(0, description="当期回款率")
    stat_status: int = Field(1, description="1正常 2待重算 3数据异常")
    stat_batch: Optional[str] = Field(None, description="统计批次号", max_length=64)
    create_user_id: int = Field(..., description="统计生成人ID")


class ReceivableStatUpdate(BaseModel):
    """应收款统计表更新请求模型"""
    stat_date: Optional[date] = Field(None, description="统计日期")
    stat_month: Optional[str] = Field(None, description="统计月份（YYYY-MM）", max_length=32)
    stat_type: Optional[int] = Field(None, description="统计类型")
    total_receivable: Optional[Decimal] = Field(None, description="累计应收总额")
    current_period_receivable: Optional[Decimal] = Field(None, description="当期新增应收")
    total_received: Optional[Decimal] = Field(None, description="累计已收总额")
    current_period_received: Optional[Decimal] = Field(None, description="当期回款金额")
    unpaid_amount: Optional[Decimal] = Field(None, description="当前未收余额")
    overdue_amount: Optional[Decimal] = Field(None, description="当前逾期总金额")
    overdue_count: Optional[int] = Field(None, description="逾期单据笔数")
    max_overdue_days: Optional[int] = Field(None, description="当期最大逾期天数")
    receive_rate: Optional[Decimal] = Field(None, description="当期回款率")
    stat_status: Optional[int] = Field(None, description="统计状态")
    stat_batch: Optional[str] = Field(None, description="统计批次号", max_length=64)


class ReceivableStatResponse(BaseModel):
    """应收款统计表响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    project_id: int
    project_name: str
    stat_date: date
    stat_month: str
    stat_type: int
    total_receivable: Decimal
    current_period_receivable: Decimal
    total_received: Decimal
    current_period_received: Decimal
    unpaid_amount: Decimal
    overdue_amount: Decimal
    overdue_count: int
    max_overdue_days: int
    receive_rate: Decimal
    stat_status: int
    stat_batch: Optional[str]
    create_user_id: int
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 税务统计表 ==========

class TaxStatCreate(BaseModel):
    """税务统计表创建请求模型"""
    project_id: int = Field(..., description="楼盘ID")
    project_name: str = Field(..., description="楼盘名称冗余", max_length=128)
    stat_month: str = Field(..., description="统计月份（YYYY-MM）", max_length=32)
    stat_year: int = Field(..., description="统计年度")
    invoice_amount: Decimal = Field(0, description="当期含税开票总额")
    invoice_untax_amount: Decimal = Field(0, description="当期不含税开票金额")
    output_tax: Decimal = Field(0, description="销项税额")
    input_tax: Decimal = Field(0, description="进项税额")
    deduct_tax: Decimal = Field(0, description="当期抵扣税额")
    tax_amount: Decimal = Field(0, description="当期应缴税额")
    declare_amount: Decimal = Field(0, description="已申报税额")
    declared_status: int = Field(1, description="1未申报 2已申报 3申报异常")
    tax_burden_rate: Decimal = Field(0, description="当期税负率")
    stat_status: int = Field(1, description="1正常 2待重算 3数据异常")
    stat_batch: Optional[str] = Field(None, description="统计批次号", max_length=64)
    create_user_id: int = Field(..., description="统计生成人ID")

    @field_validator('declared_status')
    def validate_declared_status(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError('申报状态必须为1(未申报)、2(已申报)或3(申报异常)')
        return v


class TaxStatUpdate(BaseModel):
    """税务统计表更新请求模型"""
    stat_month: Optional[str] = Field(None, description="统计月份（YYYY-MM）", max_length=32)
    stat_year: Optional[int] = Field(None, description="统计年度")
    invoice_amount: Optional[Decimal] = Field(None, description="当期含税开票总额")
    invoice_untax_amount: Optional[Decimal] = Field(None, description="当期不含税开票金额")
    output_tax: Optional[Decimal] = Field(None, description="销项税额")
    input_tax: Optional[Decimal] = Field(None, description="进项税额")
    deduct_tax: Optional[Decimal] = Field(None, description="当期抵扣税额")
    tax_amount: Optional[Decimal] = Field(None, description="当期应缴税额")
    declare_amount: Optional[Decimal] = Field(None, description="已申报税额")
    declared_status: Optional[int] = Field(None, description="申报状态")
    tax_burden_rate: Optional[Decimal] = Field(None, description="当期税负率")
    stat_status: Optional[int] = Field(None, description="统计状态")
    stat_batch: Optional[str] = Field(None, description="统计批次号", max_length=64)


class TaxStatResponse(BaseModel):
    """税务统计表响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    project_id: int
    project_name: str
    stat_month: str
    stat_year: int
    invoice_amount: Decimal
    invoice_untax_amount: Decimal
    output_tax: Decimal
    input_tax: Decimal
    deduct_tax: Decimal
    tax_amount: Decimal
    declare_amount: Decimal
    declared_status: int
    tax_burden_rate: Decimal
    stat_status: int
    stat_batch: Optional[str]
    create_user_id: int
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 佣金统计表 ==========

class CommissionStatCreate(BaseModel):
    """佣金统计表创建请求模型"""
    project_id: int = Field(..., description="楼盘ID")
    project_name: str = Field(..., description="楼盘名称冗余", max_length=128)
    channel_id: int = Field(..., description="渠道ID")
    channel_name: str = Field(..., description="渠道名称冗余", max_length=100)
    channel_type: int = Field(..., description="渠道类型：1全民分销 2中介渠道 3内部销售")
    stat_month: str = Field(..., description="统计月份（YYYY-MM）", max_length=32)
    stat_year: int = Field(..., description="统计年度")
    deal_num: int = Field(0, description="当期成交套数")
    deal_amount: Decimal = Field(0, description="当期成交总额")
    total_commission: Decimal = Field(0, description="当期应付佣金总额")
    deduct_commission: Decimal = Field(0, description="当期扣减佣金（退房/违规）")
    real_commission: Decimal = Field(0, description="当期实际应付佣金")
    paid_amount: Decimal = Field(0, description="当期已支付佣金")
    unpaid_amount: Decimal = Field(0, description="当期未付佣金余额")
    stat_status: int = Field(1, description="1正常 2待重算 3数据异常")
    stat_batch: Optional[str] = Field(None, description="统计批次号", max_length=64)
    create_user_id: int = Field(..., description="统计生成人ID")

    @field_validator('channel_type')
    def validate_channel_type(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError('渠道类型必须为1(全民分销)、2(中介渠道)或3(内部销售)')
        return v


class CommissionStatUpdate(BaseModel):
    """佣金统计表更新请求模型"""
    stat_month: Optional[str] = Field(None, description="统计月份（YYYY-MM）", max_length=32)
    stat_year: Optional[int] = Field(None, description="统计年度")
    deal_num: Optional[int] = Field(None, description="当期成交套数")
    deal_amount: Optional[Decimal] = Field(None, description="当期成交总额")
    total_commission: Optional[Decimal] = Field(None, description="当期应付佣金总额")
    deduct_commission: Optional[Decimal] = Field(None, description="当期扣减佣金")
    real_commission: Optional[Decimal] = Field(None, description="当期实际应付佣金")
    paid_amount: Optional[Decimal] = Field(None, description="当期已支付佣金")
    unpaid_amount: Optional[Decimal] = Field(None, description="当期未付佣金余额")
    stat_status: Optional[int] = Field(None, description="统计状态")
    stat_batch: Optional[str] = Field(None, description="统计批次号", max_length=64)


class CommissionStatResponse(BaseModel):
    """佣金统计表响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    project_id: int
    project_name: str
    channel_id: int
    channel_name: str
    channel_type: int
    stat_month: str
    stat_year: int
    deal_num: int
    deal_amount: Decimal
    total_commission: Decimal
    deduct_commission: Decimal
    real_commission: Decimal
    paid_amount: Decimal
    unpaid_amount: Decimal
    stat_status: int
    stat_batch: Optional[str]
    create_user_id: int
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 现金流量表（正式报表） ==========

class CashFlowStatementCreate(BaseModel):
    """现金流量表创建请求模型"""
    report_period: str = Field(..., description="报表期间（YYYY-MM）", max_length=7)
    report_year: int = Field(..., description="报表年度")
    operating_cash_in: Decimal = Field(0, description="经营活动现金流入")
    operating_cash_out: Decimal = Field(0, description="经营活动现金流出")
    operating_cash_flow: Decimal = Field(0, description="经营活动净现金流")
    investing_cash_in: Decimal = Field(0, description="投资活动现金流入")
    investing_cash_out: Decimal = Field(0, description="投资活动现金流出")
    investing_cash_flow: Decimal = Field(0, description="投资活动净现金流")
    financing_cash_in: Decimal = Field(0, description="筹资活动现金流入")
    financing_cash_out: Decimal = Field(0, description="筹资活动现金流出")
    financing_cash_flow: Decimal = Field(0, description="筹资活动净现金流")
    net_cash_flow: Decimal = Field(0, description="当期净现金流量")
    last_period_net_flow: Decimal = Field(0, description="上期同期净现金流（对比分析）")
    report_status: int = Field(1, description="1草稿 2已审核 3已归档 4作废")
    create_user_id: int = Field(..., description="制表人ID")

    @field_validator('report_status')
    def validate_report_status(cls, v):
        if v not in [1, 2, 3, 4]:
            raise ValueError('报表状态必须为1(草稿)、2(已审核)、3(已归档)或4(作废)')
        return v


class CashFlowStatementUpdate(BaseModel):
    """现金流量表更新请求模型"""
    report_period: Optional[str] = Field(None, description="报表期间（YYYY-MM）", max_length=7)
    report_year: Optional[int] = Field(None, description="报表年度")
    operating_cash_in: Optional[Decimal] = Field(None, description="经营活动现金流入")
    operating_cash_out: Optional[Decimal] = Field(None, description="经营活动现金流出")
    operating_cash_flow: Optional[Decimal] = Field(None, description="经营活动净现金流")
    investing_cash_in: Optional[Decimal] = Field(None, description="投资活动现金流入")
    investing_cash_out: Optional[Decimal] = Field(None, description="投资活动现金流出")
    investing_cash_flow: Optional[Decimal] = Field(None, description="投资活动净现金流")
    financing_cash_in: Optional[Decimal] = Field(None, description="筹资活动现金流入")
    financing_cash_out: Optional[Decimal] = Field(None, description="筹资活动现金流出")
    financing_cash_flow: Optional[Decimal] = Field(None, description="筹资活动净现金流")
    net_cash_flow: Optional[Decimal] = Field(None, description="当期净现金流量")
    last_period_net_flow: Optional[Decimal] = Field(None, description="上期同期净现金流")
    report_status: Optional[int] = Field(None, description="报表状态")
    audit_user_id: Optional[int] = Field(None, description="审核人ID")


class CashFlowStatementResponse(BaseModel):
    """现金流量表响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    report_period: str
    report_year: int
    operating_cash_in: Decimal
    operating_cash_out: Decimal
    operating_cash_flow: Decimal
    investing_cash_in: Decimal
    investing_cash_out: Decimal
    investing_cash_flow: Decimal
    financing_cash_in: Decimal
    financing_cash_out: Decimal
    financing_cash_flow: Decimal
    net_cash_flow: Decimal
    last_period_net_flow: Decimal
    report_status: int
    create_user_id: int
    audit_user_id: Optional[int]
    audit_time: Optional[datetime]
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 利润表（正式报表） ==========

class ProfitStatementCreate(BaseModel):
    """利润表创建请求模型"""
    report_period: str = Field(..., description="报表期间（YYYY-MM）", max_length=7)
    report_year: int = Field(..., description="报表年度")
    revenue: Decimal = Field(0, description="营业收入")
    other_business_revenue: Decimal = Field(0, description="其他业务收入")
    cost: Decimal = Field(0, description="营业成本")
    other_business_cost: Decimal = Field(0, description="其他业务成本")
    business_tax: Decimal = Field(0, description="营业税金及附加")
    gross_profit: Decimal = Field(0, description="销售毛利润")
    operating_expense: Decimal = Field(0, description="营业费用")
    admin_expense: Decimal = Field(0, description="管理费用")
    financial_expense: Decimal = Field(0, description="财务费用")
    operating_profit: Decimal = Field(0, description="营业利润")
    total_profit: Decimal = Field(0, description="利润总额")
    income_tax: Decimal = Field(0, description="企业所得税")
    net_profit: Decimal = Field(0, description="净利润")
    last_period_net_profit: Decimal = Field(0, description="上期同期净利润")
    report_status: int = Field(1, description="1草稿 2已审核 3已归档 4作废")
    create_user_id: int = Field(..., description="制表人ID")


class ProfitStatementUpdate(BaseModel):
    """利润表更新请求模型"""
    report_period: Optional[str] = Field(None, description="报表期间（YYYY-MM）", max_length=7)
    report_year: Optional[int] = Field(None, description="报表年度")
    revenue: Optional[Decimal] = Field(None, description="营业收入")
    other_business_revenue: Optional[Decimal] = Field(None, description="其他业务收入")
    cost: Optional[Decimal] = Field(None, description="营业成本")
    other_business_cost: Optional[Decimal] = Field(None, description="其他业务成本")
    business_tax: Optional[Decimal] = Field(None, description="营业税金及附加")
    gross_profit: Optional[Decimal] = Field(None, description="销售毛利润")
    operating_expense: Optional[Decimal] = Field(None, description="营业费用")
    admin_expense: Optional[Decimal] = Field(None, description="管理费用")
    financial_expense: Optional[Decimal] = Field(None, description="财务费用")
    operating_profit: Optional[Decimal] = Field(None, description="营业利润")
    total_profit: Optional[Decimal] = Field(None, description="利润总额")
    income_tax: Optional[Decimal] = Field(None, description="企业所得税")
    net_profit: Optional[Decimal] = Field(None, description="净利润")
    last_period_net_profit: Optional[Decimal] = Field(None, description="上期同期净利润")
    report_status: Optional[int] = Field(None, description="报表状态")
    audit_user_id: Optional[int] = Field(None, description="审核人ID")


class ProfitStatementResponse(BaseModel):
    """利润表响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    report_period: str
    report_year: int
    revenue: Decimal
    other_business_revenue: Decimal
    cost: Decimal
    other_business_cost: Decimal
    business_tax: Decimal
    gross_profit: Decimal
    operating_expense: Decimal
    admin_expense: Decimal
    financial_expense: Decimal
    operating_profit: Decimal
    total_profit: Decimal
    income_tax: Decimal
    net_profit: Decimal
    last_period_net_profit: Decimal
    report_status: int
    create_user_id: int
    audit_user_id: Optional[int]
    audit_time: Optional[datetime]
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 资产负债表（正式报表） ==========

class BalanceSheetCreate(BaseModel):
    """资产负债表创建请求模型"""
    report_period: str = Field(..., description="报表期间（YYYY-MM）", max_length=7)
    report_year: int = Field(..., description="报表年度")
    current_assets: Decimal = Field(0, description="流动资产合计")
    non_current_assets: Decimal = Field(0, description="非流动资产合计")
    total_assets: Decimal = Field(0, description="资产总计")
    current_liabilities: Decimal = Field(0, description="流动负债合计")
    non_current_liabilities: Decimal = Field(0, description="非流动负债合计")
    total_liabilities: Decimal = Field(0, description="负债总计")
    owner_equity: Decimal = Field(0, description="所有者权益合计")
    asset_equity_balance: Decimal = Field(0, description="资产权益平衡差值（校验用）")
    begin_total_assets: Decimal = Field(0, description="期初资产总额")
    begin_total_liabilities: Decimal = Field(0, description="期初负债总额")
    begin_equity: Decimal = Field(0, description="期初权益总额")
    report_status: int = Field(1, description="1草稿 2已审核 3已归档 4作废")
    create_user_id: int = Field(..., description="制表人ID")


class BalanceSheetUpdate(BaseModel):
    """资产负债表更新请求模型"""
    report_period: Optional[str] = Field(None, description="报表期间（YYYY-MM）", max_length=7)
    report_year: Optional[int] = Field(None, description="报表年度")
    current_assets: Optional[Decimal] = Field(None, description="流动资产合计")
    non_current_assets: Optional[Decimal] = Field(None, description="非流动资产合计")
    total_assets: Optional[Decimal] = Field(None, description="资产总计")
    current_liabilities: Optional[Decimal] = Field(None, description="流动负债合计")
    non_current_liabilities: Optional[Decimal] = Field(None, description="非流动负债合计")
    total_liabilities: Optional[Decimal] = Field(None, description="负债总计")
    owner_equity: Optional[Decimal] = Field(None, description="所有者权益合计")
    asset_equity_balance: Optional[Decimal] = Field(None, description="资产权益平衡差值")
    begin_total_assets: Optional[Decimal] = Field(None, description="期初资产总额")
    begin_total_liabilities: Optional[Decimal] = Field(None, description="期初负债总额")
    begin_equity: Optional[Decimal] = Field(None, description="期初权益总额")
    report_status: Optional[int] = Field(None, description="报表状态")
    audit_user_id: Optional[int] = Field(None, description="审核人ID")


class BalanceSheetResponse(BaseModel):
    """资产负债表响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    report_period: str
    report_year: int
    current_assets: Decimal
    non_current_assets: Decimal
    total_assets: Decimal
    current_liabilities: Decimal
    non_current_liabilities: Decimal
    total_liabilities: Decimal
    owner_equity: Decimal
    asset_equity_balance: Decimal
    begin_total_assets: Decimal
    begin_total_liabilities: Decimal
    begin_equity: Decimal
    report_status: int
    create_user_id: int
    audit_user_id: Optional[int]
    audit_time: Optional[datetime]
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 财务报表主表 ==========

class FinancialReportCreate(BaseModel):
    """财务报表主表创建请求模型"""
    report_name: str = Field(..., description="报表名称", max_length=100)
    report_type: int = Field(..., description="报表类型：1现金流量表 2利润表 3资产负债表 4综合财报")
    report_period: str = Field(..., description="报表期间（YYYY-MM）", max_length=7)
    report_year: int = Field(..., description="报表年度")
    cash_flow_statement_id: Optional[int] = Field(None, description="现金流量表ID")
    profit_statement_id: Optional[int] = Field(None, description="利润表ID")
    balance_sheet_id: Optional[int] = Field(None, description="资产负债表ID")
    report_file_url: Optional[str] = Field(None, description="导出报表附件文件", max_length=1024)
    status: int = Field(1, description="1草稿 2已编制 3已审核 4已归档 5作废")
    create_user_id: int = Field(..., description="报表编制人ID")
    remark: Optional[str] = Field(None, description="报表编制说明、数据异常备注")

    @field_validator('report_type')
    def validate_report_type(cls, v):
        if v not in [1, 2, 3, 4]:
            raise ValueError('报表类型必须为1(现金流量表)、2(利润表)、3(资产负债表)或4(综合财报)')
        return v

    @field_validator('status')
    def validate_status(cls, v):
        if v not in [1, 2, 3, 4, 5]:
            raise ValueError('状态必须为1(草稿)、2(已编制)、3(已审核)、4(已归档)或5(作废)')
        return v


class FinancialReportUpdate(BaseModel):
    """财务报表主表更新请求模型"""
    report_name: Optional[str] = Field(None, description="报表名称", max_length=100)
    report_type: Optional[int] = Field(None, description="报表类型")
    report_period: Optional[str] = Field(None, description="报表期间（YYYY-MM）", max_length=7)
    report_year: Optional[int] = Field(None, description="报表年度")
    cash_flow_statement_id: Optional[int] = Field(None, description="现金流量表ID")
    profit_statement_id: Optional[int] = Field(None, description="利润表ID")
    balance_sheet_id: Optional[int] = Field(None, description="资产负债表ID")
    report_file_url: Optional[str] = Field(None, description="导出报表附件文件", max_length=1024)
    status: Optional[int] = Field(None, description="报表状态")
    audit_user_id: Optional[int] = Field(None, description="报表审核人ID")
    archive_user_id: Optional[int] = Field(None, description="报表归档人ID")
    remark: Optional[str] = Field(None, description="报表编制说明、数据异常备注")


class FinancialReportResponse(BaseModel):
    """财务报表主表响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    report_name: str
    report_type: int
    report_period: str
    report_year: int
    cash_flow_statement_id: Optional[int]
    profit_statement_id: Optional[int]
    balance_sheet_id: Optional[int]
    report_file_url: Optional[str]
    status: int
    create_user_id: int
    audit_user_id: Optional[int]
    audit_time: Optional[datetime]
    archive_user_id: Optional[int]
    archive_time: Optional[datetime]
    remark: Optional[str]
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 报表审核模型 ==========

class ReportAudit(BaseModel):
    """报表审核请求模型"""
    id: int = Field(..., description="报表ID")
    audit_user_id: int = Field(..., description="审核人ID")
    audit_status: int = Field(..., description="审核状态：2(已审核)或4(作废)")


# ========== 报表查询条件 ==========

class ReportQuery(BaseModel):
    """报表查询请求模型"""
    project_id: Optional[int] = Field(None, description="楼盘ID")
    channel_id: Optional[int] = Field(None, description="渠道ID")
    stat_month: Optional[str] = Field(None, description="统计月份(YYYY-MM)")
    start_month: Optional[str] = Field(None, description="开始月份")
    end_month: Optional[str] = Field(None, description="结束月份")
    report_period: Optional[str] = Field(None, description="报表期间(YYYY-MM)")
    report_type: Optional[int] = Field(None, description="报表类型")
    stat_type: Optional[int] = Field(None, description="统计类型")
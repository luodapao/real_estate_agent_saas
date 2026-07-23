"""
房地产SaaS财务管理系统 - 财务基础档案模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ========== 项目财务配置 ==========

class ProjectFinConfigCreate(BaseModel):
    """创建项目财务配置请求模型"""
    project_id: int = Field(..., description="楼盘ID")
    project_name: str = Field(..., description="楼盘名称")
    finance_status: int = Field(1, description="财务启用状态：1启用 2停用")
    calc_mode: int = Field(1, description="计税模式：1一般计税 2简易计税")
    default_tax_rate_id: Optional[int] = Field(None, description="默认计税税率模板ID")
    default_income_subject_id: Optional[int] = Field(None, description="默认收入科目ID")
    default_receive_account_id: Optional[int] = Field(None, description="默认通用收款账户ID")
    default_mortgage_account_id: Optional[int] = Field(None, description="按揭回款专用收款账户ID")
    default_supervise_account_id: Optional[int] = Field(None, description="预售资金监管专户ID")
    default_cap_cost_subject_id: Optional[int] = Field(None, description="资本化开发成本默认科目ID")
    default_market_subject_id: Optional[int] = Field(None, description="广告营销费用默认科目ID")
    default_payable_subject_id: Optional[int] = Field(None, description="供应商应付账款科目ID")
    default_advance_subject_id: Optional[int] = Field(None, description="供应商预付账款科目ID")
    default_channel_subject_id: Optional[int] = Field(None, description="分销渠道佣金往来科目ID")
    default_tax_subject_id: Optional[int] = Field(None, description="应交税费总账科目ID")
    deposit_ratio: Decimal = Field(0.0, description="定金比例上限")
    installment_rule: Optional[str] = Field(None, description="分期规则JSON配置")
    max_advance_ratio: Decimal = Field(0.0, description="供应商预付工程款比例上限")
    settle_cycle_type: int = Field(1, description="默认供应商结算周期：1月结 2季结 3竣工一次性结算")
    close_status: int = Field(0, description="项目财务归档状态：0在建未结账 1竣工已结账归档")
    remark: Optional[str] = Field(None, description="财务配置备注说明")


class ProjectFinConfigUpdate(BaseModel):
    """更新项目财务配置请求模型"""
    finance_status: Optional[int] = Field(None, description="财务启用状态：1启用 2停用")
    calc_mode: Optional[int] = Field(None, description="计税模式：1一般计税 2简易计税")
    default_tax_rate_id: Optional[int] = Field(None, description="默认计税税率模板ID")
    default_income_subject_id: Optional[int] = Field(None, description="默认收入科目ID")
    default_receive_account_id: Optional[int] = Field(None, description="默认通用收款账户ID")
    default_mortgage_account_id: Optional[int] = Field(None, description="按揭回款专用收款账户ID")
    default_supervise_account_id: Optional[int] = Field(None, description="预售资金监管专户ID")
    default_cap_cost_subject_id: Optional[int] = Field(None, description="资本化开发成本默认科目ID")
    default_market_subject_id: Optional[int] = Field(None, description="广告营销费用默认科目ID")
    default_payable_subject_id: Optional[int] = Field(None, description="供应商应付账款科目ID")
    default_advance_subject_id: Optional[int] = Field(None, description="供应商预付账款科目ID")
    default_channel_subject_id: Optional[int] = Field(None, description="分销渠道佣金往来科目ID")
    default_tax_subject_id: Optional[int] = Field(None, description="应交税费总账科目ID")
    deposit_ratio: Optional[Decimal] = Field(None, description="定金比例上限")
    installment_rule: Optional[str] = Field(None, description="分期规则JSON配置")
    max_advance_ratio: Optional[Decimal] = Field(None, description="供应商预付工程款比例上限")
    settle_cycle_type: Optional[int] = Field(None, description="默认供应商结算周期：1月结 2季结 3竣工一次性结算")
    close_status: Optional[int] = Field(None, description="项目财务归档状态：0在建未结账 1竣工已结账归档")
    remark: Optional[str] = Field(None, description="财务配置备注说明")


class ProjectFinConfigResponse(BaseModel):
    """项目财务配置响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    project_id: int
    project_name: str = Field(description="楼盘名称")
    finance_status: int = Field(description="财务启用状态：1启用 2停用")
    calc_mode: int = Field(description="计税模式：1一般计税 2简易计税")
    default_tax_rate_id: Optional[int] = Field(None, description="默认计税税率模板ID")
    default_income_subject_id: Optional[int] = Field(None, description="默认收入科目ID")
    default_receive_account_id: Optional[int] = Field(None, description="默认通用收款账户ID")
    default_mortgage_account_id: Optional[int] = Field(None, description="按揭回款专用收款账户ID")
    default_supervise_account_id: Optional[int] = Field(None, description="预售资金监管专户ID")
    default_cap_cost_subject_id: Optional[int] = Field(None, description="资本化开发成本默认科目ID")
    default_market_subject_id: Optional[int] = Field(None, description="广告营销费用默认科目ID")
    default_payable_subject_id: Optional[int] = Field(None, description="供应商应付账款科目ID")
    default_advance_subject_id: Optional[int] = Field(None, description="供应商预付账款科目ID")
    default_channel_subject_id: Optional[int] = Field(None, description="分销渠道佣金往来科目ID")
    default_tax_subject_id: Optional[int] = Field(None, description="应交税费总账科目ID")
    deposit_ratio: Decimal = Field(description="定金比例上限")
    installment_rule: Optional[str] = Field(None, description="分期规则JSON配置")
    max_advance_ratio: Decimal = Field(description="供应商预付工程款比例上限")
    settle_cycle_type: int = Field(description="默认供应商结算周期：1月结 2季结 3竣工一次性结算")
    close_status: int = Field(description="项目财务归档状态：0在建未结账 1竣工已结账归档")
    remark: Optional[str] = Field(None, description="财务配置备注说明")
    create_user_id: int = Field(description="配置创建人ID")
    update_user_id: Optional[int] = Field(None, description="配置最后修改人ID")
    version: int = Field(description="乐观锁版本号")
    is_del: int = Field(description="0正常 1逻辑删除")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")


# ========== 账户管理 ==========

class AccountCreate(BaseModel):
    """创建账户请求模型"""
    account_code: Optional[str] = Field(None, description="账户编码（自动生成，无需传入）", max_length=64)
    account_name: str = Field(..., description="账户名称", max_length=100)
    account_type: int = Field(..., description="账户类型：1现金 2银行存款 3支付宝 4微信")
    bank_name: Optional[str] = Field(None, description="开户银行名称", max_length=100)
    bank_account: Optional[str] = Field(None, description="银行账号（脱敏存储）", max_length=50)
    cnaps_code: Optional[str] = Field(None, description="联行号", max_length=20)
    account_status: int = Field(1, description="账户状态：1启用 2停用")
    is_default: int = Field(0, description="是否默认账户：0否 1是")
    account_holder: Optional[str] = Field(None, description="开户人姓名")
    mobile: Optional[str] = Field(None, description="联系电话")
    remark: Optional[str] = Field(None, description="账户备注")


class AccountUpdate(BaseModel):
    """更新账户请求模型"""
    account_name: Optional[str] = Field(None, description="账户名称", max_length=100)
    account_type: Optional[int] = Field(None, description="账户类型：1现金 2银行存款 3支付宝 4微信")
    bank_name: Optional[str] = Field(None, description="开户银行名称", max_length=100)
    bank_account: Optional[str] = Field(None, description="银行账号（脱敏存储）", max_length=50)
    cnaps_code: Optional[str] = Field(None, description="联行号", max_length=20)
    account_status: Optional[int] = Field(None, description="账户状态：1启用 2停用")
    is_default: Optional[int] = Field(None, description="是否默认账户：0否 1是")
    account_holder: Optional[str] = Field(None, description="开户人姓名")
    mobile: Optional[str] = Field(None, description="联系电话")
    remark: Optional[str] = Field(None, description="账户备注")


class AccountResponse(BaseModel):
    """账户响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    account_code: str = Field(description="账户编码，租户内唯一")
    account_name: str = Field(description="账户名称")
    account_type: int = Field(description="账户类型：1现金 2银行存款 3支付宝 4微信")
    bank_name: Optional[str] = Field(None, description="开户银行名称")
    bank_account: Optional[str] = Field(None, description="银行账号（脱敏存储）")
    cnaps_code: Optional[str] = Field(None, description="联行号")
    account_status: int = Field(description="账户状态：1启用 2停用")
    is_default: int = Field(description="是否默认账户：0否 1是")
    account_holder: Optional[str] = Field(None, description="开户人姓名")
    mobile: Optional[str] = Field(None, description="联系电话")
    remark: Optional[str] = Field(None, description="账户备注")
    create_user_id: int = Field(description="创建人ID")
    update_user_id: Optional[int] = Field(None, description="最后修改人ID")
    version: int = Field(description="乐观锁版本号")
    is_del: int = Field(description="0正常 1逻辑删除")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")


# ========== 科目管理 ==========

class SubjectCreate(BaseModel):
    """创建科目请求模型"""
    subject_code: Optional[str] = Field(None, description="科目编码（自动生成，无需传入）", max_length=64)
    subject_name: str = Field(..., description="科目名称", max_length=100)
    subject_level: int = Field(1, description="科目级别：1-4")
    parent_id: int = Field(0, description="上级科目ID")
    subject_type: int = Field(..., description="科目类型：1资产 2负债 3权益 4成本 5损益")
    subject_nature: int = Field(..., description="科目性质：1借方 2贷方")
    is_leaf: int = Field(1, description="是否末级科目：1是 0否")
    is_enabled: int = Field(1, description="是否启用：1是 0否")
    account_id: Optional[int] = Field(None, description="关联账户ID")
    remark: Optional[str] = Field(None, description="科目备注")


class SubjectUpdate(BaseModel):
    """更新科目请求模型"""
    subject_name: Optional[str] = Field(None, description="科目名称", max_length=100)
    subject_level: Optional[int] = Field(None, description="科目级别：1-4")
    parent_id: Optional[int] = Field(None, description="上级科目ID")
    subject_type: Optional[int] = Field(None, description="科目类型：1资产 2负债 3权益 4成本 5损益")
    subject_nature: Optional[int] = Field(None, description="科目性质：1借方 2贷方")
    is_leaf: Optional[int] = Field(None, description="是否末级科目：1是 0否")
    is_enabled: Optional[int] = Field(None, description="是否启用：1是 0否")
    account_id: Optional[int] = Field(None, description="关联账户ID")
    remark: Optional[str] = Field(None, description="科目备注")


class SubjectResponse(BaseModel):
    """科目响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    subject_code: str = Field(description="科目编码")
    subject_name: str = Field(description="科目名称")
    subject_level: int = Field(description="科目级别：1-4")
    parent_id: int = Field(description="上级科目ID")
    subject_type: int = Field(description="科目类型：1资产 2负债 3权益 4成本 5损益")
    subject_nature: int = Field(description="科目性质：1借方 2贷方")
    is_leaf: int = Field(description="是否末级科目：1是 0否")
    is_enabled: int = Field(description="是否启用：1是 0否")
    account_id: Optional[int] = Field(None, description="关联账户ID")
    remark: Optional[str] = Field(None, description="科目备注")
    create_user_id: int = Field(description="创建人ID")
    update_user_id: Optional[int] = Field(None, description="最后修改人ID")
    version: int = Field(description="乐观锁版本号")
    is_del: int = Field(description="0正常 1逻辑删除")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")


# ========== 税率管理 ==========

class TaxRateCreate(BaseModel):
    """创建税率请求模型"""
    tax_rate_code: Optional[str] = Field(None, description="税率编码（自动生成，无需传入）")
    tax_rate_name: str = Field(..., description="税率名称")
    tax_type: int = Field(1, description="税种类型：1增值税 2企业所得税 3个人所得税")
    rate_value: Decimal = Field(0.0, description="税率值")
    tax_status: int = Field(1, description="税率状态：1启用 2停用")
    is_default: int = Field(0, description="是否默认：0否 1是")
    calc_mode: int = Field(1, description="计税模式：1一般计税 2简易计税")
    bind_subject_id: Optional[int] = Field(None, description="绑定的计税科目ID")
    biz_scope: Optional[str] = Field(None, description="适用业务范围JSON")
    create_user_id: Optional[int] = Field(None, description="创建人ID")
    remark: Optional[str] = Field(None, description="备注说明")


class TaxRateUpdate(BaseModel):
    """更新税率请求模型"""
    tax_rate_code: Optional[str] = Field(None, description="税率编码")
    tax_rate_name: Optional[str] = Field(None, description="税率名称")
    tax_type: Optional[int] = Field(None, description="税种类型：1增值税 2企业所得税 3个人所得税")
    rate_value: Optional[Decimal] = Field(None, description="税率值")
    tax_status: Optional[int] = Field(None, description="税率状态：1启用 2停用")
    is_default: Optional[int] = Field(None, description="是否默认：0否 1是")
    calc_mode: Optional[int] = Field(None, description="计税模式：1一般计税 2简易计税")
    bind_subject_id: Optional[int] = Field(None, description="绑定的计税科目ID")
    biz_scope: Optional[str] = Field(None, description="适用业务范围JSON")
    remark: Optional[str] = Field(None, description="备注说明")


class TaxRateResponse(BaseModel):
    """税率响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    tax_code: str = Field(description="税率编码")
    tax_name: str = Field(description="税率名称")
    tax_type: int = Field(description="税种类型：1增值税 2企业所得税 3个人所得税")
    tax_rate: Decimal = Field(description="税率值")
    tax_status: int = Field(description="税率状态：1启用 2停用")
    is_default: int = Field(description="是否默认：0否 1是")
    calc_mode: int = Field(description="计税模式：1一般计税 2简易计税")
    bind_subject_id: Optional[int] = Field(None, description="绑定的计税科目ID")
    biz_scope: Optional[str] = Field(None, description="适用业务范围JSON")
    create_user_id: int = Field(description="创建人ID")
    update_user_id: Optional[int] = Field(None, description="最后修改人ID")
    remark: Optional[str] = Field(None, description="备注说明")
    version: int = Field(description="乐观锁版本号")
    is_del: int = Field(description="0正常 1逻辑删除")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")


# ========== 银行信息管理 ==========

class BankInfoCreate(BaseModel):
    """创建银行信息请求模型"""
    bank_info_code: Optional[str] = Field(None, description="银行档案编码（自动生成，无需传入）", max_length=64)
    bank_name: str = Field(..., description="开户银行名称", max_length=100)
    bank_account: str = Field(..., description="银行账号（脱敏）", max_length=50)
    account_name: str = Field(..., description="账户名称", max_length=100)
    cnaps_code: Optional[str] = Field(None, description="联行号", max_length=20)
    company_type: int = Field(..., description="账户主体类型：1开发商 2渠道 3供应商")
    company_id: Optional[int] = Field(None, description="关联主体ID")
    bank_status: int = Field(1, description="状态：1启用 2停用")
    remark: Optional[str] = Field(None, description="备注说明")


class BankInfoUpdate(BaseModel):
    """更新银行信息请求模型"""
    bank_name: Optional[str] = Field(None, description="开户银行名称", max_length=100)
    bank_account: Optional[str] = Field(None, description="银行账号（脱敏）", max_length=50)
    account_name: Optional[str] = Field(None, description="账户名称", max_length=100)
    cnaps_code: Optional[str] = Field(None, description="联行号", max_length=20)
    company_type: Optional[int] = Field(None, description="账户主体类型：1开发商 2渠道 3供应商")
    company_id: Optional[int] = Field(None, description="关联主体ID")
    bank_status: Optional[int] = Field(None, description="状态：1启用 2停用")
    remark: Optional[str] = Field(None, description="备注说明")


class BankInfoResponse(BaseModel):
    """银行信息响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    bank_info_code: str = Field(description="银行档案编码")
    bank_name: str = Field(description="开户银行名称")
    bank_account: str = Field(description="银行账号（脱敏）")
    account_name: str = Field(description="账户名称")
    cnaps_code: Optional[str] = Field(None, description="联行号")
    company_type: int = Field(description="账户主体类型：1开发商 2渠道 3供应商")
    company_id: Optional[int] = Field(None, description="关联主体ID")
    bank_status: int = Field(description="状态：1启用 2停用")
    remark: Optional[str] = Field(None, description="备注说明")
    create_user_id: int = Field(description="创建人ID")
    update_user_id: Optional[int] = Field(None, description="最后修改人ID")
    version: int = Field(description="乐观锁版本号")
    is_del: int = Field(description="0正常 1逻辑删除")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")


# ========== 优惠规则管理 ==========

class DiscountRuleCreate(BaseModel):
    """创建优惠规则请求模型"""
    project_id: int = Field(..., description="关联楼盘ID")
    project_name: str = Field(..., description="楼盘名称", max_length=128)
    discount_code: Optional[str] = Field(None, description="优惠规则编码（自动生成，无需传入）", max_length=64)
    discount_name: str = Field(..., description="优惠规则名称", max_length=100)
    discount_type: int = Field(..., description="优惠类型：1折扣 2一口价 3减免 4组合")
    property_type: str = Field(..., description="适用物业类型", max_length=30)
    discount_rate: Decimal = Field(1.0, description="折扣比例")
    fixed_price: Decimal = Field(0, description="一口价金额")
    max_discount_amount: Decimal = Field(0, description="单房源最大优惠上限")
    start_time: datetime = Field(..., description="规则生效时间")
    end_time: Optional[datetime] = Field(None, description="规则失效时间")
    is_stack: int = Field(0, description="是否支持叠加：0否 1是")
    offset_income: int = Field(1, description="是否冲减收入：1是 0否")
    rule_status: int = Field(1, description="状态：1启用 2停用")
    remark: Optional[str] = Field(None, description="优惠规则备注")


class DiscountRuleUpdate(BaseModel):
    """更新优惠规则请求模型"""
    discount_name: Optional[str] = Field(None, description="优惠规则名称", max_length=100)
    discount_type: Optional[int] = Field(None, description="优惠类型：1折扣 2一口价 3减免 4组合")
    property_type: Optional[str] = Field(None, description="适用物业类型", max_length=30)
    discount_rate: Optional[Decimal] = Field(None, description="折扣比例")
    fixed_price: Optional[Decimal] = Field(None, description="一口价金额")
    max_discount_amount: Optional[Decimal] = Field(None, description="单房源最大优惠上限")
    end_time: Optional[datetime] = Field(None, description="规则失效时间")
    is_stack: Optional[int] = Field(None, description="是否支持叠加：0否 1是")
    offset_income: Optional[int] = Field(None, description="是否冲减收入：1是 0否")
    rule_status: Optional[int] = Field(None, description="状态：1启用 2停用")
    remark: Optional[str] = Field(None, description="优惠规则备注")


class DiscountRuleResponse(BaseModel):
    """优惠规则响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    project_id: int = Field(description="关联楼盘ID")
    project_name: Optional[str] = Field(None, description="楼盘名称")
    discount_code: str = Field(description="优惠规则编码")
    discount_name: str = Field(description="优惠规则名称")
    discount_type: int = Field(description="优惠类型：1折扣 2一口价 3减免 4组合")
    property_type: str = Field(description="适用物业类型")
    discount_rate: Decimal = Field(description="折扣比例")
    fixed_price: Decimal = Field(description="一口价金额")
    max_discount_amount: Decimal = Field(description="单房源最大优惠上限")
    start_time: datetime = Field(description="规则生效时间")
    end_time: Optional[datetime] = Field(None, description="规则失效时间")
    is_stack: int = Field(description="是否支持叠加：0否 1是")
    offset_income: int = Field(description="是否冲减收入：1是 0否")
    rule_status: int = Field(description="状态：1启用 2停用")
    remark: Optional[str] = Field(None, description="优惠规则备注")
    create_user_id: int = Field(description="创建人ID")
    update_user_id: Optional[int] = Field(None, description="最后修改人ID")
    version: int = Field(description="乐观锁版本号")
    is_del: int = Field(description="0正常 1逻辑删除")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")
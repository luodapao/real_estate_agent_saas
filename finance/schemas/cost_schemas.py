"""
房地产SaaS财务管理系统 - 项目成本&运营费用模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field\nfrom common.schemas.response import ORMBaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


# ========== 通用费用申请（事前审批） ==========

class CostExpenseCreate(BaseModel):
    """创建通用费用申请请求模型"""
    project_id: Optional[int] = Field(None, description="归属楼盘ID")
    project_name: Optional[str] = Field(None, description="楼盘名称冗余", max_length=128)
    building_id: Optional[int] = Field(None, description="分摊楼栋ID")
    building_name: Optional[str] = Field(None, description="分摊楼栋名称冗余", max_length=512)
    apply_user_id: int = Field(..., description="申请人员工ID")
    apply_user_name: str = Field(..., description="申请人姓名冗余", max_length=80)
    dept_id: Optional[int] = Field(None, description="申请人部门ID")
    project_fin_config_id: Optional[int] = Field(None, description="楼盘财务配置ID")
    expense_subject_id: int = Field(..., description="费用归属会计科目ID")
    tax_tpl_id: Optional[int] = Field(None, description="预计进项税率模板ID")
    expense_type: int = Field(..., description="费用类型：1办公费 2差旅费 3业务招待 4营销杂费 5行政水电")
    apply_time: datetime = Field(..., description="申请提交时间")
    expense_start_date: date = Field(..., description="费用发生起始日期")
    expense_end_date: date = Field(..., description="费用发生截止日期")
    total_amount: Decimal = Field(..., description="申请含税总金额")
    untax_amount: Decimal = Field(..., description="申请不含税成本金额")
    tax_amount: Decimal = Field(0, description="预计可抵扣进项税额")
    reimburse_id: Optional[int] = Field(None, description="核销后关联报销单ID")
    expense_file_url: Optional[str] = Field(None, description="申请预算说明、报价单附件OSS链接", max_length=1024)
    remark: Optional[str] = Field(None, description="费用用途、分摊楼栋说明")
    create_user_id: int = Field(..., description="单据制单人ID")
    expense_no: Optional[str] = Field(default=None, description="费用申请单号（系统自动生成）", max_length=64)


class CostExpenseUpdate(BaseModel):
    """更新通用费用申请请求模型"""
    project_id: Optional[int] = Field(None, description="归属楼盘ID")
    project_name: Optional[str] = Field(None, description="楼盘名称冗余", max_length=128)
    building_id: Optional[int] = Field(None, description="分摊楼栋ID")
    building_name: Optional[str] = Field(None, description="分摊楼栋名称冗余", max_length=512)
    dept_id: Optional[int] = Field(None, description="申请人部门ID")
    expense_subject_id: Optional[int] = Field(None, description="费用归属会计科目ID")
    tax_tpl_id: Optional[int] = Field(None, description="预计进项税率模板ID")
    expense_type: Optional[int] = Field(None, description="费用类型")
    expense_start_date: Optional[date] = Field(None, description="费用发生起始日期")
    expense_end_date: Optional[date] = Field(None, description="费用发生截止日期")
    total_amount: Optional[Decimal] = Field(None, description="申请含税总金额")
    untax_amount: Optional[Decimal] = Field(None, description="申请不含税成本金额")
    tax_amount: Optional[Decimal] = Field(None, description="预计可抵扣进项税额")
    expense_file_url: Optional[str] = Field(None, description="申请预算说明、报价单附件OSS链接", max_length=1024)
    remark: Optional[str] = Field(None, description="费用用途、分摊楼栋说明")


class CostExpenseResponse(ORMBaseModel):
    """通用费用申请响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    expense_no: str
    project_id: Optional[int]
    project_name: Optional[str] = Field(None, description="楼盘名称")
    building_id: Optional[int]
    building_name: Optional[str] = Field(None, description="分摊楼栋名称")
    apply_user_id: int
    apply_user_name: str
    dept_id: Optional[int]
    project_fin_config_id: Optional[int]
    expense_subject_id: int
    tax_tpl_id: Optional[int]
    expense_type: int
    apply_time: datetime
    expense_start_date: date
    expense_end_date: date
    total_amount: Decimal
    untax_amount: Decimal
    tax_amount: Decimal
    reimburse_id: Optional[int]
    audit_status: int
    audit_user_id: Optional[int]
    audit_time: Optional[datetime]
    expense_file_url: Optional[str]
    remark: Optional[str]
    create_user_id: int
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 费用报销（事后核销） ==========

class ExpenseReimbursementCreate(BaseModel):
    """创建费用报销请求模型"""
    project_id: Optional[int] = Field(None, description="归属楼盘ID")
    project_name: Optional[str] = Field(None, description="楼盘名称冗余", max_length=128)
    building_id: Optional[int] = Field(None, description="分摊楼栋ID")
    building_name: Optional[str] = Field(None, description="分摊楼栋名称冗余", max_length=512)
    employee_id: int = Field(..., description="报销员工ID")
    employee_name: str = Field(..., description="报销人姓名冗余", max_length=80)
    dept_id: Optional[int] = Field(None, description="报销人部门ID")
    cost_expense_id: Optional[int] = Field(None, description="关联事前费用申请单ID")
    project_fin_config_id: Optional[int] = Field(None, description="楼盘财务配置ID")
    expense_subject_id: int = Field(..., description="费用会计科目ID")
    tax_tpl_id: int = Field(..., description="发票进项税率模板ID")
    expense_type: int = Field(..., description="费用类型：1办公费 2差旅费 3业务招待 4营销杂费 5行政水电")
    reimburse_date: date = Field(..., description="费用实际发生日期")
    invoice_no: Optional[str] = Field(None, description="增值税发票号码", max_length=256)
    invoice_date: Optional[date] = Field(None, description="发票开具日期")
    total_amount: Decimal = Field(..., description="报销含税总金额")
    untax_amount: Decimal = Field(..., description="报销不含税入账成本")
    tax_amount: Decimal = Field(0, description="可抵扣增值税进项税额")
    deduct_amount: Decimal = Field(0, description="不予抵扣/个人扣款金额")
    actual_reimburse_amount: Decimal = Field(..., description="实际应报销净额")
    cost_pay_id: Optional[int] = Field(None, description="核销后关联费用付款单ID")
    voucher_no: Optional[str] = Field(None, description="费用报销财务凭证编号", max_length=64)
    reimburse_file_url: Optional[str] = Field(None, description="发票、行程单、消费凭证多附件链接", max_length=1024)
    remark: Optional[str] = Field(None, description="费用用途、楼栋分摊、发票特殊说明")
    create_user_id: int = Field(..., description="报销单制单人ID")
    reimburse_no: Optional[str] = Field(default=None, description="报销单号（系统自动生成）", max_length=64)


class ExpenseReimbursementUpdate(BaseModel):
    """更新费用报销请求模型"""
    project_id: Optional[int] = Field(None, description="归属楼盘ID")
    project_name: Optional[str] = Field(None, description="楼盘名称冗余", max_length=128)
    building_id: Optional[int] = Field(None, description="分摊楼栋ID")
    building_name: Optional[str] = Field(None, description="分摊楼栋名称冗余", max_length=512)
    expense_subject_id: Optional[int] = Field(None, description="费用会计科目ID")
    tax_tpl_id: Optional[int] = Field(None, description="发票进项税率模板ID")
    expense_type: Optional[int] = Field(None, description="费用类型")
    reimburse_date: Optional[date] = Field(None, description="费用实际发生日期")
    invoice_no: Optional[str] = Field(None, description="增值税发票号码", max_length=256)
    invoice_date: Optional[date] = Field(None, description="发票开具日期")
    total_amount: Optional[Decimal] = Field(None, description="报销含税总金额")
    untax_amount: Optional[Decimal] = Field(None, description="报销不含税入账成本")
    tax_amount: Optional[Decimal] = Field(None, description="可抵扣增值税进项税额")
    deduct_amount: Optional[Decimal] = Field(None, description="不予抵扣/个人扣款金额")
    actual_reimburse_amount: Optional[Decimal] = Field(None, description="实际应报销净额")
    reimburse_file_url: Optional[str] = Field(None, description="发票、行程单、消费凭证多附件链接", max_length=1024)
    remark: Optional[str] = Field(None, description="费用用途、楼栋分摊、发票特殊说明")


class ExpenseReimbursementResponse(ORMBaseModel):
    """费用报销响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    reimburse_no: str
    project_id: Optional[int]
    project_name: Optional[str] = Field(None, description="楼盘名称")
    building_id: Optional[int]
    building_name: Optional[str] = Field(None, description="分摊楼栋名称")
    employee_id: int
    employee_name: str
    dept_id: Optional[int]
    cost_expense_id: Optional[int]
    project_fin_config_id: Optional[int]
    expense_subject_id: int
    tax_tpl_id: int
    expense_type: int
    reimburse_date: date
    invoice_no: Optional[str]
    invoice_date: Optional[date]
    total_amount: Decimal
    untax_amount: Decimal
    tax_amount: Decimal
    deduct_amount: Decimal
    actual_reimburse_amount: Decimal
    cost_pay_id: Optional[int]
    voucher_no: Optional[str]
    audit_status: int
    audit_user_id: Optional[int]
    audit_time: Optional[datetime]
    reimburse_file_url: Optional[str]
    remark: Optional[str]
    create_user_id: int
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 费用付款（资金执行层） ==========

class CostPayCreate(BaseModel):
    """创建费用付款请求模型"""
    project_id: Optional[int] = Field(None, description="归属楼盘ID")
    project_name: Optional[str] = Field(None, description="楼盘名称冗余", max_length=128)
    building_scope: Optional[str] = Field(None, description="本次付款分摊楼栋ID，逗号分隔", max_length=512)
    account_id: int = Field(..., description="我方付款账户ID")
    account_name: str = Field(..., description="账户名称冗余", max_length=100)
    project_fin_config_id: Optional[int] = Field(None, description="楼盘财务配置ID")
    cost_subject_id: int = Field(..., description="费用付款对应总账科目ID")
    reimburse_ids: Optional[str] = Field(None, description="批量付款关联报销单ID集合", max_length=1024)
    expense_ids: Optional[str] = Field(None, description="批量付款关联费用申请单ID集合", max_length=1024)
    ad_cost_ids: Optional[str] = Field(None, description="批量付款关联广告成本ID集合", max_length=1024)
    eng_cost_ids: Optional[str] = Field(None, description="批量付款关联工程成本ID集合", max_length=1024)
    total_pay_untax: Decimal = Field(..., description="本次付款不含税总成本汇总")
    total_pay_tax: Decimal = Field(0, description="本次付款进项税总额汇总")
    total_pay_amount: Decimal = Field(..., description="应付含税付款总额")
    deduct_total: Decimal = Field(0, description="扣款合计金额")
    pay_amount: Decimal = Field(..., description="银行实际出账净额")
    pay_target_type: int = Field(..., description="1内部员工报销 2外部供应商对公付款")
    target_name: str = Field(..., description="收款户名", max_length=100)
    target_bank_info_id: Optional[int] = Field(None, description="外部供应商对公账户ID")
    target_bank_card: Optional[str] = Field(None, description="员工报销收款银行卡", max_length=50)
    bank_flow_id: Optional[int] = Field(None, description="对应银行资金流水ID")
    bank_flow_no: Optional[str] = Field(None, description="银行流水单号冗余", max_length=64)
    voucher_no: Optional[str] = Field(None, description="费用付款财务凭证编号", max_length=64)
    pay_file_url: Optional[str] = Field(None, description="付款审批单、网银回单、批量代发明细附件", max_length=1024)
    remark: Optional[str] = Field(None, description="批量付款汇总说明、付款失败原因备注")
    create_user_id: int = Field(..., description="付款单制单人ID")
    pay_no: Optional[str] = Field(default=None, description="付款单号（系统自动生成）", max_length=64)


class CostPayUpdate(BaseModel):
    """更新费用付款请求模型"""
    project_id: Optional[int] = Field(None, description="归属楼盘ID")
    project_name: Optional[str] = Field(None, description="楼盘名称冗余", max_length=128)
    building_scope: Optional[str] = Field(None, description="本次付款分摊楼栋ID，逗号分隔", max_length=512)
    account_id: Optional[int] = Field(None, description="我方付款账户ID")
    account_name: Optional[str] = Field(None, description="账户名称冗余", max_length=100)
    cost_subject_id: Optional[int] = Field(None, description="费用付款对应总账科目ID")
    total_pay_untax: Optional[Decimal] = Field(None, description="本次付款不含税总成本汇总")
    total_pay_tax: Optional[Decimal] = Field(None, description="本次付款进项税总额汇总")
    total_pay_amount: Optional[Decimal] = Field(None, description="应付含税付款总额")
    deduct_total: Optional[Decimal] = Field(None, description="扣款合计金额")
    pay_amount: Optional[Decimal] = Field(None, description="银行实际出账净额")
    pay_target_type: Optional[int] = Field(None, description="1内部员工报销 2外部供应商对公付款")
    target_name: Optional[str] = Field(None, description="收款户名", max_length=100)
    pay_status: Optional[int] = Field(None, description="资金执行状态")
    pay_time: Optional[datetime] = Field(None, description="银行实际出账时间")
    bank_flow_id: Optional[int] = Field(None, description="对应银行资金流水ID")
    bank_flow_no: Optional[str] = Field(None, description="银行流水单号冗余", max_length=64)
    voucher_no: Optional[str] = Field(None, description="费用付款财务凭证编号", max_length=64)
    pay_file_url: Optional[str] = Field(None, description="付款审批单、网银回单、批量代发明细附件", max_length=1024)
    remark: Optional[str] = Field(None, description="批量付款汇总说明、付款失败原因备注")


class CostPayResponse(ORMBaseModel):
    """费用付款响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    pay_no: str
    project_id: Optional[int]
    project_name: Optional[str] = Field(None, description="楼盘名称")
    building_scope: Optional[str]
    account_id: int
    account_name: str
    project_fin_config_id: Optional[int]
    cost_subject_id: int
    reimburse_ids: Optional[str]
    expense_ids: Optional[str]
    ad_cost_ids: Optional[str]
    eng_cost_ids: Optional[str]
    total_pay_untax: Decimal
    total_pay_tax: Decimal
    total_pay_amount: Decimal
    deduct_total: Decimal
    pay_amount: Decimal
    pay_target_type: int
    target_name: str
    target_bank_info_id: Optional[int]
    target_bank_card: Optional[str]
    audit_status: int
    pay_status: int
    pay_time: Optional[datetime]
    pay_user_id: Optional[int]
    audit_user_id: Optional[int]
    bank_flow_id: Optional[int]
    bank_flow_no: Optional[str]
    voucher_no: Optional[str]
    pay_file_url: Optional[str]
    remark: Optional[str]
    create_user_id: int
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 广告推广成本 ==========

class AdCostCreate(BaseModel):
    """创建广告推广成本请求模型"""
    project_id: int = Field(..., description="归属楼盘ID")
    project_name: str = Field(..., description="楼盘名称冗余", max_length=128)
    building_id: Optional[int] = Field(None, description="分摊楼栋ID")
    building_name: Optional[str] = Field(None, description="分摊楼栋名称冗余", max_length=512)
    supplier_id: int = Field(..., description="广告渠道供应商ID")
    supplier_name: str = Field(..., description="供应商名称冗余", max_length=100)
    bank_info_id: Optional[int] = Field(None, description="供应商对公收款账户ID")
    project_fin_config_id: int = Field(..., description="楼盘财务配置ID")
    cost_subject_id: int = Field(..., description="营销费用会计科目ID")
    tax_tpl_id: int = Field(..., description="广告服务进项税率模板ID")
    ad_type: int = Field(..., description="广告类型：1线上媒体 2线下活动 3户外大牌 4分销推广")
    ad_channel: Optional[str] = Field(None, description="投放渠道名称", max_length=100)
    ad_contract_id: Optional[int] = Field(None, description="广告合作合同ID")
    ad_start_date: date = Field(..., description="广告投放起始日期")
    ad_end_date: date = Field(..., description="广告投放结束日期")
    cost_date: date = Field(..., description="成本入账归属日期")
    invoice_no: Optional[str] = Field(None, description="广告服务费发票号码", max_length=256)
    invoice_date: Optional[date] = Field(None, description="发票开具日期")
    total_amount: Decimal = Field(..., description="广告含税总金额")
    untax_amount: Decimal = Field(..., description="广告不含税营销成本")
    tax_amount: Decimal = Field(0, description="可抵扣进项税额")
    deduct_amount: Decimal = Field(0, description="扣款、违约金金额")
    actual_cost_amount: Decimal = Field(..., description="应付实际成本净额")
    relate_pay_id: Optional[int] = Field(None, description="核销后关联费用付款单ID")
    voucher_no: Optional[str] = Field(None, description="广告成本财务凭证编号", max_length=64)
    ad_file_url: Optional[str] = Field(None, description="广告合同、投放排期、发票、验收单附件", max_length=1024)
    remark: Optional[str] = Field(None, description="投放内容、楼栋分摊比例、结算特殊约定")
    create_user_id: int = Field(..., description="广告成本录入制单人ID")
    cost_no: Optional[str] = Field(default=None, description="广告成本单号（系统自动生成）", max_length=64)


class AdCostUpdate(BaseModel):
    """更新广告推广成本请求模型"""
    building_id: Optional[int] = Field(None, description="分摊楼栋ID")
    building_name: Optional[str] = Field(None, description="分摊楼栋名称冗余", max_length=512)
    ad_type: Optional[int] = Field(None, description="广告类型")
    ad_channel: Optional[str] = Field(None, description="投放渠道名称", max_length=100)
    ad_end_date: Optional[date] = Field(None, description="广告投放结束日期")
    cost_date: Optional[date] = Field(None, description="成本入账归属日期")
    invoice_no: Optional[str] = Field(None, description="广告服务费发票号码", max_length=256)
    invoice_date: Optional[date] = Field(None, description="发票开具日期")
    total_amount: Optional[Decimal] = Field(None, description="广告含税总金额")
    untax_amount: Optional[Decimal] = Field(None, description="广告不含税营销成本")
    tax_amount: Optional[Decimal] = Field(None, description="可抵扣进项税额")
    deduct_amount: Optional[Decimal] = Field(None, description="扣款、违约金金额")
    actual_cost_amount: Optional[Decimal] = Field(None, description="应付实际成本净额")
    ad_file_url: Optional[str] = Field(None, description="广告合同、投放排期、发票、验收单附件", max_length=1024)
    remark: Optional[str] = Field(None, description="投放内容、楼栋分摊比例、结算特殊约定")


class AdCostResponse(ORMBaseModel):
    """广告推广成本响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    cost_no: str
    project_id: int
    project_name: str
    building_id: Optional[int]
    building_name: Optional[str] = Field(None, description="分摊楼栋名称")
    supplier_id: int
    supplier_name: str
    bank_info_id: Optional[int]
    project_fin_config_id: int
    cost_subject_id: int
    tax_tpl_id: int
    ad_type: int
    ad_channel: Optional[str]
    ad_contract_id: Optional[int]
    ad_start_date: date
    ad_end_date: date
    cost_date: date
    invoice_no: Optional[str]
    invoice_date: Optional[date]
    total_amount: Decimal
    untax_amount: Decimal
    tax_amount: Decimal
    deduct_amount: Decimal
    actual_cost_amount: Decimal
    cost_status: int
    relate_pay_id: Optional[int]
    voucher_no: Optional[str]
    ad_file_url: Optional[str]
    remark: Optional[str]
    create_user_id: int
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 工程建设成本 ==========

class ProjectEngCostCreate(BaseModel):
    """创建工程建设成本请求模型"""
    project_id: int = Field(..., description="归属楼盘ID")
    project_name: str = Field(..., description="楼盘名称冗余", max_length=128)
    building_id: int = Field(..., description="分摊楼栋ID")
    building_name: str = Field(..., description="分摊楼栋名称冗余", max_length=512)
    supplier_id: int = Field(..., description="施工单位供应商ID")
    supplier_name: str = Field(..., description="施工单位名称冗余", max_length=100)
    bank_info_id: Optional[int] = Field(None, description="施工方对公收款账户ID")
    project_fin_config_id: int = Field(..., description="楼盘财务配置ID")
    cost_subject_id: int = Field(..., description="资本化开发成本科目ID")
    tax_tpl_id: int = Field(..., description="工程建安进项税率模板ID")
    eng_type: int = Field(..., description="工程类型：1土建总包 2园林景观 3配套道路管网 4水电安装 5监理设计")
    eng_name: str = Field(..., description="分项工程名称", max_length=100)
    eng_contract_id: int = Field(..., description="工程施工合同ID")
    settle_cycle: str = Field(..., description="本期结算周期", max_length=32)
    settle_start: date = Field(..., description="结算周期起始日")
    settle_end: date = Field(..., description="结算周期截止日")
    cost_date: date = Field(..., description="成本资本化入账日期")
    invoice_no: Optional[str] = Field(None, description="建安工程款增值税发票号码", max_length=256)
    invoice_date: Optional[date] = Field(None, description="发票开具日期")
    total_amount: Decimal = Field(..., description="本期结算含税工程款总额")
    untax_amount: Decimal = Field(..., description="资本化不含税开发成本")
    tax_amount: Decimal = Field(0, description="建安进项可抵扣税额")
    deduct_amount: Decimal = Field(0, description="质保金、违约金扣款金额")
    actual_cost_amount: Decimal = Field(..., description="本期应付工程净额")
    relate_pay_id: Optional[int] = Field(None, description="核销后关联费用付款单ID")
    voucher_no: Optional[str] = Field(None, description="开发成本资本化财务凭证编号", max_length=64)
    eng_file_url: Optional[str] = Field(None, description="工程合同、结算单、验收单、工程款发票附件", max_length=1024)
    remark: Optional[str] = Field(None, description="工程内容、楼栋成本分摊比例、质保金约定说明")
    create_user_id: int = Field(..., description="工程成本录入制单人ID")
    cost_no: Optional[str] = Field(default=None, description="工程成本单号（系统自动生成）", max_length=64)


class ProjectEngCostUpdate(BaseModel):
    """更新工程建设成本请求模型"""
    eng_type: Optional[int] = Field(None, description="工程类型")
    eng_name: Optional[str] = Field(None, description="分项工程名称", max_length=100)
    settle_cycle: Optional[str] = Field(None, description="本期结算周期", max_length=32)
    settle_start: Optional[date] = Field(None, description="结算周期起始日")
    settle_end: Optional[date] = Field(None, description="结算周期截止日")
    cost_date: Optional[date] = Field(None, description="成本资本化入账日期")
    invoice_no: Optional[str] = Field(None, description="建安工程款增值税发票号码", max_length=256)
    invoice_date: Optional[date] = Field(None, description="发票开具日期")
    total_amount: Optional[Decimal] = Field(None, description="本期结算含税工程款总额")
    untax_amount: Optional[Decimal] = Field(None, description="资本化不含税开发成本")
    tax_amount: Optional[Decimal] = Field(None, description="建安进项可抵扣税额")
    deduct_amount: Optional[Decimal] = Field(None, description="质保金、违约金扣款金额")
    actual_cost_amount: Optional[Decimal] = Field(None, description="本期应付工程净额")
    eng_file_url: Optional[str] = Field(None, description="工程合同、结算单、验收单、工程款发票附件", max_length=1024)
    remark: Optional[str] = Field(None, description="工程内容、楼栋成本分摊比例、质保金约定说明")


class ProjectEngCostResponse(ORMBaseModel):
    """工程建设成本响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    cost_no: str
    project_id: int
    project_name: str
    building_id: int
    building_name: str
    supplier_id: int
    supplier_name: str
    bank_info_id: Optional[int]
    project_fin_config_id: int
    cost_subject_id: int
    tax_tpl_id: int
    eng_type: int
    eng_name: str
    eng_contract_id: int
    settle_cycle: str
    settle_start: date
    settle_end: date
    cost_date: date
    invoice_no: Optional[str]
    invoice_date: Optional[date]
    total_amount: Decimal
    untax_amount: Decimal
    tax_amount: Decimal
    deduct_amount: Decimal
    actual_cost_amount: Decimal
    cost_status: int
    relate_pay_id: Optional[int]
    voucher_no: Optional[str]
    eng_file_url: Optional[str]
    remark: Optional[str]
    create_user_id: int
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime
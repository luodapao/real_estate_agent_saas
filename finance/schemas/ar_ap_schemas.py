"""
房地产SaaS财务管理系统 - 应收应付往来台账模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field\nfrom common.schemas.response import ORMBaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# ========== 客户应收台账 ==========

class AccountReceivableCreate(BaseModel):
    """创建客户应收台账请求模型"""
    project_id: int = Field(..., description="楼盘ID")
    project_name: str = Field(..., description="楼盘名称冗余", max_length=128)
    building_id: int = Field(..., description="楼栋ID，成本分摊核心维度")
    building_name: str = Field(..., description="楼栋名称冗余", max_length=60)
    house_id: int = Field(..., description="房源ID")
    house_no: str = Field(..., description="房源房号冗余", max_length=60)
    contract_id: int = Field(..., description="购房合同ID")
    customer_id: int = Field(..., description="客户ID")
    customer_name: str = Field(..., description="客户姓名冗余", max_length=80)
    customer_phone: Optional[str] = Field(None, description="客户手机号冗余", max_length=20)
    project_fin_config_id: int = Field(..., description="楼盘财务配置ID")
    tax_tpl_id: int = Field(..., description="房款销项税率模板ID")
    receivable_subject_id: int = Field(..., description="应收账款会计科目ID")
    first_receivable_date: date = Field(..., description="首期应收账期起始日")
    last_receivable_date: date = Field(..., description="尾款应收截止日")
    total_receivable: Decimal = Field(..., description="应收含税总金额")
    principal_receivable: Decimal = Field(..., description="应收不含税房款本金")
    tax_receivable: Decimal = Field(..., description="应收增值税销项税额")
    total_received: Decimal = Field(0, description="累计已收含税金额")
    total_unpaid: Decimal = Field(..., description="剩余未收含税金额")
    remark: Optional[str] = Field(None, description="应收台账业务备注")
    create_user_id: int = Field(..., description="台账制单人ID")


class AccountReceivableUpdate(BaseModel):
    """更新客户应收台账请求模型"""
    project_id: Optional[int] = Field(None, description="楼盘ID")
    project_name: Optional[str] = Field(None, description="楼盘名称冗余", max_length=128)
    building_id: Optional[int] = Field(None, description="楼栋ID")
    building_name: Optional[str] = Field(None, description="楼栋名称冗余", max_length=60)
    customer_phone: Optional[str] = Field(None, description="客户手机号冗余", max_length=20)
    total_received: Optional[Decimal] = Field(None, description="累计已收含税金额")
    total_unpaid: Optional[Decimal] = Field(None, description="剩余未收含税金额")
    overdue_amount: Optional[Decimal] = Field(None, description="当前逾期未收金额")
    overdue_interest: Optional[Decimal] = Field(None, description="逾期罚息/违约金金额")
    account_status: Optional[int] = Field(None, description="1正常未结清 2全额结清 3部分逾期 4全部逾期 5作废红冲")
    settle_time: Optional[datetime] = Field(None, description="全款结清时间")
    voucher_no: Optional[str] = Field(None, description="应收入账凭证编号", max_length=64)
    settle_voucher_no: Optional[str] = Field(None, description="回款结清核销凭证编号", max_length=64)
    reconcile_remark: Optional[str] = Field(None, description="账龄差异、逾期特殊说明")
    remark: Optional[str] = Field(None, description="应收台账业务备注")


class AccountReceivableResponse(ORMBaseModel):
    """客户应收台账响应模型"""
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
    customer_id: int
    customer_name: str
    customer_phone: Optional[str]
    project_fin_config_id: int
    tax_tpl_id: int
    receivable_subject_id: int
    first_receivable_date: date
    last_receivable_date: date
    overdue_date: Optional[date]
    max_overdue_days: int
    total_receivable: Decimal
    principal_receivable: Decimal
    tax_receivable: Decimal
    total_received: Decimal
    total_unpaid: Decimal
    overdue_amount: Decimal
    overdue_interest: Decimal
    account_status: int
    settle_time: Optional[datetime]
    voucher_no: Optional[str]
    settle_voucher_no: Optional[str]
    reconcile_remark: Optional[str]
    remark: Optional[str]
    create_user_id: int
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 供应商应付台账 ==========

class AccountPayableCreate(BaseModel):
    """创建供应商应付台账请求模型"""
    project_id: int = Field(..., description="归属楼盘ID")
    project_name: str = Field(..., description="楼盘名称冗余", max_length=128)
    building_id: Optional[int] = Field(None, description="分摊楼栋ID，多楼栋逗号分隔")
    building_name: Optional[str] = Field(None, description="分摊楼栋名称冗余", max_length=512)
    supplier_id: int = Field(..., description="供应商ID")
    supplier_name: str = Field(..., description="供应商名称冗余", max_length=100)
    supplier_type: int = Field(..., description="供应商类型：1工程总包 2营销服务 3设计监理 4物资采购")
    relate_biz_type: int = Field(..., description="关联业务类型：1工程成本 2广告营销 3通用费用")
    relate_biz_id: int = Field(..., description="关联业务单据ID")
    contract_id: Optional[int] = Field(None, description="对应供应商合同ID")
    project_fin_config_id: int = Field(..., description="楼盘财务配置ID")
    cost_subject_id: int = Field(..., description="应付账款对应会计科目ID")
    tax_tpl_id: int = Field(..., description="进项税税率模板ID")
    bill_date: date = Field(..., description="应付账单入账日期")
    due_date: date = Field(..., description="付款到期日，账龄计算依据")
    payable_total_amt: Decimal = Field(..., description="应付含税总金额")
    payable_untax_amt: Decimal = Field(..., description="应付不含税成本金额")
    payable_tax_amt: Decimal = Field(..., description="可抵扣进项税额")
    paid_amount: Decimal = Field(0, description="累计已付含税金额")
    unpaid_amount: Decimal = Field(..., description="剩余未付余额")
    payable_file_url: Optional[str] = Field(None, description="结算单、发票、验收单附件", max_length=1024)
    remark: Optional[str] = Field(None, description="应付台账业务备注")
    create_user_id: int = Field(..., description="台账制单人ID")
    payable_no: Optional[str] = Field(None, description="应付台账单号（系统自动生成）", max_length=64)


class AccountPayableUpdate(BaseModel):
    """更新供应商应付台账请求模型"""
    project_id: Optional[int] = Field(None, description="归属楼盘ID")
    project_name: Optional[str] = Field(None, description="楼盘名称冗余", max_length=128)
    building_id: Optional[int] = Field(None, description="分摊楼栋ID")
    building_name: Optional[str] = Field(None, description="分摊楼栋名称冗余", max_length=512)
    supplier_type: Optional[int] = Field(None, description="供应商类型")
    contract_id: Optional[int] = Field(None, description="对应供应商合同ID")
    cost_subject_id: Optional[int] = Field(None, description="应付账款对应会计科目ID")
    tax_tpl_id: Optional[int] = Field(None, description="进项税税率模板ID")
    due_date: Optional[date] = Field(None, description="付款到期日")
    paid_amount: Optional[Decimal] = Field(None, description="累计已付含税金额")
    unpaid_amount: Optional[Decimal] = Field(None, description="剩余未付余额")
    deduct_amount: Optional[Decimal] = Field(None, description="质保金/违约金扣减总额")
    payable_status: Optional[int] = Field(None, description="1未结清 2已结清 3部分结清 4逾期挂账 5作废")
    settle_time: Optional[datetime] = Field(None, description="全额结清时间")
    bank_flow_ids: Optional[str] = Field(None, description="关联付款银行流水ID集合", max_length=1024)
    voucher_no: Optional[str] = Field(None, description="应付入账凭证编号", max_length=64)
    settle_voucher_no: Optional[str] = Field(None, description="付款核销凭证编号", max_length=64)
    payable_file_url: Optional[str] = Field(None, description="结算单、发票、验收单附件", max_length=1024)
    reconcile_remark: Optional[str] = Field(None, description="往来对账差异说明")
    remark: Optional[str] = Field(None, description="应付台账业务备注")


class AccountPayableResponse(ORMBaseModel):
    """供应商应付台账响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    payable_no: str
    project_id: int
    project_name: str
    building_id: Optional[int]
    building_name: Optional[str]
    supplier_id: int
    supplier_name: str
    supplier_type: int
    relate_biz_type: int
    relate_biz_id: int
    contract_id: Optional[int]
    project_fin_config_id: int
    cost_subject_id: int
    tax_tpl_id: int
    bill_date: date
    due_date: date
    overdue_date: Optional[date]
    overdue_days: int
    payable_total_amt: Decimal
    payable_untax_amt: Decimal
    payable_tax_amt: Decimal
    paid_amount: Decimal
    unpaid_amount: Decimal
    deduct_amount: Decimal
    payable_status: int
    settle_time: Optional[datetime]
    bank_flow_ids: Optional[str]
    voucher_no: Optional[str]
    settle_voucher_no: Optional[str]
    payable_file_url: Optional[str]
    reconcile_remark: Optional[str]
    remark: Optional[str]
    create_user_id: int
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 预付款台账 ==========

class AdvancePayCreate(BaseModel):
    """创建预付款台账请求模型"""
    project_id: int = Field(..., description="归属楼盘ID")
    project_name: str = Field(..., description="楼盘名称冗余", max_length=128)
    building_id: Optional[int] = Field(None, description="成本分摊楼栋ID")
    building_name: Optional[str] = Field(None, description="分摊楼栋名称冗余", max_length=512)
    supplier_id: int = Field(..., description="供应商ID")
    supplier_name: str = Field(..., description="供应商名称冗余", max_length=100)
    advance_type: int = Field(..., description="1工程预付款 2营销预付款 3质保金预付 4其他预付")
    project_fin_config_id: int = Field(..., description="楼盘财务配置ID")
    advance_subject_id: int = Field(..., description="预付账款会计科目ID")
    tax_tpl_id: int = Field(..., description="进项税税率模板ID")
    advance_date: date = Field(..., description="预付付款日期")
    expire_date: Optional[date] = Field(None, description="预付核销过期日期")
    advance_total_amt: Decimal = Field(..., description="预付含税总金额")
    advance_untax_amt: Decimal = Field(..., description="预付不含税成本金额")
    advance_tax_amt: Decimal = Field(..., description="预付可抵扣进项税额")
    used_amount: Decimal = Field(0, description="已核销含税金额")
    balance_amount: Decimal = Field(..., description="剩余可核销余额")
    relate_pay_id: int = Field(..., description="关联预付款付款单ID")
    invoice_no: Optional[str] = Field(None, description="核销对应发票号码", max_length=256)
    invoice_date: Optional[date] = Field(None, description="发票开具日期")
    advance_file_url: Optional[str] = Field(None, description="预付协议、付款回单、核销结算附件", max_length=1024)
    remark: Optional[str] = Field(None, description="预付款业务备注")
    create_user_id: int = Field(..., description="台账制单人ID")
    advance_no: Optional[str] = Field(None, description="预付款单号（系统自动生成）", max_length=64)


class AdvancePayUpdate(BaseModel):
    """更新预付款台账请求模型"""
    project_id: Optional[int] = Field(None, description="归属楼盘ID")
    project_name: Optional[str] = Field(None, description="楼盘名称冗余", max_length=128)
    building_id: Optional[int] = Field(None, description="成本分摊楼栋ID")
    building_name: Optional[str] = Field(None, description="分摊楼栋名称冗余", max_length=512)
    advance_type: Optional[int] = Field(None, description="预付款类型")
    expire_date: Optional[date] = Field(None, description="预付核销过期日期")
    used_amount: Optional[Decimal] = Field(None, description="已核销含税金额")
    balance_amount: Optional[Decimal] = Field(None, description="剩余可核销余额")
    relate_payable_ids: Optional[str] = Field(None, description="核销关联应付台账ID集合", max_length=1024)
    invoice_no: Optional[str] = Field(None, description="核销对应发票号码", max_length=256)
    invoice_date: Optional[date] = Field(None, description="发票开具日期")
    advance_status: Optional[int] = Field(None, description="1使用中可核销 2已全额核销 3过期作废 4红冲取消")
    settle_time: Optional[datetime] = Field(None, description="全额核销完成时间")
    voucher_no: Optional[str] = Field(None, description="预付入账凭证编号", max_length=64)
    settle_voucher_no: Optional[str] = Field(None, description="核销冲抵凭证编号", max_length=64)
    advance_file_url: Optional[str] = Field(None, description="预付协议、付款回单、核销结算附件", max_length=1024)
    reconcile_remark: Optional[str] = Field(None, description="核销差异、过期说明")
    remark: Optional[str] = Field(None, description="预付款业务备注")


class AdvancePayResponse(ORMBaseModel):
    """预付款台账响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    advance_no: str
    project_id: int
    project_name: str
    building_id: Optional[int]
    building_name: Optional[str]
    supplier_id: int
    supplier_name: str
    advance_type: int
    project_fin_config_id: int
    advance_subject_id: int
    tax_tpl_id: int
    advance_date: date
    expire_date: Optional[date]
    advance_total_amt: Decimal
    advance_untax_amt: Decimal
    advance_tax_amt: Decimal
    used_amount: Decimal
    balance_amount: Decimal
    relate_pay_id: int
    relate_payable_ids: Optional[str]
    invoice_no: Optional[str]
    invoice_date: Optional[date]
    advance_status: int
    settle_time: Optional[datetime]
    voucher_no: Optional[str]
    settle_voucher_no: Optional[str]
    advance_file_url: Optional[str]
    reconcile_remark: Optional[str]
    remark: Optional[str]
    create_user_id: int
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 其他往来款台账 ==========

class OtherLoanCreate(BaseModel):
    """创建其他往来款台账请求模型"""
    project_id: Optional[int] = Field(None, description="归属楼盘ID，集团总部往来为空")
    project_name: Optional[str] = Field(None, description="楼盘名称冗余", max_length=128)
    loan_counterparty_type: int = Field(..., description="1内部员工 2外部供应商 3集团公司 4外部机构")
    counterparty_id: int = Field(..., description="对方主体ID")
    counterparty_name: str = Field(..., description="对方名称冗余", max_length=100)
    counterparty_dept: Optional[str] = Field(None, description="对方部门/所属单位", max_length=100)
    loan_type: int = Field(..., description="1员工借款 2保证金 3集团拆借 4临时挂账 5押金")
    loan_direction: int = Field(..., description="1其他应收 2其他应付")
    project_fin_config_id: Optional[int] = Field(None, description="楼盘财务配置ID")
    loan_subject_id: int = Field(..., description="往来款对应会计科目ID")
    loan_date: date = Field(..., description="往来挂账日期")
    due_date: Optional[date] = Field(None, description="结清截止日期")
    loan_total_amt: Decimal = Field(..., description="往来含税总金额")
    loan_untax_amt: Decimal = Field(..., description="往来不含税金额")
    loan_tax_amt: Decimal = Field(0, description="往来对应税额")
    settle_amt: Decimal = Field(0, description="已结清金额")
    balance_amt: Decimal = Field(..., description="剩余挂账余额")
    loan_file_url: Optional[str] = Field(None, description="借款单、协议、收据附件", max_length=1024)
    remark: Optional[str] = Field(None, description="往来款业务备注")
    create_user_id: int = Field(..., description="台账制单人ID")
    loan_no: Optional[str] = Field(None, description="往来款单号（系统自动生成）", max_length=64)


class OtherLoanUpdate(BaseModel):
    """更新其他往来款台账请求模型"""
    project_id: Optional[int] = Field(None, description="归属楼盘ID")
    project_name: Optional[str] = Field(None, description="楼盘名称冗余", max_length=128)
    loan_counterparty_type: Optional[int] = Field(None, description="对方主体类型")
    counterparty_name: Optional[str] = Field(None, description="对方名称冗余", max_length=100)
    counterparty_dept: Optional[str] = Field(None, description="对方部门/所属单位", max_length=100)
    loan_type: Optional[int] = Field(None, description="往来类型")
    loan_direction: Optional[int] = Field(None, description="往来方向")
    loan_subject_id: Optional[int] = Field(None, description="往来款对应会计科目ID")
    due_date: Optional[date] = Field(None, description="结清截止日期")
    settle_amt: Optional[Decimal] = Field(None, description="已结清金额")
    balance_amt: Optional[Decimal] = Field(None, description="剩余挂账余额")
    loan_status: Optional[int] = Field(None, description="1挂账中 2部分结清 3全额结清 4作废红冲")
    settle_time: Optional[datetime] = Field(None, description="最终结清时间")
    relate_flow_id: Optional[int] = Field(None, description="关联银行流水ID")
    voucher_no: Optional[str] = Field(None, description="往来挂账凭证编号", max_length=64)
    settle_voucher_no: Optional[str] = Field(None, description="结清冲销凭证编号", max_length=64)
    loan_file_url: Optional[str] = Field(None, description="借款单、协议、收据附件", max_length=1024)
    reconcile_remark: Optional[str] = Field(None, description="往来对账差异、结清说明")
    remark: Optional[str] = Field(None, description="往来款业务备注")


class OtherLoanResponse(ORMBaseModel):
    """其他往来款台账响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    loan_no: str
    project_id: Optional[int]
    project_name: Optional[str]
    loan_counterparty_type: int
    counterparty_id: int
    counterparty_name: str
    counterparty_dept: Optional[str]
    loan_type: int
    loan_direction: int
    project_fin_config_id: Optional[int]
    loan_subject_id: int
    loan_date: date
    due_date: Optional[date]
    loan_total_amt: Decimal
    loan_untax_amt: Decimal
    loan_tax_amt: Decimal
    settle_amt: Decimal
    balance_amt: Decimal
    loan_status: int
    settle_time: Optional[datetime]
    relate_flow_id: Optional[int]
    voucher_no: Optional[str]
    settle_voucher_no: Optional[str]
    loan_file_url: Optional[str]
    reconcile_remark: Optional[str]
    remark: Optional[str]
    create_user_id: int
    version: int
    is_del: int
    create_time: datetime
    update_time: datetime

"""
房地产SaaS销售管理系统 - 认购签约交易模块数据模型
"""

from pydantic import BaseModel, Field\nfrom common.schemas.response import ORMBaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ========== 认购管理模型 ==========

class SubscribeCreate(BaseModel):
    """创建认购单请求模型"""
    customer_id: int = Field(..., description="客户ID")
    house_id: int = Field(..., description="房源ID")
    subscribe_amount: Decimal = Field(..., description="认购金额", ge=0)
    deposit_amount: Decimal = Field(..., description="定金金额", ge=0)
    discount_amount: Optional[Decimal] = Field(Decimal('0'), description="优惠金额", ge=0)
    subscribe_date: Optional[str] = Field(None, description="认购日期")
    sign_user_id: Optional[int] = Field(None, description="签约人ID")
    remark: Optional[str] = Field(None, description="备注")


class SubscribeUpdate(BaseModel):
    """更新认购单请求模型"""
    subscribe_amount: Optional[Decimal] = Field(None, description="认购金额", ge=0)
    deposit_amount: Optional[Decimal] = Field(None, description="定金金额", ge=0)
    discount_amount: Optional[Decimal] = Field(None, description="优惠金额", ge=0)
    sign_user_id: Optional[int] = Field(None, description="签约人ID")
    remark: Optional[str] = Field(None, description="备注")


class SubscribeResponse(ORMBaseModel):
    """认购单响应模型"""
    subscribe_id: int
    subscribe_no: str
    customer_id: int
    customer_name: str
    customer_mobile: str
    project_id: int
    project_name: str
    house_id: int
    house_code: str
    house_name: str
    subscribe_amount: Decimal
    deposit_amount: Decimal
    discount_amount: Optional[Decimal]
    subscribe_date: Optional[datetime]
    subscribe_status: int
    sign_user_id: Optional[int]
    sign_user_name: Optional[str]
    cancel_reason: Optional[str]
    cancel_time: Optional[datetime]
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]


class SubscribeCancelRequest(BaseModel):
    """取消认购单请求模型"""
    subscribe_id: int = Field(..., description="认购单ID")
    cancel_reason: str = Field(..., description="取消原因")


# ========== 签约管理模型 ==========

class ContractCreate(BaseModel):
    """创建签约合同请求模型"""
    subscribe_id: int = Field(..., description="认购单ID")
    contract_no: str = Field(..., description="合同编号", max_length=50)
    contract_amount: Decimal = Field(..., description="签约金额", ge=0)
    contract_date: str = Field(..., description="签约日期")
    contract_type: Optional[str] = Field("商品房买卖合同", description="合同类型")
    payment_method: Optional[str] = Field("按揭", description="付款方式（一次性/按揭/分期）")
    sale_user_id: Optional[int] = Field(None, description="销售ID")
    remark: Optional[str] = Field(None, description="备注")


class ContractUpdate(BaseModel):
    """更新签约合同请求模型"""
    contract_amount: Optional[Decimal] = Field(None, description="签约金额", ge=0)
    contract_date: Optional[str] = Field(None, description="签约日期")
    payment_method: Optional[str] = Field(None, description="付款方式")
    sale_user_id: Optional[int] = Field(None, description="销售ID")
    remark: Optional[str] = Field(None, description="备注")


class ContractResponse(ORMBaseModel):
    """签约合同响应模型"""
    contract_id: int
    contract_no: str
    subscribe_id: int
    customer_id: int
    customer_name: str
    customer_mobile: str
    project_id: int
    project_name: str
    house_id: int
    house_code: str
    house_name: str
    contract_amount: Decimal
    contract_date: Optional[datetime]
    contract_type: Optional[str]
    contract_status: int
    payment_method: Optional[str]
    sale_user_id: Optional[int]
    sale_user_name: Optional[str]
    record_status: int
    record_date: Optional[datetime]
    record_user_id: Optional[int]
    complete_status: int
    complete_date: Optional[datetime]
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]


class ContractRecordRequest(BaseModel):
    """合同备案请求模型"""
    contract_id: int = Field(..., description="合同ID")
    record_date: str = Field(..., description="备案日期")


# ========== 回款管理模型 ==========

class PaymentCreate(BaseModel):
    """创建回款记录请求模型"""
    contract_id: int = Field(..., description="合同ID")
    payment_type: str = Field(..., description="回款类型（首付/按揭/尾款）")
    payment_amount: Decimal = Field(..., description="回款金额", ge=0)
    plan_payment_date: str = Field(..., description="计划回款日期")
    payment_account: Optional[str] = Field(None, description="付款账户")
    remark: Optional[str] = Field(None, description="备注")


class PaymentUpdate(BaseModel):
    """更新回款记录请求模型"""
    payment_type: Optional[str] = Field(None, description="回款类型")
    payment_amount: Optional[Decimal] = Field(None, description="回款金额", ge=0)
    plan_payment_date: Optional[str] = Field(None, description="计划回款日期")
    payment_account: Optional[str] = Field(None, description="付款账户")
    remark: Optional[str] = Field(None, description="备注")


class PaymentResponse(ORMBaseModel):
    """回款记录响应模型"""
    payment_id: int
    payment_no: str
    contract_id: int
    contract_no: str
    customer_id: int
    customer_name: str
    payment_type: str
    payment_amount: Decimal
    plan_payment_date: Optional[datetime]
    actual_payment_date: Optional[datetime]
    payment_status: int
    payment_account: Optional[str]
    confirm_user_id: Optional[int]
    confirm_user_name: Optional[str]
    confirm_time: Optional[datetime]
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]


# ========== 贷款管理模型 ==========

class LoanCreate(BaseModel):
    """创建贷款记录请求模型"""
    contract_id: int = Field(..., description="合同ID")
    loan_bank: str = Field(..., description="贷款银行", max_length=100)
    loan_amount: Decimal = Field(..., description="贷款金额", ge=0)
    loan_rate: Optional[float] = Field(None, description="贷款利率")
    loan_months: Optional[int] = Field(None, description="贷款期限（月）")
    loan_type: Optional[str] = Field("商业贷款", description="贷款类型（商业贷款/公积金贷款/组合贷款）")
    loan_status: Optional[int] = Field(1, description="贷款状态（1：申请中 2：已批贷 3：已放款 4：已结清）")
    remark: Optional[str] = Field(None, description="备注")


class LoanUpdate(BaseModel):
    """更新贷款记录请求模型"""
    loan_bank: Optional[str] = Field(None, description="贷款银行", max_length=100)
    loan_amount: Optional[Decimal] = Field(None, description="贷款金额", ge=0)
    loan_rate: Optional[float] = Field(None, description="贷款利率")
    loan_months: Optional[int] = Field(None, description="贷款期限（月）")
    loan_type: Optional[str] = Field(None, description="贷款类型")
    loan_status: Optional[int] = Field(None, description="贷款状态")
    remark: Optional[str] = Field(None, description="备注")


class LoanResponse(ORMBaseModel):
    """贷款记录响应模型"""
    loan_id: int
    contract_id: int
    contract_no: str
    customer_id: int
    customer_name: str
    loan_bank: str
    loan_amount: Decimal
    loan_rate: Optional[float]
    loan_months: Optional[int]
    loan_type: Optional[str]
    loan_status: int
    approve_date: Optional[datetime]
    payment_date: Optional[datetime]
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]


# ========== 发票管理模型 ==========

class ReceiptCreate(BaseModel):
    """创建发票记录请求模型"""
    contract_id: int = Field(..., description="合同ID")
    receipt_type: str = Field(..., description="发票类型（普通发票/专用发票）")
    receipt_title: str = Field(..., description="发票抬头", max_length=200)
    receipt_amount: Decimal = Field(..., description="发票金额", ge=0)
    receipt_tax_no: Optional[str] = Field(None, description="税号", max_length=50)
    receipt_address: Optional[str] = Field(None, description="地址", max_length=200)
    receipt_phone: Optional[str] = Field(None, description="电话", max_length=20)
    receipt_status: Optional[int] = Field(1, description="发票状态（1：待开票 2：已开票 3：已作废）")
    remark: Optional[str] = Field(None, description="备注")


class ReceiptUpdate(BaseModel):
    """更新发票记录请求模型"""
    receipt_type: Optional[str] = Field(None, description="发票类型")
    receipt_title: Optional[str] = Field(None, description="发票抬头", max_length=200)
    receipt_amount: Optional[Decimal] = Field(None, description="发票金额", ge=0)
    receipt_tax_no: Optional[str] = Field(None, description="税号", max_length=50)
    receipt_address: Optional[str] = Field(None, description="地址", max_length=200)
    receipt_phone: Optional[str] = Field(None, description="电话", max_length=20)
    receipt_status: Optional[int] = Field(None, description="发票状态")
    remark: Optional[str] = Field(None, description="备注")


class ReceiptResponse(ORMBaseModel):
    """发票记录响应模型"""
    receipt_id: int
    receipt_no: str
    contract_id: int
    contract_no: str
    customer_id: int
    customer_name: str
    receipt_type: str
    receipt_title: str
    receipt_amount: Decimal
    receipt_tax_no: Optional[str]
    receipt_address: Optional[str]
    receipt_phone: Optional[str]
    receipt_status: int
    invoice_date: Optional[datetime]
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]


# ========== 交易综合查询模型 ==========

class TransactionListResponse(ORMBaseModel):
    """交易综合列表响应模型"""
    total: int
    page: int
    page_size: int
    pages: int
    data: List[dict]


class SubscribeDetailResponse(ORMBaseModel):
    """认购单详情响应模型"""
    subscribe_id: int
    subscribe_no: str
    customer: dict
    project: dict
    house: dict
    subscribe_amount: Decimal
    deposit_amount: Decimal
    discount_amount: Optional[Decimal]
    subscribe_date: Optional[datetime]
    subscribe_status: int
    sign_user: Optional[dict]
    cancel_reason: Optional[str]
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]


class ContractDetailResponse(ORMBaseModel):
    """合同详情响应模型"""
    contract_id: int
    contract_no: str
    subscribe: Optional[dict]
    customer: dict
    project: dict
    house: dict
    contract_amount: Decimal
    contract_date: Optional[datetime]
    contract_type: Optional[str]
    contract_status: int
    payment_method: Optional[str]
    sale_user: Optional[dict]
    record_status: int
    record_date: Optional[datetime]
    complete_status: int
    complete_date: Optional[datetime]
    remark: Optional[str]
    payments: List[dict]
    loans: List[dict]
    receipts: List[dict]
    create_time: Optional[datetime]
    update_time: Optional[datetime]
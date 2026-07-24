"""
房地产SaaS财务管理系统 - 票据税务合规模块数据模型
用于API接口的请求和响应数据验证
"""

from pydantic import BaseModel, Field\nfrom common.schemas.response import ORMBaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ========== 蓝字发票 ==========

class InvoiceCreate(BaseModel):
    """创建蓝字发票请求模型"""
    invoice_no: Optional[str] = Field(None, description="发票编号，不传则自动生成", max_length=50)
    order_id: int = Field(..., description="销售订单ID")
    customer_id: int = Field(..., description="客户ID")
    project_id: int = Field(..., description="楼盘ID")
    invoice_type: str = Field(..., description="发票类型（增值税普通发票/增值税专用发票）", max_length=50)
    invoice_amount: Decimal = Field(..., description="发票金额")
    tax_amount: Decimal = Field(..., description="税额")
    total_amount: Decimal = Field(..., description="价税合计")
    tax_rate_id: int = Field(..., description="税率ID")
    invoice_date: datetime = Field(..., description="开票日期")
    customer_name: str = Field(..., description="客户名称", max_length=100)
    customer_tax_no: Optional[str] = Field(None, description="客户税号", max_length=50)
    customer_address: Optional[str] = Field(None, description="客户地址", max_length=200)
    customer_phone: Optional[str] = Field(None, description="客户电话", max_length=20)
    remark: Optional[str] = Field(None, description="备注")


class InvoiceUpdate(BaseModel):
    """更新蓝字发票请求模型"""
    invoice_amount: Optional[Decimal] = Field(None, description="发票金额")
    tax_amount: Optional[Decimal] = Field(None, description="税额")
    total_amount: Optional[Decimal] = Field(None, description="价税合计")
    customer_name: Optional[str] = Field(None, description="客户名称", max_length=100)
    customer_tax_no: Optional[str] = Field(None, description="客户税号", max_length=50)
    customer_address: Optional[str] = Field(None, description="客户地址", max_length=200)
    customer_phone: Optional[str] = Field(None, description="客户电话", max_length=20)
    remark: Optional[str] = Field(None, description="备注")


class InvoiceResponse(ORMBaseModel):
    """蓝字发票响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    invoice_no: str
    invoice_code: str
    invoice_num: str
    project_id: int
    contract_id: int
    house_id: int
    customer_id: int
    seller_name: str
    seller_credit_code: str
    buyer_name: str
    buyer_credit_code: Optional[str]
    buyer_phone: Optional[str]
    buyer_address: Optional[str]
    invoice_type: int
    invoice_amount: Decimal
    tax_amount: Decimal
    ex_tax_amount: Decimal
    tax_rate: Decimal
    invoice_item: str
    invoice_status: int
    red_count: int = Field(0, description="已红冲次数")
    invoice_time: datetime
    make_user_id: int = Field(description="开票操作员ID")
    invoice_file_url: Optional[str] = Field(None, description="电子发票链接")
    remark: Optional[str]
    version: int = Field(0, description="乐观锁版本号")
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 红字发票 ==========

class InvoiceRedCreate(BaseModel):
    """创建红字发票请求模型"""
    red_no: Optional[str] = Field(None, description="红字发票编号，不传则自动生成", max_length=50)
    original_invoice_id: int = Field(..., description="原蓝字发票ID")
    red_reason: str = Field(..., description="冲销原因", max_length=200)
    invoice_amount: Decimal = Field(..., description="冲销金额")
    tax_amount: Decimal = Field(..., description="冲销税额")
    total_amount: Decimal = Field(..., description="价税合计")


class InvoiceRedUpdate(BaseModel):
    """更新红字发票请求模型"""
    red_reason: Optional[str] = Field(None, description="冲销原因", max_length=200)
    invoice_amount: Optional[Decimal] = Field(None, description="冲销金额")
    tax_amount: Optional[Decimal] = Field(None, description="冲销税额")
    total_amount: Optional[Decimal] = Field(None, description="价税合计")


class InvoiceRedResponse(ORMBaseModel):
    """红字发票响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    red_invoice_no: str
    source_invoice_id: int
    invoice_code: str
    invoice_num: str
    red_invoice_time: datetime
    red_amount: Decimal
    red_tax: Decimal
    red_reason: int
    remark: str
    red_file_url: Optional[str] = Field(None, description="红字发票附件")
    make_user_id: int = Field(description="操作人ID")
    version: int = Field(0, description="乐观锁版本号")
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 内部收据 ==========

class ReceiptCreate(BaseModel):
    """创建内部收据请求模型"""
    receipt_no: Optional[str] = Field(None, description="收据编号，不传则自动生成", max_length=50)
    order_id: int = Field(..., description="销售订单ID")
    customer_id: int = Field(..., description="客户ID")
    receipt_amount: Decimal = Field(..., description="收据金额")
    receipt_type: str = Field(..., description="收据类型", max_length=50)
    payer_name: str = Field(..., description="付款人", max_length=100)
    payer_phone: Optional[str] = Field(None, description="付款人电话", max_length=20)
    remark: Optional[str] = Field(None, description="备注")


class ReceiptUpdate(BaseModel):
    """更新内部收据请求模型"""
    receipt_amount: Optional[Decimal] = Field(None, description="收据金额")
    payer_name: Optional[str] = Field(None, description="付款人", max_length=100)
    payer_phone: Optional[str] = Field(None, description="付款人电话", max_length=20)
    remark: Optional[str] = Field(None, description="备注")


class ReceiptResponse(ORMBaseModel):
    """内部收据响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    receipt_no: str
    project_id: int
    customer_id: int
    receipt_type: int
    receipt_amount: Decimal
    receipt_content: str
    receipt_status: int
    receipt_time: datetime
    make_user_id: int = Field(description="开据人ID")
    receipt_file_url: Optional[str] = Field(None, description="收据附件链接")
    remark: Optional[str]
    version: int = Field(0, description="乐观锁版本号")
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 维修基金台账 ==========

class MaintenanceFundCreate(BaseModel):
    """创建维修基金台账请求模型"""
    fund_no: Optional[str] = Field(None, description="维修基金单据编号，不传则自动生成", max_length=64)
    order_id: int = Field(..., description="销售订单ID")
    customer_id: int = Field(..., description="客户ID")
    project_id: int = Field(..., description="楼盘ID")
    house_id: int = Field(..., description="房源ID")
    house_area: Decimal = Field(..., description="房屋面积")
    unit_price: Decimal = Field(..., description="单价")
    total_amount: Decimal = Field(..., description="总金额")
    pay_status: str = Field("未缴纳", description="缴纳状态", max_length=20)
    remark: Optional[str] = Field(None, description="备注")


class MaintenanceFundUpdate(BaseModel):
    """更新维修基金台账请求模型"""
    pay_status: Optional[str] = Field(None, description="缴纳状态", max_length=20)
    remark: Optional[str] = Field(None, description="备注")


class MaintenanceFundResponse(ORMBaseModel):
    """维修基金台账响应模型"""
    model_config = {'from_attributes': True}
    id: int
    tenant: str
    fund_no: str
    project_id: int
    house_id: int
    contract_id: int
    customer_id: int
    fund_amount: Decimal
    pay_status: int
    pay_time: Optional[datetime]
    pay_way: Optional[int]
    transfer_time: Optional[datetime]
    remark: Optional[str]
    version: int = Field(0, description="乐观锁版本号")
    is_del: int
    create_time: datetime
    update_time: datetime


# ========== 税务申报 ==========

class TaxDeclareCreate(BaseModel):
    """创建税务申报请求模型"""
    declare_no: Optional[str] = Field(None, description="申报编号，不传则自动生成", max_length=50)
    project_id: int = Field(..., description="楼盘ID")
    declare_month: str = Field(..., description="申报月份", max_length=20)
    declare_type: str = Field(..., description="申报类型", max_length=50)
    invoice_total: Decimal = Field(..., description="开票总额")
    tax_total: Decimal = Field(..., description="税额总额")
    declare_amount: Decimal = Field(..., description="申报金额")
    declare_date: datetime = Field(..., description="申报日期")
    remark: Optional[str] = Field(None, description="备注")


class TaxDeclareUpdate(BaseModel):
    """更新税务申报请求模型"""
    invoice_total: Optional[Decimal] = Field(None, description="开票总额")
    tax_total: Optional[Decimal] = Field(None, description="税额总额")
    declare_amount: Optional[Decimal] = Field(None, description="申报金额")
    declare_date: Optional[datetime] = Field(None, description="申报日期")
    remark: Optional[str] = Field(None, description="备注")


class TaxDeclareResponse(ORMBaseModel):
    """税务申报响应模型"""
    model_config = {'from_attributes': True}
    id: int
    declare_no: str
    project_id: int
    project_name: Optional[str] = Field(None, description="楼盘名称")
    declare_month: str
    declare_type: str
    invoice_total: Decimal
    tax_total: Decimal
    declare_amount: Decimal
    declare_date: datetime
    declare_status: str
    remark: Optional[str]
    is_del: int
    create_time: datetime
    update_time: datetime
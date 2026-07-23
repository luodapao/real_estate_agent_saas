"""
房地产SaaS财务管理系统 - 票据税务合规模块服务层
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from ..dao import (
    FinInvoiceDAO,
    FinInvoiceRedDAO,
    FinReceiptDAO,
    FinMaintainFundDAO,
    FinTaxDeclareDAO,
)
from ..schemas.invoice_schemas import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceRedCreate,
    InvoiceRedUpdate,
    InvoiceRedResponse,
    ReceiptCreate,
    ReceiptUpdate,
    ReceiptResponse,
    MaintenanceFundCreate,
    MaintenanceFundUpdate,
    MaintenanceFundResponse,
    TaxDeclareCreate,
    TaxDeclareUpdate,
    TaxDeclareResponse,
)
from ..schemas.base_schemas import PageRequest, PageResponse


class InvoiceService:
    """票据税务合规模块服务类"""

    @staticmethod
    def _generate_doc_no(db: Session, tenant_id: int, prefix: str) -> str:
        """
        生成单据编号（私有方法）
        :param db: 数据库会话
        :param tenant_id: 租户ID
        :param prefix: 编号前缀（FP:发票, HF:红字发票, SJ:收据, WXJJ:维修基金, SB:申报）
        :return: 生成的单据编号
        """
        date_str = datetime.now().strftime("%Y%m%d")
        max_no = 0

        if prefix == "FP":
            result = db.execute(
                text("SELECT MAX(invoice_no) FROM fin_invoice WHERE tenant = :tenant AND invoice_no LIKE :pattern"),
                {"tenant": tenant_id, "pattern": f"{prefix}{date_str}%"}
            ).scalar()
        elif prefix == "HF":
            result = db.execute(
                text("SELECT MAX(red_invoice_no) FROM fin_invoice_red WHERE tenant = :tenant AND red_invoice_no LIKE :pattern"),
                {"tenant": tenant_id, "pattern": f"{prefix}{date_str}%"}
            ).scalar()
        elif prefix == "SJ":
            result = db.execute(
                text("SELECT MAX(receipt_no) FROM fin_receipt WHERE tenant = :tenant AND receipt_no LIKE :pattern"),
                {"tenant": tenant_id, "pattern": f"{prefix}{date_str}%"}
            ).scalar()
        elif prefix == "WXJJ":
            result = db.execute(
                text("SELECT MAX(fund_no) FROM fin_maintain_fund WHERE tenant = :tenant AND fund_no LIKE :pattern"),
                {"tenant": tenant_id, "pattern": f"{prefix}{date_str}%"}
            ).scalar()
        elif prefix == "SB":
            result = db.execute(
                text("SELECT MAX(declare_no) FROM fin_tax_declare WHERE tenant = :tenant AND declare_no LIKE :pattern"),
                {"tenant": tenant_id, "pattern": f"{prefix}{date_str}%"}
            ).scalar()

        if result:
            seq_str = result[-4:]
            max_no = int(seq_str) + 1

        seq_str = str(max_no).zfill(4)
        return f"{prefix}{date_str}{seq_str}"

    @staticmethod
    def create_invoice(db: Session, tenant_id: int, data: InvoiceCreate, create_user_id: int = 1) -> InvoiceResponse:
        """创建蓝字发票"""
        invoice_no = data.invoice_no or InvoiceService._generate_doc_no(db, tenant_id, "FP")
        invoice_type_map = {'增值税普通发票': 2, '增值税专用发票': 1}
        data_dict = {
            'invoice_no': invoice_no,
            'invoice_code': 'FP' + invoice_no,
            'invoice_num': invoice_no[-8:],
            'project_id': data.project_id,
            'contract_id': 1,
            'house_id': 1,
            'customer_id': data.customer_id,
            'seller_name': '测试销售方',
            'seller_credit_code': '911100001234567890',
            'buyer_name': data.customer_name,
            'buyer_credit_code': getattr(data, 'customer_tax_no', '') or '',
            'buyer_phone': getattr(data, 'customer_phone', '') or '',
            'buyer_address': getattr(data, 'customer_address', '') or '',
            'invoice_type': invoice_type_map.get(data.invoice_type, 2),
            'invoice_amount': data.invoice_amount,
            'tax_amount': data.tax_amount,
            'ex_tax_amount': data.total_amount - data.tax_amount,
            'tax_rate': 0.09,
            'invoice_item': '不动产销售',
            'invoice_time': data.invoice_date,
            'invoice_status': getattr(data, 'invoice_status', 1),
            'make_user_id': create_user_id,
            'remark': data.remark or '',
        }
        entity = FinInvoiceDAO.create(db, tenant_id, data_dict)
        return InvoiceResponse.from_orm(entity)

    @staticmethod
    def get_invoice(db: Session, tenant_id: int, id: int) -> Optional[InvoiceResponse]:
        """获取蓝字发票详情"""
        entity = FinInvoiceDAO.get_by_id(db, tenant_id, id)
        return InvoiceResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_invoice(db: Session, tenant_id: int, id: int, data: InvoiceUpdate) -> Optional[InvoiceResponse]:
        """更新蓝字发票"""
        entity = FinInvoiceDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return InvoiceResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_invoice(db: Session, tenant_id: int, id: int) -> bool:
        """删除蓝字发票"""
        return FinInvoiceDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_invoices(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[InvoiceResponse]:
        """分页查询蓝字发票列表"""
        total, items = FinInvoiceDAO.list(db, tenant_id, page_request.model_dump())
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[InvoiceResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_invoice_red(db: Session, tenant_id: int, data: InvoiceRedCreate, create_user_id: int = 1) -> InvoiceRedResponse:
        """创建红字发票"""
        red_no = data.red_no or InvoiceService._generate_doc_no(db, tenant_id, "HF")
        red_reason_map = {'开票错误': 1, '退房退款': 2, '金额调整': 3, '其他': 4}
        data_dict = {
            'red_invoice_no': red_no,
            'source_invoice_id': data.original_invoice_id,
            'invoice_code': 'HF' + red_no,
            'invoice_num': red_no[-8:],
            'red_invoice_time': datetime.now(),
            'red_amount': data.invoice_amount,
            'red_tax': data.tax_amount,
            'red_reason': red_reason_map.get(data.red_reason, 4),
            'remark': data.red_reason,
            'make_user_id': create_user_id,
        }
        entity = FinInvoiceRedDAO.create(db, tenant_id, data_dict)
        return InvoiceRedResponse.from_orm(entity)

    @staticmethod
    def get_invoice_red(db: Session, tenant_id: int, id: int) -> Optional[InvoiceRedResponse]:
        """获取红字发票详情"""
        entity = FinInvoiceRedDAO.get_by_id(db, tenant_id, id)
        return InvoiceRedResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_invoice_red(db: Session, tenant_id: int, id: int, data: InvoiceRedUpdate) -> Optional[InvoiceRedResponse]:
        """更新红字发票"""
        entity = FinInvoiceRedDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return InvoiceRedResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_invoice_red(db: Session, tenant_id: int, id: int) -> bool:
        """删除红字发票"""
        return FinInvoiceRedDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_invoice_reds(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[InvoiceRedResponse]:
        """分页查询红字发票列表"""
        total, items = FinInvoiceRedDAO.list(db, tenant_id, page_request.model_dump())
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[InvoiceRedResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_receipt(db: Session, tenant_id: int, data: ReceiptCreate, create_user_id: int = 1) -> ReceiptResponse:
        """创建内部收据"""
        receipt_no = InvoiceService._generate_doc_no(db, tenant_id, "SJ")
        receipt_type_map = {'定金': 1, '首付': 2, '分期': 3, '其他': 4}
        data_dict = {
            'receipt_no': receipt_no,
            'project_id': 1,
            'customer_id': data.customer_id,
            'receipt_type': receipt_type_map.get(data.receipt_type, 4),
            'receipt_amount': data.receipt_amount,
            'receipt_content': data.receipt_type + '收款',
            'receipt_time': datetime.now(),
            'make_user_id': create_user_id,
            'remark': data.remark or '',
        }
        entity = FinReceiptDAO.create(db, tenant_id, data_dict)
        return ReceiptResponse.from_orm(entity)

    @staticmethod
    def get_receipt(db: Session, tenant_id: int, id: int) -> Optional[ReceiptResponse]:
        """获取内部收据详情"""
        entity = FinReceiptDAO.get_by_id(db, tenant_id, id)
        return ReceiptResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_receipt(db: Session, tenant_id: int, id: int, data: ReceiptUpdate) -> Optional[ReceiptResponse]:
        """更新内部收据"""
        entity = FinReceiptDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return ReceiptResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_receipt(db: Session, tenant_id: int, id: int) -> bool:
        """删除内部收据"""
        return FinReceiptDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_receipts(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[ReceiptResponse]:
        """分页查询内部收据列表"""
        total, items = FinReceiptDAO.list(db, tenant_id, page_request.model_dump())
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[ReceiptResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_maintenance_fund(db: Session, tenant_id: int, data: MaintenanceFundCreate, create_user_id: int = 1) -> MaintenanceFundResponse:
        """创建维修基金台账"""
        fund_no = InvoiceService._generate_doc_no(db, tenant_id, "WXJJ")
        pay_status_map = {'未缴纳': 1, '已缴纳': 2, '已上缴': 3}
        data_dict = {
            'fund_no': fund_no,
            'project_id': data.project_id,
            'house_id': data.house_id,
            'contract_id': 1,
            'customer_id': data.customer_id,
            'fund_amount': data.total_amount,
            'pay_status': pay_status_map.get(data.pay_status, 1),
            'remark': data.remark or '',
        }
        entity = FinMaintainFundDAO.create(db, tenant_id, data_dict)
        return MaintenanceFundResponse.from_orm(entity)

    @staticmethod
    def get_maintenance_fund(db: Session, tenant_id: int, id: int) -> Optional[MaintenanceFundResponse]:
        """获取维修基金台账详情"""
        entity = FinMaintainFundDAO.get_by_id(db, tenant_id, id)
        return MaintenanceFundResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_maintenance_fund(db: Session, tenant_id: int, id: int, data: MaintenanceFundUpdate) -> Optional[MaintenanceFundResponse]:
        """更新维修基金台账"""
        entity = FinMaintainFundDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return MaintenanceFundResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_maintenance_fund(db: Session, tenant_id: int, id: int) -> bool:
        """删除维修基金台账"""
        return FinMaintainFundDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_maintenance_funds(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[MaintenanceFundResponse]:
        """分页查询维修基金台账列表"""
        total, items = FinMaintainFundDAO.list(db, tenant_id, page_request.model_dump())
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[MaintenanceFundResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def create_tax_declare(db: Session, tenant_id: int, data: TaxDeclareCreate, create_user_id: int = 1) -> TaxDeclareResponse:
        """创建税务申报记录"""
        data_dict = data.model_dump()
        if not data_dict.get('declare_no'):
            data_dict['declare_no'] = InvoiceService._generate_doc_no(db, tenant_id, "SB")
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinTaxDeclareDAO.create(db, tenant_id, data_dict)
        return TaxDeclareResponse.from_orm(entity)

    @staticmethod
    def get_tax_declare(db: Session, tenant_id: int, id: int) -> Optional[TaxDeclareResponse]:
        """获取税务申报记录详情"""
        entity = FinTaxDeclareDAO.get_by_id(db, tenant_id, id)
        return TaxDeclareResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_tax_declare(db: Session, tenant_id: int, id: int, data: TaxDeclareUpdate) -> Optional[TaxDeclareResponse]:
        """更新税务申报记录"""
        entity = FinTaxDeclareDAO.update(db, tenant_id, id, data.model_dump(exclude_unset=True))
        return TaxDeclareResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_tax_declare(db: Session, tenant_id: int, id: int) -> bool:
        """删除税务申报记录"""
        return FinTaxDeclareDAO.delete(db, tenant_id, id)

    @staticmethod
    def list_tax_declares(db: Session, tenant_id: int, page_request: PageRequest) -> PageResponse[TaxDeclareResponse]:
        """分页查询税务申报记录列表"""
        total, items = FinTaxDeclareDAO.list(db, tenant_id, page_request.model_dump())
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[TaxDeclareResponse.from_orm(item) for item in items]
        )

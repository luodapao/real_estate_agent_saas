"""
房地产SaaS财务管理系统 - 渠道佣金&内部提成支付模块服务层
"""

from sqlalchemy.orm import Session
from typing import Optional, Tuple, List
from datetime import datetime

from ..model.finance_models import (
    FinCommissionPay, FinCommissionDeduct, 
    FinSalesCommission, FinSalesBonusPay
)
from ..dao.finance_dao_ext import (
    FinCommissionPayDAO, FinCommissionDeductDAO, 
    FinSalesCommissionDAO, FinSalesBonusPayDAO
)
from ..schemas.commission_schemas import (
    CommissionPayCreate, CommissionPayUpdate, CommissionPayResponse,
    CommissionDeductCreate, CommissionDeductUpdate, CommissionDeductResponse,
    SalesCommissionCreate, SalesCommissionUpdate, SalesCommissionResponse,
    SalesBonusPayCreate, SalesBonusPayUpdate, SalesBonusPayResponse
)
from ..schemas.base_schemas import PageRequest, PageResponse


def generate_doc_no(db: Session, tenant_id: str, prefix: str) -> str:
    """
    生成单据编号（公共方法）
    :param db: 数据库会话
    :param tenant_id: 租户ID
    :param prefix: 编号前缀（YJFK:佣金付款, YJKF:佣金扣罚, YJ:佣金明细, TC:提成付款）
    :return: 生成的单据编号
    """
    date_str = datetime.now().strftime("%Y%m%d")
    max_no = 0

    if prefix == "YJFK":
        result = db.execute(
            "SELECT MAX(pay_no) FROM fin_commission_pay WHERE tenant = :tenant_id AND pay_no LIKE :pattern",
            {"tenant_id": tenant_id, "pattern": f"{prefix}{date_str}%"}
        ).scalar()
    elif prefix == "YJKF":
        result = db.execute(
            "SELECT MAX(deduct_no) FROM fin_commission_deduct WHERE tenant = :tenant_id AND deduct_no LIKE :pattern",
            {"tenant_id": tenant_id, "pattern": f"{prefix}{date_str}%"}
        ).scalar()
    elif prefix == "TC":
        result = db.execute(
            "SELECT MAX(pay_no) FROM fin_sales_bonus_pay WHERE tenant = :tenant_id AND pay_no LIKE :pattern",
            {"tenant_id": tenant_id, "pattern": f"{prefix}{date_str}%"}
        ).scalar()

    if result:
        seq_str = result[-4:]
        max_no = int(seq_str) + 1

    seq_str = str(max_no).zfill(4)
    return f"{prefix}{date_str}{seq_str}"


# ========== 佣金付款单服务 ==========

class CommissionPayService:
    """佣金付款单服务类"""

    @staticmethod
    def create(db: Session, tenant_id: str, data: CommissionPayCreate, create_user_id: int = 1) -> CommissionPayResponse:
        """创建佣金付款单"""
        pay_data = data.model_dump()
        if not pay_data.get('pay_no'):
            pay_data['pay_no'] = generate_doc_no(db, tenant_id, "YJFK")
        pay_data.update({
            "tenant": tenant_id,
            "audit_status": 1,
            "pay_status": 1,
            "is_del": 0,
            "version": 1,
            "create_user_id": create_user_id,
            "update_user_id": create_user_id,
            "create_time": datetime.now(),
            "update_time": datetime.now()
        })
        entity = FinCommissionPayDAO.create(db, pay_data)
        return CommissionPayResponse.from_orm(entity)

    @staticmethod
    def get_by_id(db: Session, tenant_id: str, pay_id: int) -> Optional[CommissionPayResponse]:
        """根据ID获取佣金付款单"""
        entity = FinCommissionPayDAO.get_by_id(db, tenant_id, pay_id)
        return CommissionPayResponse.from_orm(entity) if entity else None

    @staticmethod
    def get_by_pay_no(db: Session, tenant_id: str, pay_no: str) -> Optional[CommissionPayResponse]:
        """根据付款单号获取佣金付款单"""
        entity = FinCommissionPayDAO.get_by_pay_no(db, tenant_id, pay_no)
        return CommissionPayResponse.from_orm(entity) if entity else None

    @staticmethod
    def list(db: Session, tenant_id: str, page_request: PageRequest, 
             project_id: Optional[int] = None, channel_id: Optional[int] = None, 
             audit_status: Optional[int] = None, pay_status: Optional[int] = None) -> PageResponse[CommissionPayResponse]:
        """分页查询佣金付款单列表"""
        filters = {}
        if project_id:
            filters["project_id"] = project_id
        if channel_id:
            filters["channel_id"] = channel_id
        if audit_status:
            filters["audit_status"] = audit_status
        if pay_status:
            filters["pay_status"] = pay_status
        
        total, items = FinCommissionPayDAO.list(db, tenant_id, page_request.page, page_request.size, **filters)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.size,
            items=[CommissionPayResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def update(db: Session, tenant_id: str, pay_id: int, data: CommissionPayUpdate) -> Optional[CommissionPayResponse]:
        """更新佣金付款单"""
        update_data = {}
        if data.building_scope is not None:
            update_data["building_scope"] = data.building_scope
        if data.refund_deduct_flag is not None:
            update_data["refund_deduct_flag"] = data.refund_deduct_flag
        if data.deduct_amount is not None:
            update_data["deduct_amount"] = data.deduct_amount
        if data.actual_pay_untax is not None:
            update_data["actual_pay_untax"] = data.actual_pay_untax
        if data.actual_pay_tax is not None:
            update_data["actual_pay_tax"] = data.actual_pay_tax
        if data.actual_pay_amount is not None:
            update_data["actual_pay_amount"] = data.actual_pay_amount
        if data.audit_status is not None:
            update_data["audit_status"] = data.audit_status
        if data.pay_status is not None:
            update_data["pay_status"] = data.pay_status
        if data.pay_time is not None:
            update_data["pay_time"] = data.pay_time
        if data.audit_user_id is not None:
            update_data["audit_user_id"] = data.audit_user_id
        if data.pay_user_id is not None:
            update_data["pay_user_id"] = data.pay_user_id
        if data.bank_flow_id is not None:
            update_data["bank_flow_id"] = data.bank_flow_id
        if data.bank_flow_no is not None:
            update_data["bank_flow_no"] = data.bank_flow_no
        if data.voucher_no is not None:
            update_data["voucher_no"] = data.voucher_no
        if data.pay_file_url is not None:
            update_data["pay_file_url"] = data.pay_file_url
        if data.remark is not None:
            update_data["remark"] = data.remark
        
        if update_data:
            update_data["update_time"] = datetime.now()
            entity = FinCommissionPayDAO.update(db, tenant_id, pay_id, update_data)
            return CommissionPayResponse.from_orm(entity) if entity else None
        return CommissionPayService.get_by_id(db, tenant_id, pay_id)

    @staticmethod
    def delete(db: Session, tenant_id: str, pay_id: int) -> bool:
        """软删除佣金付款单"""
        return FinCommissionPayDAO.delete(db, tenant_id, pay_id)


# ========== 佣金扣罚记录服务 ==========

class CommissionDeductService:
    """佣金扣罚记录服务类"""

    @staticmethod
    def create(db: Session, tenant_id: str, data: CommissionDeductCreate, create_user_id: int = 1) -> CommissionDeductResponse:
        """创建佣金扣罚记录"""
        deduct_data = data.model_dump()
        if not deduct_data.get('deduct_no'):
            deduct_data['deduct_no'] = generate_doc_no(db, tenant_id, "YJKF")
        deduct_data.update({
            "tenant": tenant_id,
            "deduct_status": 1,
            "is_del": 0,
            "version": 1,
            "create_user_id": create_user_id,
            "update_user_id": create_user_id,
            "create_time": datetime.now(),
            "update_time": datetime.now()
        })
        entity = FinCommissionDeductDAO.create(db, deduct_data)
        return CommissionDeductResponse.from_orm(entity)

    @staticmethod
    def get_by_id(db: Session, tenant_id: str, deduct_id: int) -> Optional[CommissionDeductResponse]:
        """根据ID获取佣金扣罚记录"""
        entity = FinCommissionDeductDAO.get_by_id(db, tenant_id, deduct_id)
        return CommissionDeductResponse.from_orm(entity) if entity else None

    @staticmethod
    def get_by_pay_id(db: Session, tenant_id: str, pay_id: int) -> List[CommissionDeductResponse]:
        """根据付款单ID获取扣罚记录列表"""
        items = FinCommissionDeductDAO.get_by_pay_id(db, tenant_id, pay_id)
        return [CommissionDeductResponse.from_orm(item) for item in items]

    @staticmethod
    def list(db: Session, tenant_id: str, page_request: PageRequest,
             project_id: Optional[int] = None, channel_id: Optional[int] = None, 
             deduct_type: Optional[int] = None, deduct_status: Optional[int] = None) -> PageResponse[CommissionDeductResponse]:
        """分页查询佣金扣罚记录列表"""
        filters = {}
        if project_id:
            filters["project_id"] = project_id
        if channel_id:
            filters["channel_id"] = channel_id
        if deduct_type:
            filters["deduct_type"] = deduct_type
        if deduct_status:
            filters["deduct_status"] = deduct_status
        
        total, items = FinCommissionDeductDAO.list(db, tenant_id, page_request.page, page_request.size, **filters)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.size,
            items=[CommissionDeductResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def update(db: Session, tenant_id: str, deduct_id: int, data: CommissionDeductUpdate) -> Optional[CommissionDeductResponse]:
        """更新佣金扣罚记录"""
        update_data = {}
        if data.commission_pay_id is not None:
            update_data["commission_pay_id"] = data.commission_pay_id
        if data.deduct_status is not None:
            update_data["deduct_status"] = data.deduct_status
        if data.remark is not None:
            update_data["remark"] = data.remark
        
        if update_data:
            update_data["update_time"] = datetime.now()
            entity = FinCommissionDeductDAO.update(db, tenant_id, deduct_id, update_data)
            return CommissionDeductResponse.from_orm(entity) if entity else None
        return CommissionDeductService.get_by_id(db, tenant_id, deduct_id)

    @staticmethod
    def delete(db: Session, tenant_id: str, deduct_id: int) -> bool:
        """软删除佣金扣罚记录"""
        return FinCommissionDeductDAO.delete(db, tenant_id, deduct_id)


# ========== 销售提成支付明细服务 ==========

class SalesCommissionService:
    """销售提成支付明细服务类"""

    @staticmethod
    def create(db: Session, tenant_id: str, data: SalesCommissionCreate, create_user_id: int = 1) -> SalesCommissionResponse:
        """创建销售提成支付明细"""
        commission_data = data.model_dump()
        commission_data.update({
            "tenant": tenant_id,
            "commission_status": 1,
            "is_del": 0,
            "version": 1,
            "create_user_id": create_user_id,
            "update_user_id": create_user_id,
            "create_time": datetime.now(),
            "update_time": datetime.now()
        })
        entity = FinSalesCommissionDAO.create(db, commission_data)
        return SalesCommissionResponse.from_orm(entity)

    @staticmethod
    def get_by_id(db: Session, tenant_id: str, commission_id: int) -> Optional[SalesCommissionResponse]:
        """根据ID获取销售提成支付明细"""
        entity = FinSalesCommissionDAO.get_by_id(db, tenant_id, commission_id)
        return SalesCommissionResponse.from_orm(entity) if entity else None

    @staticmethod
    def get_by_order_id(db: Session, tenant_id: str, order_id: int) -> Optional[SalesCommissionResponse]:
        """根据订单ID获取销售提成明细"""
        entity = FinSalesCommissionDAO.get_by_order_id(db, tenant_id, order_id)
        return SalesCommissionResponse.from_orm(entity) if entity else None

    @staticmethod
    def list(db: Session, tenant_id: str, page_request: PageRequest,
             project_id: Optional[int] = None, employee_id: Optional[int] = None, 
             commission_status: Optional[int] = None) -> PageResponse[SalesCommissionResponse]:
        """分页查询销售提成支付明细列表"""
        filters = {}
        if project_id:
            filters["project_id"] = project_id
        if employee_id:
            filters["employee_id"] = employee_id
        if commission_status:
            filters["commission_status"] = commission_status
        
        total, items = FinSalesCommissionDAO.list(db, tenant_id, page_request.page, page_request.size, **filters)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.size,
            items=[SalesCommissionResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def update(db: Session, tenant_id: str, commission_id: int, data: SalesCommissionUpdate) -> Optional[SalesCommissionResponse]:
        """更新销售提成支付明细"""
        update_data = {}
        if data.bonus_pay_id is not None:
            update_data["bonus_pay_id"] = data.bonus_pay_id
        if data.commission_status is not None:
            update_data["commission_status"] = data.commission_status
        if data.settle_time is not None:
            update_data["settle_time"] = data.settle_time
        if data.pay_time is not None:
            update_data["pay_time"] = data.pay_time
        if data.remark is not None:
            update_data["remark"] = data.remark
        
        if update_data:
            update_data["update_time"] = datetime.now()
            entity = FinSalesCommissionDAO.update(db, tenant_id, commission_id, update_data)
            return SalesCommissionResponse.from_orm(entity) if entity else None
        return SalesCommissionService.get_by_id(db, tenant_id, commission_id)

    @staticmethod
    def delete(db: Session, tenant_id: str, commission_id: int) -> bool:
        """软删除销售提成支付明细"""
        return FinSalesCommissionDAO.delete(db, tenant_id, commission_id)


# ========== 内部销售提成付款单服务 ==========

class SalesBonusPayService:
    """内部销售提成付款单服务类"""

    @staticmethod
    def create(db: Session, tenant_id: str, data: SalesBonusPayCreate, create_user_id: int = 1) -> SalesBonusPayResponse:
        """创建内部销售提成付款单"""
        bonus_data = data.model_dump()
        if not bonus_data.get('pay_no'):
            bonus_data['pay_no'] = generate_doc_no(db, tenant_id, "TC")
        bonus_data.update({
            "tenant": tenant_id,
            "audit_status": 1,
            "pay_status": 1,
            "is_del": 0,
            "version": 1,
            "create_user_id": create_user_id,
            "update_user_id": create_user_id,
            "create_time": datetime.now(),
            "update_time": datetime.now()
        })
        entity = FinSalesBonusPayDAO.create(db, bonus_data)
        return SalesBonusPayResponse.from_orm(entity)

    @staticmethod
    def get_by_id(db: Session, tenant_id: str, pay_id: int) -> Optional[SalesBonusPayResponse]:
        """根据ID获取内部销售提成付款单"""
        entity = FinSalesBonusPayDAO.get_by_id(db, tenant_id, pay_id)
        return SalesBonusPayResponse.from_orm(entity) if entity else None

    @staticmethod
    def get_by_pay_no(db: Session, tenant_id: str, pay_no: str) -> Optional[SalesBonusPayResponse]:
        """根据付款单号获取内部销售提成付款单"""
        entity = FinSalesBonusPayDAO.get_by_pay_no(db, tenant_id, pay_no)
        return SalesBonusPayResponse.from_orm(entity) if entity else None

    @staticmethod
    def list(db: Session, tenant_id: str, page_request: PageRequest,
             project_id: Optional[int] = None, staff_id: Optional[int] = None, 
             audit_status: Optional[int] = None, pay_status: Optional[int] = None) -> PageResponse[SalesBonusPayResponse]:
        """分页查询内部销售提成付款单列表"""
        filters = {}
        if project_id:
            filters["project_id"] = project_id
        if staff_id:
            filters["staff_id"] = staff_id
        if audit_status:
            filters["audit_status"] = audit_status
        if pay_status:
            filters["pay_status"] = pay_status
        
        total, items = FinSalesBonusPayDAO.list(db, tenant_id, page_request.page, page_request.size, **filters)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.size,
            items=[SalesBonusPayResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def update(db: Session, tenant_id: str, pay_id: int, data: SalesBonusPayUpdate) -> Optional[SalesBonusPayResponse]:
        """更新内部销售提成付款单"""
        update_data = {}
        if data.building_scope is not None:
            update_data["building_scope"] = data.building_scope
        if data.deduct_amount is not None:
            update_data["deduct_amount"] = data.deduct_amount
        if data.actual_pay_untax is not None:
            update_data["actual_pay_untax"] = data.actual_pay_untax
        if data.actual_pay_tax is not None:
            update_data["actual_pay_tax"] = data.actual_pay_tax
        if data.actual_pay_amount is not None:
            update_data["actual_pay_amount"] = data.actual_pay_amount
        if data.audit_status is not None:
            update_data["audit_status"] = data.audit_status
        if data.pay_status is not None:
            update_data["pay_status"] = data.pay_status
        if data.pay_time is not None:
            update_data["pay_time"] = data.pay_time
        if data.audit_user_id is not None:
            update_data["audit_user_id"] = data.audit_user_id
        if data.pay_user_id is not None:
            update_data["pay_user_id"] = data.pay_user_id
        if data.bank_flow_id is not None:
            update_data["bank_flow_id"] = data.bank_flow_id
        if data.bank_flow_no is not None:
            update_data["bank_flow_no"] = data.bank_flow_no
        if data.voucher_no is not None:
            update_data["voucher_no"] = data.voucher_no
        if data.remark is not None:
            update_data["remark"] = data.remark
        
        if update_data:
            update_data["update_time"] = datetime.now()
            entity = FinSalesBonusPayDAO.update(db, tenant_id, pay_id, update_data)
            return SalesBonusPayResponse.from_orm(entity) if entity else None
        return SalesBonusPayService.get_by_id(db, tenant_id, pay_id)

    @staticmethod
    def delete(db: Session, tenant_id: str, pay_id: int) -> bool:
        """软删除内部销售提成付款单"""
        return FinSalesBonusPayDAO.delete(db, tenant_id, pay_id)

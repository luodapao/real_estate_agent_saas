"""
房地产SaaS财务管理系统 - 会计凭证服务层
"""
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime

from ..dao.finance_dao_ext import (
    FinVoucherDAO,
    FinVoucherItemDAO,
)
from ..schemas.voucher_schemas import (
    VoucherCreate,
    VoucherUpdate,
    VoucherResponse,
    VoucherItemCreate,
    VoucherItemUpdate,
    VoucherItemResponse,
    VoucherAudit,
    VoucherRedFlush,
    VoucherWithItemsResponse,
)
from ..schemas.base_schemas import PageRequest, PageResponse


class VoucherService:
    """会计凭证服务类"""

    @staticmethod
    def _generate_doc_no(db: Session, tenant: str, prefix: str) -> str:
        """
        生成单据编号（私有方法）
        :param db: 数据库会话
        :param tenant: 租户编码
        :param prefix: 编号前缀（PZ:凭证）
        :return: 生成的单据编号
        """
        date_str = datetime.now().strftime("%Y%m%d")
        max_no = 0

        if prefix == "PZ":
            result = db.execute(
                text("SELECT MAX(voucher_no) FROM fin_voucher WHERE tenant = :tenant AND voucher_no LIKE :pattern"),
                {"tenant": tenant, "pattern": f"{prefix}{date_str}%"}
            ).scalar()

        if result:
            seq_str = result[-4:]
            max_no = int(seq_str) + 1

        seq_str = str(max_no).zfill(4)
        return f"{prefix}{date_str}{seq_str}"

    # ==================== 会计凭证主表 ====================

    @staticmethod
    def create_voucher(db: Session, tenant: str, data: VoucherCreate, create_user_id: int = 1) -> VoucherResponse:
        """创建会计凭证主表"""
        data_dict = data.model_dump()
        data_dict['tenant'] = tenant
        if not data_dict.get('voucher_no'):
            data_dict['voucher_no'] = VoucherService._generate_doc_no(db, tenant, "PZ")
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinVoucherDAO.create(db, tenant, data_dict)
        return VoucherResponse.from_orm(entity)

    @staticmethod
    def get_voucher(db: Session, tenant: str, id: int) -> Optional[VoucherResponse]:
        """获取会计凭证主表详情"""
        entity = FinVoucherDAO.get_by_id(db, tenant, id)
        return VoucherResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_voucher(db: Session, tenant: str, id: int, data: VoucherUpdate) -> Optional[VoucherResponse]:
        """更新会计凭证主表"""
        update_data = data.model_dump(exclude_unset=True)
        entity = FinVoucherDAO.update(db, tenant, id, update_data)
        return VoucherResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_voucher(db: Session, tenant: str, id: int) -> bool:
        """删除会计凭证主表"""
        return FinVoucherDAO.delete(db, tenant, id)

    @staticmethod
    def list_vouchers(db: Session, tenant: str, page_request: PageRequest, filters: Optional[dict] = None) -> PageResponse[VoucherResponse]:
        """分页查询会计凭证主表列表"""
        query_filters = filters or {}
        query_filters['page'] = page_request.page
        query_filters['page_size'] = page_request.page_size
        total, items = FinVoucherDAO.list(db, tenant, query_filters)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[VoucherResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def audit_voucher(db: Session, tenant: str, data: VoucherAudit) -> Optional[VoucherResponse]:
        """审核会计凭证"""
        entity = FinVoucherDAO.get_by_id(db, tenant, data.id)
        if not entity:
            return None

        update_data = {
            'audit_user_id': data.audit_user_id,
            'audit_time': datetime.now(),
            'voucher_status': data.audit_status
        }

        entity = FinVoucherDAO.update(db, tenant, data.id, update_data)
        return VoucherResponse.from_orm(entity) if entity else None

    @staticmethod
    def red_flush_voucher(db: Session, tenant: str, data: VoucherRedFlush) -> Optional[VoucherResponse]:
        """红字冲销会计凭证"""
        original_entity = FinVoucherDAO.get_by_id(db, tenant, data.id)
        if not original_entity:
            return None

        if original_entity.voucher_status in [4, 5]:
            return None

        update_data = {
            'is_red_flush': 1,
            'red_flush_reason': data.red_flush_reason,
            'voucher_status': 5
        }
        entity = FinVoucherDAO.update(db, tenant, data.id, update_data)
        return VoucherResponse.from_orm(entity) if entity else None

    @staticmethod
    def get_voucher_with_items(db: Session, tenant: str, id: int) -> Optional[VoucherWithItemsResponse]:
        """获取凭证及明细"""
        voucher = FinVoucherDAO.get_by_id(db, tenant, id)
        if not voucher:
            return None

        items = FinVoucherItemDAO.get_by_voucher_id(db, tenant, id)
        return VoucherWithItemsResponse(
            voucher=VoucherResponse.from_orm(voucher),
            items=[VoucherItemResponse.from_orm(item) for item in items]
        )

    # ==================== 凭证明细 ====================

    @staticmethod
    def create_voucher_item(db: Session, tenant: str, data: VoucherItemCreate, create_user_id: int = 1) -> VoucherItemResponse:
        """创建会计凭证明细"""
        data_dict = data.model_dump()
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinVoucherItemDAO.create(db, tenant, data_dict)
        return VoucherItemResponse.from_orm(entity)

    @staticmethod
    def get_voucher_item(db: Session, tenant: str, id: int) -> Optional[VoucherItemResponse]:
        """获取会计凭证明细详情"""
        entity = FinVoucherItemDAO.get_by_id(db, tenant, id)
        return VoucherItemResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_voucher_item(db: Session, tenant: str, id: int, data: VoucherItemUpdate) -> Optional[VoucherItemResponse]:
        """更新会计凭证明细"""
        update_data = data.model_dump(exclude_unset=True)
        entity = FinVoucherItemDAO.update(db, tenant, id, update_data)
        return VoucherItemResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_voucher_item(db: Session, tenant: str, id: int) -> bool:
        """删除会计凭证明细"""
        return FinVoucherItemDAO.delete(db, tenant, id)

    @staticmethod
    def list_voucher_items(db: Session, tenant: str, page_request: PageRequest, filters: Optional[dict] = None) -> PageResponse[VoucherItemResponse]:
        """分页查询会计凭证明细列表"""
        query_filters = filters or {}
        query_filters['page'] = page_request.page
        query_filters['page_size'] = page_request.page_size
        total, items = FinVoucherItemDAO.list(db, tenant, query_filters)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[VoucherItemResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def bulk_create_voucher_items(db: Session, tenant: str, details: List[VoucherItemCreate]) -> List[VoucherItemResponse]:
        """批量创建凭证明细"""
        data_list = [item.model_dump() for item in details]
        entities = FinVoucherItemDAO.bulk_create(db, tenant, data_list)
        return [VoucherItemResponse.from_orm(entity) for entity in entities]

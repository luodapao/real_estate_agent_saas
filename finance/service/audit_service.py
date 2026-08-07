"""
房地产SaaS财务管理系统 - 财务审计追溯服务层
"""
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime

from ..dao.finance_dao_ext import (
    FinOperateLogDAO,
    FinDataChangeLogDAO,
)
from ..schemas.audit_schemas import (
    OperateLogCreate,
    OperateLogUpdate,
    OperateLogResponse,
)
from ..schemas.base_schemas import PageRequest, PageResponse


class AuditService:
    """财务审计追溯服务类"""

    @staticmethod
    def _generate_operate_no(db: Session, tenant: str) -> str:
        """生成操作日志编号"""
        date_str = datetime.now().strftime("%Y%m%d")
        prefix = "OP"
        max_no = 0
        
        result = db.execute(
            text("SELECT MAX(operate_no) FROM fin_operate_log WHERE tenant = :tenant AND operate_no LIKE :pattern"),
            {"tenant": tenant, "pattern": f"{prefix}{date_str}%"}
        ).scalar()
        
        if result:
            seq_str = result[-4:]
            max_no = int(seq_str) + 1
        
        seq_str = str(max_no).zfill(4)
        return f"{prefix}{date_str}{seq_str}"

    # ==================== 财务操作审计日志 ====================

    @staticmethod
    def create_operate_log(db: Session, tenant: str, data: OperateLogCreate, create_user_id: int = 1) -> OperateLogResponse:
        """创建财务操作审计日志"""
        data_dict = data.model_dump()
        data_dict['tenant'] = tenant
        if not data_dict.get('operate_no'):
            data_dict['operate_no'] = AuditService._generate_operate_no(db, tenant)
        data_dict['create_user_id'] = create_user_id
        data_dict['update_user_id'] = create_user_id
        entity = FinOperateLogDAO.create(db, tenant, data_dict)
        return OperateLogResponse.from_orm(entity)

    @staticmethod
    def get_operate_log(db: Session, tenant: str, id: int) -> Optional[OperateLogResponse]:
        """获取财务操作审计日志详情"""
        entity = FinOperateLogDAO.get_by_id(db, tenant, id)
        return OperateLogResponse.from_orm(entity) if entity else None

    @staticmethod
    def update_operate_log(db: Session, tenant: str, id: int, data: OperateLogUpdate) -> Optional[OperateLogResponse]:
        """更新财务操作审计日志"""
        update_data = data.model_dump(exclude_unset=True)
        entity = FinOperateLogDAO.update(db, tenant, id, update_data)
        return OperateLogResponse.from_orm(entity) if entity else None

    @staticmethod
    def delete_operate_log(db: Session, tenant: str, id: int) -> bool:
        """删除财务操作审计日志"""
        return FinOperateLogDAO.delete(db, tenant, id)

    @staticmethod
    def list_operate_logs(db: Session, tenant: str, page_request: PageRequest, filters: Optional[dict] = None) -> PageResponse[OperateLogResponse]:
        """分页查询财务操作审计日志列表"""
        query_filters = filters or {}
        query_filters['page'] = page_request.page
        query_filters['page_size'] = page_request.page_size
        total, items = FinOperateLogDAO.list(db, tenant, query_filters)
        return PageResponse(
            total=total,
            page=page_request.page,
            size=page_request.page_size,
            data=[OperateLogResponse.from_orm(item) for item in items]
        )

    @staticmethod
    def quick_create_operate_log(
        db: Session,
        tenant: str,
        operate_user_id: int,
        operate_user_name: str,
        biz_module: int,
        operate_type: int,
        operate_summary: str,
        operate_content: str,
        biz_type: Optional[int] = None,
        biz_id: Optional[int] = None,
        biz_no: Optional[str] = None,
        voucher_id: Optional[int] = None,
        voucher_no: Optional[str] = None,
        old_data: Optional[str] = None,
        new_data: Optional[str] = None,
        operate_status: int = 1,
        error_msg: Optional[str] = None,
        operate_ip: Optional[str] = None,
        terminal_type: int = 1
    ) -> OperateLogResponse:
        """快速创建操作日志（简化接口）"""
        operate_no = AuditService._generate_operate_no(db, tenant)
        
        data = OperateLogCreate(
            operate_no=operate_no,
            operate_user_id=operate_user_id,
            operate_user_name=operate_user_name,
            biz_module=biz_module,
            operate_type=operate_type,
            operate_summary=operate_summary,
            operate_content=operate_content,
            biz_type=biz_type,
            biz_id=biz_id,
            biz_no=biz_no,
            voucher_id=voucher_id,
            voucher_no=voucher_no,
            old_data=old_data,
            new_data=new_data,
            operate_status=operate_status,
            error_msg=error_msg,
            operate_ip=operate_ip,
            terminal_type=terminal_type
        )
        
        return AuditService.create_operate_log(db, tenant, data)

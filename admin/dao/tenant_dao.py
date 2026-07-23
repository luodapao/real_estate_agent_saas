"""
租户数据访问层
"""
from sqlalchemy.orm import Session
from admin.model.sys_tenant import SysTenant
from config.constants import TENANT_STATUS


class TenantDAO:
    """租户数据访问对象"""
    
    @staticmethod
    def get(db: Session, tenant_id: int):
        """根据ID查询租户"""
        return db.query(SysTenant).filter(
            SysTenant.tenant_id == tenant_id,
            SysTenant.is_del == 0
        ).first()
    
    @staticmethod
    def get_by_code(db: Session, tenant_code: str):
        """根据编码查询租户"""
        return db.query(SysTenant).filter(
            SysTenant.tenant_code == tenant_code,
            SysTenant.is_del == 0
        ).first()
    
    @staticmethod
    def get_list(db: Session, tenant_name: str = None, status: int = None, page: int = 1, size: int = 10):
        """分页查询租户列表"""
        query = db.query(SysTenant).filter(SysTenant.is_del == 0)
        if tenant_name:
            query = query.filter(SysTenant.tenant_name.like(f'%{tenant_name}%'))
        if status is not None:
            query = query.filter(SysTenant.status == status)
        total = query.count()
        data = query.offset((page - 1) * size).limit(size).all()
        return total, data
    
    @staticmethod
    def create(db: Session, tenant: SysTenant):
        """创建租户"""
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        return tenant
    
    @staticmethod
    def update(db: Session, tenant_id: int, update_data: dict):
        """更新租户"""
        db.query(SysTenant).filter(SysTenant.tenant_id == tenant_id).update(update_data)
        db.commit()
        return TenantDAO.get(db, tenant_id)
    
    @staticmethod
    def delete(db: Session, tenant_id: int):
        """删除租户（软删除）"""
        return TenantDAO.update(db, tenant_id, {'is_del': 1})
    
    @staticmethod
    def enable(db: Session, tenant_id: int):
        """启用租户"""
        return TenantDAO.update(db, tenant_id, {'status': TENANT_STATUS['NORMAL']})
    
    @staticmethod
    def disable(db: Session, tenant_id: int):
        """禁用租户"""
        return TenantDAO.update(db, tenant_id, {'status': TENANT_STATUS['DISABLED']})
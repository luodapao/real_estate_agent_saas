"""
角色数据访问层
"""
from sqlalchemy.orm import Session
from admin.model.sys_role import SysRole
from admin.model.sys_user_role import SysUserRole


class RoleDAO:
    """角色数据访问对象"""
    
    @staticmethod
    def get(db: Session, role_id: int):
        """根据ID查询角色"""
        return db.query(SysRole).filter(
            SysRole.role_id == role_id,
            SysRole.is_del == 0
        ).first()
    
    @staticmethod
    def get_by_code(db: Session, tenant_id: int, role_code: str):
        """根据租户和编码查询角色"""
        return db.query(SysRole).filter(
            SysRole.tenant_id == tenant_id,
            SysRole.role_code == role_code,
            SysRole.is_del == 0
        ).first()
    
    @staticmethod
    def get_list(db: Session, tenant_id: int, role_name: str = None, status: int = None, page: int = 1, size: int = 10):
        """分页查询角色列表"""
        query = db.query(SysRole).filter(
            SysRole.tenant_id == tenant_id,
            SysRole.is_del == 0
        )
        if role_name:
            query = query.filter(SysRole.role_name.like(f'%{role_name}%'))
        if status is not None:
            query = query.filter(SysRole.status == status)
        total = query.count()
        data = query.offset((page - 1) * size).limit(size).all()
        return total, data
    
    @staticmethod
    def create(db: Session, role: SysRole):
        """创建角色"""
        db.add(role)
        db.commit()
        db.refresh(role)
        return role
    
    @staticmethod
    def update(db: Session, role_id: int, update_data: dict):
        """更新角色"""
        db.query(SysRole).filter(SysRole.role_id == role_id).update(update_data)
        db.commit()
        return RoleDAO.get(db, role_id)
    
    @staticmethod
    def delete(db: Session, role_id: int):
        """删除角色（软删除）"""
        return RoleDAO.update(db, role_id, {'is_del': 1})
    
    @staticmethod
    def grant_role_to_user(db: Session, tenant_id: int, user_id: int, role_ids: list):
        """给用户分配角色"""
        # 先删除用户现有角色
        db.query(SysUserRole).filter(
            SysUserRole.user_id == user_id,
            SysUserRole.is_del == 0
        ).update({'is_del': 1})
        
        # 添加新角色
        for role_id in role_ids:
            user_role = SysUserRole(
                tenant_id=tenant_id,
                user_id=user_id,
                role_id=role_id
            )
            db.add(user_role)
        
        db.commit()
    
    @staticmethod
    def get_user_roles(db: Session, user_id: int):
        """获取用户角色列表"""
        roles = db.query(SysRole).join(
            SysUserRole,
            SysRole.role_id == SysUserRole.role_id
        ).filter(
            SysUserRole.user_id == user_id,
            SysUserRole.is_del == 0,
            SysRole.is_del == 0
        ).all()
        return roles
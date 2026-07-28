"""
用户数据访问层
"""
from sqlalchemy.orm import Session
from admin.model.sys_user import SysUser
from admin.model.sys_user_role import SysUserRole
from admin.model.sys_role import SysRole
from admin.model.sys_role_menu import SysRoleMenu
from admin.model.sys_menu import SysMenu
from config.constants import USER_STATUS


class UserDAO:
    """用户数据访问对象"""
    
    @staticmethod
    def get(db: Session, user_id: int):
        """根据ID查询用户"""
        return db.query(SysUser).filter(
            SysUser.user_id == user_id,
            SysUser.is_del == 0
        ).first()
    
    @staticmethod
    def get_by_account(db: Session, account: str):
        """根据账号查询用户"""
        return db.query(SysUser).filter(
            SysUser.account == account,
            SysUser.is_del == 0
        ).first()
    
    @staticmethod
    def get_list(db: Session, tenant_id: int, name: str = None, status: int = None, page: int = 1, size: int = 10):
        """分页查询用户列表"""
        query = db.query(SysUser).filter(
            SysUser.tenant_id == tenant_id,
            SysUser.is_del == 0
        )
        if name:
            query = query.filter(SysUser.name.like(f'%{name}%'))
        if status is not None:
            query = query.filter(SysUser.status == status)
        total = query.count()
        data = query.offset((page - 1) * size).limit(size).all()
        return total, data
    
    @staticmethod
    def create(db: Session, user: SysUser):
        """创建用户"""
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update(db: Session, user_id: int, update_data: dict):
        """更新用户"""
        db.query(SysUser).filter(SysUser.user_id == user_id).update(update_data)
        db.commit()
        return UserDAO.get(db, user_id)
    
    @staticmethod
    def delete(db: Session, user_id: int):
        """删除用户（软删除）"""
        return UserDAO.update(db, user_id, {'is_del': 1})
    
    @staticmethod
    def update_password(db: Session, user_id: int, password: str):
        """更新密码"""
        return UserDAO.update(db, user_id, {'password': password})
    
    @staticmethod
    def update_login_failed_count(db: Session, user_id: int, count: int):
        """更新登录失败次数"""
        return UserDAO.update(db, user_id, {'login_failed_count': count})
    
    @staticmethod
    def reset_login_failed_count(db: Session, user_id: int):
        """重置登录失败次数"""
        return UserDAO.update(db, user_id, {'login_failed_count': 0})
    
    @staticmethod
    def lock_account(db: Session, user_id: int):
        """锁定账号"""
        from datetime import datetime
        return UserDAO.update(db, user_id, {
            'status': USER_STATUS['LOCKED'],
            'locked_time': datetime.now()
        })
    
    @staticmethod
    def unlock_account(db: Session, user_id: int):
        """解锁账号"""
        return UserDAO.update(db, user_id, {
            'status': USER_STATUS['NORMAL'],
            'login_failed_count': 0
        })
    
    @staticmethod
    def update_last_login(db: Session, user_id: int, ip: str):
        """更新最后登录信息"""
        from datetime import datetime
        return UserDAO.update(db, user_id, {
            'last_login_time': datetime.now(),
            'last_login_ip': ip
        })
    
    @staticmethod
    def get_user_permissions(db: Session, user_id: int):
        """获取用户权限列表"""
        # 查询用户角色
        roles = db.query(SysUserRole.role_id).filter(
            SysUserRole.user_id == user_id,
            SysUserRole.is_del == 0
        ).subquery()
        
        # 查询角色菜单权限
        menu_ids = db.query(SysRoleMenu.menu_id).filter(
            SysRoleMenu.role_id.in_(roles),
            SysRoleMenu.is_del == 0
        ).subquery()
        
        # 查询权限标识
        permissions = db.query(SysMenu.permission).filter(
            SysMenu.menu_id.in_(menu_ids),
            SysMenu.status == 1,
            SysMenu.is_del == 0,
            SysMenu.permission.isnot(None)
        ).all()
        
        return [p[0] for p in permissions] if permissions else []
    
    @staticmethod
    def get_platform_user_list(db: Session, name: str = None, login_name: str = None, status: int = None, page: int = 1, size: int = 10):
        """分页查询平台超级用户列表（tenant_id=0, user_type=0）"""
        query = db.query(SysUser).filter(
            SysUser.tenant_id == 0,
            SysUser.user_type == 0,
            SysUser.is_del == 0
        )
        if name:
            query = query.filter(SysUser.name.like(f'%{name}%'))
        if login_name:
            query = query.filter(SysUser.account.like(f'%{login_name}%'))
        if status is not None:
            query = query.filter(SysUser.status == status)
        total = query.count()
        data = query.offset((page - 1) * size).limit(size).all()
        return total, data
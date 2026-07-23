"""
角色业务服务层
用于租户下的角色管理
"""
from sqlalchemy.orm import Session
from admin.model.sys_role import SysRole
from admin.model.sys_user_role import SysUserRole
from admin.dao.role_dao import RoleDAO
from admin.dao.user_dao import UserDAO
from admin.schemas.role_schemas import RoleCreate, RoleUpdate, RoleResponse
from config.exception import BusinessException, ParamException
from config.constants import REDIS_KEY
from core.redis_base import redis_client


class RoleService:
    """角色业务服务"""
    
    @staticmethod
    def get_role(db: Session, role_id: int) -> RoleResponse:
        """查询角色详情"""
        role = RoleDAO.get(db, role_id)
        if not role:
            raise BusinessException("角色不存在")
        return RoleResponse.from_orm(role)
    
    @staticmethod
    def get_role_list(db: Session, tenant_id: int, role_name: str = None, status: int = None, page: int = 1, size: int = 10):
        """分页查询角色列表"""
        total, data = RoleDAO.get_list(db, tenant_id, role_name, status, page, size)
        role_list = [RoleResponse.from_orm(role).model_dump() for role in data]
        return {
            'total': total,
            'page': page,
            'size': size,
            'data': role_list
        }
    
    @staticmethod
    def create_role(db: Session, tenant_id: int, data: RoleCreate) -> RoleResponse:
        """创建角色"""
        # 校验角色编码是否存在
        existing = RoleDAO.get_by_code(db, tenant_id, data.role_code)
        if existing:
            raise ParamException("角色编码已存在")
        
        role = SysRole(
            tenant_id=tenant_id,
            role_name=data.role_name,
            role_code=data.role_code,
            role_type=data.role_type or 2,
            status=data.status or 1,
            remark=data.remark
        )
        
        created_role = RoleDAO.create(db, role)
        return RoleResponse.from_orm(created_role)
    
    @staticmethod
    def update_role(db: Session, role_id: int, data: RoleUpdate) -> RoleResponse:
        """更新角色"""
        role = RoleDAO.get(db, role_id)
        if not role:
            raise BusinessException("角色不存在")
        
        # 如果修改编码，校验新编码是否存在
        update_dict = data.model_dump(exclude_unset=True)
        if 'role_code' in update_dict and update_dict['role_code'] != role.role_code:
            existing = RoleDAO.get_by_code(db, role.tenant_id, update_dict['role_code'])
            if existing:
                raise ParamException("角色编码已存在")
        
        updated_role = RoleDAO.update(db, role_id, update_dict)
        return RoleResponse.from_orm(updated_role)
    
    @staticmethod
    def delete_role(db: Session, role_id: int) -> RoleResponse:
        """删除角色"""
        role = RoleDAO.get(db, role_id)
        if not role:
            raise BusinessException("角色不存在")
        
        # 检查是否有用户关联该角色
        user_count = db.query(SysUserRole).filter(
            SysUserRole.role_id == role_id,
            SysUserRole.is_del == 0
        ).count()
        
        if user_count > 0:
            raise ParamException("该角色下还有用户，无法删除")
        
        RoleDAO.delete(db, role_id)
        return RoleResponse.from_orm(role)
    
    @staticmethod
    def grant_role_to_user(db: Session, tenant_id: int, user_id: int, role_ids: list):
        """给用户分配角色"""
        # 校验用户是否存在
        user = UserDAO.get(db, user_id)
        if not user:
            raise BusinessException("用户不存在")
        
        # 校验角色是否存在
        for role_id in role_ids:
            role = RoleDAO.get(db, role_id)
            if not role:
                raise BusinessException(f"角色ID {role_id} 不存在")
        
        RoleDAO.grant_role_to_user(db, tenant_id, user_id, role_ids)
        
        # 清除用户权限缓存
        perm_key = REDIS_KEY['USER_PERM'].format(user_id)
        redis_client.delete(perm_key)
    
    @staticmethod
    def get_user_roles(db: Session, user_id: int):
        """获取用户角色列表"""
        return RoleDAO.get_user_roles(db, user_id)

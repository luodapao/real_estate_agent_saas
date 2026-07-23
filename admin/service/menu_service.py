"""
菜单业务服务层
"""
from sqlalchemy.orm import Session
from admin.model.sys_menu import SysMenu
from admin.dao.menu_dao import MenuDAO
from admin.schemas.menu_schemas import MenuCreate, MenuUpdate, MenuResponse
from config.exception import BusinessException, ParamException
from config.constants import REDIS_KEY
from core.redis_base import redis_client


class MenuService:
    """菜单业务服务"""
    
    @staticmethod
    def get_menu(db: Session, menu_id: int) -> MenuResponse:
        """查询菜单详情"""
        menu = MenuDAO.get(db, menu_id)
        if not menu:
            raise BusinessException("菜单不存在")
        return MenuResponse.from_orm(menu)
    
    @staticmethod
    def get_menu_list(db: Session, tenant_id: int, menu_name: str = None, menu_type: int = None, status: int = None):
        """查询菜单列表"""
        menus = MenuDAO.get_list(db, tenant_id, menu_name, menu_type, status)
        return [MenuResponse.from_orm(menu).model_dump() for menu in menus]
    
    @staticmethod
    def get_menu_tree(db: Session, tenant_id: int):
        """获取菜单树结构"""
        return MenuDAO.get_tree(db, tenant_id)
    
    @staticmethod
    def create_menu(db: Session, tenant_id: int, data: MenuCreate) -> MenuResponse:
        """创建菜单"""
        # 校验菜单编码是否存在
        existing = MenuDAO.get_by_code(db, tenant_id, data.menu_code)
        if existing:
            raise ParamException("菜单编码已存在")
        
        # 如果有父菜单，校验父菜单是否存在
        if data.parent_id != 0:
            parent = MenuDAO.get(db, data.parent_id)
            if not parent:
                raise BusinessException("父菜单不存在")
        
        menu = SysMenu(
            tenant_id=tenant_id,
            parent_id=data.parent_id,
            menu_name=data.menu_name,
            menu_code=data.menu_code,
            menu_type=data.menu_type,
            path=data.path,
            component=data.component,
            icon=data.icon,
            sort_order=data.sort_order,
            permission=data.permission,
            remark=data.remark,
            status=data.status or 1
        )
        
        created_menu = MenuDAO.create(db, menu)
        return MenuResponse.from_orm(created_menu)
    
    @staticmethod
    def update_menu(db: Session, menu_id: int, data: MenuUpdate) -> MenuResponse:
        """更新菜单"""
        menu = MenuDAO.get(db, menu_id)
        if not menu:
            raise BusinessException("菜单不存在")
        
        update_dict = data.model_dump(exclude_unset=True)
        
        # 如果修改编码，校验新编码是否存在
        if 'menu_code' in update_dict and update_dict['menu_code'] != menu.menu_code:
            existing = MenuDAO.get_by_code(db, menu.tenant_id, update_dict['menu_code'])
            if existing:
                raise ParamException("菜单编码已存在")
        
        updated_menu = MenuDAO.update(db, menu_id, update_dict)
        
        # 清除所有用户权限缓存
        redis_client.delete_pattern(REDIS_KEY['USER_PERM'].format('*'))
        
        return MenuResponse.from_orm(updated_menu)
    
    @staticmethod
    def delete_menu(db: Session, menu_id: int) -> MenuResponse:
        """删除菜单"""
        menu = MenuDAO.get(db, menu_id)
        if not menu:
            raise BusinessException("菜单不存在")
        
        # 检查是否有子菜单
        children_count = db.query(SysMenu).filter(
            SysMenu.parent_id == menu_id,
            SysMenu.is_del == 0
        ).count()
        
        if children_count > 0:
            raise ParamException("该菜单下还有子菜单，无法删除")
        
        MenuDAO.delete(db, menu_id)
        
        # 清除所有用户权限缓存
        redis_client.delete_pattern(REDIS_KEY['USER_PERM'].format('*'))
        
        return MenuResponse.from_orm(menu)
    
    @staticmethod
    def grant_menu_to_role(db: Session, tenant_id: int, role_id: int, menu_ids: list):
        """给角色分配菜单权限"""
        # 校验角色是否存在
        from admin.dao.role_dao import RoleDAO
        role = RoleDAO.get(db, role_id)
        if not role:
            raise BusinessException("角色不存在")
        
        # 校验菜单是否存在
        for menu_id in menu_ids:
            menu = MenuDAO.get(db, menu_id)
            if not menu:
                raise BusinessException(f"菜单ID {menu_id} 不存在")
        
        MenuDAO.grant_menu_to_role(db, tenant_id, role_id, menu_ids)
        
        # 清除所有用户权限缓存
        redis_client.delete_pattern(REDIS_KEY['USER_PERM'].format('*'))
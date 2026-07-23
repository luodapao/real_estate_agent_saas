"""
菜单数据访问层
"""
from sqlalchemy.orm import Session
from admin.model.sys_menu import SysMenu
from admin.model.sys_role_menu import SysRoleMenu


class MenuDAO:
    """菜单数据访问对象"""
    
    @staticmethod
    def get(db: Session, menu_id: int):
        """根据ID查询菜单"""
        return db.query(SysMenu).filter(
            SysMenu.menu_id == menu_id,
            SysMenu.is_del == 0
        ).first()
    
    @staticmethod
    def get_by_code(db: Session, tenant_id: int, menu_code: str):
        """根据租户和编码查询菜单"""
        return db.query(SysMenu).filter(
            SysMenu.tenant_id == tenant_id,
            SysMenu.menu_code == menu_code,
            SysMenu.is_del == 0
        ).first()
    
    @staticmethod
    def get_list(db: Session, tenant_id: int, menu_name: str = None, menu_type: int = None, status: int = None):
        """查询菜单列表"""
        query = db.query(SysMenu).filter(
            SysMenu.tenant_id == tenant_id,
            SysMenu.is_del == 0
        )
        if menu_name:
            query = query.filter(SysMenu.menu_name.like(f'%{menu_name}%'))
        if menu_type is not None:
            query = query.filter(SysMenu.menu_type == menu_type)
        if status is not None:
            query = query.filter(SysMenu.status == status)
        return query.order_by(SysMenu.sort_order).all()
    
    @staticmethod
    def get_tree(db: Session, tenant_id: int, parent_id: int = 0):
        """递归获取菜单树"""
        menus = db.query(SysMenu).filter(
            SysMenu.tenant_id == tenant_id,
            SysMenu.parent_id == parent_id,
            SysMenu.status == 1,
            SysMenu.is_del == 0
        ).order_by(SysMenu.sort_order).all()
        
        result = []
        for menu in menus:
            children = MenuDAO.get_tree(db, tenant_id, menu.menu_id)
            menu_dict = {
                'menu_id': menu.menu_id,
                'menu_name': menu.menu_name,
                'menu_code': menu.menu_code,
                'menu_type': menu.menu_type,
                'path': menu.path,
                'component': menu.component,
                'icon': menu.icon,
                'permission': menu.permission,
                'children': children
            }
            result.append(menu_dict)
        return result
    
    @staticmethod
    def create(db: Session, menu: SysMenu):
        """创建菜单"""
        db.add(menu)
        db.commit()
        db.refresh(menu)
        return menu
    
    @staticmethod
    def update(db: Session, menu_id: int, update_data: dict):
        """更新菜单"""
        db.query(SysMenu).filter(SysMenu.menu_id == menu_id).update(update_data)
        db.commit()
        return MenuDAO.get(db, menu_id)
    
    @staticmethod
    def delete(db: Session, menu_id: int):
        """删除菜单（软删除）"""
        return MenuDAO.update(db, menu_id, {'is_del': 1})
    
    @staticmethod
    def grant_menu_to_role(db: Session, tenant_id: int, role_id: int, menu_ids: list):
        """给角色分配菜单权限"""
        # 先删除角色现有权限
        db.query(SysRoleMenu).filter(
            SysRoleMenu.role_id == role_id,
            SysRoleMenu.is_del == 0
        ).update({'is_del': 1})
        
        # 添加新权限
        for menu_id in menu_ids:
            role_menu = SysRoleMenu(
                tenant_id=tenant_id,
                role_id=role_id,
                menu_id=menu_id
            )
            db.add(role_menu)
        
        db.commit()
    
    @staticmethod
    def get_role_menus(db: Session, role_id: int):
        """获取角色菜单列表"""
        menus = db.query(SysMenu).join(
            SysRoleMenu,
            SysMenu.menu_id == SysRoleMenu.menu_id
        ).filter(
            SysRoleMenu.role_id == role_id,
            SysRoleMenu.is_del == 0,
            SysMenu.is_del == 0
        ).all()
        return menus
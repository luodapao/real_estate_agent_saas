"""
角色菜单关联表模型
"""
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.mysql import BIGINT
from core.db_base import Base
from datetime import datetime


class SysRoleMenu(Base):
    """角色菜单关联表"""
    __tablename__ = 'sys_role_menu'
    
    role_menu_id = Column(BIGINT, primary_key=True, autoincrement=True, comment='关联ID')
    tenant_id = Column(BIGINT, nullable=False, comment='租户ID')
    role_id = Column(BIGINT, nullable=False, comment='角色ID')
    menu_id = Column(BIGINT, nullable=False, comment='菜单ID')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    created_by = Column(BIGINT, comment='创建人')
    is_del = Column(BIGINT, default=0, comment='删除标识：0-正常，1-删除')
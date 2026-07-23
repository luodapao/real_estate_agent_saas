"""
菜单信息表模型
"""
from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from core.db_base import Base
from datetime import datetime


class SysMenu(Base):
    """菜单信息表"""
    __tablename__ = 'sys_menu'
    
    menu_id = Column(BIGINT, primary_key=True, autoincrement=True, comment='菜单ID')
    tenant_id = Column(BIGINT, nullable=False, comment='租户ID')
    parent_id = Column(BIGINT, default=0, comment='父菜单ID')
    menu_name = Column(String(100), nullable=False, comment='菜单名称')
    menu_code = Column(String(100), nullable=False, comment='菜单编码')
    menu_type = Column(TINYINT, nullable=False, comment='菜单类型：1-目录，2-菜单，3-按钮')
    path = Column(String(255), comment='路由路径')
    component = Column(String(255), comment='组件路径')
    icon = Column(String(100), comment='图标')
    sort_order = Column(Integer, default=0, comment='排序号')
    status = Column(TINYINT, default=1, comment='状态：1-正常，2-禁用')
    permission = Column(String(100), comment='权限标识')
    remark = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    created_by = Column(BIGINT, comment='创建人')
    updated_by = Column(BIGINT, comment='更新人')
    is_del = Column(TINYINT, default=0, comment='删除标识：0-正常，1-删除')
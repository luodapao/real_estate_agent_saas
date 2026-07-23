"""
角色信息表模型
"""
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from core.db_base import Base
from datetime import datetime


class SysRole(Base):
    """角色信息表"""
    __tablename__ = 'sys_role'
    
    role_id = Column(BIGINT, primary_key=True, autoincrement=True, comment='角色ID')
    tenant_id = Column(BIGINT, nullable=False, comment='租户ID')
    role_name = Column(String(100), nullable=False, comment='角色名称')
    role_code = Column(String(50), nullable=False, comment='角色编码')
    role_type = Column(TINYINT, default=1, comment='角色类型：1-系统角色，2-自定义角色')
    status = Column(TINYINT, default=1, comment='状态：1-正常，2-禁用')
    remark = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    created_by = Column(BIGINT, comment='创建人')
    updated_by = Column(BIGINT, comment='更新人')
    is_del = Column(TINYINT, default=0, comment='删除标识：0-正常，1-删除')
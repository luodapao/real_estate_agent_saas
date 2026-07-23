"""
租户信息表模型
"""
from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from core.db_base import Base
from datetime import datetime


class SysTenant(Base):
    """租户信息表"""
    __tablename__ = 'sys_tenant'
    
    tenant_id = Column(BIGINT, primary_key=True, autoincrement=True, comment='租户ID')
    tenant_name = Column(String(100), nullable=False, comment='租户名称')
    tenant_code = Column(String(50), unique=True, nullable=False, comment='租户编码')
    contact_name = Column(String(50), comment='联系人')
    contact_mobile = Column(String(20), comment='联系电话')
    email = Column(String(100), comment='邮箱')
    address = Column(String(500), comment='地址')
    status = Column(TINYINT, default=1, comment='状态：1-正常，2-禁用')
    expire_time = Column(DateTime, comment='到期时间')
    remark = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    created_by = Column(BIGINT, comment='创建人')
    updated_by = Column(BIGINT, comment='更新人')
    is_del = Column(TINYINT, default=0, comment='删除标识：0-正常，1-删除')
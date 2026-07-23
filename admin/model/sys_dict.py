"""
数据字典表模型
"""
from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from core.db_base import Base
from datetime import datetime


class SysDict(Base):
    """数据字典表"""
    __tablename__ = 'sys_dict'
    
    dict_id = Column(BIGINT, primary_key=True, autoincrement=True, comment='字典ID')
    tenant_id = Column(BIGINT, nullable=False, comment='租户ID')
    dict_type = Column(String(50), nullable=False, comment='字典类型')
    dict_code = Column(String(50), nullable=False, comment='字典编码')
    dict_name = Column(String(100), nullable=False, comment='字典名称')
    dict_value = Column(String(500), comment='字典值')
    sort_order = Column(Integer, default=0, comment='排序号')
    status = Column(TINYINT, default=1, comment='状态：1-正常，2-禁用')
    remark = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    created_by = Column(BIGINT, comment='创建人')
    updated_by = Column(BIGINT, comment='更新人')
    is_del = Column(TINYINT, default=0, comment='删除标识：0-正常，1-删除')
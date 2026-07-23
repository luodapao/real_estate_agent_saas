"""
令牌信息表模型
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from core.db_base import Base
from datetime import datetime


class SysToken(Base):
    """令牌信息表"""
    __tablename__ = 'sys_token'
    
    token_id = Column(BIGINT, primary_key=True, autoincrement=True, comment='令牌ID')
    tenant_id = Column(BIGINT, nullable=False, comment='租户ID')
    user_id = Column(BIGINT, nullable=False, comment='用户ID')
    access_token = Column(String(500), nullable=False, comment='访问令牌')
    refresh_token = Column(String(500), nullable=False, comment='刷新令牌')
    expires_time = Column(DateTime, nullable=False, comment='过期时间')
    login_ip = Column(String(50), comment='登录IP')
    user_agent = Column(String(500), comment='用户代理')
    is_invalid = Column(TINYINT, default=0, comment='是否作废：0-有效，1-作废')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
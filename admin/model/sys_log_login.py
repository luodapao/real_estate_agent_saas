"""
登录日志表模型
"""
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from core.db_base import Base
from datetime import datetime


class SysLogLogin(Base):
    """登录日志表"""
    __tablename__ = 'sys_log_login'
    
    login_log_id = Column(BIGINT, primary_key=True, autoincrement=True, comment='日志ID')
    tenant_id = Column(BIGINT, nullable=False, comment='租户ID')
    user_id = Column(BIGINT, comment='用户ID')
    account = Column(String(50), comment='登录账号')
    login_time = Column(DateTime, default=datetime.now, comment='登录时间')
    login_ip = Column(String(50), comment='登录IP')
    login_type = Column(TINYINT, comment='登录类型：1-账号密码登录，2-验证码登录')
    login_status = Column(TINYINT, comment='登录状态：1-成功，2-失败')
    error_msg = Column(Text, comment='错误信息')
    user_agent = Column(String(500), comment='用户代理')
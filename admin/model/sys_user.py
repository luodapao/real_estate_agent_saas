"""
用户信息表模型
"""
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from core.db_base import Base
from datetime import datetime


class SysUser(Base):
    """用户信息表"""
    __tablename__ = 'sys_user'
    
    user_id = Column(BIGINT, primary_key=True, autoincrement=True, comment='用户ID')
    tenant_id = Column(BIGINT, nullable=False, comment='租户ID')
    account = Column(String(50), unique=True, nullable=False, comment='账号')
    password = Column(String(255), nullable=False, comment='密码')
    name = Column(String(50), nullable=False, comment='姓名')
    mobile = Column(String(20), comment='手机号')
    email = Column(String(100), comment='邮箱')
    avatar = Column(String(500), comment='头像')
    dept_id = Column(BIGINT, comment='部门ID')
    status = Column(TINYINT, default=1, comment='状态：1-正常，2-禁用，3-锁定，4-待审核')
    pwd_expire_time = Column(DateTime, comment='密码过期时间')
    user_type = Column(TINYINT, default=1, comment='用户类型：1-内部用户，2-分销渠道后台管理员、3-外部经纪人')
    last_login_time = Column(DateTime, comment='最后登录时间')
    last_login_ip = Column(String(50), comment='最后登录IP')
    login_failed_count = Column(BIGINT, default=0, comment='登录失败次数')
    locked_time = Column(DateTime, comment='锁定时间')
    remark = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    created_by = Column(BIGINT, comment='创建人')
    updated_by = Column(BIGINT, comment='更新人')
    is_del = Column(TINYINT, default=0, comment='删除标识：0-正常，1-删除')
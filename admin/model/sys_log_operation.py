"""
操作日志表模型
"""
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from core.db_base import Base
from datetime import datetime


class SysLogOperation(Base):
    """操作日志表"""
    __tablename__ = 'sys_log_operation'
    
    operation_log_id = Column(BIGINT, primary_key=True, autoincrement=True, comment='日志ID')
    tenant_id = Column(BIGINT, nullable=False, comment='租户ID')
    user_id = Column(BIGINT, comment='用户ID')
    user_name = Column(String(50), comment='用户名称')
    operation_type = Column(TINYINT, comment='操作类型：1-新增，2-修改，3-删除，4-查询')
    module_name = Column(String(100), comment='模块名称')
    operation_desc = Column(String(500), comment='操作描述')
    request_url = Column(String(500), comment='请求URL')
    request_method = Column(String(10), comment='请求方法')
    request_params = Column(Text, comment='请求参数')
    response_data = Column(Text, comment='响应数据')
    status = Column(TINYINT, comment='操作状态：1-成功，2-失败')
    error_msg = Column(Text, comment='错误信息')
    operation_time = Column(DateTime, default=datetime.now, comment='操作时间')
    ip_address = Column(String(50), comment='IP地址')
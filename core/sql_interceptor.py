"""
全局SQL租户+层级数据拦截器
"""
from sqlalchemy import event
from sqlalchemy.orm import Session
from core.db_base import engine


class SQLInterceptor:
    """SQL拦截器类"""
    
    @staticmethod
    def before_execute(conn, clauseelement, multiparams, params):
        """执行前拦截"""
        # 可以在这里添加SQL审计、租户过滤等逻辑
        pass
    
    @staticmethod
    def after_execute(conn, clauseelement, multiparams, params, result):
        """执行后拦截"""
        # 可以在这里添加执行时间统计等逻辑
        pass


# 注册SQL拦截器
event.listen(engine, 'before_execute', SQLInterceptor.before_execute)
event.listen(engine, 'after_execute', SQLInterceptor.after_execute)
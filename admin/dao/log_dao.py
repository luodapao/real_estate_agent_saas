"""
日志数据访问层
"""
from sqlalchemy.orm import Session
from admin.model.sys_log_login import SysLogLogin
from admin.model.sys_log_operation import SysLogOperation


class LogDAO:
    """日志数据访问对象"""

    @staticmethod
    def add_login_log(db: Session, login_log: SysLogLogin):
        """添加登录日志"""
        db.add(login_log)
        db.commit()
        db.refresh(login_log)
        return login_log

    @staticmethod
    def get_login_log_list(db: Session, tenant_id: int, user_id: int = None,
                          login_name: str = None, status: int = None,
                          start_time: str = None, end_time: str = None,
                          page: int = 1, size: int = 10):
        """分页查询登录日志列表"""
        query = db.query(SysLogLogin).filter(
            SysLogLogin.tenant_id == tenant_id
        )
        if user_id:
            query = query.filter(SysLogLogin.user_id == user_id)
        if login_name:
            query = query.filter(SysLogLogin.account.like(f'%{login_name}%'))
        if status is not None:
            query = query.filter(SysLogLogin.login_status == status)
        if start_time:
            query = query.filter(SysLogLogin.login_time >= start_time)
        if end_time:
            query = query.filter(SysLogLogin.login_time <= end_time)

        query = query.order_by(SysLogLogin.login_time.desc())
        total = query.count()
        data = query.offset((page - 1) * size).limit(size).all()
        return total, data

    @staticmethod
    def add_operation_log(db: Session, operation_log: SysLogOperation):
        """添加操作日志"""
        db.add(operation_log)
        db.commit()
        db.refresh(operation_log)
        return operation_log

    @staticmethod
    def get_operation_log_list(db: Session, tenant_id: int, user_id: int = None,
                              user_name: str = None, module: str = None,
                              status: int = None, start_time: str = None,
                              end_time: str = None, page: int = 1, size: int = 10):
        """分页查询操作日志列表"""
        query = db.query(SysLogOperation).filter(
            SysLogOperation.tenant_id == tenant_id
        )
        if user_id:
            query = query.filter(SysLogOperation.user_id == user_id)
        if user_name:
            query = query.filter(SysLogOperation.user_name.like(f'%{user_name}%'))
        if module:
            query = query.filter(SysLogOperation.module_name.like(f'%{module}%'))
        if status is not None:
            query = query.filter(SysLogOperation.status == status)
        if start_time:
            query = query.filter(SysLogOperation.operation_time >= start_time)
        if end_time:
            query = query.filter(SysLogOperation.operation_time <= end_time)

        query = query.order_by(SysLogOperation.operation_time.desc())
        total = query.count()
        data = query.offset((page - 1) * size).limit(size).all()
        return total, data

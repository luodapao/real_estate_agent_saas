"""
日志业务服务层
"""
from sqlalchemy.orm import Session
from admin.model.sys_log_login import SysLogLogin
from admin.model.sys_log_operation import SysLogOperation
from admin.dao.log_dao import LogDAO


class LogService:
    """日志业务服务"""
    
    @staticmethod
    def add_login_log(db: Session, tenant_id: int, user_id: int, login_name: str, 
                     login_type: int, status: int, message: str, ip: str, 
                     browser: str = None, os: str = None, device: str = None):
        """添加登录日志"""
        login_log = SysLogLogin(
            tenant_id=tenant_id,
            user_id=user_id,
            account=login_name,
            login_type=login_type,
            login_status=status,
            error_msg=message,
            login_ip=ip
        )
        return LogDAO.add_login_log(db, login_log)
    
    @staticmethod
    def get_login_log_list(db: Session, tenant_id: int, user_id: int = None, 
                          login_name: str = None, status: int = None, 
                          start_time: str = None, end_time: str = None,
                          page: int = 1, size: int = 10):
        """分页查询登录日志列表"""
        total, data = LogDAO.get_login_log_list(db, tenant_id, user_id, login_name, 
                                               status, start_time, end_time, page, size)
        return {
            'total': total,
            'page': page,
            'size': size,
            'list': data
        }
    
    @staticmethod
    def add_operation_log(db: Session, tenant_id: int, user_id: int, user_name: str,
                         module: str, method: str, url: str, params: str, 
                         status: int, message: str = None, ip: str = None,
                         browser: str = None, os: str = None, duration: int = None):
        """添加操作日志"""
        operation_type_map = {
            'POST': 1,
            'PUT': 2,
            'DELETE': 3,
            'GET': 4
        }
        operation_log = SysLogOperation(
            tenant_id=tenant_id,
            user_id=user_id,
            user_name=user_name,
            operation_type=operation_type_map.get(method, 4),
            module_name=module,
            operation_desc=message,
            request_url=url,
            request_method=method,
            request_params=params,
            status=status,
            ip_address=ip
        )
        return LogDAO.add_operation_log(db, operation_log)
    
    @staticmethod
    def get_operation_log_list(db: Session, tenant_id: int, user_id: int = None,
                              user_name: str = None, module: str = None,
                              status: int = None, start_time: str = None, 
                              end_time: str = None, page: int = 1, size: int = 10):
        """分页查询操作日志列表"""
        total, data = LogDAO.get_operation_log_list(db, tenant_id, user_id, user_name,
                                                   module, status, start_time, end_time, 
                                                   page, size)
        return {
            'total': total,
            'page': page,
            'size': size,
            'list': data
        }
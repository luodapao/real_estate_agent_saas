"""
全局异常处理 - 统一异常封装和响应格式
"""
import json
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from config.constants import CODE, MESSAGE

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class ErrorCode:
    """错误码枚举类"""
    PARAM_VALID_ERROR = 1001
    SYSTEM_ERROR = 5000


class CustomException(Exception):
    """自定义异常"""
    def __init__(self, error_code: int, message: str, status_code: int = 200):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class BusinessException(Exception):
    """业务异常基类"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class AuthException(BusinessException):
    """认证异常"""
    def __init__(self, message: str = MESSAGE['AUTH_ERROR']):
        super().__init__(CODE['AUTH_ERROR'], message)


class TokenExpiredException(BusinessException):
    """Token过期异常"""
    def __init__(self, message: str = MESSAGE['TOKEN_EXPIRED']):
        super().__init__(CODE['TOKEN_EXPIRED'], message)


class TokenInvalidException(BusinessException):
    """Token无效异常"""
    def __init__(self, message: str = MESSAGE['TOKEN_INVALID']):
        super().__init__(CODE['TOKEN_INVALID'], message)


class PermissionDeniedException(BusinessException):
    """权限拒绝异常"""
    def __init__(self, message: str = MESSAGE['PERMISSION_DENIED']):
        super().__init__(CODE['PERMISSION_DENIED'], message)


class AccountDisabledException(BusinessException):
    """账号禁用异常"""
    def __init__(self, message: str = MESSAGE['ACCOUNT_DISABLED']):
        super().__init__(CODE['ACCOUNT_DISABLED'], message)


class PasswordExpiredException(BusinessException):
    """密码过期异常"""
    def __init__(self, message: str = MESSAGE['PASSWORD_EXPIRED']):
        super().__init__(CODE['PASSWORD_EXPIRED'], message)


class AccountLockedException(BusinessException):
    """账号锁定异常"""
    def __init__(self, message: str = MESSAGE['ACCOUNT_LOCKED']):
        super().__init__(CODE['ACCOUNT_LOCKED'], message)


class VerifyCodeException(BusinessException):
    """验证码异常"""
    def __init__(self, message: str = MESSAGE['VERIFY_CODE_ERROR']):
        super().__init__(CODE['VERIFY_CODE_ERROR'], message)


class DataNotFoundException(BusinessException):
    """数据不存在异常"""
    def __init__(self, message: str = MESSAGE['DATA_NOT_FOUND']):
        super().__init__(CODE['DATA_NOT_FOUND'], message)


class DataExistsException(BusinessException):
    """数据已存在异常"""
    def __init__(self, message: str = MESSAGE['DATA_EXISTS']):
        super().__init__(CODE['DATA_EXISTS'], message)


class OperateFailedException(BusinessException):
    """操作失败异常"""
    def __init__(self, message: str = MESSAGE['OPERATE_FAILED']):
        super().__init__(CODE['OPERATE_FAILED'], message)


class ParamException(BusinessException):
    """参数异常"""
    def __init__(self, message: str = MESSAGE['PARAM_ERROR']):
        super().__init__(CODE['PARAM_ERROR'], message)


def success_response(data=None, message: str = MESSAGE['SUCCESS']):
    """成功响应"""
    from fastapi.encoders import jsonable_encoder
    response_data = {
        'code': CODE['SUCCESS'],
        'message': message,
        'data': jsonable_encoder(data)
    }
    return JSONResponse(content=response_data)


def error_response(code: int, message: str):
    """错误响应"""
    return JSONResponse({
        'code': code,
        'message': message,
        'data': None
    }, status_code=status.HTTP_200_OK)


def exception_handler(request, exc: BusinessException):
    """全局异常处理器"""
    return JSONResponse({
        'code': exc.code,
        'message': exc.message,
        'data': None
    }, status_code=status.HTTP_200_OK)


def http_exception_handler(request, exc: HTTPException):
    """HTTP异常处理器"""
    return JSONResponse({
        'code': exc.status_code,
        'message': exc.detail,
        'data': None
    }, status_code=exc.status_code)
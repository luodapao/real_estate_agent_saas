"""
系统异常定义
"""


class BusinessError(Exception):
    """业务异常"""
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationError(Exception):
    """参数验证异常"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(Exception):
    """认证异常"""
    def __init__(self, message: str = "认证失败"):
        self.message = message
        super().__init__(self.message)


class PermissionError(Exception):
    """权限异常"""
    def __init__(self, message: str = "权限不足"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(Exception):
    """资源不存在异常"""
    def __init__(self, message: str = "资源不存在"):
        self.message = message
        super().__init__(self.message)
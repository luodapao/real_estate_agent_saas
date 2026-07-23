"""
全局参数校验工具
"""
import re
from config.exception import ParamException


class Validator:
    """参数校验工具类"""
    
    @staticmethod
    def validate_mobile(mobile: str) -> bool:
        """校验手机号格式"""
        pattern = r'^1[3-9]\d{9}$'
        if not re.match(pattern, mobile):
            raise ParamException("手机号格式不正确")
        return True
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """校验邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ParamException("邮箱格式不正确")
        return True
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """校验密码强度"""
        if len(password) < 8:
            raise ParamException("密码长度至少8位")
        if not any(c.isupper() for c in password):
            raise ParamException("密码必须包含大写字母")
        if not any(c.islower() for c in password):
            raise ParamException("密码必须包含小写字母")
        if not any(c.isdigit() for c in password):
            raise ParamException("密码必须包含数字")
        return True
    
    @staticmethod
    def validate_account(account: str) -> bool:
        """校验账号格式"""
        # 账号只能包含字母、数字、下划线，长度3-50
        pattern = r'^[a-zA-Z0-9_]{3,50}$'
        if not re.match(pattern, account):
            raise ParamException("账号格式不正确，只能包含字母、数字、下划线，长度3-50")
        return True
    
    @staticmethod
    def validate_verify_code(code: str) -> bool:
        """校验验证码格式"""
        if not code.isdigit() or len(code) != 6:
            raise ParamException("验证码必须是6位数字")
        return True
    
    @staticmethod
    def validate_ip(ip: str) -> bool:
        """校验IP地址格式"""
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if not re.match(pattern, ip):
            raise ParamException("IP地址格式不正确")
        return True
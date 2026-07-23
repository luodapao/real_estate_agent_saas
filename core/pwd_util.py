"""
BCrypt密码工具
"""
import bcrypt


class PasswordUtil:
    """密码工具类"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """加密密码"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def is_password_strong(password: str) -> bool:
        """检查密码强度"""
        # 至少8位，包含大小写字母和数字
        if len(password) < 8:
            return False
        if not any(c.isupper() for c in password):
            return False
        if not any(c.islower() for c in password):
            return False
        if not any(c.isdigit() for c in password):
            return False
        return True
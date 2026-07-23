"""
JWT签发/校验工具
"""
import jwt
from datetime import datetime, timedelta
from config.settings import JWT_CONFIG
from config.constants import REDIS_KEY
from core.redis_base import redis_client


class JWTUtil:
    """JWT工具类"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=JWT_CONFIG['access_token_expire_minutes'])
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_CONFIG['secret_key'], algorithm=JWT_CONFIG['algorithm'])
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict, expires_delta: timedelta = None):
        """创建刷新令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=JWT_CONFIG['refresh_token_expire_days'])
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_CONFIG['secret_key'], algorithm=JWT_CONFIG['algorithm'])
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str):
        """解码令牌"""
        try:
            payload = jwt.decode(token, JWT_CONFIG['secret_key'], algorithms=[JWT_CONFIG['algorithm']])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def is_token_blacklisted(access_token: str):
        """检查Token是否在黑名单中"""
        key = REDIS_KEY['TOKEN_BLACK'].format(access_token)
        return redis_client.exists(key)
    
    @staticmethod
    def blacklist_token(access_token: str, expire_seconds: int = 2 * 60 * 60):
        """将Token加入黑名单"""
        key = REDIS_KEY['TOKEN_BLACK'].format(access_token)
        redis_client.set(key, '1', expire=expire_seconds)
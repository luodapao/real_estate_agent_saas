"""
Redis全局单例客户端
"""
import redis
from config.settings import REDIS_CONFIG


class RedisClient:
    """Redis客户端单例类"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            try:
                cls._instance._client = redis.Redis(**REDIS_CONFIG)
                cls._instance._client.ping()
                cls._instance._connected = True
            except Exception:
                cls._instance._client = None
                cls._instance._connected = False
        return cls._instance
    
    def get_client(self):
        """获取Redis客户端"""
        return self._client
    
    def set(self, key: str, value, expire=None):
        """设置缓存"""
        if not self._connected:
            return None
        try:
            self._client.set(key, value, ex=expire)
        except Exception:
            return None
    
    def get(self, key: str):
        """获取缓存"""
        if not self._connected:
            return None
        try:
            return self._client.get(key)
        except Exception:
            return None
    
    def delete(self, key: str):
        """删除缓存"""
        if not self._connected:
            return 0
        try:
            return self._client.delete(key)
        except Exception:
            return 0
    
    def exists(self, key: str):
        """检查缓存是否存在"""
        if not self._connected:
            return 0
        try:
            return self._client.exists(key)
        except Exception:
            return 0
    
    def incr(self, key: str):
        """原子递增"""
        if not self._connected:
            return None
        try:
            return self._client.incr(key)
        except Exception:
            return None
    
    def expire(self, key: str, seconds: int):
        """设置过期时间"""
        if not self._connected:
            return None
        try:
            return self._client.expire(key, seconds)
        except Exception:
            return None
    
    def setnx(self, key: str, value, expire=None):
        """设置缓存（不存在时才设置）"""
        if not self._connected:
            return None
        try:
            result = self._client.setnx(key, value)
            if expire and result:
                self._client.expire(key, expire)
            return result
        except Exception:
            return None
    
    def setex(self, key: str, expire: int, value):
        """设置带过期时间的缓存"""
        if not self._connected:
            return None
        try:
            return self._client.setex(key, expire, value)
        except Exception:
            return None
    
    def keys(self, pattern: str):
        """模糊查询key"""
        if not self._connected:
            return []
        try:
            return self._client.keys(pattern)
        except Exception:
            return []


# 创建全局Redis客户端实例
redis_client = RedisClient()
"""
Redis全局单例客户端
"""
import uuid
import logging
import redis
from config.settings import REDIS_CONFIG

logger = logging.getLogger("redis_base")

# Lua脚本：仅当锁值与持有者token一致时才删除，避免误删他人锁（原子操作）
_RELEASE_LOCK_LUA = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
"""


class RedisClient:
    """Redis客户端单例类"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._instance._client = None
            cls._instance._connected = False
            cls._instance._connect()
        return cls._instance
    
    def _connect(self):
        """建立连接并ping校验，成功返回True"""
        try:
            self._client = redis.Redis(**REDIS_CONFIG)
            self._client.ping()
            self._connected = True
        except Exception as e:
            self._client = None
            self._connected = False
            logger.error("Redis连接失败: %s", e)
        return self._connected
    
    def _ensure_connection(self):
        """确保连接可用；若之前失败则做一次性重连尝试，不永久缓存失败状态"""
        if self._connected:
            return True
        return self._connect()
    
    def is_available(self) -> bool:
        """Redis当前是否可用（用于区分锁竞争失败与Redis宕机降级）"""
        return self._ensure_connection()
    
    def get_client(self):
        """获取Redis客户端"""
        return self._client
    
    def set(self, key: str, value, expire=None):
        """设置缓存"""
        if not self._ensure_connection():
            return None
        try:
            self._client.set(key, value, ex=expire)
        except Exception as e:
            logger.error("Redis set失败 key=%s: %s", key, e)
            return None
    
    def get(self, key: str):
        """获取缓存"""
        if not self._ensure_connection():
            return None
        try:
            return self._client.get(key)
        except Exception as e:
            logger.error("Redis get失败 key=%s: %s", key, e)
            return None
    
    def delete(self, key: str):
        """删除缓存"""
        if not self._ensure_connection():
            return 0
        try:
            return self._client.delete(key)
        except Exception as e:
            logger.error("Redis delete失败 key=%s: %s", key, e)
            return 0
    
    def exists(self, key: str):
        """检查缓存是否存在"""
        if not self._ensure_connection():
            return 0
        try:
            return self._client.exists(key)
        except Exception as e:
            logger.error("Redis exists失败 key=%s: %s", key, e)
            return 0
    
    def incr(self, key: str):
        """原子递增"""
        if not self._ensure_connection():
            return None
        try:
            return self._client.incr(key)
        except Exception as e:
            logger.error("Redis incr失败 key=%s: %s", key, e)
            return None
    
    def expire(self, key: str, seconds: int):
        """设置过期时间"""
        if not self._ensure_connection():
            return None
        try:
            return self._client.expire(key, seconds)
        except Exception as e:
            logger.error("Redis expire失败 key=%s: %s", key, e)
            return None
            
    def setnx(self, key: str, value, expire=None):
        """设置缓存（不存在时才设置）——原子SET NX EX，保证key与TTL同时写入"""
        if not self._ensure_connection():
            return None
        try:
            # nx=True 仅当key不存在时设置；ex与nx在同一条命令内原子生效
            return self._client.set(key, value, nx=True, ex=expire)
        except Exception as e:
            logger.error("Redis setnx失败 key=%s: %s", key, e)
            return None
    
    def setex(self, key: str, expire: int, value):
        """设置带过期时间的缓存"""
        if not self._ensure_connection():
            return None
        try:
            return self._client.setex(key, expire, value)
        except Exception as e:
            logger.error("Redis setex失败 key=%s: %s", key, e)
            return None
    
    def keys(self, pattern: str):
        """模糊查询key"""
        if not self._ensure_connection():
            return []
        try:
            return self._client.keys(pattern)
        except Exception as e:
            logger.error("Redis keys失败 pattern=%s: %s", pattern, e)
            return []
    
    def acquire_lock(self, key: str, expire: int = 10):
        """获取分布式锁：原子SET NX EX，成功返回唯一token，失败返回None。
        token用于释放时校验持有者，避免误删他人锁。"""
        if not self._ensure_connection():
            return None
        token = uuid.uuid4().hex
        try:
            ok = self._client.set(key, token, nx=True, ex=expire)
            return token if ok else None
        except Exception as e:
            logger.error("获取分布式锁失败 key=%s: %s", key, e)
            return None
    
    def release_lock(self, key: str, token) -> bool:
        """释放分布式锁：仅当锁值与token一致时才删除（Lua原子操作）。
        token为None时为安全no-op（未持有锁）。"""
        if not token:
            return False
        if not self._ensure_connection():
            logger.warning("释放锁时Redis不可用 key=%s，依赖TTL自动过期兜底", key)
            return False
        try:
            result = self._client.eval(_RELEASE_LOCK_LUA, 1, key, token)
            if not result:
                logger.warning("释放锁时token不匹配或锁已过期 key=%s，跳过删除", key)
            return bool(result)
        except Exception as e:
            logger.error("释放锁失败 key=%s: %s，依赖TTL自动过期兜底", key, e)
            return False

    def publish(self, channel: str, message):
        """发布消息到指定频道"""
        if not self._ensure_connection():
            return None
        try:
            return self._client.publish(channel, message)
        except Exception as e:
            logger.error("Redis publish失败 channel=%s: %s", channel, e)
            return None


# 创建全局Redis客户端实例
redis_client = RedisClient()

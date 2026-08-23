"""
全局配置文件 - 读取.env环境变量
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'database': os.getenv('DB_DATABASE', 'admin')
}

# Redis配置
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'password': os.getenv('REDIS_PASSWORD', None),
    'db': int(os.getenv('REDIS_DB', 0)),
    'decode_responses': True
}

# RocketMQ配置
MQ_CONFIG = {
    'namesrv_addr': os.getenv('MQ_NAMESRV_ADDR', 'localhost:9876'),
    'producer_group': os.getenv('MQ_PRODUCER_GROUP', 'real_estate_producer')
}

# 飞书配置
FEISHU_CONFIG = {
    'app_id': os.getenv('FEISHU_APP_ID', ''),
    'app_secret': os.getenv('FEISHU_APP_SECRET', ''),
    'webhook_url': os.getenv('FEISHU_WEBHOOK_URL', '')
}

# JWT配置
JWT_CONFIG = {
    'secret_key': os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key'),
    'algorithm': os.getenv('JWT_ALGORITHM', 'HS256'),
    'access_token_expire_minutes': int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 120)),
    'refresh_token_expire_days': int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', 7))
}

# 密码过期配置
PWD_EXPIRE_DAYS = int(os.getenv('PWD_EXPIRE_DAYS', 90))

# 登录失败配置
LOGIN_CONFIG = {
    'fail_max_count': int(os.getenv('LOGIN_FAIL_MAX_COUNT', 5)),
    'lock_minutes': int(os.getenv('LOGIN_LOCK_MINUTES', 15))
}

# Agent闲置下线时间（小时）
AGENT_IDLE_HOURS = int(os.getenv('AGENT_IDLE_HOURS', 72))

# Redis Key过期时间配置（秒）
REDIS_EXPIRE = {
    'login_err': 5 * 60,  # 5分钟
    'token_black': 2 * 60 * 60,  # 2小时
    'user_perm': 7 * 24 * 60 * 60,  # 7天
    'verify_code': 5 * 60,  # 5分钟
    'register_limit': 60  # 1分钟
}

# 允许放行的接口（不需要鉴权）
# 格式: {'path': 路径, 'methods': [HTTP方法列表], 'exact': 是否精确匹配}
WHITE_LIST = [
    # 根路径
    {'path': '/', 'methods': ['GET', 'HEAD'], 'exact': True},
    # 登录页（用户浏览器直接打开）
    {'path': '/login', 'methods': ['GET', 'HEAD'], 'exact': True},
    # 认证相关（公开接口）
    {'path': '/api/admin/login', 'methods': ['POST'], 'exact': True},
    {'path': '/api/admin/refresh-token', 'methods': ['POST'], 'exact': True},
    {'path': '/api/admin/prepare-login', 'methods': ['POST'], 'exact': True},
    {'path': '/api/admin/wait-login', 'methods': ['POST'], 'exact': True},
    # 平台超级用户创建（用于初始化账号）
    {'path': '/api/admin/platform/users', 'methods': ['POST'], 'exact': True},
    # 用户注册已移除，改为由平台超级管理员创建账号
    # 文档页面（不限制方法）
    {'path': '/docs', 'methods': ['GET', 'HEAD'], 'exact': True},
    {'path': '/redoc', 'methods': ['GET', 'HEAD'], 'exact': True},
    {'path': '/openapi.json', 'methods': ['GET', 'HEAD'], 'exact': True},
    {'path': '/favicon.ico', 'methods': ['GET', 'HEAD'], 'exact': True},
    # Finance子系统健康检查（仅放开存活探测，业务接口仍需鉴权）
    {'path': '/api/finance/health', 'methods': ['GET', 'HEAD'], 'exact': True}
]

# 允许放行的路径前缀（不需要鉴权）
WHITE_LIST_PREFIX = [
    '/docs/',
    '/redoc/',
    '/static/',
    '/frontend/'
]

# 应用运行配置
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8000))
DEBUG = bool(os.getenv('DEBUG', True))
WORKERS = int(os.getenv('WORKERS', 1))

# CORS配置
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')


class Settings:
    """配置类，供main.py使用"""
    HOST = HOST
    PORT = PORT
    DEBUG = DEBUG
    WORKERS = WORKERS
    ALLOWED_ORIGINS = ALLOWED_ORIGINS


settings = Settings()
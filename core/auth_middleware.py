"""
全局统一鉴权中间件 - 全系统接口统一拦截
"""
from datetime import datetime
from fastapi import Request
from config.settings import WHITE_LIST, WHITE_LIST_PREFIX
from config.constants import USER_STATUS, REDIS_KEY
from config.exception import (
    AuthException, TokenExpiredException, TokenInvalidException,
    AccountDisabledException, PasswordExpiredException, PermissionDeniedException
)
from core.jwt_util import JWTUtil
from core.redis_base import redis_client
from admin.dao.user_dao import UserDAO
from admin.dao.token_dao import TokenDAO


async def auth_middleware(request: Request, call_next):
    """全局鉴权中间件"""
    
    # 获取请求路径和方法
    path = request.url.path
    method = request.method
    
    # 白名单接口直接放行（支持路径+方法匹配）
    for white_item in WHITE_LIST:
        white_path = white_item['path']
        white_methods = white_item.get('methods', ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
        exact_match = white_item.get('exact', True)
        
        # 路径匹配（同时处理带/不带末尾斜杠的情况）
        path_matched = False
        if exact_match:
            # 精确匹配：支持 path == white_path 或 path == white_path + '/'
            path_matched = path == white_path or path == white_path + '/'
        else:
            path_matched = path.startswith(white_path)
        
        # 方法匹配
        method_matched = method.upper() in [m.upper() for m in white_methods]
        
        if path_matched and method_matched:
            # 白名单接口：初始化必要属性，避免后续代码访问不存在的属性
            request.state.user = None
            request.state.token = None
            request.state.permissions = []
            request.state.user_info = {
                'user_id': None,
                'tenant_id': None,
                'login_name': None,
                'user_name': None
            }
            return await call_next(request)
    
    # 白名单前缀路径直接放行（如 /docs/xxx, /redoc/xxx, /static/xxx）
    for prefix in WHITE_LIST_PREFIX:
        if path.startswith(prefix):
            # 白名单前缀接口：初始化必要属性
            request.state.user = None
            request.state.token = None
            request.state.permissions = []
            request.state.user_info = {
                'user_id': None,
                'tenant_id': None,
                'login_name': None,
                'user_name': None
            }
            return await call_next(request)
    
    # 获取Token
    access_token = request.headers.get('Authorization')
    if not access_token or not access_token.startswith('Bearer '):
        raise AuthException()
    
    access_token = access_token[7:]
    
    # 第一层：检查Redis黑名单
    if JWTUtil.is_token_blacklisted(access_token):
        raise TokenInvalidException()
    
    # 解码Token
    payload = JWTUtil.decode_token(access_token)
    if not payload:
        raise TokenExpiredException()
    
    user_id = payload.get('user_id')
    agent_identifier = payload.get('agent_identifier')
    
    # 获取请求头中的Agent标识
    request_agent = request.headers.get('X-Agent-Identifier')
    if not request_agent:
        raise AuthException("缺少Agent标识")
    
    # Agent标识绑定校验
    if agent_identifier != request_agent:
        # 作废Token
        JWTUtil.blacklist_token(access_token)
        raise TokenInvalidException("Agent标识不匹配")
    
    # 查询用户信息
    from sqlalchemy.orm import Session
    from core.db_base import SessionLocal
    db: Session = SessionLocal()
    
    try:
        # 查询Token记录
        token_info = TokenDAO.get_by_access_token(db, access_token)
        if not token_info or token_info.is_invalid == 1:
            raise TokenInvalidException()
        
        # 查询用户信息
        user = UserDAO.get(db, user_id)
        if not user or user.is_del == 1:
            raise AuthException()
        
        # 账号状态校验
        if user.status != USER_STATUS['NORMAL']:
            if user.status == USER_STATUS['DISABLED']:
                raise AccountDisabledException()
            elif user.status == USER_STATUS['LOCKED']:
                raise AccountDisabledException("账号已被锁定")
            elif user.status == USER_STATUS['PENDING']:
                raise AccountDisabledException("账号待审核")
            elif user.status == USER_STATUS['LOGICAL_DELETE']:
                raise AuthException("账号已注销")
        
        # 密码过期校验
        if user.pwd_expire_time and datetime.now() > user.pwd_expire_time:
            raise PasswordExpiredException()
        
        # 权限加载
        perm_key = REDIS_KEY['USER_PERM'].format(user_id)
        user_perms = redis_client.get(perm_key)
        
        if not user_perms:
            # 从数据库加载权限
            user_perms = UserDAO.get_user_permissions(db, user_id)
            redis_client.set(perm_key, user_perms)
        
        # 权限校验（简化版，实际应根据接口配置的权限进行校验）
        # 这里可以根据实际需求进行细粒度权限控制
        
        # 将用户信息存入请求状态
        request.state.user = user
        request.state.token = token_info
        request.state.permissions = user_perms
        request.state.user_info = {
            'user_id': user.user_id,
            'tenant_id': user.tenant_id,
            'login_name': user.account,
            'user_name': user.name
        }
        
    finally:
        db.close()
    
    return await call_next(request)


def get_current_user(request: Request):
    """获取当前用户信息（FastAPI依赖注入）"""
    if not hasattr(request.state, 'user'):
        raise AuthException()
    
    user = request.state.user
    return {
        'user_id': user.user_id,
        'tenant': user.tenant_id,
        'login_name': user.account,
        'user_name': user.name,
        'status': user.status
    }
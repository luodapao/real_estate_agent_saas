"""
路由权限依赖注入函数
用于在路由层进行角色权限校验，避免在service层混用权限逻辑
"""
from fastapi import Request, Depends
from config.exception import PermissionDeniedException
from config.constants import MESSAGE


def require_platform_admin(request: Request) -> dict:
    """
    平台超级管理员权限依赖
    要求：tenant_id=0 且 user_type=0
    """
    user_info = request.state.user_info
    user = request.state.user
    
    # 平台超级管理员：tenant_id=0 且 user_type=0
    if user_info.get('tenant_id') != 0 or user.user_type != 0:
        raise PermissionDeniedException(MESSAGE['PERMISSION_DENIED'])
    
    return user_info


def require_tenant_admin(request: Request) -> dict:
    """
    租户超级管理员权限依赖
    要求：tenant_id>0 且 user_type=1（租户超级管理员）
    """
    user_info = request.state.user_info
    user = request.state.user
    
    # 租户超级管理员：tenant_id>0 且 user_type=1
    if user_info.get('tenant_id') <= 0 or user.user_type != 1:
        raise PermissionDeniedException(MESSAGE['PERMISSION_DENIED'])
    
    return user_info


def require_admin(request: Request) -> dict:
    """
    管理员权限依赖（平台超级管理员或租户超级管理员）
    要求：tenant_id=0 且 user_type=0，或者 tenant_id>0 且 user_type=1
    """
    user_info = request.state.user_info
    user = request.state.user
    
    # 平台超级管理员
    if user_info.get('tenant_id') == 0 and user.user_type == 0:
        return user_info
    
    # 租户超级管理员
    if user_info.get('tenant_id') > 0 and user.user_type == 1:
        return user_info
    
    raise PermissionDeniedException(MESSAGE['PERMISSION_DENIED'])


def get_current_user_info(request: Request) -> dict:
    """
    获取当前用户信息
    """
    return request.state.user_info
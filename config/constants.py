"""
全局常量配置 - 状态码、Redis Key模板、账号状态等
"""

# HTTP状态码
HTTP_STATUS = {
    'SUCCESS': 200,
    'CREATED': 201,
    'BAD_REQUEST': 400,
    'UNAUTHORIZED': 401,
    'FORBIDDEN': 403,
    'NOT_FOUND': 404,
    'INTERNAL_ERROR': 500
}

# 业务状态码
CODE = {
    'SUCCESS': 0,
    'ERROR': -1,
    'PARAM_ERROR': 1001,
    'AUTH_ERROR': 2001,
    'TOKEN_EXPIRED': 2002,
    'TOKEN_INVALID': 2003,
    'PERMISSION_DENIED': 2004,
    'ACCOUNT_DISABLED': 2005,
    'PASSWORD_EXPIRED': 2006,
    'ACCOUNT_LOCKED': 2007,
    'VERIFY_CODE_ERROR': 2008,
    'DATA_NOT_FOUND': 3001,
    'DATA_EXISTS': 3002,
    'OPERATE_FAILED': 3003
}

# 账号状态
USER_STATUS = {
    'PENDING': 0,      # 待审核
    'NORMAL': 1,       # 正常
    'DISABLED': 2,     # 禁用
    'LOCKED': 3,       # 密码锁定
    'TEMP_EXPIRED': 4, # 临时过期
    'LOGICAL_DELETE': 5 # 逻辑注销
}

# 租户状态
TENANT_STATUS = {
    'NORMAL': 1,     # 正常
    'DISABLED': 2,   # 停用
    'EXPIRED': 3     # 过期
}

# 登录结果
LOGIN_RESULT = {
    'SUCCESS': 1,
    'FAILED': 0
}

# 验证码状态
VERIFY_CODE_STATUS = {
    'UNUSED': 0,   # 未使用
    'USED': 1      # 已核销
}

# Token状态
TOKEN_STATUS = {
    'VALID': 0,      # 有效
    'INVALID': 1     # 作废
}

# 操作类型
OPER_TYPE = {
    'LOGIN': 'login',
    'QUERY': 'query',
    'UPDATE': 'update',
    'EXPORT': 'export',
    'RESET_PWD': 'reset_pwd',
    'CREATE': 'create',
    'DELETE': 'delete'
}

# 权限类型
PERM_TYPE = {
    'API': 'API',
    'MENU': 'MENU',
    'BUTTON': 'BUTTON'
}

# 数据权限范围
DATA_SCOPE = {
    'SELF': 'SELF',     # 本人
    'DEPT': 'DEPT',     # 本部门
    'ALL': 'ALL'        # 全部
}

# 登录配置
LOGIN_CONFIG = {
    'max_failed_attempts': 5,
    'password_expire_days': 90,
    'lock_minutes': 15
}

# Redis Key模板
REDIS_KEY = {
    'LOGIN_ERR': 'login_err:account:{}',
    'TOKEN_BLACK': 'token_black:{}',
    'USER_PERM': 'user_perm:{}',
    'VERIFY_CODE': 'verify_code:user:{}:agent:{}',
    'REGISTER_LIMIT': 'register_limit:ip:{}'
}

# 登录类型
LOGIN_TYPE = {
    'NORMAL': 1,
    'SMS': 2
}

# 响应消息
MESSAGE = {
    'SUCCESS': '操作成功',
    'ERROR': '操作失败',
    'PARAM_ERROR': '参数校验失败',
    'AUTH_ERROR': '未授权访问',
    'TOKEN_EXPIRED': 'Token已过期',
    'TOKEN_INVALID': 'Token无效',
    'PERMISSION_DENIED': '权限不足',
    'ACCOUNT_DISABLED': '账号已禁用',
    'PASSWORD_EXPIRED': '密码已过期，请修改密码',
    'ACCOUNT_LOCKED': '账号已被锁定',
    'VERIFY_CODE_ERROR': '验证码错误或已过期',
    'DATA_NOT_FOUND': '数据不存在',
    'DATA_EXISTS': '数据已存在',
    'OPERATE_FAILED': '操作失败',
    'LOGIN_SUCCESS': '登录成功',
    'LOGIN_FAILED': '登录失败',
    'PASSWORD_ERROR': '密码错误',
    'AGENT_NOT_MATCH': 'Agent标识不匹配',
    'OLD_PASSWORD_ERROR': '原密码错误'
}
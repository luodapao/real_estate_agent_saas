"""
用户业务服务层
"""
from sqlalchemy.orm import Session
from admin.model.sys_user import SysUser
from admin.model.sys_token import SysToken
from admin.model.sys_user_role import SysUserRole
from admin.dao.user_dao import UserDAO
from admin.dao.token_dao import TokenDAO
from admin.schemas.user_schemas import (
    UserCreate, UserUpdate, UserResponse, UserDetailResponse,
    ResetPasswordRequest, GrantRoleRequest, PlatformUserCreate, PlatformUserUpdate
)
from config.exception import (
    AuthException, ParamException, PasswordExpiredException,
    AccountDisabledException, BusinessException
)
from config.constants import USER_STATUS, LOGIN_CONFIG
from config.settings import JWT_CONFIG
from core.jwt_util import JWTUtil
from core.pwd_util import PasswordUtil
from datetime import datetime, timedelta


class UserService:
    """用户业务服务"""
    
    @staticmethod
    def login(db: Session, account: str, password: str, agent_identifier: str, ip: str = None):
        """账号密码登录"""
        # 查询用户
        user = UserDAO.get_by_account(db, account)
        if not user:
            raise AuthException("账号或密码错误")
        
        # 检查账号状态
        if user.status == USER_STATUS['DISABLED']:
            raise AccountDisabledException("账号已被禁用")
        if user.status == USER_STATUS['LOCKED']:
            raise AccountDisabledException("账号已被锁定")
        if user.status == USER_STATUS['PENDING']:
            raise AccountDisabledException("账号待审核")
        
        # 验证密码
        if not PasswordUtil.verify_password(password, user.password):
            # 登录失败次数增加
            failed_count = user.login_failed_count + 1
            UserDAO.update_login_failed_count(db, user.user_id, failed_count)
            
            # 检查是否达到锁定阈值
            if failed_count >= LOGIN_CONFIG['max_failed_attempts']:
                UserDAO.lock_account(db, user.user_id)
                raise AuthException("登录失败次数过多，账号已被锁定")
            
            raise AuthException(f"账号或密码错误，还剩{LOGIN_CONFIG['max_failed_attempts'] - failed_count}次机会")
        
        # 重置登录失败次数
        UserDAO.reset_login_failed_count(db, user.user_id)
        
        # 检查密码是否过期
        if user.pwd_expire_time and datetime.now() > user.pwd_expire_time:
            raise PasswordExpiredException()
        
        # 生成Token
        return UserService.generate_token(db, user, agent_identifier, ip)
    
    @staticmethod
    def generate_token(db: Session, user: SysUser, agent_identifier: str, ip: str = None):
        """生成Token"""
        # 生成访问令牌和刷新令牌
        access_token = JWTUtil.create_access_token({
            'user_id': user.user_id,
            'tenant_id': user.tenant_id,
            'agent_identifier': agent_identifier
        })
        
        refresh_token = JWTUtil.create_refresh_token({
            'user_id': user.user_id,
            'tenant_id': user.tenant_id
        })
        
        # 计算过期时间
        expires_time = datetime.now() + timedelta(minutes=JWT_CONFIG['access_token_expire_minutes'])
        
        # 创建令牌记录
        token = SysToken(
            tenant_id=user.tenant_id,
            user_id=user.user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_time=expires_time,
            login_ip=ip
        )
        TokenDAO.create(db, token)
        
        # 更新最后登录信息
        UserDAO.update_last_login(db, user.user_id, ip)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': JWT_CONFIG['access_token_expire_minutes'] * 60,
            'user': UserResponse.from_orm(user).model_dump()
        }
    
    @staticmethod
    def logout(db: Session, access_token: str):
        """登出"""
        # 查询令牌记录
        token = TokenDAO.get_by_access_token(db, access_token)
        if token:
            # 作废数据库中的Token
            TokenDAO.invalidate(db, token.token_id)
            # 将Token加入黑名单
            JWTUtil.blacklist_token(access_token)
    
    @staticmethod
    def refresh_token(db: Session, refresh_token: str):
        """刷新Token"""
        # 查询刷新令牌
        token_info = TokenDAO.get_by_refresh_token(db, refresh_token)
        if not token_info:
            raise AuthException("刷新令牌无效")
        
        # 解码刷新令牌
        payload = JWTUtil.decode_token(refresh_token)
        if not payload:
            raise AuthException("刷新令牌已过期")
        
        user_id = payload.get('user_id')
        user = UserDAO.get(db, user_id)
        if not user:
            raise AuthException("用户不存在")
        
        # 生成新的访问令牌
        access_token = JWTUtil.create_access_token({
            'user_id': user.user_id,
            'tenant_id': user.tenant_id,
            'agent_identifier': 'web'
        })
        
        # 更新令牌记录
        TokenDAO.update(db, token_info.token_id, {
            'access_token': access_token,
            'expires_time': datetime.now() + timedelta(minutes=JWT_CONFIG['access_token_expire_minutes'])
        })
        
        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': JWT_CONFIG['access_token_expire_minutes'] * 60
        }
    
    @staticmethod
    def change_password(db: Session, user_id: int, old_password: str, new_password: str):
        """修改密码"""
        user = UserDAO.get(db, user_id)
        if not user:
            raise BusinessException("用户不存在")
        
        # 验证旧密码
        if not PasswordUtil.verify_password(old_password, user.password):
            raise ParamException("旧密码不正确")
        
        # 验证新密码强度
        if not PasswordUtil.is_password_strong(new_password):
            raise ParamException("新密码强度不足，需要包含大小写字母和数字，至少8位")
        
        # 更新密码
        hashed_password = PasswordUtil.hash_password(new_password)
        UserDAO.update_password(db, user_id, hashed_password)
        
        # 更新密码过期时间
        expire_time = datetime.now() + timedelta(days=LOGIN_CONFIG['password_expire_days'])
        UserDAO.update(db, user_id, {'pwd_expire_time': expire_time})
        
        # 强制用户重新登录（作废所有Token）
        TokenDAO.invalidate_by_user(db, user_id)
    
    @staticmethod
    def reset_password(db: Session, user_id: int, data: ResetPasswordRequest):
        """重置密码（管理员操作）"""
        user = UserDAO.get(db, user_id)
        if not user:
            raise BusinessException("用户不存在")
        
        # 验证新密码强度
        if not PasswordUtil.is_password_strong(data.new_password):
            raise ParamException("新密码强度不足，需要包含大小写字母和数字，至少8位")
        
        # 更新密码
        hashed_password = PasswordUtil.hash_password(data.new_password)
        UserDAO.update_password(db, user_id, hashed_password)
        
        # 更新密码过期时间
        expire_time = datetime.now() + timedelta(days=LOGIN_CONFIG['password_expire_days'])
        UserDAO.update(db, user_id, {'pwd_expire_time': expire_time})
        
        # 强制用户重新登录
        TokenDAO.invalidate_by_user(db, user_id)
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> UserDetailResponse:
        """查询用户详情"""
        user = UserDAO.get(db, user_id)
        if not user:
            raise BusinessException("用户不存在")
        return UserDetailResponse.from_orm(user)
    
    @staticmethod
    def get_user_list(db: Session, tenant_id: int, user_name: str = None, login_name: str = None, status: int = None, page: int = 1, size: int = 10):
        """分页查询用户列表"""
        total, data = UserDAO.get_list(db, tenant_id, user_name, status, page, size)
        user_list = [UserResponse.from_orm(user).model_dump() for user in data]
        return {
            'total': total,
            'page': page,
            'size': size,
            'data': user_list
        }
    
    @staticmethod
    def create_user(db: Session, tenant_id: int, data: UserCreate) -> UserResponse:
        """创建用户"""
        existing = UserDAO.get_by_account(db, data.account)
        if existing:
            raise ParamException("账号已存在")
        
        if not PasswordUtil.is_password_strong(data.password):
            raise ParamException("密码强度不足，需要包含大小写字母和数字，至少8位")
        
        expire_time = datetime.now() + timedelta(days=LOGIN_CONFIG['password_expire_days'])
        
        user = SysUser(
            tenant_id=tenant_id,
            account=data.account,
            password=PasswordUtil.hash_password(data.password),
            name=data.name,
            mobile=data.mobile,
            email=data.email,
            avatar=data.avatar,
            dept_id=data.dept_id,
            status=data.status or USER_STATUS['NORMAL'],
            user_type=data.user_type or 1,
            pwd_expire_time=expire_time,
            remark=data.remark
        )
        
        created_user = UserDAO.create(db, user)
        return UserResponse.from_orm(created_user)
    
    @staticmethod
    def update_user(db: Session, user_id: int, data: UserUpdate) -> UserResponse:
        """更新用户信息"""
        user = UserDAO.get(db, user_id)
        if not user:
            raise BusinessException("用户不存在")
        
        update_dict = data.model_dump(exclude_unset=True)
        
        updated_user = UserDAO.update(db, user_id, update_dict)
        return UserResponse.from_orm(updated_user)
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> UserResponse:
        """删除用户"""
        user = UserDAO.get(db, user_id)
        if not user:
            raise BusinessException("用户不存在")
        
        UserDAO.delete(db, user_id)
        return UserResponse.from_orm(user)
    
    @staticmethod
    def unlock_user(db: Session, user_id: int) -> UserResponse:
        """解锁用户"""
        user = UserDAO.get(db, user_id)
        if not user:
            raise BusinessException("用户不存在")
        
        unlocked_user = UserDAO.unlock_account(db, user_id)
        return UserResponse.from_orm(unlocked_user)
    
    @staticmethod
    def grant_role(db: Session, tenant_id: int, user_id: int, data: GrantRoleRequest):
        """给用户分配角色"""
        user = UserDAO.get(db, user_id)
        if not user:
            raise BusinessException("用户不存在")
        
        db.query(SysUserRole).filter(
            SysUserRole.user_id == user_id,
            SysUserRole.is_del == 0
        ).update({'is_del': 1})
        
        for role_id in data.role_ids:
            user_role = SysUserRole(
                tenant_id=tenant_id,
                user_id=user_id,
                role_id=role_id
            )
            db.add(user_role)
        
        db.commit()
        return {'user_id': user_id, 'role_ids': data.role_ids}
    
    # ========== 平台超级用户管理方法 ==========
    
    @staticmethod
    def create_platform_user(db: Session, data: PlatformUserCreate) -> UserResponse:
        """创建平台超级用户（tenant_id=0, user_type=0）"""
        existing = UserDAO.get_by_account(db, data.account)
        if existing:
            raise ParamException("账号已存在")
        
        if not PasswordUtil.is_password_strong(data.password):
            raise ParamException("密码强度不足，需要包含大小写字母和数字，至少8位")
        
        expire_time = datetime.now() + timedelta(days=LOGIN_CONFIG['password_expire_days'])
        
        user = SysUser(
            tenant_id=0,
            account=data.account,
            password=PasswordUtil.hash_password(data.password),
            name=data.name,
            mobile=data.mobile,
            email=data.email,
            status=data.status or USER_STATUS['NORMAL'],
            user_type=0,  # 平台超级管理员
            pwd_expire_time=expire_time,
            remark=data.remark
        )
        
        created_user = UserDAO.create(db, user)
        return UserResponse.from_orm(created_user)
    
    @staticmethod
    def get_platform_user_list(db: Session, user_name: str = None, login_name: str = None, status: int = None, page: int = 1, size: int = 10):
        """分页查询平台超级用户列表（tenant_id=0）"""
        total, data = UserDAO.get_platform_user_list(db, user_name, login_name, status, page, size)
        user_list = [UserResponse.from_orm(user).model_dump() for user in data]
        return {
            'total': total,
            'page': page,
            'size': size,
            'data': user_list
        }
    
    @staticmethod
    def update_platform_user(db: Session, user_id: int, data: PlatformUserUpdate) -> UserResponse:
        """更新平台超级用户"""
        user = UserDAO.get(db, user_id)
        if not user:
            raise BusinessException("用户不存在")
        
        if user.tenant_id != 0 or user.user_type != 0:
            raise BusinessException("只能更新平台超级用户")
        
        update_dict = data.model_dump(exclude_unset=True)
        
        updated_user = UserDAO.update(db, user_id, update_dict)
        return UserResponse.from_orm(updated_user)

"""
租户业务服务层
"""
from sqlalchemy.orm import Session
from admin.model.sys_tenant import SysTenant
from admin.model.sys_user import SysUser
from admin.model.sys_role import SysRole
from admin.model.sys_user_role import SysUserRole
from admin.dao.tenant_dao import TenantDAO
from admin.dao.user_dao import UserDAO
from admin.dao.role_dao import RoleDAO
from admin.schemas.tenant_schemas import TenantCreate, TenantUpdate, TenantResponse
from config.exception import BusinessException, ParamException
from config.constants import TENANT_STATUS, USER_STATUS
# from core.feishu_alert import FeishuAlert
from core.pwd_util import PasswordUtil
from datetime import datetime


class TenantService:
    """租户业务服务"""
    
    @staticmethod
    def get_tenant(db: Session, tenant_id: int) -> TenantResponse:
        """查询租户详情"""
        tenant = TenantDAO.get(db, tenant_id)
        if not tenant:
            raise BusinessException("租户不存在")
        return TenantResponse.from_orm(tenant)
    
    @staticmethod
    def get_tenant_by_code(db: Session, tenant_code: str) -> TenantResponse:
        """根据编码查询租户"""
        tenant = TenantDAO.get_by_code(db, tenant_code)
        if not tenant:
            raise BusinessException("租户不存在")
        return TenantResponse.from_orm(tenant)
    
    @staticmethod
    def get_tenant_list(db: Session, tenant_name: str = None, status: int = None, page: int = 1, size: int = 10):
        """分页查询租户列表"""
        total, data = TenantDAO.get_list(db, tenant_name, status, page, size)
        tenant_list = [TenantResponse.from_orm(tenant).model_dump() for tenant in data]
        return {
            'total': total,
            'page': page,
            'size': size,
            'data': tenant_list
        }
    
    @staticmethod
    def create_tenant(db: Session, data: TenantCreate) -> TenantResponse:
        """创建租户"""
        # 校验租户编码是否存在
        existing = TenantDAO.get_by_code(db, data.tenant_code)
        if existing:
            raise ParamException("租户编码已存在")
        
        tenant = SysTenant(
            tenant_name=data.tenant_name,
            tenant_code=data.tenant_code,
            contact_name=data.contact_name,
            contact_mobile=data.contact_mobile,
            email=data.email,
            address=data.address,
            remark=data.remark,
            expire_time=data.expire_time,
            status=data.status or TENANT_STATUS['NORMAL']
        )
        
        # 创建租户
        tenant = TenantDAO.create(db, tenant)
        
        # 创建租户超级管理员用户
        # 使用tenant_code作为登录账号，更符合业务习惯
        # 默认密码使用tenant_code，平台管理员可以后续重置
        sys_user = SysUser(
            tenant_id=tenant.tenant_id,
            account=data.tenant_code,
            password=PasswordUtil.hash_password(data.tenant_code),
            name=data.contact_name or data.tenant_name,
            mobile=data.contact_mobile,
            email=data.contact_email,
            status=USER_STATUS['NORMAL'],
            user_type=1  # 租户超级管理员
        )
        sys_user = UserDAO.create(db, sys_user)
        
        # 创建超级管理员角色
        admin_role = SysRole(
            tenant_id=tenant.tenant_id,
            role_name='超级管理员',
            role_code='admin',
            role_type=1,
            status=1,
            remark='租户超级管理员角色，拥有所有权限'
        )
        admin_role = RoleDAO.create(db, admin_role)
        
        # 关联用户和角色
        user_role = SysUserRole(
            tenant_id=tenant.tenant_id,
            user_id=sys_user.user_id,
            role_id=admin_role.role_id
        )
        db.add(user_role)
        db.commit()
        
        return TenantResponse.from_orm(tenant)
    
    @staticmethod
    def update_tenant(db: Session, tenant_id: int, data: TenantUpdate) -> TenantResponse:
        """更新租户信息"""
        tenant = TenantDAO.get(db, tenant_id)
        if not tenant:
            raise BusinessException("租户不存在")
        
        update_dict = data.model_dump(exclude_unset=True)
        updated_tenant = TenantDAO.update(db, tenant_id, update_dict)
        
        return TenantResponse.from_orm(updated_tenant)
    
    @staticmethod
    def delete_tenant(db: Session, tenant_id: int) -> TenantResponse:
        """删除租户"""
        tenant = TenantDAO.get(db, tenant_id)
        if not tenant:
            raise BusinessException("租户不存在")
        
        TenantDAO.delete(db, tenant_id)
        return TenantResponse.from_orm(tenant)
    
    @staticmethod
    def enable_tenant(db: Session, tenant_id: int) -> TenantResponse:
        """启用租户"""
        tenant = TenantDAO.get(db, tenant_id)
        if not tenant:
            raise BusinessException("租户不存在")
        
        enabled_tenant = TenantDAO.enable(db, tenant_id)
        return TenantResponse.from_orm(enabled_tenant)
    
    @staticmethod
    def disable_tenant(db: Session, tenant_id: int) -> TenantResponse:
        """禁用租户"""
        tenant = TenantDAO.get(db, tenant_id)
        if not tenant:
            raise BusinessException("租户不存在")
        
        disabled_tenant = TenantDAO.disable(db, tenant_id)
        return TenantResponse.from_orm(disabled_tenant)
    
    @staticmethod
    # 如何调用，需要定时任务
    def check_tenant_expire(db: Session):
        """检查租户到期并发送告警"""
        tenants = db.query(SysTenant).filter(
            SysTenant.status == TENANT_STATUS['NORMAL'],
            SysTenant.is_del == 0,
            SysTenant.expire_time.isnot(None)
        ).all()
        
        now = datetime.now()
        for tenant in tenants:
            # 检查是否即将到期（7天内）
            days_diff = (tenant.expire_time - now).days
            if 0 < days_diff <= 7:
                pass
                # FeishuAlert.send_tenant_expire_alert(
                #     tenant.tenant_name,
                #     tenant.contact_name,
                #     tenant.contact_mobile,
                #     tenant.expire_time.strftime('%Y-%m-%d')
                # )
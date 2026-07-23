"""
租户到期禁用任务
检测即将到期和已到期的租户，发送告警并禁用
"""

from datetime import datetime, timedelta
from sqlalchemy import update
from core.db_base import get_session
from admin.model.tenant_model import SysTenant
from admin.model.user_model import SysUser
from admin.model.user_token_model import SysUserToken
from core.feishu_alert import send_feishu_alert
from core.redis_base import get_redis_client
from config.constants import RedisKey, TenantStatus


def check_tenant_expire():
    """检查租户到期情况"""
    session = get_session()
    redis_client = get_redis_client()
    
    try:
        now = datetime.now()
        # 检查即将到期的租户（提前7天提醒）
        expire_soon_threshold = now + timedelta(days=7)
        
        # 查询即将到期的租户
        expire_soon_tenants = session.query(SysTenant).filter(
            SysTenant.status == TenantStatus.NORMAL,
            SysTenant.expire_date.between(now, expire_soon_threshold)
        ).all()
        
        # 发送即将到期告警
        for tenant in expire_soon_tenants:
            alert_msg = f"【租户到期提醒】租户 {tenant.tenant_name}({tenant.tenant_code}) 将在 {tenant.expire_date.strftime('%Y-%m-%d %H:%M')} 到期，请及时续费"
            send_feishu_alert(alert_msg)
            print(f"[{datetime.now()}] 发送租户到期提醒: {tenant.tenant_name}")
        
        # 查询已到期的租户
        expired_tenants = session.query(SysTenant).filter(
            SysTenant.status == TenantStatus.NORMAL,
            SysTenant.expire_date < now
        ).all()
        
        if not expired_tenants:
            print(f"[{datetime.now()}] 无已到期租户")
            return len(expire_soon_tenants), 0
        
        # 禁用已到期租户
        tenant_codes = []
        for tenant in expired_tenants:
            tenant.status = TenantStatus.EXPIRED
            tenant_codes.append(tenant.tenant_code)
            alert_msg = f"【租户已禁用】租户 {tenant.tenant_name}({tenant.tenant_code}) 已到期，已自动禁用"
            send_feishu_alert(alert_msg)
        
        session.commit()
        
        # 作废该租户下所有用户的Token
        expired_users = session.query(SysUser).filter(
            SysUser.tenant.in_(tenant_codes),
            SysUser.status == 1
        ).all()
        
        user_ids = [user.user_id for user in expired_users]
        tokens_to_invalidate = session.query(SysUserToken).filter(
            SysUserToken.user_id.in_(user_ids),
            SysUserToken.is_invalid == 0
        ).all()
        
        for token in tokens_to_invalidate:
            token.is_invalid = 1
            # 加入黑名单
            black_key = RedisKey.TOKEN_BLACK.format(access_token=token.access_token)
            redis_client.setex(black_key, 7200, "1")
        
        session.commit()
        
        print(f"[{datetime.now()}] 租户到期检查完成，即将到期 {len(expire_soon_tenants)} 个，已禁用 {len(expired_tenants)} 个，作废 {len(tokens_to_invalidate)} 个Token")
        return len(expire_soon_tenants), len(expired_tenants)
    except Exception as e:
        session.rollback()
        print(f"[{datetime.now()}] 租户到期检查失败: {str(e)}")
        return 0, 0
    finally:
        session.close()
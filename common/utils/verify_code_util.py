"""
验证码工具
用于生成和校验敏感操作验证码
"""

import random
import string
from datetime import datetime, timedelta
from core.db_base import get_session
from admin.model.verify_code_model import SysVerifyCode
from core.redis_base import get_redis_client
from config.constants import RedisKey


def generate_verify_code(length: int = 6) -> str:
    """生成指定长度的数字验证码"""
    return ''.join(random.choices(string.digits, k=length))


def save_verify_code(user_id: int, agent_identifier: str, perm_code: str) -> str:
    """保存验证码到数据库和Redis"""
    verify_code = generate_verify_code()
    
    # 计算过期时间（5分钟）
    expire_time = datetime.now() + timedelta(minutes=5)
    
    # 保存到数据库
    session = get_session()
    try:
        # 删除该用户之前未使用的验证码
        session.query(SysVerifyCode).filter(
            SysVerifyCode.user_id == user_id,
            SysVerifyCode.agent_identifier == agent_identifier,
            SysVerifyCode.is_used == 0
        ).delete()
        
        # 创建新验证码记录
        verify_code_record = SysVerifyCode(
            user_id=user_id,
            agent_identifier=agent_identifier,
            verify_code=verify_code,
            oper_perm_code=perm_code,
            expire_time=expire_time,
            is_used=0
        )
        session.add(verify_code_record)
        session.commit()
        
        # 保存到Redis
        redis_client = get_redis_client()
        redis_key = RedisKey.VERIFY_CODE.format(
            user_id=user_id,
            agent_identifier=agent_identifier
        )
        redis_client.setex(redis_key, 300, verify_code)
        
        return verify_code
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def verify_code(user_id: int, agent_identifier: str, code: str, perm_code: str) -> bool:
    """校验验证码"""
    session = get_session()
    try:
        # 先从Redis查询
        redis_client = get_redis_client()
        redis_key = RedisKey.VERIFY_CODE.format(
            user_id=user_id,
            agent_identifier=agent_identifier
        )
        cached_code = redis_client.get(redis_key)
        
        if cached_code and cached_code.decode('utf-8') == code:
            # 校验成功，标记为已使用
            session.query(SysVerifyCode).filter(
                SysVerifyCode.user_id == user_id,
                SysVerifyCode.agent_identifier == agent_identifier,
                SysVerifyCode.verify_code == code,
                SysVerifyCode.is_used == 0,
                SysVerifyCode.expire_time > datetime.now(),
                SysVerifyCode.oper_perm_code == perm_code
            ).update({'is_used': 1})
            session.commit()
            
            # 删除Redis缓存
            redis_client.delete(redis_key)
            return True
        
        # 从数据库查询
        verify_code_record = session.query(SysVerifyCode).filter(
            SysVerifyCode.user_id == user_id,
            SysVerifyCode.agent_identifier == agent_identifier,
            SysVerifyCode.verify_code == code,
            SysVerifyCode.is_used == 0,
            SysVerifyCode.expire_time > datetime.now(),
            SysVerifyCode.oper_perm_code == perm_code
        ).first()
        
        if verify_code_record:
            verify_code_record.is_used = 1
            session.commit()
            
            # 删除Redis缓存
            redis_client.delete(redis_key)
            return True
        
        return False
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()


def clear_expired_codes():
    """清理过期验证码"""
    session = get_session()
    try:
        deleted_count = session.query(SysVerifyCode).filter(
            SysVerifyCode.expire_time < datetime.now()
        ).delete()
        session.commit()
        return deleted_count
    except Exception as e:
        session.rollback()
        return 0
    finally:
        session.close()
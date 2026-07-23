"""
Agent闲置下线任务
检测Agent闲置72小时以上自动下线，作废所有Token
"""

from datetime import datetime, timedelta
from sqlalchemy import update
from core.db_base import SessionLocal
from admin.model.sys_token import SysToken
from config.constants import REDIS_KEY


def logout_idle_agents():
    """下线闲置超过72小时的Agent"""
    session = SessionLocal()
    idle_hours = 72
    
    try:
        idle_time_threshold = datetime.now() - timedelta(hours=idle_hours)
        
        idle_tokens = session.query(SysToken).filter(
            SysToken.status == 0,
            SysToken.updated_at < idle_time_threshold
        ).all()
        
        if not idle_tokens:
            print(f"[{datetime.now()}] 无闲置超过{idle_hours}小时的Agent")
            return 0
        
        user_ids = []
        access_tokens = []
        for token in idle_tokens:
            user_ids.append(token.user_id)
            access_tokens.append(token.access_token)
            token.status = 1
        
        session.commit()
        
        print(f"[{datetime.now()}] 下线闲置Agent完成，共作废 {len(idle_tokens)} 个Token，涉及 {len(set(user_ids))} 个用户")
        return len(idle_tokens)
    except Exception as e:
        session.rollback()
        print(f"[{datetime.now()}] 下线闲置Agent失败: {str(e)}")
        return 0
    finally:
        session.close()
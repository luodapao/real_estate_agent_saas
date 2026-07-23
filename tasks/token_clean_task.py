"""
过期Token清理任务
定期清理sys_user_token表中已过期的Token记录
"""

from datetime import datetime
from sqlalchemy import delete
from core.db_base import SessionLocal
from admin.model.sys_token import SysToken


def clean_expired_tokens():
    """清理过期Token"""
    session = SessionLocal()
    try:
        # 删除过期的Token记录
        delete_stmt = delete(SysToken).where(
            SysToken.expires_time < datetime.now()
        )
        result = session.execute(delete_stmt)
        session.commit()
        
        deleted_count = result.rowcount
        if deleted_count > 0:
            print(f"[{datetime.now()}] 清理过期Token完成，共删除 {deleted_count} 条记录")
        return deleted_count
    except Exception as e:
        session.rollback()
        print(f"[{datetime.now()}] 清理过期Token失败: {str(e)}")
        return 0
    finally:
        session.close()
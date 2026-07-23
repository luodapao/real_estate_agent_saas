"""
登录异常巡检告警任务
检测异常登录行为，发送安全告警
"""

from datetime import datetime, timedelta
from sqlalchemy import func
from core.db_base import get_session
from admin.model.login_log_model import SysLoginLog
from admin.model.user_model import SysUser
from core.feishu_alert import send_feishu_alert


def security_monitor():
    """安全巡检：检测异常登录行为"""
    session = get_session()
    
    try:
        now = datetime.now()
        # 检查最近1小时内登录失败超过5次的账号
        one_hour_ago = now - timedelta(hours=1)
        
        # 查询登录失败统计
        failed_login_stats = session.query(
            SysLoginLog.account,
            func.count(SysLoginLog.log_id).label('fail_count')
        ).filter(
            SysLoginLog.login_time >= one_hour_ago,
            SysLoginLog.login_result == 0
        ).group_by(SysLoginLog.account).having(
            func.count(SysLoginLog.log_id) >= 5
        ).all()
        
        for account, fail_count in failed_login_stats:
            alert_msg = f"【登录异常告警】账号 {account} 在最近1小时内登录失败 {fail_count} 次，请关注是否存在暴力破解攻击"
            send_feishu_alert(alert_msg)
            print(f"[{datetime.now()}] 发送登录异常告警: {account}, 失败次数: {fail_count}")
        
        # 检查异地登录
        # 查询最近24小时内同一个账号在不同地区登录的情况
        twenty_four_hours_ago = now - timedelta(hours=24)
        
        # 获取有多次登录记录的账号
        accounts_with_multiple_logins = session.query(
            SysLoginLog.account
        ).filter(
            SysLoginLog.login_time >= twenty_four_hours_ago,
            SysLoginLog.login_result == 1
        ).group_by(SysLoginLog.account).having(
            func.count(SysLoginLog.log_id) >= 2
        ).all()
        
        for (account,) in accounts_with_multiple_logins:
            # 获取该账号最近24小时的登录IP地区
            ip_areas = session.query(
                SysLoginLog.ip_area
            ).filter(
                SysLoginLog.account == account,
                SysLoginLog.login_time >= twenty_four_hours_ago,
                SysLoginLog.login_result == 1,
                SysLoginLog.ip_area.isnot(None)
            ).distinct().all()
            
            areas = [area[0] for area in ip_areas]
            if len(areas) >= 2:
                alert_msg = f"【异地登录告警】账号 {account} 在最近24小时内从多个地区登录: {', '.join(areas)}"
                send_feishu_alert(alert_msg)
                print(f"[{datetime.now()}] 发送异地登录告警: {account}, 地区: {areas}")
        
        print(f"[{datetime.now()}] 安全巡检完成")
        return True
    except Exception as e:
        print(f"[{datetime.now()}] 安全巡检失败: {str(e)}")
        return False
    finally:
        session.close()
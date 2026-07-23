"""
定时任务全局注册
注册所有定时任务，使用APScheduler调度
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from tasks.token_clean_task import clean_expired_tokens
from tasks.idle_logout_task import logout_idle_agents
from tasks.tenant_expire_task import check_tenant_expire
from tasks.security_monitor_task import security_monitor


# 全局调度器实例
scheduler = None

def start_scheduler():
    """启动定时任务调度器"""
    global scheduler
    
    if scheduler is not None:
        print("定时任务调度器已启动")
        return
    
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    
    # 注册定时任务
    
    # 1. 过期Token清理 - 每小时执行一次
    scheduler.add_job(
        clean_expired_tokens,
        CronTrigger(hour='*'),
        id='token_clean_task',
        name='过期Token清理',
        replace_existing=True
    )
    
    # 2. Agent闲置下线 - 每天凌晨3点执行
    scheduler.add_job(
        logout_idle_agents,
        CronTrigger(hour=3, minute=0),
        id='idle_logout_task',
        name='Agent闲置下线',
        replace_existing=True
    )
    
    # 3. 租户到期检查 - 每6小时执行一次
    scheduler.add_job(
        check_tenant_expire,
        CronTrigger(hour='0,6,12,18'),
        id='tenant_expire_task',
        name='租户到期检查',
        replace_existing=True
    )
    
    # 4. 安全巡检 - 每小时执行一次
    scheduler.add_job(
        security_monitor,
        CronTrigger(hour='*'),
        id='security_monitor_task',
        name='安全巡检告警',
        replace_existing=True
    )
    

    
    # 启动调度器
    scheduler.start()
    print("定时任务调度器启动完成，共注册 {} 个任务".format(len(scheduler.get_jobs())))

def stop_scheduler():
    """停止定时任务调度器"""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        print("定时任务调度器已停止")
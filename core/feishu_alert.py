"""
飞书全局告警推送工具
"""
import json
import requests
from config.settings import FEISHU_CONFIG


class FeishuAlert:
    """飞书告警工具类"""
    
    @staticmethod
    def send_alert(title: str, content: str):
        """发送飞书告警消息"""
        if not FEISHU_CONFIG['webhook_url']:
            return None
        
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        
        payload = {
            "msg_type": "text",
            "content": {
                "text": f"【{title}】\n{content}"
            }
        }
        
        try:
            response = requests.post(
                FEISHU_CONFIG['webhook_url'],
                headers=headers,
                data=json.dumps(payload)
            )
            return response.json()
        except Exception as e:
            print(f"飞书告警发送失败: {e}")
            return None
    
    @staticmethod
    def send_security_alert(account: str, ip: str, alert_type: str, detail: str):
        """发送安全告警"""
        title = "安全告警"
        content = f"账号: {account}\nIP: {ip}\n告警类型: {alert_type}\n详情: {detail}"
        return FeishuAlert.send_alert(title, content)
    
    @staticmethod
    def send_tenant_expire_alert(tenant_name: str, expire_date: str):
        """发送租户到期告警"""
        title = "租户到期提醒"
        content = f"租户: {tenant_name}\n到期时间: {expire_date}"
        return FeishuAlert.send_alert(title, content)
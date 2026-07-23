"""
IP归属地工具
用于获取IP地址的地理位置信息
"""

import socket
import requests


def get_ip_location(ip: str) -> str:
    """获取IP地址归属地"""
    if not ip:
        return "未知"
    
    # 本地IP不查询
    if ip.startswith('127.') or ip.startswith('192.168.') or ip == '::1':
        return "本地网络"
    
    try:
        # 使用ipinfo.io查询IP归属地
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            city = data.get('city', '')
            region = data.get('region', '')
            country = data.get('country', '')
            
            location_parts = []
            if country:
                location_parts.append(country)
            if region:
                location_parts.append(region)
            if city:
                location_parts.append(city)
            
            return ', '.join(location_parts) if location_parts else "未知"
    except Exception as e:
        print(f"获取IP归属地失败: {str(e)}")
    
    return "未知"


def get_client_ip(request) -> str:
    """从请求中获取客户端IP"""
    # 检查X-Forwarded-For头（代理场景）
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    
    # 检查X-Real-IP头
    x_real_ip = request.headers.get('X-Real-IP')
    if x_real_ip:
        return x_real_ip
    
    # 直接获取远程地址
    client_host = request.client.host if request.client else 'unknown'
    
    # 如果是IPv6本地地址，转换为IPv4表示
    if client_host == '::1':
        return '127.0.0.1'
    
    return client_host


def is_local_ip(ip: str) -> bool:
    """判断是否为本地IP"""
    if not ip:
        return False
    
    local_prefixes = [
        '127.',
        '192.168.',
        '10.',
        '172.16.',
        '172.17.',
        '172.18.',
        '172.19.',
        '172.20.',
        '172.21.',
        '172.22.',
        '172.23.',
        '172.24.',
        '172.25.',
        '172.26.',
        '172.27.',
        '172.28.',
        '172.29.',
        '172.30.',
        '172.31.',
        '::1',
        'localhost'
    ]
    
    return any(ip.startswith(prefix) for prefix in local_prefixes)
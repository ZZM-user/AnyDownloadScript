import socket

import requests


def get_local_ip() -> str:
    """获取本机局域网 IP"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 不需要实际连接，只是触发路由查找
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_public_ip() -> str:
    """获取公网 IP"""
    try:
        resp = requests.get("https://api.ipify.org?format=json", timeout = 5)
        if resp.status_code == 200:
            return resp.json().get("ip", "")
    except Exception:
        return "无法获取公网 IP"

import logging
import os
import socket

from dotenv import load_dotenv


def get_avatars_url(key):
    if not key or key.startswith("http"):
        return key
    return f"{os.getenv('QINIU_DOMAIN')}/{key}-slim"


def get_local_ip():
    """自动获取本机局域网 IPv4 地址"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 连接到一个外部地址（不需要实际连通）
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


import os


def get_env_file_path():
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 向上查找直到找到.env文件或到达根目录
    while True:
        env_path = os.path.join(current_dir, ".env")
        if os.path.isfile(env_path):
            return env_path
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            # 已到达文件系统根目录
            return None
        current_dir = parent_dir


def load_env():
    dotenv_path = get_env_file_path()
    logging.info(f"加载环境变量文件: {dotenv_path}")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)


if __name__ == "__main__":
    ip = get_local_ip()
    print(ip)

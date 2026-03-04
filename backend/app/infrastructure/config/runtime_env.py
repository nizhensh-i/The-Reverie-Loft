import logging
import os
import socket

from dotenv import load_dotenv


def get_local_ip() -> str:
    """自动获取本机局域网 IPv4 地址"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_env_file_path() -> str | None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        env_path = os.path.join(current_dir, ".env")
        if os.path.isfile(env_path):
            return env_path
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            return None
        current_dir = parent_dir


def load_env():
    dotenv_path = get_env_file_path()
    logging.info(f"加载环境变量文件: {dotenv_path}")
    if dotenv_path and os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

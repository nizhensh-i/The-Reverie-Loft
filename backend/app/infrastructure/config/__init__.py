"""
基础设施配置管理中心
集中管理所有第三方扩展的配置，避免配置分散在代码各处
"""

import os
from typing import Optional


class InfraConfig:
    """
    基础设施配置中心
    提供统一的配置管理接口，避免在代码中硬编码配置
    """

    @staticmethod
    def is_testing() -> bool:
        """判断是否处于测试环境"""
        return os.getenv("FLASK_CONFIG") == "testing"

    @staticmethod
    def get_redis_password() -> str:
        """
        获取 Redis 密码
        测试环境不使用密码
        """
        return "" if InfraConfig.is_testing() else ":1234@"

    @staticmethod
    def get_redis_host() -> str:
        """获取 Redis 主机地址"""
        return os.getenv("REDIS_HOST") or os.getenv("FLASK_RUN_HOST") or "127.0.0.1"

    @staticmethod
    def build_redis_url(
        db: int = 0, host: Optional[str] = None, password: Optional[str] = None
    ) -> str:
        """
        构建 Redis URL

        Args:
            db: Redis 数据库编号
            host: Redis 主机地址，为 None 时使用环境变量
            password: Redis 密码，为 None 时使用默认密码

        Returns:
            Redis 连接 URL
        """
        redis_pass = (
            password if password is not None else InfraConfig.get_redis_password()
        )
        redis_host = host if host is not None else InfraConfig.get_redis_host()
        return f"redis://{redis_pass}{redis_host}:6379/{db}"

    @staticmethod
    def get_mail_credentials() -> dict:
        """
        获取邮件服务凭证

        Returns:
            dict: 包含 MAIL_USERNAME 和 MAIL_PASSWORD 的字典
        """
        return {
            "username": os.getenv("MAIL_USERNAME"),
            "password": os.getenv("MAIL_PASSWORD"),
        }

    @staticmethod
    def has_mail_credentials() -> bool:
        """检查是否配置了邮件服务凭证"""
        credentials = InfraConfig.get_mail_credentials()
        return bool(credentials["username"] and credentials["password"])

    @staticmethod
    def get_database_uri() -> Optional[str]:
        """获取数据库 URI"""
        from flask import current_app

        try:
            return current_app.config.get("SQLALCHEMY_DATABASE_URI")
        except RuntimeError:
            # 当没有应用上下文时，从环境变量获取
            return os.getenv("DATABASE_URL")

    @staticmethod
    def is_database_configured() -> bool:
        """检查是否配置了数据库"""
        return bool(InfraConfig.get_database_uri())

    @staticmethod
    def get_socketio_config() -> dict:
        """
        获取 SocketIO 配置

        Returns:
            dict: SocketIO 配置选项
        """
        from flask import current_app

        try:
            message_queue = current_app.config.get("SOCKETIO_MESSAGE_QUEUE")
        except RuntimeError:
            message_queue = None

        return {
            "cors_allowed_origins": "*",
            "ping_timeout": 30,
            "ping_interval": 60,
            "message_queue": message_queue or InfraConfig.build_redis_url(db=4),
        }


from .runtime_env import get_env_file_path, get_local_ip, load_env

__all__ = ["InfraConfig", "get_local_ip", "get_env_file_path", "load_env"]

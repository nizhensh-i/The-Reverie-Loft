"""
基础设施层异常定义
统一异常体系，避免抛出字符串或使用不明确的异常类型
"""

from ..exceptions import AppError


class InfrastructureError(AppError):
    """基础设施层基础异常"""

    default_code = 500
    default_message = "基础设施服务异常"

    def __init__(
        self,
        message: str = None,
        component: str = None,
        original_error: Exception = None,
        code: int = None,
    ):
        super().__init__(message=message, code=code)
        self.component = component
        self.original_error = original_error


class ConfigurationError(InfrastructureError):
    """配置错误 - 当配置缺失或无效时抛出"""

    default_code = 500
    default_message = "基础设施配置错误"


class DatabaseError(InfrastructureError):
    """数据库相关异常"""

    default_code = 500
    default_message = "数据库服务异常"


class CacheError(InfrastructureError):
    """缓存相关异常"""

    default_code = 500
    default_message = "缓存服务异常"


class StorageError(InfrastructureError):
    """存储服务异常（文件上传/删除等）"""

    default_code = 500
    default_message = "存储服务异常"


class MailError(InfrastructureError):
    """邮件服务异常"""

    default_code = 500
    default_message = "邮件服务异常"


class AuthenticationError(InfrastructureError):
    """认证服务异常"""

    default_code = 401
    default_message = "认证服务异常"


class RateLimitError(InfrastructureError):
    """限流服务异常"""

    default_code = 429
    default_message = "请求频率超限"


class MessagingError(InfrastructureError):
    """消息队列/WebSocket 服务异常"""

    default_code = 500
    default_message = "消息服务异常"


__all__ = [
    "InfrastructureError",
    "ConfigurationError",
    "DatabaseError",
    "CacheError",
    "StorageError",
    "MailError",
    "AuthenticationError",
    "RateLimitError",
    "MessagingError",
]

"""
应用层统一异常定义
"""


class AppError(Exception):
    """全局统一基类异常"""

    default_code = 500
    default_message = "服务器内部错误"

    def __init__(self, message=None, code=None):
        self.message = message or self.default_message
        self.code = code if code is not None else self.default_code
        super().__init__(self.message)


class ValidationError(AppError, ValueError):
    """参数或领域校验错误"""

    default_code = 400
    default_message = "参数错误"


class BusinessError(AppError):
    """通用业务异常"""

    default_code = 400
    default_message = "业务处理失败"


class PermissionDeniedError(AppError):
    """业务权限不足"""

    default_code = 403
    default_message = "权限不足"


class NotFoundError(AppError):
    """业务资源不存在"""

    default_code = 404
    default_message = "资源不存在"


__all__ = [
    "AppError",
    "ValidationError",
    "BusinessError",
    "PermissionDeniedError",
    "NotFoundError",
]

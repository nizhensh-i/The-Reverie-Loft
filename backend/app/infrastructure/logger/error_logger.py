"""
日志工具模块
提供统一的日志记录接口和错误日志记录工具
"""

import logging
from typing import Optional

from .logger import setup_logging


def log_infrastructure_error(
    error: Exception,
    component: str,
    operation: str,
    level: str = "error",
    extra: Optional[dict] = None,
):
    """
    统一的基础设施错误日志记录

    Args:
        error: 异常对象
        component: 组件名称（如 'database', 'cache', 'mail'）
        operation: 操作描述（如 'query_user', 'send_email'）
        level: 日志级别（'error', 'warning', 'critical'）
        extra: 额外信息
    """
    logger = logging.getLogger(f"infra.{component}")

    # 构建错误消息
    error_msg = f"[{component}.{operation}] {type(error).__name__}: {str(error)}"

    # 构建日志上下文
    context = {
        "component": component,
        "operation": operation,
        "error_type": type(error).__name__,
    }

    if extra:
        context.update(extra)

    # 记录日志
    if level.lower() == "error":
        logger.error(error_msg, exc_info=True, extra=context)
    elif level.lower() == "warning":
        logger.warning(error_msg, exc_info=True, extra=context)
    elif level.lower() == "critical":
        logger.critical(error_msg, exc_info=True, extra=context)
    else:
        logger.error(error_msg, exc_info=True, extra=context)


def log_database_error(
    operation: str, error: Exception, query: Optional[str] = None, **kwargs
):
    """
    记录数据库错误日志

    Args:
        operation: 数据库操作描述
        error: 异常对象
        query: SQL 查询语句（可选）
        **kwargs: 其他上下文信息
    """
    extra = kwargs
    if query:
        extra["query"] = query

    log_infrastructure_error(
        error=error,
        component="database",
        operation=operation,
        level="error",
        extra=extra,
    )


def log_cache_error(
    operation: str, error: Exception, key: Optional[str] = None, **kwargs
):
    """
    记录缓存错误日志

    Args:
        operation: 缓存操作描述
        error: 异常对象
        key: 缓存键（可选）
        **kwargs: 其他上下文信息
    """
    extra = kwargs
    if key:
        extra["cache_key"] = key

    log_infrastructure_error(
        error=error,
        component="cache",
        operation=operation,
        level="warning",  # 缓存错误通常为警告级别
        extra=extra,
    )


def log_mail_error(
    operation: str, error: Exception, recipient: Optional[str] = None, **kwargs
):
    """
    记录邮件错误日志

    Args:
        operation: 邮件操作描述
        error: 异常对象
        recipient: 收件人（可选）
        **kwargs: 其他上下文信息
    """
    extra = kwargs
    if recipient:
        extra["recipient"] = recipient

    log_infrastructure_error(
        error=error,
        component="mail",
        operation=operation,
        level="error",
        extra=extra,
    )


def log_storage_error(
    operation: str, error: Exception, key: Optional[str] = None, **kwargs
):
    """
    记录存储服务错误日志

    Args:
        operation: 存储操作描述
        error: 异常对象
        key: 文件键名（可选）
        **kwargs: 其他上下文信息
    """
    extra = kwargs
    if key:
        extra["storage_key"] = key

    log_infrastructure_error(
        error=error,
        component="storage",
        operation=operation,
        level="error",
        extra=extra,
    )


def get_logger(component: str) -> logging.Logger:
    """
    获取指定组件的日志记录器

    Args:
        component: 组件名称

    Returns:
        logging.Logger: 日志记录器
    """
    return logging.getLogger(f"infra.{component}")


__all__ = [
    "setup_logging",
    "log_infrastructure_error",
    "log_database_error",
    "log_cache_error",
    "log_mail_error",
    "log_storage_error",
    "get_logger",
]

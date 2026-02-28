"""
基础设施层接口抽象
定义基础设施组件应该实现的接口，遵循依赖倒置原则
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class CacheInterface(ABC):
    """缓存服务接口"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, timeout: int = None) -> bool:
        """设置缓存值"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存"""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """清空所有缓存"""
        pass


class StorageInterface(ABC):
    """文件存储服务接口"""

    @abstractmethod
    def upload(self, file_data: bytes, key: str, **kwargs) -> str:
        """
        上传文件

        Args:
            file_data: 文件二进制数据
            key: 文件存储键名
            **kwargs: 其他参数（如 content_type 等）

        Returns:
            str: 文件访问 URL
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        删除文件

        Args:
            key: 文件存储键名

        Returns:
            bool: 是否删除成功
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        检查文件是否存在

        Args:
            key: 文件存储键名

        Returns:
            bool: 文件是否存在
        """
        pass

    @abstractmethod
    def get_url(self, key: str, expires_in: int = 3600) -> str:
        """
        获取文件访问 URL

        Args:
            key: 文件存储键名
            expires_in: URL 过期时间（秒）

        Returns:
            str: 文件访问 URL
        """
        pass


class MailInterface(ABC):
    """邮件服务接口"""

    @abstractmethod
    def send(
        self, to: str, subject: str, body: str, html: bool = False, **kwargs
    ) -> bool:
        """
        发送邮件

        Args:
            to: 收件人邮箱
            subject: 邮件主题
            body: 邮件内容
            html: 是否为 HTML 格式
            **kwargs: 其他参数（如 cc, bcc, attachments 等）

        Returns:
            bool: 是否发送成功
        """
        pass

    @abstractmethod
    def send_bulk(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        html: bool = False,
        **kwargs
    ) -> bool:
        """
        批量发送邮件

        Args:
            recipients: 收件人邮箱列表
            subject: 邮件主题
            body: 邮件内容
            html: 是否为 HTML 格式
            **kwargs: 其他参数

        Returns:
            bool: 是否发送成功
        """
        pass


class LoggerInterface(ABC):
    """日志服务接口"""

    @abstractmethod
    def debug(self, message: str, **kwargs):
        """记录 DEBUG 级别日志"""
        pass

    @abstractmethod
    def info(self, message: str, **kwargs):
        """记录 INFO 级别日志"""
        pass

    @abstractmethod
    def warning(self, message: str, **kwargs):
        """记录 WARNING 级别日志"""
        pass

    @abstractmethod
    def error(self, message: str, **kwargs):
        """记录 ERROR 级别日志"""
        pass

    @abstractmethod
    def critical(self, message: str, **kwargs):
        """记录 CRITICAL 级别日志"""
        pass


class AuthenticationInterface(ABC):
    """认证服务接口"""

    @abstractmethod
    def create_token(self, identity: Any, **kwargs) -> str:
        """
        创建认证令牌

        Args:
            identity: 用户标识
            **kwargs: 其他参数（如过期时间等）

        Returns:
            str: 认证令牌
        """
        pass

    @abstractmethod
    def verify_token(self, token: str) -> Optional[Any]:
        """
        验证认证令牌

        Args:
            token: 认证令牌

        Returns:
            Optional[Any]: 验证通过返回用户标识，否则返回 None
        """
        pass

    @abstractmethod
    def revoke_token(self, token: str) -> bool:
        """
        撤销认证令牌

        Args:
            token: 认证令牌

        Returns:
            bool: 是否撤销成功
        """
        pass


class RateLimiterInterface(ABC):
    """限流服务接口"""

    @abstractmethod
    def check_limit(self, key: str, limit: int, period: int) -> bool:
        """
        检查是否超过限流

        Args:
            key: 限流键
            limit: 限制次数
            period: 时间周期（秒）

        Returns:
            bool: True 表示未超过限制，False 表示已超过限制
        """
        pass

    @abstractmethod
    def get_remaining(self, key: str, limit: int, period: int) -> int:
        """
        获取剩余可用次数

        Args:
            key: 限流键
            limit: 限制次数
            period: 时间周期（秒）

        Returns:
            int: 剩余可用次数
        """
        pass


class MessageQueueInterface(ABC):
    """消息队列服务接口"""

    @abstractmethod
    def publish(self, channel: str, message: Any) -> bool:
        """
        发布消息

        Args:
            channel: 消息频道
            message: 消息内容

        Returns:
            bool: 是否发布成功
        """
        pass

    @abstractmethod
    def subscribe(self, channel: str, callback: Callable) -> bool:
        """
        订阅消息

        Args:
            channel: 消息频道
            callback: 消息回调函数

        Returns:
            bool: 是否订阅成功
        """
        pass


class DatabaseInterface(ABC):
    """数据库服务接口"""

    @abstractmethod
    def execute(self, query: str, params: dict = None) -> Any:
        """
        执行 SQL 查询

        Args:
            query: SQL 查询语句
            params: 查询参数

        Returns:
            Any: 查询结果
        """
        pass

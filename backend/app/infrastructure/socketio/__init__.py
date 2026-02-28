import logging

from flask_socketio import SocketIO

from ..capabilities import capability_enabled, get_capability, set_capability
from ..config import InfraConfig
from ..exceptions import MessagingError

_socketio_client = None

socketio = SocketIO()


class NoopSocketIOClient:
    """Redis 不可用时的空实现，保持调用方不崩溃。"""

    @staticmethod
    def emit(*args, **kwargs):
        return None


def build_message_queue_url():
    """构建消息队列 URL"""
    return InfraConfig.build_redis_url(db=4)


def setup_socketio(app):
    """初始化 SocketIO"""
    try:
        config = InfraConfig.get_socketio_config()
        if capability_enabled("redis", default=True):
            message_queue = (
                app.config.get("SOCKETIO_MESSAGE_QUEUE") or config["message_queue"]
            )
            set_capability("socketio", enabled=True, degraded=False, reason="")
        else:
            # Redis 不可用时关闭跨进程消息队列，保留当前进程通信能力。
            message_queue = None
            reason = (get_capability("redis") or {}).get("reason", "redis unavailable")
            set_capability(
                "socketio",
                enabled=True,
                degraded=True,
                reason=f"message_queue disabled: {reason}",
            )
            logging.warning("SocketIO 降级运行：message_queue 已禁用")
        socketio.init_app(
            app,
            cors_allowed_origins=config["cors_allowed_origins"],
            ping_timeout=config["ping_timeout"],
            ping_interval=config["ping_interval"],
            message_queue=message_queue,
        )
        return socketio
    except Exception as e:
        set_capability("socketio", enabled=False, degraded=True, reason=str(e))
        raise MessagingError(
            f"初始化 SocketIO 失败: {str(e)}", component="socketio", original_error=e
        )


def get_socketio_client():
    """
    供 Celery / 后台任务使用的 SocketIO 客户端实例（通过 Redis 消息队列）
    """
    global _socketio_client
    if not capability_enabled("redis", default=True):
        return NoopSocketIOClient()

    if not _socketio_client:
        try:
            _socketio_client = SocketIO(message_queue=build_message_queue_url())
        except Exception as e:
            set_capability(
                "socketio_client", enabled=False, degraded=True, reason=str(e)
            )
            logging.warning("SocketIO 客户端降级为 Noop: %s", e)
            return NoopSocketIOClient()
    set_capability("socketio_client", enabled=True, degraded=False, reason="")
    return _socketio_client

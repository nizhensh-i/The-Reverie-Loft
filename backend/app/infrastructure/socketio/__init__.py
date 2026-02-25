import os

from flask_socketio import SocketIO

_socketio_client = None

socketio = SocketIO()


def _build_redis_pass():
    # github工作流上redis容器不使用密码
    return "" if os.getenv("FLASK_CONFIG") == "testing" else ":1234@"


def build_message_queue_url():
    redis_pass = _build_redis_pass()
    redis_host = os.getenv("REDIS_HOST") or os.getenv("FLASK_RUN_HOST") or "127.0.0.1"
    return f"redis://{redis_pass}{redis_host}:6379/4"


def setup_socketio(app):
    socketio.init_app(
        app,
        cors_allowed_origins="*",
        ping_timeout=30,
        ping_interval=60,
        message_queue=app.config.get("SOCKETIO_MESSAGE_QUEUE")
        or build_message_queue_url(),
    )
    return socketio


def get_socketio_client():
    """
    供 Celery / 后台任务使用的 SocketIO 客户端实例（通过 Redis 消息队列）
    """
    global _socketio_client
    if not _socketio_client:
        _socketio_client = SocketIO(message_queue=build_message_queue_url())
    return _socketio_client

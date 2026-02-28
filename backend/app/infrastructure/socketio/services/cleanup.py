import logging
import time
from threading import Event, Thread


class WebSocketCleanupService:
    """WebSocket 后台清理服务"""

    CLEANUP_INTERVAL = 60

    def __init__(self, redis, presence, connection):
        self.redis = redis
        self.presence = presence
        self.connection = connection
        self.stop_event = Event()
        self.cleanup_thread = None

    def start(self):
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            logging.warning("清理服务已经在运行")
            return

        self.stop_event.clear()
        self.cleanup_thread = Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        logging.info("WebSocket 后台清理服务已启动")

    def stop(self):
        if not self.cleanup_thread or not self.cleanup_thread.is_alive():
            return

        logging.info("正在停止 WebSocket 清理服务...")
        self.stop_event.set()
        self.cleanup_thread.join(timeout=5)

        if self.cleanup_thread.is_alive():
            logging.warning("清理线程未能在 5 秒内停止，强制终止")
        else:
            logging.info("WebSocket 清理服务已停止")

    def _cleanup_loop(self):
        while not self.stop_event.is_set():
            try:
                self._cleanup_timeout_users()
                self._cleanup_orphan_sockets()
            except Exception as e:
                logging.error(f"清理任务执行失败: {str(e)}", exc_info=True)

            self.stop_event.wait(self.CLEANUP_INTERVAL)

    def _cleanup_timeout_users(self):
        online_users = self.redis.smembers("online:users")
        if not online_users:
            return

        current_time = int(time.time())
        timeout_count = 0

        for user_id_str in online_users:
            user_id = int(user_id_str)
            status = self.presence.get_user_presence(user_id)

            if not status:
                self.presence.mark_user_offline(user_id)
                timeout_count += 1
                logging.warning(f"清理孤立在线状态: user_id={user_id}")
                continue

            last_active = int(status.get("last_active", 0))
            time_diff = current_time - last_active

            if time_diff > self.presence.HEARTBEAT_TIMEOUT:
                self.presence.mark_user_offline(user_id)
                timeout_count += 1
                logging.info(
                    f"用户心跳超时: user_id={user_id}, "
                    f"超时时间={time_diff}秒, "
                    f"最后活跃={last_active}"
                )

        if timeout_count > 0:
            logging.info(f"清理完成: 共清理 {timeout_count} 个超时用户")

    def _cleanup_orphan_sockets(self):
        socket_keys = self.redis.keys("socket:*")
        if not socket_keys:
            return

        orphan_count = 0
        for socket_key in socket_keys:
            sid = socket_key.replace("socket:", "")
            user_id = self.redis.get(socket_key)

            if not user_id:
                self.redis.delete(socket_key)
                orphan_count += 1
                logging.warning(f"清理孤立 socket: sid={sid}")
                continue

            user_sockets_key = f"user:{user_id}:sockets"
            if not self.redis.sismember(user_sockets_key, sid):
                self.redis.delete(socket_key)
                orphan_count += 1
                logging.warning(f"清理不一致 socket: sid={sid}, user_id={user_id}")

        if orphan_count > 0:
            logging.info(f"清理完成: 共清理 {orphan_count} 个孤立 socket")

    def cleanup_all(self):
        logging.warning("正在清理所有 WebSocket 相关数据...")

        online_users = self.redis.smembers("online:users")
        for user_id in online_users:
            self.presence.mark_user_offline(int(user_id))

        socket_keys = self.redis.keys("socket:*")
        if socket_keys:
            self.redis.delete(*socket_keys)

        user_socket_keys = self.redis.keys("user:*:sockets")
        if user_socket_keys:
            self.redis.delete(*user_socket_keys)

        active_chat_keys = self.redis.keys("user:*:active_chat")
        if active_chat_keys:
            self.redis.delete(*active_chat_keys)

        logging.warning("所有 WebSocket 数据已清理")

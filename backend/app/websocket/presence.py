import time


class UserPresenceService:
    """
    管理用户在线状态与活跃信息

    结构设计:
    Key: online:users  ->    { user_id1, user_id2, ... }
    Type: SET
    是否在线的唯一判断


    Key: user:{user_id}:status  ->
    Type: HASH
    Fields:
    - online       -> 0 / 1
    - last_active  -> unix_timestamp
    """

    # 心跳超时时间：5分钟（300秒）
    HEARTBEAT_TIMEOUT = 300

    def __init__(self, redis):
        self.redis = redis

    # ---------- 状态变更（明确副作用） ----------

    def mark_user_online(self, user_id: int):
        """
        将用户标记为在线
        """
        pipe = self.redis.pipeline()
        pipe.sadd("online:users", user_id)
        pipe.hset(
            f"user:{user_id}:status",
            mapping={"online": 1, "last_active": int(time.time())},
        )
        pipe.execute()

    def mark_user_offline(self, user_id: int):
        """
        将用户标记为离线
        """
        pipe = self.redis.pipeline()
        pipe.srem("online:users", user_id)
        pipe.hset(f"user:{user_id}:status", "online", 0)
        pipe.execute()

    def update_last_active(self, user_id: int):
        """
        更新用户最后活跃时间
        """
        self.redis.hset(f"user:{user_id}:status", "last_active", int(time.time()))

    # ---------- 查询（无副作用） ----------

    def is_user_online(self, user_id: int) -> bool:
        """
        判断用户是否在线（检查心跳是否超时）
        """
        if not self.redis.sismember("online:users", user_id):
            return False

        # 检查最后活跃时间是否超时
        status = self.get_user_presence(user_id)
        if not status:
            return False

        last_active = int(status.get("last_active", 0))
        current_time = int(time.time())

        # 如果超过心跳超时时间，认为已离线
        if current_time - last_active > self.HEARTBEAT_TIMEOUT:
            # 异步清理（不阻塞当前调用）
            self.mark_user_offline(user_id)
            return False

        return True

    def list_online_users(self) -> set[int]:
        """
        获取所有在线用户 ID（过滤心跳超时的用户）
        """
        online_users = self.redis.smembers("online:users")
        active_users = set()

        for user_id in online_users:
            user_id_int = int(user_id)
            if self.is_user_online(user_id_int):  # 这会检查心跳超时
                active_users.add(user_id_int)

        return active_users

    def count_online_users(self) -> int:
        """
        获取在线用户数量（过滤心跳超时）
        """
        return len(self.list_online_users())

    def get_user_presence(self, user_id: int) -> dict:
        """
        获取用户在线相关状态
        """
        return self.redis.hgetall(f"user:{user_id}:status") or {}

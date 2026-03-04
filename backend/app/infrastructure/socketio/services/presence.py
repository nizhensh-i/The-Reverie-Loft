import time


class UserPresenceService:
    """
    管理用户在线状态与活跃信息

    结构设计:
    Key: online:users  -> { user_id1, user_id2, ... }
    Type: SET

    Key: user:{user_id}:status ->
    Type: HASH
    Fields:
    - online       -> 0 / 1
    - last_active  -> unix_timestamp
    """

    HEARTBEAT_TIMEOUT = 300

    def __init__(self, redis):
        self.redis = redis

    def mark_user_online(self, user_id: int):
        pipe = self.redis.pipeline()
        pipe.sadd("online:users", user_id)
        pipe.hset(
            f"user:{user_id}:status",
            mapping={"online": 1, "last_active": int(time.time())},
        )
        pipe.execute()

    def mark_user_offline(self, user_id: int):
        pipe = self.redis.pipeline()
        pipe.srem("online:users", user_id)
        pipe.hset(f"user:{user_id}:status", "online", 0)
        pipe.execute()

    def update_last_active(self, user_id: int):
        self.redis.hset(f"user:{user_id}:status", "last_active", int(time.time()))

    def is_user_online(self, user_id: int) -> bool:
        if not self.redis.sismember("online:users", user_id):
            return False

        status = self.get_user_presence(user_id)
        if not status:
            return False

        last_active = int(status.get("last_active", 0))
        if int(time.time()) - last_active > self.HEARTBEAT_TIMEOUT:
            self.mark_user_offline(user_id)
            return False

        return True

    def list_online_users(self) -> set[int]:
        online_users = self.redis.smembers("online:users")
        active_users = set()

        for user_id in online_users:
            user_id_int = int(user_id)
            if self.is_user_online(user_id_int):
                active_users.add(user_id_int)

        return active_users

    def count_online_users(self) -> int:
        return len(self.list_online_users())

    def get_user_presence(self, user_id: int) -> dict:
        return self.redis.hgetall(f"user:{user_id}:status") or {}

class WSConnectionManager:
    """
    管理 socket <-> user_id 的绑定关系

    结构设计:
    Key: user:{user_id}:sockets  ->  { sid1, sid2, sid3, ... }
    Type: SET
    一个用户可以有多个 websocket 连接

    Key: socket:{sid}   ->  user_id
    Type: STRING
    用于通过 sid 快速反查 user
    """

    def __init__(self, redis):
        self.redis = redis

    def bind_socket_to_user(self, user_id: int, sid: str):
        """建立 socket 与用户的绑定关系"""
        pipe = self.redis.pipeline()
        pipe.sadd(f"user:{user_id}:sockets", sid)
        pipe.set(f"socket:{sid}", user_id)
        pipe.execute()

    def unbind_socket(self, sid: str) -> int | None:
        """解除 socket 与用户的绑定关系并返回 user_id"""
        user_id = self.redis.get(f"socket:{sid}")
        if not user_id:
            return None

        user_id = int(user_id)
        pipe = self.redis.pipeline()
        pipe.srem(f"user:{user_id}:sockets", sid)
        pipe.delete(f"socket:{sid}")
        pipe.execute()
        return user_id

    def get_bound_sockets(self, user_id: int) -> set[str]:
        """查询用户当前绑定的所有 socket"""
        return self.redis.smembers(f"user:{user_id}:sockets") or set()

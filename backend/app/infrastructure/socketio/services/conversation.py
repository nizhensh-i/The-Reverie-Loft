class ConversationStateService:
    """
    管理用户会话行为态（active_chat / typing）
    """

    ACTIVE_CHAT_TTL = 60 * 5
    TYPING_TTL = 3

    def __init__(self, redis):
        self.redis = redis

    def set_active_chat(self, user_id: int, target_user_id: int):
        self.redis.set(
            f"user:{user_id}:active_chat", target_user_id, ex=self.ACTIVE_CHAT_TTL
        )

    def clear_active_chat(self, user_id: int):
        self.redis.delete(f"user:{user_id}:active_chat")

    def get_active_chat(self, user_id: int) -> int | None:
        value = self.redis.get(f"user:{user_id}:active_chat")
        return int(value) if value else None

    def mark_typing(self, user_id: int, target_user_id: int):
        self.redis.set(f"typing:{user_id}:{target_user_id}", 1, ex=self.TYPING_TTL)

    def is_typing(self, user_id: int, target_user_id: int) -> bool:
        return self.redis.exists(f"typing:{user_id}:{target_user_id}")

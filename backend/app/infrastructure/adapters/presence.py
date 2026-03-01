from ...domain.ports.presence import PresencePort


class RedisPresenceAdapter(PresencePort):
    def __init__(self, presence_service):
        self._presence = presence_service

    def list_online_user_ids(self) -> set[int]:
        return self._presence.list_online_users()

from .cleanup import WebSocketCleanupService
from .connection import WSConnectionManager
from .conversation import ConversationStateService
from .presence import UserPresenceService


def init_ws_services(redis):
    connection = WSConnectionManager(redis)
    presence = UserPresenceService(redis)
    conversation = ConversationStateService(redis)
    cleanup = WebSocketCleanupService(redis, presence, connection)
    return connection, presence, conversation, cleanup


__all__ = [
    "WSConnectionManager",
    "UserPresenceService",
    "ConversationStateService",
    "WebSocketCleanupService",
    "init_ws_services",
]

from __future__ import annotations

from ..domain.common.exceptions import NotFoundError
from ..domain.ports.notifications import NotificationDispatcherPort


class ChatWsService:
    def __init__(self, *, uow_factory, notifier: NotificationDispatcherPort):
        self.uow_factory = uow_factory
        self.notifier = notifier

    def get_user_identity(self, *, user_id: int):
        uow = self.uow_factory()
        user = uow.users.get_by_id(user_id)
        if not user:
            raise NotFoundError("用户不存在")
        return user.username, user.id

    def mark_enter_chat_read(self, *, user_id: int, target_id: int):
        uow = self.uow_factory()
        try:
            updated_messages = uow.messages.mark_all_unread_from_sender(
                receiver_id=user_id,
                sender_id=target_id,
            )
            updated_notifications = uow.notifications.mark_chat_read(
                receiver_id=user_id,
                trigger_user_id=target_id,
            )
            uow.commit()
            return {
                "updated_messages": int(updated_messages or 0),
                "updated_notifications": int(updated_notifications or 0),
            }
        except Exception:
            uow.rollback()
            raise

    def create_message(
        self, *, sender_id: int, receiver_id: int, content: str, mark_read: bool
    ):
        uow = self.uow_factory()
        try:
            message = uow.messages.create_message(
                sender_id=sender_id,
                receiver_id=receiver_id,
                content=content,
                is_read=mark_read,
            )
            uow.messages.add(message)
            uow.flush()
            message_id = message.id
            uow.commit()
            return uow.messages.get_message_detail(message_id)
        except Exception:
            uow.rollback()
            raise

    def dispatch_chat_notification(
        self, *, receiver_id: int, sender_id: int, message_id: int
    ):
        self.notifier.dispatch_chat(
            receiver_id=receiver_id,
            sender_id=sender_id,
            message_id=message_id,
        )

from ...domain.ports.notifications import NotificationDispatcherPort
from ..my_celery import (
    create_chat_notifications,
    create_comment_notifications,
    create_like_notifications,
    create_new_post_notifications,
)


class CeleryNotificationDispatcher(NotificationDispatcherPort):
    def dispatch_new_post(
        self, *, post_id: int, author_id: int, follower_ids: list[int]
    ) -> None:
        create_new_post_notifications.delay(post_id, author_id, follower_ids)

    def dispatch_comment(
        self,
        *,
        post_id: int,
        comment_id: int,
        trigger_user_id: int,
        notifications_data,
    ) -> None:
        create_comment_notifications.delay(
            post_id,
            comment_id,
            trigger_user_id,
            notifications_data,
        )

    def dispatch_like(
        self,
        *,
        post_id: int,
        comment_id: int | None,
        liker_id: int,
        receiver_id: int | None,
    ) -> None:
        if receiver_id is None:
            return
        create_like_notifications.delay(post_id, comment_id, liker_id, receiver_id)

    def dispatch_chat(
        self, *, receiver_id: int, sender_id: int, message_id: int
    ) -> None:
        create_chat_notifications.delay(receiver_id, sender_id, message_id)

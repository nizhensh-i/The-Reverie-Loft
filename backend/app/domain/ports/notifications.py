from __future__ import annotations

from typing import Protocol


class NotificationDispatcherPort(Protocol):
    def dispatch_new_post(
        self, *, post_id: int, author_id: int, follower_ids: list[int]
    ) -> None:
        ...

    def dispatch_comment(
        self,
        *,
        post_id: int,
        comment_id: int,
        trigger_user_id: int,
        notifications_data,
    ) -> None:
        ...

    def dispatch_like(
        self,
        *,
        post_id: int,
        comment_id: int | None,
        liker_id: int,
        receiver_id: int | None,
    ) -> None:
        ...

    def dispatch_chat(
        self, *, receiver_id: int, sender_id: int, message_id: int
    ) -> None:
        ...

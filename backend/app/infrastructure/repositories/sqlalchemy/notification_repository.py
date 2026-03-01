from sqlalchemy.orm import joinedload

from ....domain.notification.repositories import NotificationRepository
from ....infrastructure.persistence.models import Notification, NotificationType, User


class SqlAlchemyNotificationRepository(NotificationRepository):
    def __init__(self, session):
        self.session = session

    @staticmethod
    def list_by_receiver(*, user_id: int):
        return (
            Notification.query.options(
                joinedload(Notification.trigger_user).load_only(
                    User.id, User.username, User.nickname, User.image
                )
            )
            .filter_by(receiver_id=user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )

    @staticmethod
    def mark_read(*, user_id: int, ids: list[int]) -> None:
        Notification.query.filter(
            Notification.id.in_(ids), Notification.receiver_id == user_id
        ).update({"is_read": True}, synchronize_session=False)

    @staticmethod
    def mark_chat_read(*, receiver_id: int, trigger_user_id: int) -> int:
        return (
            Notification.query.filter_by(
                receiver_id=receiver_id,
                trigger_user_id=trigger_user_id,
                type=NotificationType.CHAT,
            )
            .filter(Notification.is_read.is_(False))
            .update({"is_read": True}, synchronize_session=False)
        )

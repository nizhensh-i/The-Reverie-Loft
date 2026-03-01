from sqlalchemy.orm import joinedload

from ....domain.common.repositories import PageEntities
from ....domain.message.repositories import MessageRepository
from ....infrastructure.persistence.models import Message, User


class SqlAlchemyMessageRepository(MessageRepository):
    def __init__(self, session):
        self.session = session

    @staticmethod
    def list_conversation_messages(
        *, current_user_id: int, other_user_id: int, page: int, per_page: int
    ) -> PageEntities:
        query = Message.query.filter(
            (
                (Message.sender_id == current_user_id)
                & (Message.receiver_id == other_user_id)
            )
            | (
                (Message.sender_id == other_user_id)
                & (Message.receiver_id == current_user_id)
            )
        ).order_by(Message.timestamp.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return PageEntities(items=pagination.items, total=pagination.total)

    @staticmethod
    def mark_conversation_read(
        *, current_user_id: int, sender_user_id: int, message_ids: list[int]
    ) -> None:
        Message.query.filter(
            Message.id.in_(message_ids),
            Message.receiver_id == current_user_id,
            Message.sender_id == sender_user_id,
        ).update({"is_read": True}, synchronize_session=False)

    @staticmethod
    def mark_all_unread_from_sender(*, receiver_id: int, sender_id: int) -> int:
        return Message.query.filter(
            Message.receiver_id == receiver_id,
            Message.sender_id == sender_id,
            Message.is_read.is_(False),
        ).update({"is_read": True}, synchronize_session=False)

    @staticmethod
    def create_message(
        *, sender_id: int, receiver_id: int, content: str, is_read: bool = False
    ):
        return Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            is_read=is_read,
        )

    def add(self, message) -> None:
        self.session.add(message)

    @staticmethod
    def get_message_detail(message_id: int):
        return (
            Message.query.options(
                joinedload(Message.sender).load_only(
                    User.id, User.username, User.nickname, User.image
                )
            )
            .filter(Message.id == message_id)
            .first()
        )

from flask import current_app

from ..infrastructure.database.sqlalchemy import db
from ..models import Message
from .common.dto import ActionResult, PageResult
from .common.unit_of_work import SqlAlchemyUnitOfWork


class MessageService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.uow = SqlAlchemyUnitOfWork(self.session)

    def list_conversation_messages(
        self, *, current_user_id: int, other_user_id: int, page: int
    ):
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
        pagination = query.paginate(
            page=page,
            per_page=current_app.config["FLASKY_CHAT_PER_PAGE"],
            error_out=False,
        )
        messages = pagination.items
        result = []
        index = len(messages)
        for message in messages:
            item = message.to_json()
            item.update({"id": index})
            result.append(item)
            index -= 1
        return PageResult(data=result, total=pagination.total)

    def mark_conversation_messages_read(
        self, *, current_user_id: int, sender_user_id: int, message_ids: list[int]
    ):
        Message.query.filter(
            Message.id.in_(message_ids),
            Message.receiver_id == current_user_id,
            Message.sender_id == sender_user_id,
        ).update({"is_read": True}, synchronize_session=False)
        self.uow.commit()
        return ActionResult(message="消息已标记为已读")

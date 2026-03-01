from ..application.dto import ActionResult, PageResult
from ..domain.common.unit_of_work import UnitOfWork
from ..domain.message.policies import (
    build_conversation_message_items,
    normalize_message_ids,
)
from ..domain.ports.assemblers import ResponseAssemblerPort
from ..domain.ports.settings import PaginationSettingsPort


class MessageService:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        assembler: ResponseAssemblerPort,
        settings: PaginationSettingsPort,
    ):
        self.uow = uow
        self.assembler = assembler
        self.settings = settings

    def list_conversation_messages(
        self, *, current_user_id: int, other_user_id: int, page: int
    ):
        page_entities = self.uow.messages.list_conversation_messages(
            current_user_id=current_user_id,
            other_user_id=other_user_id,
            page=page,
            per_page=self.settings.chat_per_page(),
        )
        return PageResult(
            data=build_conversation_message_items(
                page_entities.items,
                serializer=self.assembler.map_message,
            ),
            total=page_entities.total,
        )

    def update_conversation_messages_read(
        self, *, current_user_id: int, sender_user_id: int, message_ids: list[int]
    ):
        normalized_ids = normalize_message_ids(message_ids)
        if not normalized_ids:
            return ActionResult(message="消息已标记为已读")
        self.uow.messages.mark_conversation_read(
            current_user_id=current_user_id,
            sender_user_id=sender_user_id,
            message_ids=normalized_ids,
        )
        self.uow.commit()
        return ActionResult(message="消息已标记为已读")

    def mark_conversation_messages_read(
        self, *, current_user_id: int, sender_user_id: int, message_ids: list[int]
    ):
        return self.update_conversation_messages_read(
            current_user_id=current_user_id,
            sender_user_id=sender_user_id,
            message_ids=message_ids,
        )

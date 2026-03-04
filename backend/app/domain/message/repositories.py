from abc import ABC, abstractmethod

from ..common.repositories import PageEntities


class MessageRepository(ABC):
    @abstractmethod
    def list_conversation_messages(
        self, *, current_user_id: int, other_user_id: int, page: int, per_page: int
    ) -> PageEntities:
        raise NotImplementedError

    @abstractmethod
    def mark_conversation_read(
        self, *, current_user_id: int, sender_user_id: int, message_ids: list[int]
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def mark_all_unread_from_sender(self, *, receiver_id: int, sender_id: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def create_message(
        self, *, sender_id: int, receiver_id: int, content: str, is_read: bool = False
    ):
        raise NotImplementedError

    @abstractmethod
    def add(self, message) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_message_detail(self, message_id: int):
        raise NotImplementedError

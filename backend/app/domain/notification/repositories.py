from abc import ABC, abstractmethod


class NotificationRepository(ABC):
    @abstractmethod
    def list_by_receiver(self, *, user_id: int):
        raise NotImplementedError

    @abstractmethod
    def mark_read(self, *, user_id: int, ids: list[int]) -> None:
        raise NotImplementedError

    @abstractmethod
    def mark_chat_read(self, *, receiver_id: int, trigger_user_id: int) -> int:
        raise NotImplementedError

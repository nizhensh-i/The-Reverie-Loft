from abc import ABC, abstractmethod

from ..common.repositories import PageEntities


class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int):
        raise NotImplementedError

    @abstractmethod
    def get_by_username(self, username: str):
        raise NotImplementedError

    @abstractmethod
    def get_role_by_id(self, role_id: int):
        raise NotImplementedError

    @abstractmethod
    def list_user_posts(
        self, *, user_id: int, page: int, per_page: int
    ) -> PageEntities:
        raise NotImplementedError

    @abstractmethod
    def list_by_ids(self, user_ids: list[int]):
        raise NotImplementedError

    @abstractmethod
    def add(self, entity) -> None:
        raise NotImplementedError

    @abstractmethod
    def init_roles(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def touch_last_seen(self, *, user_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def build_user_extra_data(
        self, *, user_id: int, viewer_id: int | None = None
    ) -> dict:
        raise NotImplementedError

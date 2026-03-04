from abc import ABC, abstractmethod


class OAuthRepository(ABC):
    @abstractmethod
    def username_exists(self, username: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_user_by_id(self, user_id: int):
        raise NotImplementedError

    @abstractmethod
    def get_account_by_provider_uuid(self, *, provider: str, uuid: str):
        raise NotImplementedError

    @abstractmethod
    def get_account_by_provider_user(self, *, provider: str, user_id: int):
        raise NotImplementedError

    @abstractmethod
    def count_user_accounts(self, *, user_id: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def add(self, entity) -> None:
        raise NotImplementedError

    @abstractmethod
    def create_user(
        self,
        *,
        username: str,
        nickname: str | None,
        image: str | None,
        password: str,
        has_password: bool,
    ):
        raise NotImplementedError

    @abstractmethod
    def create_account(self, *, provider: str, user_id: int, profile: dict):
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity) -> None:
        raise NotImplementedError

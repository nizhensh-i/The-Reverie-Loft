from abc import ABC, abstractmethod


class AuthRepository(ABC):
    @abstractmethod
    def get_user_by_username(self, username: str):
        raise NotImplementedError

    @abstractmethod
    def get_user_by_email(self, email: str):
        raise NotImplementedError

    @abstractmethod
    def get_role_by_name(self, role_name: str):
        raise NotImplementedError

    @abstractmethod
    def add_user(self, user) -> None:
        raise NotImplementedError

    @abstractmethod
    def create_user(
        self,
        *,
        email: str | None,
        username: str,
        password: str,
        image: str,
        has_password: bool = True,
        nickname: str | None = None,
    ):
        raise NotImplementedError

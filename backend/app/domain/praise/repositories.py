from abc import ABC, abstractmethod


class PraiseRepository(ABC):
    @abstractmethod
    def list_praised_comment_ids_for_post(self, *, user_id: int, post_id: int):
        raise NotImplementedError

    @abstractmethod
    def get_post(self, post_id: int):
        raise NotImplementedError

    @abstractmethod
    def get_comment(self, comment_id: int):
        raise NotImplementedError

    @abstractmethod
    def exists_post_praise(self, *, user_id: int, post_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def exists_comment_praise(self, *, user_id: int, comment_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def add(self, praise) -> None:
        raise NotImplementedError

    @abstractmethod
    def create_post_praise(self, *, post, author):
        raise NotImplementedError

    @abstractmethod
    def create_comment_praise(self, *, comment, author):
        raise NotImplementedError

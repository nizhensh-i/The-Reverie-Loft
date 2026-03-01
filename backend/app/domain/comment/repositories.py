from abc import ABC, abstractmethod

from ..common.repositories import PageEntities


class CommentRepository(ABC):
    @abstractmethod
    def get_post(self, post_id: int):
        raise NotImplementedError

    @abstractmethod
    def get_comment(self, comment_id: int):
        raise NotImplementedError

    @abstractmethod
    def list_replies(
        self, *, root_comment_id: int, page: int, per_page: int
    ) -> PageEntities:
        raise NotImplementedError

    @abstractmethod
    def list_post_root_comments(
        self, *, post_id: int, page: int, per_page: int
    ) -> PageEntities:
        raise NotImplementedError

    @abstractmethod
    def list_all_comments(self, *, page: int, per_page: int) -> PageEntities:
        raise NotImplementedError

    @abstractmethod
    def add(self, comment) -> None:
        raise NotImplementedError

    @abstractmethod
    def create_comment(
        self,
        *,
        post,
        author,
        body: str,
        direct_parent=None,
        root_comment=None,
    ):
        raise NotImplementedError

    @abstractmethod
    def delete(self, comment) -> None:
        raise NotImplementedError

    @abstractmethod
    def resolve_notification_type(self, *, notification_type_code: str):
        raise NotImplementedError

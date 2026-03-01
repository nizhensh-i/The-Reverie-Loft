from abc import ABC, abstractmethod
from typing import Any

from ..common.repositories import PageEntities


class PostRepository(ABC):
    @abstractmethod
    def create_post(
        self,
        *,
        author,
        content: str,
        summary: str,
        post_type_value: str,
        has_image: bool,
    ):
        raise NotImplementedError

    @abstractmethod
    def list_posts(
        self, *, page: int, per_page: int, viewer=None, tab_name: str | None = None
    ) -> PageEntities[Any]:
        raise NotImplementedError

    @abstractmethod
    def get_post_detail(self, post_id: int):
        raise NotImplementedError

    @abstractmethod
    def get_post_for_update(self, post_id: int):
        raise NotImplementedError

    @abstractmethod
    def get_active_post(self, post_id: int):
        raise NotImplementedError

    @abstractmethod
    def add(self, post) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_images(self, image_entities) -> None:
        raise NotImplementedError

    @abstractmethod
    def create_post_images(self, image_payloads):
        raise NotImplementedError

    @abstractmethod
    def set_post_type(self, post, *, post_type_value: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_follower_ids(self, *, author_id: int) -> list[int]:
        raise NotImplementedError

    @abstractmethod
    def list_posts_without_summary(self):
        raise NotImplementedError

    @abstractmethod
    def list_posts_without_content(self):
        raise NotImplementedError

    @abstractmethod
    def list_post_ids_with_images(self):
        raise NotImplementedError

    @abstractmethod
    def bulk_mark_posts_has_image(self, post_ids: list[int]) -> None:
        raise NotImplementedError

    @abstractmethod
    def count_posts(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def count_posts_has_image(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def count_posts_with_content(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, post_id: int):
        raise NotImplementedError

    @abstractmethod
    def build_post_extra_data_map(
        self, posts, *, viewer_id: int | None = None
    ) -> dict[int, dict]:
        raise NotImplementedError

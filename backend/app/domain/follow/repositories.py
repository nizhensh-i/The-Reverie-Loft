from abc import ABC, abstractmethod

from ..common.repositories import PageEntities


class FollowRepository(ABC):
    @abstractmethod
    def list_matched_following_users(self, *, user_id: int, search_query: str):
        raise NotImplementedError

    @abstractmethod
    def list_matched_follower_users(self, *, user_id: int, search_query: str):
        raise NotImplementedError

    @abstractmethod
    def list_followers(self, *, user_id: int, page: int, per_page: int) -> PageEntities:
        raise NotImplementedError

    @abstractmethod
    def list_following(self, *, user_id: int, page: int, per_page: int) -> PageEntities:
        raise NotImplementedError

    @abstractmethod
    def list_followed_ids(
        self, *, follower_id: int, candidate_ids: list[int]
    ) -> set[int]:
        raise NotImplementedError

    @abstractmethod
    def list_follower_ids(
        self, *, followed_id: int, candidate_ids: list[int]
    ) -> set[int]:
        raise NotImplementedError

    @abstractmethod
    def exists_follow_relation(self, *, follower_id: int, followed_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create_follow_relation(self, *, follower_id: int, followed_id: int):
        raise NotImplementedError

    @abstractmethod
    def add(self, entity) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_follow_relation(self, *, follower_id: int, followed_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def ensure_self_follows(self) -> int:
        raise NotImplementedError

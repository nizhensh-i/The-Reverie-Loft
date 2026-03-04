from abc import ABC, abstractmethod

from ..common.repositories import PageEntities


class LogRepository(ABC):
    @abstractmethod
    def list_logs(self, *, page: int, per_page: int) -> PageEntities:
        raise NotImplementedError

    @abstractmethod
    def delete_by_ids(self, ids: list[int]) -> int:
        raise NotImplementedError

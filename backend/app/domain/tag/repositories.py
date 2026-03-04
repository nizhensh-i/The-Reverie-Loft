from abc import ABC, abstractmethod


class TagRepository(ABC):
    @abstractmethod
    def list_all(self):
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, name: str):
        raise NotImplementedError

    @abstractmethod
    def list_by_names(self, names: set[str]):
        raise NotImplementedError

    @abstractmethod
    def add(self, tag) -> None:
        raise NotImplementedError

    @abstractmethod
    def create_tag(self, *, name: str):
        raise NotImplementedError

    @abstractmethod
    def add_all(self, tags) -> None:
        raise NotImplementedError

    @abstractmethod
    def create_tags(self, *, names):
        raise NotImplementedError

    @abstractmethod
    def delete(self, tag) -> None:
        raise NotImplementedError

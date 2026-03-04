from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    posts = None
    comments = None
    users = None
    follows = None
    tags = None
    auth = None
    oauth = None
    uploads = None
    notifications = None
    messages = None
    logs = None
    praises = None

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def flush(self) -> None:
        raise NotImplementedError

from abc import ABC, abstractmethod


class UploadRepository(ABC):
    @abstractmethod
    def list_interest_images(self, *, user_id: int, image_type):
        raise NotImplementedError

    @abstractmethod
    def add_all(self, entities) -> None:
        raise NotImplementedError

    @abstractmethod
    def create_interest_images(
        self, *, user_id: int, interest_type_code: str, urls, names
    ):
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity) -> None:
        raise NotImplementedError

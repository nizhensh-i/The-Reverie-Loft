from sqlalchemy import and_

from ....domain.upload.repositories import UploadRepository
from ....infrastructure.persistence.models import Image, ImageType


class SqlAlchemyUploadRepository(UploadRepository):
    def __init__(self, session):
        self.session = session

    @staticmethod
    def list_interest_images(*, user_id: int, image_type):
        image_type_map = {
            "movie": ImageType.MOVIE,
            "book": ImageType.BOOK,
        }
        resolved_image_type = image_type_map[image_type]
        return Image.query.filter(
            and_(Image.type == resolved_image_type, Image.related_id == user_id)
        ).all()

    def add_all(self, entities) -> None:
        if entities:
            self.session.add_all(entities)

    @staticmethod
    def create_interest_images(*, user_id: int, interest_type_code: str, urls, names):
        image_type_map = {
            "movie": ImageType.MOVIE,
            "book": ImageType.BOOK,
        }
        image_type = image_type_map[interest_type_code]
        return [
            Image(url=url, type=image_type, describe=name, related_id=user_id)
            for url, name in zip(urls, names)
        ]

    def delete(self, entity) -> None:
        self.session.delete(entity)

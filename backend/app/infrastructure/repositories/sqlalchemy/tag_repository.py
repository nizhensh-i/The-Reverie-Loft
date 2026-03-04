from ....domain.tag.repositories import TagRepository
from ....infrastructure.persistence.models import Tag


class SqlAlchemyTagRepository(TagRepository):
    def __init__(self, session):
        self.session = session

    @staticmethod
    def list_all():
        return Tag.query.all()

    @staticmethod
    def get_by_name(name: str):
        return Tag.query.filter_by(name=name).first()

    @staticmethod
    def list_by_names(names: set[str]):
        if not names:
            return []
        return Tag.query.filter(Tag.name.in_(names)).all()

    def add(self, tag) -> None:
        self.session.add(tag)

    @staticmethod
    def create_tag(*, name: str):
        return Tag(name=name)

    def add_all(self, tags) -> None:
        if tags:
            self.session.add_all(tags)

    @staticmethod
    def create_tags(*, names):
        return [Tag(name=name) for name in names if name]

    def delete(self, tag) -> None:
        self.session.delete(tag)

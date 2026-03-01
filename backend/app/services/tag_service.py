from ..infrastructure.database.sqlalchemy import db
from ..models import Tag
from .common.dto import ActionResult, ListResult
from .common.unit_of_work import SqlAlchemyUnitOfWork


class TagService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.uow = SqlAlchemyUnitOfWork(self.session)

    def rollback(self):
        self.uow.rollback()

    def list_tags(self):
        tags = Tag.query.all()
        return ListResult(data=[tag.name for tag in tags])

    def update_user_tags(self, *, user, tag_add: set[str], tag_remove: set[str]):
        for tag_name in tag_add:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                self.session.add(tag)
            user.tags.append(tag)

        for tag_name in tag_remove:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                user.tags.remove(tag)
        self.uow.commit()
        return ActionResult(message="用户标签更新成功")

    def update_public_tags(self, *, tag_add: set[str], tag_remove: set[str]):
        to_add = [Tag(name=tag) for tag in tag_add if tag]
        if to_add:
            self.session.add_all(to_add)

        if tag_remove:
            tags_to_delete = Tag.query.filter(Tag.name.in_(tag_remove)).all()
            for tag in tags_to_delete:
                self.session.delete(tag)
        self.uow.commit()
        return ActionResult(message="公共标签库更新成功")

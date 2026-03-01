from ..application.dto import ActionResult, ListResult
from ..domain.common.unit_of_work import UnitOfWork
from ..domain.tag.policies import normalize_tag_changes


class TagService:
    def __init__(self, *, uow: UnitOfWork):
        self.uow = uow

    def rollback(self):
        self.uow.rollback()

    def list_tags(self):
        tags = self.uow.tags.list_all()
        return ListResult(data=[tag.name for tag in tags])

    @staticmethod
    def can_update_user_tags(*, operator, target_user_id: int) -> bool:
        return bool(
            operator and (operator.is_administrator() or operator.id == target_user_id)
        )

    def update_user_tags(self, *, user, tag_add: set[str], tag_remove: set[str]):
        tag_add, tag_remove = normalize_tag_changes(
            tag_add=tag_add, tag_remove=tag_remove
        )
        for tag_name in tag_add:
            tag = self.uow.tags.get_by_name(tag_name)
            if not tag:
                tag = self.uow.tags.create_tag(name=tag_name)
                self.uow.tags.add(tag)
            user.tags.append(tag)

        for tag_name in tag_remove:
            tag = self.uow.tags.get_by_name(tag_name)
            if tag:
                user.tags.remove(tag)
        self.uow.commit()
        return ActionResult(message="用户标签更新成功")

    def update_public_tags(self, *, tag_add: set[str], tag_remove: set[str]):
        tag_add, tag_remove = normalize_tag_changes(
            tag_add=tag_add, tag_remove=tag_remove
        )
        to_add = self.uow.tags.create_tags(names=tag_add)
        self.uow.tags.add_all(to_add)

        if tag_remove:
            tags_to_delete = self.uow.tags.list_by_names(tag_remove)
            for tag in tags_to_delete:
                self.uow.tags.delete(tag)
        self.uow.commit()
        return ActionResult(message="公共标签库更新成功")

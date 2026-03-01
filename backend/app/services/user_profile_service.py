from ..domain.common.exceptions import NotFoundError
from ..infrastructure.database.sqlalchemy import db
from ..infrastructure.storage import get_random_user_avatars
from ..models import User
from ..utils.common import get_avatars_url
from .common.dto import ActionResult, ItemResult
from .common.unit_of_work import SqlAlchemyUnitOfWork


class UserProfileService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.uow = SqlAlchemyUnitOfWork(self.session)

    def rollback(self):
        self.uow.rollback()

    def get_user_by_id(self, user_id: int):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("用户不存在")
        return user

    def get_user_by_username(self, username: str):
        user = User.query.filter_by(username=username).first()
        if not user:
            raise NotFoundError("用户不存在")
        return user

    def update_user_profile(self, *, user, payload: dict):
        for key, value in payload.items():
            if hasattr(user, key):
                setattr(user, key, value)
        self.uow.commit()
        return ActionResult(message="用户资料更新成功")

    def get_user_image(self, *, user_id: int):
        user = self.get_user_by_id(user_id)
        return ItemResult(data={"image": get_avatars_url(user.image)})

    def update_user_image(self, *, user_id: int, image: str | None):
        user = self.get_user_by_id(user_id)
        user.image = image or get_random_user_avatars()
        self.uow.commit()
        return ItemResult(data={"image": get_avatars_url(user.image)})

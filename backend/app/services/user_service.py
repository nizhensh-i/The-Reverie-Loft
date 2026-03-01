from flask import current_app
from sqlalchemy.orm import joinedload

from ..domain.common.exceptions import NotFoundError
from ..infrastructure.database.sqlalchemy import db
from ..models import Post, Role, User
from .common.dto import ActionResult, ItemResult, PageResult
from .common.unit_of_work import SqlAlchemyUnitOfWork


class UserService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.uow = SqlAlchemyUnitOfWork(self.session)

    def rollback(self):
        self.uow.rollback()

    def get_user_by_username(self, username: str):
        return User.query.filter_by(username=username).first()

    def get_user_profile(self, username: str):
        user = self.get_user_by_username(username)
        if not user:
            raise NotFoundError("用户不存在")
        return ItemResult(data=user.to_json())

    def list_user_posts(self, *, username: str, page: int):
        user = self.get_user_by_username(username)
        if not user:
            raise NotFoundError("用户不存在")

        pagination = (
            user.posts.filter_by(deleted=False)
            .options(
                joinedload(Post.author).load_only(
                    User.id, User.username, User.nickname, User.image
                )
            )
            .order_by(Post.timestamp.desc())
            .paginate(
                page=page,
                per_page=current_app.config["FLASKY_POSTS_PER_PAGE"],
                error_out=False,
            )
        )
        posts_json = Post.batch_query_with_data(pagination.items, is_list=True)
        return PageResult(data={"posts": posts_json}, total=pagination.total)

    def generate_users_and_posts(self):
        from ..fake import Fake

        Role.insert_roles()
        Fake.users()
        Fake.posts()
        return ActionResult(message="用户和文章生成成功")

    def update_user_profile_by_admin(self, *, user_id: int, payload: dict):
        try:
            user = User.query.get(user_id)
            if not user:
                raise NotFoundError("用户不存在")
            user.email = payload.get("email")
            user.username = payload.get("username")
            user.confirmed = payload.get("confirmed")
            user.role = Role.query.get(int(payload.get("roleId")))
            user.nickname = payload.get("nickname")
            user.location = payload.get("location")
            user.about_me = payload.get("about_me")
            self.uow.commit()
            return ActionResult(message="用户资料更新成功")
        except Exception:
            self.uow.rollback()
            raise

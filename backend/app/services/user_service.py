from ..application.dto import ActionResult, ItemResult, PageResult
from ..domain.common.exceptions import NotFoundError
from ..domain.common.unit_of_work import UnitOfWork
from ..domain.ports.assemblers import ResponseAssemblerPort
from ..domain.ports.settings import PaginationSettingsPort
from ..domain.user.policies import extract_admin_update_payload


class UserService:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        assembler: ResponseAssemblerPort,
        settings: PaginationSettingsPort,
    ):
        self.uow = uow
        self.assembler = assembler
        self.settings = settings

    def rollback(self):
        self.uow.rollback()

    def get_user_by_username(self, username: str):
        return self.uow.users.get_by_username(username)

    def get_user(self, username: str, *, viewer=None):
        user = self.get_user_by_username(username)
        if not user:
            raise NotFoundError("用户不存在")
        user_extra_data = self.uow.users.build_user_extra_data(
            user_id=user.id,
            viewer_id=(viewer.id if viewer else None),
        )
        return ItemResult(
            data=self.assembler.map_user(user, extra_data=user_extra_data)
        )

    def get_user_profile(self, username: str, *, viewer=None):
        return self.get_user(username, viewer=viewer)

    def list_user_posts(self, *, username: str, page: int, viewer=None):
        user = self.get_user_by_username(username)
        if not user:
            raise NotFoundError("用户不存在")

        pagination = self.uow.users.list_user_posts(
            user_id=user.id,
            page=page,
            per_page=self.settings.posts_per_page(),
        )
        extra_data_map = self.uow.posts.build_post_extra_data_map(
            pagination.items,
            viewer_id=(viewer.id if viewer else None),
        )
        posts_json = self.assembler.batch_map_posts(
            pagination.items,
            extra_data_map=extra_data_map,
            is_list=True,
        )
        return PageResult(data={"posts": posts_json}, total=pagination.total)

    def update_user_profile_by_admin(self, *, user_id: int, payload: dict):
        parsed_payload = extract_admin_update_payload(payload)
        try:
            user = self.uow.users.get_by_id(user_id)
            if not user:
                raise NotFoundError("用户不存在")
            role = self.uow.users.get_role_by_id(parsed_payload.role_id)
            if role is None:
                raise NotFoundError("角色不存在")

            user.email = parsed_payload.email
            user.username = parsed_payload.username
            user.confirmed = parsed_payload.confirmed
            user.role = role
            user.nickname = parsed_payload.nickname
            user.location = parsed_payload.location
            user.about_me = parsed_payload.about_me
            self.uow.commit()
            return ActionResult(message="用户资料更新成功")
        except Exception:
            self.uow.rollback()
            raise

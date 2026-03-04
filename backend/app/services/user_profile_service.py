from ..application.dto import ActionResult, ItemResult
from ..domain.common.exceptions import NotFoundError
from ..domain.common.unit_of_work import UnitOfWork
from ..domain.ports.assemblers import ResponseAssemblerPort
from ..domain.ports.asset_url import AssetUrlPort
from ..domain.ports.storage import AvatarProviderPort
from ..domain.user.policies import should_update_profile_field


class UserProfileService:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        assembler: ResponseAssemblerPort,
        avatar_provider: AvatarProviderPort,
        asset_url: AssetUrlPort,
    ):
        self.uow = uow
        self.assembler = assembler
        self.avatar_provider = avatar_provider
        self.asset_url = asset_url

    def rollback(self):
        self.uow.rollback()

    def get_user_by_id(self, user_id: int):
        user = self.uow.users.get_by_id(user_id)
        if not user:
            raise NotFoundError("用户不存在")
        return user

    def get_user_by_username(self, username: str):
        user = self.uow.users.get_by_username(username)
        if not user:
            raise NotFoundError("用户不存在")
        return user

    def get_user(self, *, user_id: int, viewer=None):
        user = self.get_user_by_id(user_id)
        user_extra_data = self.uow.users.build_user_extra_data(
            user_id=user.id,
            viewer_id=(viewer.id if viewer else None),
        )
        return ItemResult(
            data=self.assembler.map_user(user, extra_data=user_extra_data)
        )

    def get_user_by_name(self, *, username: str, viewer=None):
        user = self.get_user_by_username(username)
        user_extra_data = self.uow.users.build_user_extra_data(
            user_id=user.id,
            viewer_id=(viewer.id if viewer else None),
        )
        return ItemResult(
            data=self.assembler.map_user(user, extra_data=user_extra_data)
        )

    def update_user_profile(self, *, user, payload: dict):
        for key, value in (payload or {}).items():
            if should_update_profile_field(key) and hasattr(user, key):
                setattr(user, key, value)
        self.uow.commit()
        return ActionResult(message="用户资料更新成功")

    def get_user_image(self, *, user_id: int):
        user = self.get_user_by_id(user_id)
        return ItemResult(data={"image": self.asset_url.build(user.image)})

    @staticmethod
    def can_update_user_image(*, operator, target_user_id: int) -> bool:
        return bool(
            operator and (operator.is_administrator() or operator.id == target_user_id)
        )

    def update_user_image(self, *, operator, user_id: int, image: str | None):
        if not self.can_update_user_image(operator=operator, target_user_id=user_id):
            return ActionResult(ok=False, message="非当前用户，修改失败")
        user = self.get_user_by_id(user_id)
        user.image = image or self.avatar_provider.get_random_avatar()
        self.uow.commit()
        return ActionResult(ok=True, data={"image": self.asset_url.build(user.image)})

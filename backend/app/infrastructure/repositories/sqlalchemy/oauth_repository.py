from ....domain.oauth.repositories import OAuthRepository
from ....infrastructure.persistence.models import Role, ThirdPartyAccount, User


class SqlAlchemyOAuthRepository(OAuthRepository):
    def __init__(self, session):
        self.session = session

    @staticmethod
    def username_exists(username: str) -> bool:
        return User.query.filter_by(username=username).first() is not None

    @staticmethod
    def get_user_by_id(user_id: int):
        return User.query.get(user_id)

    @staticmethod
    def get_account_by_provider_uuid(*, provider: str, uuid: str):
        return ThirdPartyAccount.query.filter_by(
            provider=provider, uuid=uuid
        ).one_or_none()

    @staticmethod
    def get_account_by_provider_user(*, provider: str, user_id: int):
        return ThirdPartyAccount.query.filter_by(
            provider=provider, user_id=user_id
        ).one_or_none()

    @staticmethod
    def count_user_accounts(*, user_id: int) -> int:
        return ThirdPartyAccount.query.filter_by(user_id=user_id).count()

    def add(self, entity) -> None:
        self.session.add(entity)

    @staticmethod
    def create_user(
        *,
        username: str,
        nickname: str | None,
        image: str | None,
        password: str,
        has_password: bool,
    ):
        default_role = Role.query.filter_by(default=True).first()
        return User(
            username=username,
            nickname=nickname,
            image=image,
            password=password,
            has_password=has_password,
            role=default_role,
        )

    @staticmethod
    def create_account(*, provider: str, user_id: int, profile: dict):
        return ThirdPartyAccount(provider=provider, user_id=user_id, **profile)

    def delete(self, entity) -> None:
        self.session.delete(entity)

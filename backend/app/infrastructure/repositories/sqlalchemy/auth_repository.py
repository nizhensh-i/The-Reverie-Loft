from ....domain.auth.repositories import AuthRepository
from ....infrastructure.persistence.models import Role, User


class SqlAlchemyAuthRepository(AuthRepository):
    def __init__(self, session):
        self.session = session

    @staticmethod
    def get_user_by_username(username: str):
        return User.query.filter_by(username=username).one_or_none()

    @staticmethod
    def get_user_by_email(email: str):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_role_by_name(role_name: str):
        return Role.query.filter_by(name=role_name).first()

    def add_user(self, user) -> None:
        self.session.add(user)

    @staticmethod
    def create_user(
        *,
        email: str | None,
        username: str,
        password: str,
        image: str,
        has_password: bool = True,
        nickname: str | None = None,
    ):
        default_role = Role.query.filter_by(default=True).first()
        return User(
            email=email,
            username=username,
            password=password,
            image=image,
            has_password=has_password,
            nickname=nickname,
            role=default_role,
        )

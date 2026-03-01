from __future__ import annotations

from ..application.admin import SeedUseCases
from ..application.ws import ChatWsUseCases
from ..domain.common.unit_of_work import UnitOfWork
from ..infrastructure.adapters import (
    AvatarUrlAdapter,
    CeleryMailSender,
    CeleryNotificationDispatcher,
    FlaskConfigSettingsAdapter,
    OAuthNetworkAdapter,
    QiniuAvatarProvider,
    QiniuStorageAdapter,
    RedisEmailCodeAdapter,
    RedisPresenceAdapter,
)
from ..infrastructure.oauth import OAuthInfraService, get_frontend_oauth_redirect
from ..infrastructure.providers import get_db, get_redis
from ..infrastructure.repositories.sqlalchemy.unit_of_work import (
    SqlAlchemyRepositoryUnitOfWork,
)
from ..infrastructure.socketio.services import init_ws_services
from ..presenters import ApiResponseAssembler
from ..services.admin_post_service import AdminPostService
from ..services.auth_service import AuthService
from ..services.comment_service import CommentService
from ..services.follow_service import FollowService
from ..services.jwt_service import JwtService
from ..services.log_service import LogService
from ..services.message_service import MessageService
from ..services.notification_service import NotificationService
from ..services.oauth_flow_service import OAuthFlowService
from ..services.post_service import PostService
from ..services.praise_service import PraiseService
from ..services.tag_service import TagService
from ..services.upload_service import UploadService
from ..services.user_profile_service import UserProfileService
from ..services.user_service import UserService


class AppContainer:
    def __init__(self, app):
        redis_client = get_redis()
        (
            self.ws_connection,
            self.ws_presence,
            self.ws_conversation,
            self.ws_cleanup,
        ) = init_ws_services(redis_client)

        self.assembler = ApiResponseAssembler()
        self.notification_dispatcher = CeleryNotificationDispatcher()
        self.email_code_port = RedisEmailCodeAdapter(redis_client=redis_client)
        self.mail_sender = CeleryMailSender()
        self.avatar_provider = QiniuAvatarProvider()
        self.storage_gateway = QiniuStorageAdapter()
        self.asset_url = AvatarUrlAdapter()
        self.presence_port = RedisPresenceAdapter(presence_service=self.ws_presence)
        self.settings = FlaskConfigSettingsAdapter(app.config)
        self.oauth_network = OAuthNetworkAdapter()
        self.oauth_infra_service = OAuthInfraService(redis_client=redis_client)
        self.frontend_oauth_redirect = get_frontend_oauth_redirect()

    @staticmethod
    def new_uow() -> UnitOfWork:
        return SqlAlchemyRepositoryUnitOfWork(get_db().session)

    def post_service(self) -> PostService:
        return PostService(
            uow=self.new_uow(),
            assembler=self.assembler,
            notifier=self.notification_dispatcher,
        )

    def comment_service(self) -> CommentService:
        return CommentService(
            uow=self.new_uow(),
            assembler=self.assembler,
            notifier=self.notification_dispatcher,
        )

    def praise_service(self) -> PraiseService:
        return PraiseService(
            uow=self.new_uow(),
            notifier=self.notification_dispatcher,
        )

    def user_service(self) -> UserService:
        return UserService(
            uow=self.new_uow(),
            assembler=self.assembler,
            settings=self.settings,
        )

    def user_profile_service(self) -> UserProfileService:
        return UserProfileService(
            uow=self.new_uow(),
            assembler=self.assembler,
            avatar_provider=self.avatar_provider,
            asset_url=self.asset_url,
        )

    def follow_service(self) -> FollowService:
        return FollowService(
            uow=self.new_uow(),
            assembler=self.assembler,
            asset_url=self.asset_url,
            settings=self.settings,
        )

    def tag_service(self) -> TagService:
        return TagService(uow=self.new_uow())

    def admin_post_service(self) -> AdminPostService:
        return AdminPostService(uow=self.new_uow())

    def message_service(self) -> MessageService:
        return MessageService(
            uow=self.new_uow(),
            assembler=self.assembler,
            settings=self.settings,
        )

    def notification_service(self) -> NotificationService:
        return NotificationService(uow=self.new_uow(), assembler=self.assembler)

    def log_service(self) -> LogService:
        return LogService(
            uow=self.new_uow(),
            assembler=self.assembler,
            presence_port=self.presence_port,
        )

    def upload_service(self) -> UploadService:
        return UploadService(
            uow=self.new_uow(),
            storage=self.storage_gateway,
            assembler=self.assembler,
            asset_url=self.asset_url,
        )

    def auth_service(self) -> AuthService:
        return AuthService(
            uow=self.new_uow(),
            code_token_service=self.email_code_port,
            assembler=self.assembler,
            mail_sender=self.mail_sender,
            avatar_provider=self.avatar_provider,
        )

    def jwt_service(self) -> JwtService:
        return JwtService(redis_blocklist=get_redis())

    def oauth_flow_service(self) -> OAuthFlowService:
        return OAuthFlowService(
            uow=self.new_uow(),
            oauth_infra_service=self.oauth_infra_service,
            frontend_oauth_redirect=self.frontend_oauth_redirect,
            assembler=self.assembler,
            oauth_network=self.oauth_network,
        )

    def chat_ws_use_cases(self) -> ChatWsUseCases:
        return ChatWsUseCases(
            uow_factory=self.new_uow,
            notifier=self.notification_dispatcher,
        )

    def seed_use_cases(self) -> SeedUseCases:
        return SeedUseCases(uow_factory=self.new_uow)


def setup_container(app):
    app.extensions["container"] = AppContainer(app)


def get_container(app=None) -> AppContainer:
    if app is not None:
        return app.extensions["container"]

    from flask import current_app

    return current_app.extensions["container"]

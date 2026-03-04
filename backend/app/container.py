from __future__ import annotations

from dependency_injector import containers, providers

from .application.cache import PostListCache
from .domain.common.unit_of_work import UnitOfWork
from .infrastructure.adapters import (
    AvatarUrlAdapter,
    CeleryMailSender,
    CeleryNotificationDispatcher,
    FlaskCacheAdapter,
    FlaskConfigSettingsAdapter,
    FlaskJwtAdapter,
    HybridAvatarProvider,
    OAuthNetworkAdapter,
    QiniuStorageAdapter,
    RedisEmailCodeAdapter,
    RedisPresenceAdapter,
)
from .infrastructure.oauth import OAuthInfraService, get_frontend_oauth_redirect
from .infrastructure.providers import get_cache, get_db, get_redis
from .infrastructure.repositories.sqlalchemy.unit_of_work import (
    SqlAlchemyRepositoryUnitOfWork,
)
from .infrastructure.socketio.services import init_ws_services
from .presenters import ApiResponseAssembler
from .services.admin_post_service import AdminPostService
from .services.auth_service import AuthService
from .services.chat_ws_service import ChatWsService
from .services.comment_service import CommentService
from .services.follow_service import FollowService
from .services.jwt_service import JwtService
from .services.log_service import LogService
from .services.message_service import MessageService
from .services.notification_service import NotificationService
from .services.oauth_flow_service import OAuthFlowService
from .services.post_service import PostService
from .services.praise_service import PraiseService
from .services.seed_service import SeedService
from .services.tag_service import TagService
from .services.upload_service import UploadService
from .services.user_profile_service import UserProfileService
from .services.user_service import UserService


def _build_uow() -> UnitOfWork:
    return SqlAlchemyRepositoryUnitOfWork(get_db().session)


class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    redis_client = providers.Callable(get_redis)
    cache_client = providers.Callable(get_cache)

    ws_services = providers.Singleton(init_ws_services, redis_client)
    ws_connection = providers.Callable(lambda services: services[0], ws_services)
    ws_presence = providers.Callable(lambda services: services[1], ws_services)
    ws_conversation = providers.Callable(lambda services: services[2], ws_services)
    ws_cleanup = providers.Callable(lambda services: services[3], ws_services)

    assembler = providers.Singleton(ApiResponseAssembler)
    notification_dispatcher = providers.Singleton(CeleryNotificationDispatcher)
    email_code_port = providers.Singleton(
        RedisEmailCodeAdapter, redis_client=redis_client
    )
    mail_sender = providers.Singleton(CeleryMailSender)
    avatar_provider = providers.Singleton(HybridAvatarProvider)
    storage_gateway = providers.Singleton(QiniuStorageAdapter)
    asset_url = providers.Singleton(AvatarUrlAdapter)
    presence_port = providers.Factory(
        RedisPresenceAdapter, presence_service=ws_presence
    )
    settings = providers.Factory(FlaskConfigSettingsAdapter, config=config)
    oauth_network = providers.Singleton(OAuthNetworkAdapter)
    oauth_infra_service = providers.Singleton(
        OAuthInfraService, redis_client=redis_client
    )
    frontend_oauth_redirect = providers.Callable(get_frontend_oauth_redirect)
    jwt_port = providers.Singleton(FlaskJwtAdapter)
    cache_port = providers.Singleton(FlaskCacheAdapter, cache_client=cache_client)
    post_list_cache = providers.Singleton(PostListCache, cache=cache_port)

    uow = providers.Factory(_build_uow)

    post_service = providers.Factory(
        PostService,
        uow=uow,
        assembler=assembler,
        notifier=notification_dispatcher,
    )
    comment_service = providers.Factory(
        CommentService,
        uow=uow,
        assembler=assembler,
        notifier=notification_dispatcher,
    )
    praise_service = providers.Factory(
        PraiseService,
        uow=uow,
        notifier=notification_dispatcher,
    )
    user_service = providers.Factory(
        UserService,
        uow=uow,
        assembler=assembler,
        settings=settings,
    )
    user_profile_service = providers.Factory(
        UserProfileService,
        uow=uow,
        assembler=assembler,
        avatar_provider=avatar_provider,
        asset_url=asset_url,
    )
    follow_service = providers.Factory(
        FollowService,
        uow=uow,
        assembler=assembler,
        asset_url=asset_url,
        settings=settings,
    )
    tag_service = providers.Factory(TagService, uow=uow)
    admin_post_service = providers.Factory(AdminPostService, uow=uow)
    message_service = providers.Factory(
        MessageService,
        uow=uow,
        assembler=assembler,
        settings=settings,
    )
    notification_service = providers.Factory(
        NotificationService,
        uow=uow,
        assembler=assembler,
    )
    log_service = providers.Factory(
        LogService,
        uow=uow,
        assembler=assembler,
        presence_port=presence_port,
    )
    upload_service = providers.Factory(
        UploadService,
        uow=uow,
        storage=storage_gateway,
        assembler=assembler,
        asset_url=asset_url,
    )
    auth_service = providers.Factory(
        AuthService,
        uow=uow,
        code_token_service=email_code_port,
        assembler=assembler,
        mail_sender=mail_sender,
        avatar_provider=avatar_provider,
        jwt_port=jwt_port,
    )
    jwt_service = providers.Factory(
        JwtService,
        redis_blocklist=redis_client,
        jwt_port=jwt_port,
    )
    oauth_flow_service = providers.Factory(
        OAuthFlowService,
        uow=uow,
        oauth_infra_service=oauth_infra_service,
        frontend_oauth_redirect=frontend_oauth_redirect,
        assembler=assembler,
        oauth_network=oauth_network,
        jwt_port=jwt_port,
    )
    chat_ws_service = providers.Factory(
        ChatWsService,
        uow_factory=uow.provider,
        notifier=notification_dispatcher,
    )
    seed_service = providers.Factory(SeedService, uow_factory=uow.provider)


def setup_container(app):
    container = AppContainer()
    container.config.from_dict(app.config)

    from . import api as api_pkg
    from . import auth as auth_pkg
    from . import event

    container.wire(packages=[api_pkg, auth_pkg], modules=[event])

    app.container = container
    app.extensions["container"] = container
    return container


def get_container(app=None):
    if app:
        return app.extensions["container"]

    from flask import current_app

    return current_app.extensions["container"]

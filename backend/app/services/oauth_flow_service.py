import json
import logging
from dataclasses import dataclass
from datetime import timedelta
from urllib.parse import urlencode

from ..domain.common.unit_of_work import UnitOfWork
from ..domain.oauth.policies import (
    ensure_provider_enabled,
    parse_bind_state_token,
    sanitize_oauth_authorize_url,
)
from ..domain.ports.assemblers import ResponseAssemblerPort
from ..domain.ports.jwt import JwtPort
from ..domain.ports.oauth import OAuthNetworkPort
from .oauth_service import OAuthAccountService


@dataclass(frozen=True)
class OAuthRedirectResult:
    url: str


@dataclass(frozen=True)
class OAuthApiErrorResult:
    code: int
    message: str


@dataclass(frozen=True)
class OAuthBindSuccessResult:
    provider: str


@dataclass(frozen=True)
class OAuthBindErrorResult:
    provider: str
    message: str


@dataclass(frozen=True)
class OAuthLoginSuccessResult:
    provider: str
    user: dict
    access_token: str
    refresh_token: str


@dataclass(frozen=True)
class OAuthErrorResult:
    code: int
    message: str
    is_bind_mode: bool = False


class OAuthFlowService:
    def __init__(
        self,
        *,
        oauth_infra_service,
        frontend_oauth_redirect: str,
        uow: UnitOfWork,
        assembler: ResponseAssemblerPort,
        oauth_network: OAuthNetworkPort,
        jwt_port: JwtPort,
    ):
        self.oauth_infra_service = oauth_infra_service
        self.frontend_oauth_redirect = frontend_oauth_redirect
        self.uow = uow
        self.assembler = assembler
        self.oauth_network = oauth_network
        self.jwt_port = jwt_port
        self.oauth_account_service = OAuthAccountService(uow=self.uow)

    def rollback(self):
        self.uow.rollback()

    def enabled_providers(self):
        return self.oauth_infra_service.enabled_providers()

    def create_authorize_url(self, provider: str):
        auth_request, _ = self.oauth_infra_service.get_auth_request(provider)
        auth_url = auth_request.authorize()
        return sanitize_oauth_authorize_url(auth_url)

    def create_bind_authorize_url(self, provider: str, bind_user):
        ensure_provider_enabled(
            provider=provider, enabled_providers=self.enabled_providers()
        )

        auth_request, _ = self.oauth_infra_service.get_auth_request(provider)
        user_token = self.jwt_port.create_access_token(
            identity=bind_user,
            expires_delta=timedelta(minutes=10),
            fresh=False,
        )
        bind_state = f"bind:{user_token}"
        return auth_request.authorize(state=bind_state)

    def handle_callback(self, provider: str, params: dict):
        is_bind_mode = False
        try:
            auth_request, meta = self.oauth_infra_service.get_auth_request(provider)
            logging.info(
                "处理第三方回调 provider=%s redirect_uri=%s params=%s",
                provider,
                meta["redirect_uri"],
                params,
            )

            auth_user_response = auth_request.login(params)

            if self.oauth_network.has_network_error_message(auth_user_response.message):
                return OAuthErrorResult(
                    code=503,
                    message=f"{provider.title()} 服务连接失败，请稍后重试或检查网络配置",
                    is_bind_mode=is_bind_mode,
                )

            if auth_user_response.code != 200 or not auth_user_response.data:
                return OAuthApiErrorResult(
                    code=auth_user_response.code or 400,
                    message=auth_user_response.message or "第三方登录失败",
                )

            auth_user = auth_user_response.data
            if getattr(auth_user, "service_url", None):
                return OAuthRedirectResult(url=auth_user.service_url)

            state = params.get("state", "")
            bind_token = parse_bind_state_token(state)
            is_bind_mode = bind_token is not None

            if is_bind_mode:
                decoded_token = self.jwt_port.decode_token(
                    bind_token, allow_expired=False
                )
                user_id = decoded_token.get("sub")
                user = self.uow.users.get_by_id(user_id)
                if not user:
                    raise ValueError("用户不存在")

                self.oauth_account_service.bind_third_party_account(
                    provider, auth_user, user
                )
                self.uow.commit()
                return OAuthBindSuccessResult(provider=provider)

            user = self.oauth_account_service.get_or_create_user(provider, auth_user)
            self.uow.commit()

            user_extra_data = self.uow.users.build_user_extra_data(
                user_id=user.id,
                viewer_id=None,
            )
            user_payload = self.assembler.map_user(user, extra_data=user_extra_data)
            access_token = "Bearer " + self.jwt_port.create_access_token(
                identity=user, fresh=True
            )
            refresh_token = "Bearer " + self.jwt_port.create_refresh_token(
                identity=user
            )
            self.uow.users.touch_last_seen(user_id=user.id)
            self.uow.commit()

            return OAuthLoginSuccessResult(
                provider=provider,
                user=user_payload,
                access_token=access_token,
                refresh_token=refresh_token,
            )

        except Exception as exc:
            if self.oauth_network.has_network_error_message(str(exc)):
                logging.error(
                    "OAuth 网络异常 provider=%s error=%s",
                    provider,
                    str(exc),
                    exc_info=True,
                )
                return OAuthErrorResult(
                    code=503,
                    message=f"服务器无法连接 {provider.title()} 服务，请稍后重试",
                    is_bind_mode=is_bind_mode,
                )
            logging.exception("处理第三方登录失败: %s", exc)
            self.uow.rollback()
            if is_bind_mode:
                return OAuthBindErrorResult(
                    provider=provider,
                    message=str(exc) if str(exc) else "绑定失败",
                )
            return OAuthErrorResult(
                code=500,
                message="处理第三方登录失败，请稍后重试",
                is_bind_mode=is_bind_mode,
            )

    def unbind(self, provider: str, user):
        self.oauth_account_service.unbind_third_party_account(
            provider=provider, user=user
        )
        self.uow.commit()

    def redirect_for_bind_success(self, provider: str):
        query = urlencode(
            {
                "provider": provider,
                "action": "bind",
                "status": "success",
                "message": "绑定成功",
            }
        )
        return f"{self.frontend_oauth_redirect}?{query}"

    def redirect_for_bind_error(self, provider: str, message: str):
        query = urlencode(
            {
                "provider": provider,
                "action": "bind",
                "status": "error",
                "message": message,
            }
        )
        return f"{self.frontend_oauth_redirect}?{query}"

    def redirect_for_login_success(
        self, provider: str, access_token: str, refresh_token: str, user: dict
    ):
        query = urlencode(
            {
                "provider": provider,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": json.dumps(user),
            }
        )
        return f"{self.frontend_oauth_redirect}?{query}"

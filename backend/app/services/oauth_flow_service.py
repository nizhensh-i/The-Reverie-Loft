import json
import logging
from dataclasses import dataclass
from datetime import timedelta
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    decode_token,
)

from ..infrastructure.database.sqlalchemy import db
from ..infrastructure.oauth import has_oauth_network_error_message
from ..models import User
from .common.unit_of_work import SqlAlchemyUnitOfWork
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
    def __init__(self, oauth_infra_service, frontend_oauth_redirect: str, session=None):
        self.oauth_infra_service = oauth_infra_service
        self.frontend_oauth_redirect = frontend_oauth_redirect
        self.session = session or db.session
        self.uow = SqlAlchemyUnitOfWork(self.session)
        self.oauth_account_service = OAuthAccountService(session=self.session)

    def rollback(self):
        self.uow.rollback()

    def enabled_providers(self):
        return self.oauth_infra_service.enabled_providers()

    def create_authorize_url(self, provider: str):
        auth_request, _ = self.oauth_infra_service.get_auth_request(provider)
        auth_url = auth_request.authorize()

        parsed = urlparse(auth_url)
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        encoded_query = urlencode(query_params, doseq=True)
        encoded_url = parsed._replace(query=encoded_query).geturl()
        return encoded_url

    def create_bind_authorize_url(self, provider: str):
        if provider not in self.enabled_providers():
            raise ValueError(f"不支持的平台: {provider}")

        auth_request, _ = self.oauth_infra_service.get_auth_request(provider)
        user_token = create_access_token(
            identity=current_user, expires_delta=timedelta(minutes=10), fresh=False
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

            if has_oauth_network_error_message(auth_user_response.message):
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
            is_bind_mode = state.startswith("bind:")

            if is_bind_mode:
                token = state[5:]
                decoded_token = decode_token(token, allow_expired=False)
                user_id = decoded_token.get("sub")
                user = User.query.get(user_id)
                if not user:
                    raise ValueError("用户不存在")

                self.oauth_account_service.bind_third_party_account(
                    provider, auth_user, user
                )
                self.uow.commit()
                return OAuthBindSuccessResult(provider=provider)

            user = self.oauth_account_service.get_or_create_user(provider, auth_user)
            self.uow.commit()

            user_payload = user.to_json()
            access_token = "Bearer " + create_access_token(identity=user, fresh=True)
            refresh_token = "Bearer " + create_refresh_token(identity=user)
            user.ping()

            return OAuthLoginSuccessResult(
                provider=provider,
                user=user_payload,
                access_token=access_token,
                refresh_token=refresh_token,
            )

        except requests.exceptions.ConnectionError as exc:
            logging.error(
                "OAuth 网络连接失败 provider=%s error=%s", provider, str(exc), exc_info=True
            )
            return OAuthErrorResult(
                code=503,
                message=f"服务器无法连接 {provider.title()} 服务，请稍后重试或联系管理员检查网络配置",
                is_bind_mode=is_bind_mode,
            )
        except requests.exceptions.Timeout as exc:
            logging.error("OAuth 请求超时 provider=%s error=%s", provider, str(exc))
            return OAuthErrorResult(
                code=504,
                message=f"连接 {provider.title()} 服务超时，请稍后重试",
                is_bind_mode=is_bind_mode,
            )
        except Exception as exc:
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

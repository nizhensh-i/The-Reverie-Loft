from urllib.parse import urlencode

from dependency_injector.wiring import Provide, inject
from flask import redirect, request, url_for
from flask_jwt_extended import current_user, jwt_required

from ..container import AppContainer
from ..services.oauth_flow_service import (
    OAuthApiErrorResult,
    OAuthBindErrorResult,
    OAuthBindSuccessResult,
    OAuthErrorResult,
    OAuthFlowService,
    OAuthLoginSuccessResult,
    OAuthRedirectResult,
)
from ..utils.response import error, success
from . import auth


@inject
def _flow_service(
    flow_service: OAuthFlowService = Provide[AppContainer.oauth_flow_service],
) -> OAuthFlowService:
    return flow_service


@inject
def _oauth_infra_service(
    oauth_infra_service=Provide[AppContainer.oauth_infra_service],
):
    return oauth_infra_service


@inject
def _frontend_oauth_redirect(
    frontend_oauth_redirect: str = Provide[AppContainer.frontend_oauth_redirect],
) -> str:
    return frontend_oauth_redirect


def _handle_oauth_error(
    provider: str, error_code: int, error_message: str, is_bind: bool = False
):
    frontend_redirect = _frontend_oauth_redirect()
    if frontend_redirect:
        query = urlencode(
            {
                "provider": provider,
                "status": "error",
                "message": error_message,
                **({"action": "bind"} if is_bind else {}),
            }
        )
        return redirect(f"{frontend_redirect}?{query}")
    return error(code=error_code, message=error_message)


@auth.route("/oauth/providers", methods=["GET"])
def list_oauth_providers():
    service = _flow_service()
    oauth_infra_service = _oauth_infra_service()

    providers = []
    for provider in service.enabled_providers():
        providers.append(
            {
                "provider": provider,
                "name": oauth_infra_service.oauth_configs[provider].get(
                    "display_name", provider.title()
                ),
                "authorize_endpoint": url_for(
                    "auth.oauth_authorize", provider=provider, _external=False
                ),
            }
        )
    return success(data={"providers": providers})


@auth.route("/oauth/authorize/<provider>", methods=["GET"])
def oauth_authorize(provider: str):
    authorize_url = _flow_service().create_authorize_url(provider)
    return success(data={"authorize_url": authorize_url, "provider": provider})


@auth.route("/oauth/callback/<provider>", methods=["GET"])
def oauth_callback(provider: str):
    result = _flow_service().handle_callback(
        provider=provider, params=dict(request.args)
    )

    if isinstance(result, OAuthRedirectResult):
        return redirect(result.url)

    if isinstance(result, OAuthApiErrorResult):
        return error(code=result.code, message=result.message)

    if isinstance(result, OAuthBindSuccessResult):
        frontend_redirect = _frontend_oauth_redirect()
        if frontend_redirect:
            return redirect(_flow_service().redirect_for_bind_success(provider))
        return success(message="绑定成功")

    if isinstance(result, OAuthBindErrorResult):
        frontend_redirect = _frontend_oauth_redirect()
        if frontend_redirect:
            return redirect(
                _flow_service().redirect_for_bind_error(provider, result.message)
            )
        return error(code=400, message=result.message)

    if isinstance(result, OAuthLoginSuccessResult):
        frontend_redirect = _frontend_oauth_redirect()
        if frontend_redirect:
            return redirect(
                _flow_service().redirect_for_login_success(
                    provider=provider,
                    access_token=result.access_token,
                    refresh_token=result.refresh_token,
                    user=result.user,
                )
            )
        return success(
            data=result.user,
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            message="登录成功",
        )

    if isinstance(result, OAuthErrorResult):
        return _handle_oauth_error(
            provider=provider,
            error_code=result.code,
            error_message=result.message,
            is_bind=result.is_bind_mode,
        )

    return _handle_oauth_error(
        provider=provider,
        error_code=500,
        error_message="处理第三方登录失败，请稍后重试",
        is_bind=False,
    )


@auth.route("/oauth/bind/<provider>", methods=["POST"])
@jwt_required()
def oauth_bind(provider: str):
    authorize_url = _flow_service().create_bind_authorize_url(
        provider=provider,
        bind_user=current_user,
    )
    return success(data={"authorize_url": authorize_url, "provider": provider})


@auth.route("/oauth/unbind/<provider>", methods=["POST"])
@jwt_required()
def oauth_unbind(provider: str):
    _flow_service().unbind(provider=provider, user=current_user)
    return success(message=f"已成功解绑 {provider.title()} 账号")

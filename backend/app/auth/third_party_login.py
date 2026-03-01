import logging
from urllib.parse import urlencode

from flask import redirect, request, url_for
from flask_jwt_extended import current_user, jwt_required

from ..infrastructure.database.redis import redis
from ..infrastructure.oauth import OAuthInfraService, get_frontend_oauth_redirect
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

oauth_infra_service = OAuthInfraService(redis_client=redis)
FRONTEND_OAUTH_REDIRECT = get_frontend_oauth_redirect()
oauth_flow_service = OAuthFlowService(
    oauth_infra_service=oauth_infra_service,
    frontend_oauth_redirect=FRONTEND_OAUTH_REDIRECT,
)


def _handle_oauth_error(
    provider: str, error_code: int, error_message: str, is_bind: bool = False
):
    if FRONTEND_OAUTH_REDIRECT:
        query = urlencode(
            {
                "provider": provider,
                "status": "error",
                "message": error_message,
                **({"action": "bind"} if is_bind else {}),
            }
        )
        return redirect(f"{FRONTEND_OAUTH_REDIRECT}?{query}")
    return error(code=error_code, message=error_message)


@auth.route("/oauth/providers", methods=["GET"])
def list_oauth_providers():
    providers = []
    for provider in oauth_flow_service.enabled_providers():
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
    try:
        authorize_url = oauth_flow_service.create_authorize_url(provider)
        return success(data={"authorize_url": authorize_url, "provider": provider})
    except Exception as exc:
        logging.exception("创建授权请求失败: %s", exc)
        return error(code=400, message=str(exc))


@auth.route("/oauth/callback/<provider>", methods=["GET"])
def oauth_callback(provider: str):
    result = oauth_flow_service.handle_callback(
        provider=provider, params=dict(request.args)
    )

    if isinstance(result, OAuthRedirectResult):
        return redirect(result.url)

    if isinstance(result, OAuthApiErrorResult):
        return error(code=result.code, message=result.message)

    if isinstance(result, OAuthBindSuccessResult):
        if FRONTEND_OAUTH_REDIRECT:
            return redirect(oauth_flow_service.redirect_for_bind_success(provider))
        return success(message="绑定成功")

    if isinstance(result, OAuthBindErrorResult):
        if FRONTEND_OAUTH_REDIRECT:
            return redirect(
                oauth_flow_service.redirect_for_bind_error(provider, result.message)
            )
        return error(code=400, message=result.message)

    if isinstance(result, OAuthLoginSuccessResult):
        if FRONTEND_OAUTH_REDIRECT:
            return redirect(
                oauth_flow_service.redirect_for_login_success(
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
    try:
        authorize_url = oauth_flow_service.create_bind_authorize_url(provider)
        return success(data={"authorize_url": authorize_url, "provider": provider})
    except Exception as exc:
        logging.exception("发起第三方账号绑定失败: %s", exc)
        return error(code=500, message=f"发起绑定失败: {str(exc)}")


@auth.route("/oauth/unbind/<provider>", methods=["POST"])
@jwt_required()
def oauth_unbind(provider: str):
    try:
        oauth_flow_service.unbind(provider=provider, user=current_user)
        return success(message=f"已成功解绑 {provider.title()} 账号")
    except Exception as exc:
        logging.exception("解绑第三方账号失败: %s", exc)
        oauth_flow_service.rollback()
        return error(code=500, message=f"解绑失败: {str(exc)}")

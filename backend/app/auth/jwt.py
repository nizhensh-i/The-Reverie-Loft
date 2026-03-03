from dependency_injector.wiring import Provide, inject
from flask import current_app
from flask_jwt_extended import current_user, jwt_required

from ..container import AppContainer
from ..services.jwt_service import JwtService
from ..utils.response import success, unauthorized
from . import auth


@inject
def _jwt_service(
    jwt_service: JwtService = Provide[AppContainer.jwt_service],
) -> JwtService:
    return jwt_service


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    result = _jwt_service().refresh_access_token(user=current_user)
    return success(data=result.data)


@auth.route("/revokeToken", methods=["DELETE"])
@jwt_required(verify_type=False)
def revoke_token():
    result = _jwt_service().revoke_current_token(
        expires_seconds=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    )
    return success(message=result.message, data=result.data)


@auth.route("/checkFreshness", methods=["GET"])
@jwt_required()
def check_freshness():
    result = _jwt_service().is_fresh_token()
    if result.data["is_fresh"]:
        return success(message="令牌新鲜")
    return unauthorized(message="该操作需要重新登录以验证身份")


@auth.route("/access_token_test")
@jwt_required()
def _test_access_token():
    return success(message="这是access_token_test接口")


@auth.route("/refresh_token_test")
@jwt_required(refresh=True)
def _test_refresh_token():
    return success(message="这是refresh_token_test接口")

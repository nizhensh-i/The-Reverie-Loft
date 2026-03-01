from flask import current_app
from flask_jwt_extended import current_user, jwt_required

from ..composition import get_container
from ..utils.response import success, unauthorized
from . import auth


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    result = get_container().jwt_service().refresh_access_token(user=current_user)
    return success(data=result.data)


@auth.route("/revokeToken", methods=["DELETE"])
@jwt_required(verify_type=False)
def revoke_token():
    result = (
        get_container()
        .jwt_service()
        .revoke_current_token(
            expires_seconds=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        )
    )
    return success(message=result.message, data=result.data)


@auth.route("/checkFreshness", methods=["GET"])
@jwt_required()
def check_freshness():
    result = get_container().jwt_service().is_fresh_token()
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

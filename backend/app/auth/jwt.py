from flask import current_app
from flask_jwt_extended import current_user, jwt_required

from ..infrastructure.database.redis import redis as jwt_redis_blocklist
from ..services.jwt_service import JwtService
from ..utils.response import success, unauthorized
from . import auth

jwt_service = JwtService(redis_blocklist=jwt_redis_blocklist)


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """刷新token"""
    access_token = jwt_service.refresh_access_token(user=current_user)
    return success(data={"access_token": access_token})


@auth.route("/revokeToken", methods=["DELETE"])
@jwt_required(verify_type=False)
def revoke_token():
    """ "撤销令牌"""
    ttype = jwt_service.revoke_current_token(
        expires_seconds=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    )
    return success(message=f"{ttype.capitalize()} token successfully revoked")


@auth.route("/checkFreshness", methods=["GET"])
@jwt_required()
def check_freshness():
    """检测当前令牌是否为新鲜令牌"""
    if jwt_service.is_fresh_token():
        return success(message="令牌新鲜")
    return unauthorized(message="该操作需要重新登录以验证身份")


# ===== 以下单元测试专用 =====
@auth.route("/access_token_test")
@jwt_required()
def _test_access_token():
    """单元测试访问令牌"""
    return success(message="这是access_token_test接口")


@auth.route("/refresh_token_test")
@jwt_required(refresh=True)
def _test_refresh_token():
    """单元测试刷新令牌"""
    return success(message="这是refresh_token_test接口")

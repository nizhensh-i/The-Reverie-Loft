from flask import current_app
from flask_jwt_extended import create_access_token, current_user, get_jwt, jwt_required

from ..infrastructure.database.redis import redis as jwt_redis_blocklist
from ..utils.response import success, unauthorized
from . import auth


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """刷新token"""
    access_token = "Bearer " + create_access_token(identity=current_user)
    return success(data={"access_token": access_token})


@auth.route("/revokeToken", methods=["DELETE"])
@jwt_required(verify_type=False)
def revoke_token():
    """ "撤销令牌"""
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    jwt_redis_blocklist.set(jti, "", ex=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"])
    return success(message=f"{ttype.capitalize()} token successfully revoked")


@auth.route("/checkFreshness", methods=["GET"])
@jwt_required()
def check_freshness():
    """检测当前令牌是否为新鲜令牌"""
    jwt_data = get_jwt()
    if jwt_data.get("fresh", False):
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

import logging

from flask import request
from flask_jwt_extended import JWTManager

from ...utils.response import error, unauthorized
from ..capabilities import capability_enabled, get_capability, set_capability

jwt = JWTManager()


def setup_jwt(app, jwt_redis_blocklist):
    if capability_enabled("redis", default=True):
        set_capability("jwt_blocklist", enabled=True, degraded=False, reason="")
    else:
        reason = (get_capability("redis") or {}).get("reason", "redis unavailable")
        set_capability(
            "jwt_blocklist",
            enabled=True,
            degraded=True,
            reason=f"blocklist check degraded: {reason}",
        )
    jwt.init_app(app)

    @jwt.user_identity_loader
    def user_identify_lookup(user):
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        from ...models import User

        return User.query.filter_by(id=identity).one_or_none()

    @jwt.unauthorized_loader
    def missing_token_callback(error_msg):
        """针对伪造的/错误的token"""
        logging.warning(f"未授权访问: {request.path}, 错误: {error_msg}")
        return unauthorized("token无效")

    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        """针对token过期"""
        logging.warning(f"token已过期: {jwt_header}, 载荷: {jwt_payload}")
        return unauthorized("身份已过期")

    @jwt.revoked_token_loader
    def my_revoked_token_callback(jwt_header, jwt_payload):
        """针对token被撤销"""
        logging.warning(f"token已被撤销")
        return unauthorized("该token已被撤销")

    @jwt.needs_fresh_token_loader
    def handle_needs_fresh_token_callback(jwt_header, jwt_payload):
        """令牌新鲜度验证失败错误"""
        return error(code=401, message="该操作需要重新登录以验证身份")

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        """黑名单"""
        jti = jwt_payload["jti"]
        try:
            token_in_redis = jwt_redis_blocklist.get(jti)
            return token_in_redis is not None
        except Exception as e:
            # Redis 不可用时降级：放过黑名单检查，避免所有请求直接 500。
            logging.warning("JWT 黑名单检查降级，redis 不可用: %s", e)
            return False

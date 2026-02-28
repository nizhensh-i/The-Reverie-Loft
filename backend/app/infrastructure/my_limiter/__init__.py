from flask_jwt_extended import current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ..capabilities import capability_enabled, get_capability, set_capability
from ..config import InfraConfig
from ..exceptions import RateLimitError


def my_key_func():
    """根据当前用户id限速"""
    return current_user.id if current_user else get_remote_address


limiter = Limiter(
    my_key_func,
)


def setup_limiter(app):
    """初始化限流器"""
    try:
        if capability_enabled("redis", default=True):
            app.config.setdefault(
                "RATELIMIT_STORAGE_URI", InfraConfig.build_redis_url(db=3)
            )
            set_capability("limiter", enabled=True, degraded=False, reason="")
        else:
            # Redis 不可用时退化为内存限流，避免阻断服务启动。
            app.config["RATELIMIT_STORAGE_URI"] = "memory://"
            reason = (get_capability("redis") or {}).get("reason", "redis unavailable")
            set_capability(
                "limiter",
                enabled=True,
                degraded=True,
                reason=f"fallback to memory storage: {reason}",
            )
        limiter.init_app(app)
    except Exception as e:
        set_capability("limiter", enabled=False, degraded=True, reason=str(e))
        raise RateLimitError(
            f"初始化限流器失败: {str(e)}", component="limiter", original_error=e
        )

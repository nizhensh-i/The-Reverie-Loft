import logging
import os

from flask_redis import FlaskRedis

from ..capabilities import set_capability

redis = FlaskRedis()


REDIS_ENV_KEYS = ("REDIS_URL", "DEV_REDIS_URL", "TEST_REDIS_URL", "REDIS_HOST")


def _redis_configured(app) -> tuple[bool, str]:
    # 优先看应用最终配置，其次看环境变量，避免误判“未配置”。
    app_redis_url = app.config.get("REDIS_URL")
    if app_redis_url:
        return True, "REDIS_URL(app.config)"

    configured_keys = [key for key in REDIS_ENV_KEYS if os.getenv(key)]
    if not configured_keys:
        return (
            False,
            "missing env config: REDIS_URL/DEV_REDIS_URL/TEST_REDIS_URL/REDIS_HOST",
        )
    return True, ",".join(configured_keys)


def detect_redis_capability(app) -> dict:
    configured, reason = _redis_configured(app)
    if not configured:
        set_capability("redis", enabled=False, degraded=True, reason=reason)
        return {"enabled": False, "degraded": True, "reason": reason}

    try:
        redis.ping()
        set_capability("redis", enabled=True, reason="")
        return {"enabled": True, "degraded": False, "reason": ""}
    except Exception as exc:
        reason = f"redis probe failed: {exc}"
        set_capability("redis", enabled=False, degraded=True, reason=reason)
        return {"enabled": False, "degraded": True, "reason": reason}


def setup_redis(app):
    redis.init_app(app, decode_responses=True)
    status = detect_redis_capability(app)
    if not status["enabled"]:
        logging.warning("Redis 降级: %s", status["reason"])

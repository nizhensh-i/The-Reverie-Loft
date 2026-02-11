from .cache import cache, cache_invalidator, setup_cache
from .cors import setup_cors
from .database.redis import redis, setup_redis
from .database.sqlalchemy import db, setup_sqlalchemy
from .jwt import setup_jwt
from .jwt.my_jwt import JwtUtils
from .logger import setup_logging
from .mail import mail, setup_mail
from .my_celery import (
    create_chat_notifications,
    create_comment_notifications,
    create_like_notifications,
    create_new_post_notifications,
    hard_delete_post,
    log_visitor,
    send_email,
    setup_celery,
)
from .my_limiter import limiter, setup_limiter

__all__ = [
    "db",
    "redis",
    "cache",
    "mail",
    "limiter",
    "setup_sqlalchemy",
    "setup_redis",
    "setup_cache",
    "setup_mail",
    "setup_limiter",
    "setup_celery",
    "setup_cors",
    "setup_jwt",
    "cache_invalidator",
    "log_visitor",
    "create_new_post_notifications",
    "create_comment_notifications",
    "create_chat_notifications",
    "create_like_notifications",
    "send_email",
    "hard_delete_post",
    "JwtUtils",
    "setup_logging",
]

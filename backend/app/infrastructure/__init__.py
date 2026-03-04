from .cache import setup_cache
from .capabilities import (
    capability_enabled,
    get_all_capabilities,
    get_capability,
    set_capability,
)
from .cors import setup_cors
from .database.redis import setup_redis
from .database.sqlalchemy import setup_sqlalchemy
from .jwt import setup_jwt
from .logger import setup_logging
from .mail import setup_mail
from .migration import setup_migration
from .my_celery import setup_celery
from .my_limiter import setup_limiter
from .oauth import setup_oauth
from .observability import setup_slow_query_monitor
from .providers import get_cache, get_db, get_limiter, get_mail, get_redis, get_socketio
from .socketio import setup_socketio
from .startup_report import print_startup_report
from .storage import setup_storage

__all__ = [
    "setup_sqlalchemy",
    "setup_redis",
    "setup_cache",
    "setup_mail",
    "setup_limiter",
    "setup_celery",
    "setup_oauth",
    "setup_cors",
    "setup_jwt",
    "setup_socketio",
    "setup_storage",
    "print_startup_report",
    "setup_migration",
    "setup_logging",
    "setup_slow_query_monitor",
    "set_capability",
    "get_capability",
    "get_all_capabilities",
    "capability_enabled",
    "get_db",
    "get_redis",
    "get_cache",
    "get_mail",
    "get_limiter",
    "get_socketio",
]

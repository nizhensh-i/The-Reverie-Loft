"""
Infrastructure providers.
Expose extension instances via getter functions to avoid root-level symbol sprawl.
"""

from .cache import cache
from .database.redis import redis
from .database.sqlalchemy import db
from .mail import mail
from .my_limiter import limiter
from .socketio import socketio


def get_db():
    return db


def get_redis():
    return redis


def get_cache():
    return cache


def get_mail():
    return mail


def get_limiter():
    return limiter


def get_socketio():
    return socketio


__all__ = [
    "get_db",
    "get_redis",
    "get_cache",
    "get_mail",
    "get_limiter",
    "get_socketio",
]

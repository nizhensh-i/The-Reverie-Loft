# -*- coding: utf-8 -*-
import logging

from config import config
from flask import Flask

from .api import setup_api_bp
from .auth import setup_auth_bp
from .error_handler import setup_error_handler
from .event import cleanup, register_cleanup_handlers, register_ws_events
from .infrastructure import (
    setup_cache,
    setup_celery,
    setup_cors,
    setup_jwt,
    setup_limiter,
    setup_logging,
    setup_mail,
    setup_migration,
    setup_oauth,
    setup_redis,
    setup_socketio,
    setup_sqlalchemy,
    setup_storage,
)
from .infrastructure.observability import setup_slow_query_monitor
from .infrastructure.providers import get_db, get_redis, get_socketio
from .middleware import setup_proxyfix_middleware

db = get_db()
redis = get_redis()
socketio = get_socketio()


def create_app(config_name):
    app = Flask(__name__)
    # 设置代理配置
    setup_proxyfix_middleware(app)

    # 读取配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 跨域
    setup_cors(app)
    setup_logging(app)
    setup_sqlalchemy(app)
    setup_redis(app)
    setup_migration(app, db)
    setup_jwt(app, redis)
    setup_mail(app)
    setup_storage(app)
    setup_cache(app)
    setup_limiter(app)
    setup_oauth()
    setup_celery(app)

    setup_api_bp(app)
    setup_auth_bp(app)

    setup_error_handler(app)
    setup_slow_query_monitor(app)

    return app


def create_ws_app(config_name):
    app = Flask(__name__)

    # 设置代理配置
    setup_proxyfix_middleware(app)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 跨域
    setup_cors(app)
    setup_logging(app)
    setup_sqlalchemy(app)
    setup_redis(app)
    setup_socketio(app)
    setup_jwt(app, redis)
    setup_celery(app)

    # 注册WS事件和优雅停机处理器
    register_ws_events(socketio, app)
    # 启动WebSocket清理服务
    cleanup.start()
    logging.info("WebSocket 应用初始化完成，清理服务已启动")
    # 注册优雅停机处理器（只在WebSocket应用中注册）
    register_cleanup_handlers(app)

    return app

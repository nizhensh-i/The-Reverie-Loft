# -*- coding: utf-8 -*-
import logging

from config import config
from flask import Flask
from flask_socketio import SocketIO
from werkzeug.middleware.proxy_fix import ProxyFix

from .api import setup_api_bp
from .auth import setup_auth_bp
from .error_handler import setup_error_handler
from .infrastructure import (
    db,
    redis,
    setup_cache,
    setup_celery,
    setup_cors,
    setup_jwt,
    setup_limiter,
    setup_logging,
    setup_mail,
    setup_redis,
    setup_sqlalchemy,
)
from .management import setup_migration

socketio = SocketIO()


def setup_proxyfix_middleware(app):
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,  # 对应 X-Forwarded-For（信任1层代理）
        x_proto=1,  # 对应 X-Forwarded-Proto（信任1层代理）
        x_host=1,  # 对应 X-Forwarded-Host（信任1层代理）
        x_prefix=1,  # 对应 X-Forwarded-Prefix（信任1层代理）
    )


def create_app(config_name):
    app = Flask(__name__)
    # 设置代理配置
    setup_proxyfix_middleware(app)

    # 读取配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 跨域
    setup_cors(app)
    # 配置日志系统
    setup_logging(app)
    setup_sqlalchemy(app)
    setup_redis(app)
    setup_migration(app, db)
    setup_jwt(app, redis)
    setup_mail(app)
    setup_cache(app)
    setup_limiter(app)
    setup_celery(app)

    setup_api_bp(app)
    setup_auth_bp(app)

    setup_error_handler(app)

    return app


def create_ws_app(config_name):
    app = Flask(__name__)

    # 设置代理配置
    setup_proxyfix_middleware(app)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 跨域
    setup_cors(app)
    # 配置日志系统
    setup_logging(app)

    socketio.init_app(
        app,
        cors_allowed_origins="*",
        ping_timeout=30,
        ping_interval=60,
        message_queue=app.config["SOCKETIO_MESSAGE_QUEUE"],
    )

    setup_sqlalchemy(app)
    setup_redis(app)
    setup_jwt(app, redis)
    setup_celery(app)

    # 注册WS事件和清理服务
    from app.event import cleanup, register_cleanup_handlers, register_ws_events

    register_ws_events(socketio, app)

    # 启动WebSocket清理服务
    cleanup.start()
    logging.info("WebSocket 应用初始化完成，清理服务已启动")

    # 注册优雅停机处理器（只在WebSocket应用中注册）
    register_cleanup_handlers(app)

    return app

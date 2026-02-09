# -*- coding: utf-8 -*-
import logging
import os

from config import config
from dotenv import load_dotenv
from flask import Flask
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_redis import FlaskRedis
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

from .mycelery import celery_init_app
from .utils.logger import setup_logging
from .utils.response import server_error


def my_key_func():
    """根据当前用户id限速"""
    return current_user.id if current_user else get_remote_address


db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
redis = FlaskRedis()
socketio = SocketIO()
cache = Cache()

# github工作流上redis容器不使用密码
redis_pass = "" if os.getenv("FLASK_CONFIG") == "testing" else ":1234@"
limiter = Limiter(
    my_key_func,
    storage_uri=f"redis://{redis_pass}{os.getenv('REDIS_HOST') or os.getenv('FLASK_RUN_HOST')}:6379/3",
)


def create_app(config_name):
    app = Flask(__name__)

    # 设置代理配置
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,  # 对应 X-Forwarded-For（信任1层代理）
        x_proto=1,  # 对应 X-Forwarded-Proto（信任1层代理）
        x_host=1,  # 对应 X-Forwarded-Host（信任1层代理）
        x_prefix=1,  # 对应 X-Forwarded-Prefix（信任1层代理）
    )

    # 跨域
    CORS(app)

    # 开发模式执行celery启动命令时，需要加载环境变量
    if not os.getenv("APP_RUN"):
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录的路径
        current_dir_path = os.path.dirname(current_file_path)
        # 获取父目录的路径
        parent_dir_path = os.path.dirname(current_dir_path)
        dotenv_path = os.path.join(parent_dir_path, ".env")
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)

    # 读取配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 配置日志系统
    setup_logging(app)

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    redis.init_app(app, decode_responses=True)
    celery_init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint

    app.register_blueprint(api_blueprint, url_prefix="/api/v1")

    @app.errorhandler(Exception)
    def error_handler(e):
        logging.error(f"全局异常: {str(e)}", exc_info=True)
        if os.environ.get("FLASK_DEBUG", None):
            print(e)

        return server_error(message=str(e))

    return app


def create_ws_app(config_name):
    app = Flask(__name__)
    # 设置代理配置
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_prefix=1,
    )

    # 跨域
    CORS(app)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 配置日志系统
    setup_logging(app)

    db.init_app(app)
    jwt.init_app(app)
    redis.init_app(app, decode_responses=True)
    celery_init_app(app)
    socketio.init_app(
        app,
        cors_allowed_origins="*",
        ping_timeout=30,
        ping_interval=60,
        message_queue=app.config["SOCKETIO_MESSAGE_QUEUE"],
    )

    # 注册WS事件和清理服务
    from app.event import cleanup, register_cleanup_handlers, register_ws_events

    register_ws_events(socketio, app)

    # 启动WebSocket清理服务
    cleanup.start()
    logging.info("WebSocket 应用初始化完成，清理服务已启动")

    # 注册优雅停机处理器（只在WebSocket应用中注册）
    register_cleanup_handlers(app)

    return app

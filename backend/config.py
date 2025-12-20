import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"

    JWT_SECRET_KEY = "super-secret"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=60 * 20)

    # 邮件配置
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.qq.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or "zmc_li@foxmail.com"
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    # 发送者的邮箱
    MAIL_DEFAULT_SENDER = "zmc_li@foxmail.com"

    FLASKY_MAIL_SUBJECT_PREFIX = "[Flasky]"
    FLASKY_MAIL_SENDER = "Flasky Admin <flasky@example.com>"
    # 管理员邮箱，当用户通过网站注册时，如果用户的邮箱与配置的管理员邮箱相同，则该用户将具有管理员权限
    FLASKY_ADMIN = "zmc_li@foxmail.com"
    SSL_REDIRECT = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_size": 6, "max_overflow": 8}

    FLASKY_POSTS_PER_PAGE = 10
    FLASKY_FOLLOWERS_PER_PAGE = 15
    # 评论分页大小
    FLASKY_COMMENTS_PER_PAGE = 10
    # 回复评论分页大小
    FLASKY_COMMENTS_REPLY_PER_PAGE = 5
    FLASKY_LOG_PER_PAGE = 15
    # 聊天记录分页大小
    FLASKY_CHAT_PER_PAGE = 15

    FLASKY_SLOW_DB_QUERY_TIME = 0.5

    # 适配多进程部署
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = f"redis://:1234@{os.getenv('REDIS_HOST') or '127.0.0.1'}:6379/5"

    # CELERY
    CELERY = dict(
        broker_url=f"redis://:1234@{os.getenv('REDIS_HOST') or '127.0.0.1'}:6379/1",
        result_backend=f"redis://:1234@{os.getenv('REDIS_HOST') or '127.0.0.1'}:6379/2",
        timezone="Asia/Shanghai",
        task_serializer="pickle",
        result_serializer="pickle",
        accept_content=["pickle", "json"],
    )

    # 存储socketio的消息队列
    SOCKETIO_MESSAGE_QUEUE = (
        f"redis://:1234@{os.getenv('REDIS_HOST') or '127.0.0.1'}:6379/4"
    )

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    # mysql
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DEV_DATABASE_URL")
        or "mysql+pymysql://root:1234@"
        + os.getenv("FLASK_RUN_HOST", "127.0.0.1")
        + ":3306/backend_flask?charset=utf8mb4"
    )
    # redis  格式：redis://:<password>@<host>:<port>/<db>
    REDIS_URL = (
        os.environ.get("DEV_REDIS_URL")
        or "redis://:1234@" + os.getenv("FLASK_RUN_HOST", "127.0.0.1") + ":6379/0"
    )


class TestingConfig(Config):
    # TESTING = True会导致flask_mail发送不了邮件
    TESTING = True
    DEBUG = True
    # 关掉flask_limiter限流
    RATELIMIT_ENABLED = False
    # mysql
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("TEST_DATABASE_URL")
        or "mysql+pymysql://root:1234@127.0.0.1:3306/test_backend_flask?charset=utf8mb4"
    )
    # redis - 支持GitHub Actions的无密码Redis
    test_redis_url = os.environ.get("TEST_REDIS_URL")
    if test_redis_url:
        # GitHub Actions: 无密码Redis
        REDIS_URL = test_redis_url
        # 修改Celery配置以匹配无密码Redis
        CELERY = {
            **Config.CELERY,
            'broker_url': test_redis_url.replace('/0', '/1'),
            'result_backend': test_redis_url.replace('/0', '/2'),
            'task_always_eager': True,
            'task_eager_propagates': True,
        }
    else:
        # 本地开发：有密码Redis
        REDIS_URL = (
            "redis://:1234@" + os.getenv("FLASK_RUN_HOST", "127.0.0.1") + ":6379/0"
        )
        # Celery测试配置：强制同步执行任务
        CELERY = {
            **Config.CELERY,
            'task_always_eager': True,
            'task_eager_propagates': True,
        }
    
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    # mysql
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "mysql+pymysql://root:1234@"
        + os.getenv("FLASK_RUN_HOST", "127.0.0.1")
        + ":3306/backend_flask?charset=utf8mb4"
    )
    # redis
    REDIS_URL = (
        os.environ.get("REDIS_URL")
        or "redis://:1234@" + os.getenv("FLASK_RUN_HOST", "127.0.0.1") + ":6379/0"
    )

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class DockerConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "docker": DockerConfig,
    "default": DevelopmentConfig,
}

import os

from flask_jwt_extended import current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def my_key_func():
    """根据当前用户id限速"""
    return current_user.id if current_user else get_remote_address


# github工作流上redis容器不使用密码
redis_pass = "" if os.getenv("FLASK_CONFIG") == "testing" else ":1234@"

# 这里从环境变量中读取
redis_url = f"redis://{redis_pass}{os.getenv('REDIS_HOST') or os.getenv('FLASK_RUN_HOST')}:6379/3"


limiter = Limiter(
    my_key_func,
    storage_uri=redis_url,
)


def setup_limiter(app):
    limiter.init_app(app)

import os

from app import create_app
from app.infrastructure.config.runtime_env import load_env

# 加载.env环境变量
load_env()

flask_app = create_app(os.getenv("FLASK_CONFIG") or "default")
celery_app = flask_app.extensions["celery"]

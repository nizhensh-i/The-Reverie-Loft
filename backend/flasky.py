import os

from app.infrastructure import setup_logging
from app.infrastructure.config.runtime_env import get_local_ip, load_env

# 初始化全局日志系统
setup_logging()

# 加载.env环境变量
load_env()

# 开发环境自动获取本地地址
if os.getenv("FLASK_DEBUG"):
    os.environ["FLASK_RUN_HOST"] = get_local_ip()

from app import create_app

app = create_app(os.getenv("FLASK_CONFIG") or "default")


if __name__ == "__main__":
    app.run(host=os.getenv("FLASK_RUN_HOST"), port=os.getenv("FLASK_RUN_PORT"))

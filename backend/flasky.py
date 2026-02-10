import logging
import os

from app.utils.common import get_local_ip
from app.utils.logger import setup_logging
from dotenv import load_dotenv

# 初始化全局日志系统
setup_logging()

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
logging.info(f"加载环境变量文件: {dotenv_path}")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# 开发环境自动获取本地地址
if os.getenv("FLASK_DEBUG"):
    os.environ["FLASK_RUN_HOST"] = get_local_ip()

from app import create_app

app = create_app(os.getenv("FLASK_CONFIG") or "default")


if __name__ == "__main__":
    app.run(host=os.getenv("FLASK_RUN_HOST"), port=os.getenv("FLASK_RUN_PORT"))

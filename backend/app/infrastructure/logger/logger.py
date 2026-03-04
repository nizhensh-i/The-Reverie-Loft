import logging
import logging.handlers
import os
from datetime import datetime

from ...utils.time_util import DateUtils


class FlaskMailHandler(logging.Handler):
    """
    继承 logging.Handler，将日志通过 Flask-Mail 发送 HTML 邮件
    """

    def __init__(self):
        super().__init__()
        self.formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s"
        )

    def emit(self, record):
        try:
            from .. import send_email

            log_text = self.format(record)
            send_email.delay(
                "1912592745@qq.com",
                "Loft应用系统错误告警",
                "error_email.html",
                username="admin",
                error_message=log_text,
                year=DateUtils.get_year(),
            )
        except Exception:
            self.handleError(record)


def setup_logging(app=None):
    """
    配置全局日志系统，使用根记录器

    Args:
        app: Flask应用实例，可选
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 创建日志目录
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../logs"))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 日志文件路径
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')

    # 统一 root handler，避免重复初始化导致日志重复/格式不一致。
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=30, encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    if app:
        for handler in list(app.logger.handlers):
            app.logger.removeHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.propagate = True

        # 邮件处理器
        if not app.debug:
            mail_handler = FlaskMailHandler()
            mail_handler.setLevel(logging.ERROR)
            if not any(isinstance(h, FlaskMailHandler) for h in root_logger.handlers):
                root_logger.addHandler(mail_handler)

            logging.info("已配置邮件处理器")
        logging.info("Flask应用日志系统初始化完成")
    else:
        logging.info("基本日志系统初始化完成")

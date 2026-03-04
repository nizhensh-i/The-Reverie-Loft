import logging

from app.exceptions import AppError, ValidationError
from flask import request
from sqlalchemy.exc import OperationalError
from werkzeug.exceptions import HTTPException

from .infrastructure.exceptions import RateLimitError
from .utils.response import bad_request
from .utils.response import error as api_error
from .utils.response import forbidden, not_found, server_error, too_many_req


def setup_error_handler(app):
    """为应用注册统一的异常处理器"""

    def handle_global_exception(exc):
        if isinstance(exc, ValidationError):
            logging.warning(f"验证错误: {exc.args[0]}")
            return bad_request(message=exc.args[0])
        elif isinstance(exc, RateLimitError):
            logging.warning(f"请求频率超限: {request.path}, {str(exc)}")
            return too_many_req(message=str(exc))
        elif isinstance(exc, AppError):
            logging.warning(f"应用异常: {request.path}, {str(exc)}")
            return api_error(code=exc.code, message=str(exc))
        elif isinstance(exc, OperationalError):
            logging.error(f"数据库错误: {exc}", exc_info=True)
            return server_error(message="数据库错误")

        # HTTP 异常
        if isinstance(exc, HTTPException):
            status_code = exc.code
            if status_code == 403:
                logging.warning(f"权限不足: {request.path}")
                return forbidden(message="权限不足")
            elif status_code == 404:
                logging.warning(f"资源不存在: {request.path}")
                return not_found(message="资源不存在")
            elif status_code == 429:
                logging.warning(f"请求频率超限: {request.path}")
                return too_many_req(message="请求频率超限")
            elif status_code == 500:
                logging.error(f"服务器内部错误: {request.path}", exc_info=True)
                return server_error(message="服务器内部错误")

        # 未知异常
        logging.error(f"全局异常: {str(exc)}", exc_info=True)
        return server_error(message=str(exc))

    app.errorhandler(Exception)(handle_global_exception)

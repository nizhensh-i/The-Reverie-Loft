import logging

from app.exceptions import ValidationError
from flask import request
from sqlalchemy.exc import OperationalError
from werkzeug.exceptions import HTTPException

from .utils.response import (
    bad_request,
    forbidden,
    not_found,
    server_error,
    too_many_req,
)


def setup_error_handler(app):
    """为应用注册统一的异常处理器"""

    def handle_global_exception(error):
        if isinstance(error, ValidationError):
            logging.warning(f"验证错误: {error.args[0]}")
            return bad_request(message=error.args[0])
        elif isinstance(error, OperationalError):
            logging.error(f"数据库错误: {error}", exc_info=True)
            return server_error(message="数据库错误")

        # HTTP 异常
        if isinstance(error, HTTPException):
            status_code = error.code
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
        logging.error(f"全局异常: {str(error)}", exc_info=True)
        return server_error(message=str(error))

    app.errorhandler(Exception)(handle_global_exception)

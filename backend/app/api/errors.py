import logging

from app.exceptions import ValidationError
from flask import request
from sqlalchemy.exc import OperationalError

from ..utils.response import bad_request, server_error
from . import api


@api.errorhandler(ValidationError)
def validation_error(e):
    logging.warning(f"验证错误: {e.args[0]}")
    return bad_request(message=e.args[0])


@api.errorhandler(OperationalError)
def mysql_error(e):
    logging.info(f"数据库错误:{e}")
    return server_error(message="数据库错误")

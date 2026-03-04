import logging

from dependency_injector.wiring import Provide, inject
from flask import current_app, request
from flask_jwt_extended import jwt_required

from ..container import AppContainer
from ..decorators import DecoratedMethodView, admin_required
from ..services.log_service import LogService
from ..utils.response import success
from . import api


@inject
def _log_service(
    log_service: LogService = Provide[AppContainer.log_service],
) -> LogService:
    return log_service


class LogApi(DecoratedMethodView):
    method_decorators = {
        "get": [jwt_required(), admin_required],
        "delete": [jwt_required(), admin_required],
    }

    def get(self):
        logging.info("获取日志")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get(
            "size", current_app.config["FLASKY_LOG_PER_PAGE"], type=int
        )
        result = _log_service().list_logs(page=page, per_page=per_page)
        return success(data=result.data, total=result.total)

    def delete(self):
        logging.info("删除日志")
        payload = request.get_json() or {}
        result = _log_service().delete_logs(ids=payload.get("ids", []))
        return success(message=result.message, data=result.data)


@api.route("/online-users")
@jwt_required()
@admin_required
def get_online_users():
    result = _log_service().list_online_users()
    return success(data=result.data, total=result.total)


def register_log_api(bp, *, logs_url):
    bp.add_url_rule(logs_url, view_func=LogApi.as_view("logs"))

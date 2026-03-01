import logging

from flask import current_app, request
from flask_jwt_extended import jwt_required

from ..composition import get_container
from ..decorators import DecoratedMethodView, admin_required
from ..utils.response import success
from . import api


def _log_service():
    return get_container().log_service()


class LogApi(DecoratedMethodView):
    method_decorators = {
        "get": [jwt_required(), admin_required],
        "delete": [jwt_required(), admin_required],
    }

    def get(self):
        logging.info("查询日志")
        page = request.args.get("page", 1, type=int)
        result = _log_service().list_logs(
            page=page,
            per_page=current_app.config["FLASKY_LOG_PER_PAGE"],
        )
        return success(data=result.data, total=result.total)

    def delete(self):
        ids = (request.get_json() or {}).get("ids", [])
        result = _log_service().delete_logs(ids=ids)
        return success(message=result.message, data=result.data)


@api.route("/online-users")
@jwt_required()
@admin_required
def online_users():
    result = _log_service().list_online_users()
    return success(data=result.data, total=result.total)


def register_log_api(bp, *, logs_url):
    view = LogApi.as_view("logs")
    bp.add_url_rule(logs_url, view_func=view)

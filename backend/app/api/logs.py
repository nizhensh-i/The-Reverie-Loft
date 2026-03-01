import logging

from flask import current_app, request
from flask_jwt_extended import jwt_required

from ..decorators import DecoratedMethodView, admin_required
from ..services.log_service import LogService
from ..utils.response import error, success
from . import api

log_service = LogService()


# --------------------------- 日志管理 ---------------------------
@api.route("/online-users")
@admin_required
@jwt_required()
def online():
    """获取在线用户信息"""
    logging.info("获取在线用户信息")
    result = log_service.list_online_users()
    logging.info(f"在线用户数:{result.total}")
    return success(data=result.data, total=result.total)


class LogApi(DecoratedMethodView):
    method_decorators = {
        "share": [jwt_required(), admin_required],
    }

    def get(self):
        """获取系统日志"""
        logging.info("获取系统日志")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get(
            "per_page", current_app.config["FLASKY_LOG_PER_PAGE"], type=int
        )
        result = log_service.list_logs(page=page, per_page=per_page)
        logging.info(f"获取到 {len(result.data)} 条日志记录")
        return success(data=result.data, total=result.total)

    def delete(self):
        """删除系统日志"""
        logging.info("删除系统日志")
        try:
            ids = request.get_json().get("ids", [])
            result = log_service.delete_logs(ids=ids)
            logging.info(result.message)
            return success(message=result.message, data=result.data)
        except Exception as e:
            logging.error(f"删除日志失败: {str(e)}", exc_info=True)
            log_service.rollback()
            return error(500, f"删除日志失败: {str(e)}")


def register_log_api(bp, *, logs_url):
    _log = LogApi.as_view("logs")
    bp.add_url_rule(logs_url, view_func=_log)

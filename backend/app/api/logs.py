import logging

from flask import current_app, request
from flask_jwt_extended import jwt_required

from ..decorators import DecoratedMethodView, admin_required
from ..infrastructure import db, redis
from ..models import Log, User
from ..utils.response import error, success
from ..websocket import init_ws_services
from . import api


# --------------------------- 日志管理 ---------------------------
@api.route("/online-users")
@admin_required
@jwt_required()
def online():
    """获取在线用户信息"""
    logging.info("获取在线用户信息")

    _, presence, _, _ = init_ws_services(redis)
    # 在线人数信息
    user_ids = presence.list_online_users()
    logging.info(f"在线用户:{user_ids}")
    online_users = User.query.filter(User.id.in_(user_ids)).all()
    users = [{"username": u.username, "nickName": u.nickname} for u in online_users]
    return success(data=users, total=len(user_ids))


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
        query = Log.query
        paginate = query.order_by(Log.operate_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        logs = paginate.items
        logging.info(f"获取到 {len(logs)} 条日志记录")
        return success(data=[log.to_json() for log in logs], total=query.count())

    def delete(self):
        """删除系统日志"""
        logging.info("删除系统日志")
        try:
            ids = request.get_json().get("ids", [])
            if not ids:
                logging.info("没有提供要删除的日志ID")
                return success(message="没有提供要删除的日志ID")

            deleted_count = Log.query.filter(Log.id.in_(ids)).delete()
            db.session.commit()
            logging.info(f"成功删除 {deleted_count} 条日志记录")
            return success(message=f"成功删除 {deleted_count} 条日志记录")
        except Exception as e:
            logging.error(f"删除日志失败: {str(e)}", exc_info=True)
            db.session.rollback()
            return error(500, f"删除日志失败: {str(e)}")


def register_log_api(bp, *, logs_url):
    _log = LogApi.as_view("logs")
    bp.add_url_rule(logs_url, view_func=_log)

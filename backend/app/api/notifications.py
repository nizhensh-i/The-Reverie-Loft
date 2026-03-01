import logging

from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..decorators import DecoratedMethodView
from ..services.notification_service import NotificationService
from ..utils.response import success

notification_service = NotificationService()


# --------------------------- 通知功能 ---------------------------
class NotificationApi(DecoratedMethodView):
    method_decorators = {
        "share": [jwt_required()],
    }

    def get(self):
        """获取当前用户的所有通知"""
        logging.info(f"获取用户通知: user_id={current_user.id}")
        result = notification_service.list_user_notifications(user_id=current_user.id)
        return success(data=result.data)

    def patch(self):
        """标记通知为已读"""
        logging.info(f"标记通知已读: user_id={current_user.id}")
        ids = (request.get_json() or {}).get("ids", [])
        result = notification_service.update_notifications_read(
            user_id=current_user.id,
            ids=ids,
        )
        return success(message=result.message)


def register_notification_api(bp, *, notification_url):
    bp.add_url_rule(notification_url, view_func=NotificationApi.as_view("notification"))

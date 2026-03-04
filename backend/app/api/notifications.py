import logging

from dependency_injector.wiring import Provide, inject
from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..container import AppContainer
from ..decorators import DecoratedMethodView
from ..services.notification_service import NotificationService
from ..utils.response import success


@inject
def _notification_service(
    notification_service: NotificationService = Provide[
        AppContainer.notification_service
    ],
) -> NotificationService:
    return notification_service


class NotificationApi(DecoratedMethodView):
    method_decorators = {
        "share": [jwt_required()],
    }

    def get(self):
        logging.info(f"获取用户通知: user_id={current_user.id}")
        result = _notification_service().list_user_notifications(
            user_id=current_user.id
        )
        return success(data=result.data)

    def patch(self):
        logging.info(f"标记通知已读: user_id={current_user.id}")
        ids = (request.get_json() or {}).get("ids", [])
        result = _notification_service().update_notifications_read(
            user_id=current_user.id,
            ids=ids,
        )
        return success(message=result.message)


def register_notification_api(bp, *, notification_url):
    bp.add_url_rule(notification_url, view_func=NotificationApi.as_view("notification"))

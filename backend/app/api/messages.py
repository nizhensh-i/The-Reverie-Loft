import logging

from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..decorators import DecoratedMethodView
from ..services.message_service import MessageService
from ..utils.response import success

message_service = MessageService()

# --------------------------- 聊天消息 ---------------------------


class MessageApi(DecoratedMethodView):
    method_decorators = {
        "share": [jwt_required()],
    }

    def get(self, user_id):
        """获取聊天历史记录"""
        logging.info(f"获取聊天历史: user_id={current_user.id}")
        page = request.args.get("page", 1, type=int)
        result = message_service.list_conversation_messages(
            current_user_id=current_user.id,
            other_user_id=user_id,
            page=page,
        )
        return success(data=result.data, total=result.total)

    def post(self, user_id):
        """标记消息为已读"""
        logging.info(f"标记消息已读: user_id={current_user.id}")
        message_ids = (request.json or {}).get("ids", [])
        result = message_service.mark_conversation_messages_read(
            current_user_id=current_user.id,
            sender_user_id=user_id,
            message_ids=message_ids,
        )
        return success(message=result.message)


def register_message_api(bp, *, message_url):
    message = MessageApi.as_view("message")
    bp.add_url_rule(message_url, view_func=message)

from flask import Blueprint

api = Blueprint("api", __name__)

from . import _admin, follow, upload, users
from .comments import register_comment_api
from .follow import register_follow_api
from .logs import register_log_api
from .messages import register_message_api
from .notifications import register_notification_api
from .posts import register_post_api
from .praise import register_praise_api
from .tags import register_tag_api
from .user_1 import register_user_api

register_post_api(api, post_item_url="/posts/<int:id>", post_group_url="/posts")
register_notification_api(api, notification_url="/notifications")
register_user_api(
    api,
    user_by_id_url="/users/<int:id>",
    user_by_username_url="/users/u/<string:username>",
    user_image_url="/users/<int:id>/image",
)
register_follow_api(api, follow_url="/users/<string:username>/follow")
register_praise_api(
    api,
    post_praise_url="/posts/<int:post_id>/likes",
    comment_praise_url="/comments/<int:comment_id>/likes",
)
register_tag_api(api, tag_user_url="/users/<int:user_id>/tags", tag_url="/tags")
register_message_api(api, message_url="/conversations/<int:user_id>/messages")
register_log_api(api, logs_url="/logs")
register_comment_api(
    api,
    comment_url="/posts/<int:post_id>/comments",
    comment_manage_url="/comments/<int:comment_id>",
)


def setup_api_bp(app):
    app.register_blueprint(api, url_prefix="/api/v1")


__all__ = ["setup_api_bp"]

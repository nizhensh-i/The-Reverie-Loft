import logging

from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..decorators import DecoratedMethodView, permission_required
from ..models import Permission
from ..services.follow_service import FollowService
from ..utils.response import error, success
from . import api

follow_service = FollowService()


# --------------------------- 关注 ---------------------------
@api.route("/users/<username>/followers")
def followers(username):
    """获取用户的粉丝列表"""
    logging.info(f"获取用户粉丝列表: username={username}")
    user = follow_service.get_user_by_username(username)
    query = request.args.get("name", "")
    if query:
        result = follow_service.list_matched_followers(user=user, search_query=query)
        return success(data=result.data)
    page = request.args.get("page", 1, type=int)
    result = follow_service.list_followers(username=username, page=page)
    return success(data=result.data, total=result.total)


@api.route("/users/<username>/following")
def followed_by(username):
    """获取用户关注的人列表"""
    logging.info(f"获取用户关注列表: username={username}")
    user = follow_service.get_user_by_username(username)
    query = request.args.get("name", "")
    if query:
        result = follow_service.list_matched_following(user=user, search_query=query)
        return success(data=result.data)
    page = request.args.get("page", 1, type=int)
    result = follow_service.list_following(username=username, page=page)
    return success(data=result.data, total=result.total)


class UserFollowApi(DecoratedMethodView):
    """关注 & 粉丝"""

    method_decorators = {
        "share": [jwt_required(), permission_required(Permission.FOLLOW)],
    }

    def post(self, username):
        """关注用户"""
        logging.info(f"关注用户: {current_user.username} -> {username}")
        user = follow_service.get_user_by_username(username)
        if current_user.is_following(user):
            return error(400, "你已经关注了该用户")
        try:
            result = follow_service.create_following(
                operator=current_user, username=username
            )
            return success(data=result.data)
        except Exception as exc:
            logging.error("关注用户失败: %s", exc, exc_info=True)
            return error(500, f"关注用户失败: {exc}")

    def delete(self, username):
        """取消关注用户"""
        logging.info(f"取消关注用户: {current_user.username} -> {username}")
        user = follow_service.get_user_by_username(username)
        if not current_user.is_following(user):
            return error(400, "你未关注该用户")
        try:
            result = follow_service.delete_following(
                operator=current_user, username=username
            )
            return success(data=result.data)
        except Exception as exc:
            logging.error("取消关注用户失败: %s", exc, exc_info=True)
            return error(500, f"取消关注用户失败: {exc}")


def register_follow_api(bp, *, follow_url):
    user_follow = UserFollowApi.as_view("users_follow")
    bp.add_url_rule(follow_url, view_func=user_follow)

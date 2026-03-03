import logging

from dependency_injector.wiring import Provide, inject
from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..container import AppContainer
from ..decorators import DecoratedMethodView, permission_required
from ..domain.common.constants import PermissionCode
from ..services.follow_service import FollowService
from ..utils.response import error, success
from . import api


@inject
def _follow_service(
    follow_service: FollowService = Provide[AppContainer.follow_service],
) -> FollowService:
    return follow_service


@api.route("/users/<username>/followers")
def followers(username):
    logging.info(f"获取用户粉丝列表: username={username}")
    query = request.args.get("name", "")
    if query:
        result = _follow_service().list_matched_followers(
            username=username,
            search_query=query,
        )
        return success(data=result.data)
    page = request.args.get("page", 1, type=int)
    result = _follow_service().list_followers(username=username, page=page)
    return success(data=result.data, total=result.total)


@api.route("/users/<username>/following")
def followed_by(username):
    logging.info(f"获取用户关注列表: username={username}")
    query = request.args.get("name", "")
    if query:
        result = _follow_service().list_matched_following(
            username=username,
            search_query=query,
        )
        return success(data=result.data)
    page = request.args.get("page", 1, type=int)
    result = _follow_service().list_following(username=username, page=page)
    return success(data=result.data, total=result.total)


class UserFollowApi(DecoratedMethodView):
    method_decorators = {
        "share": [jwt_required(), permission_required(PermissionCode.FOLLOW)],
    }

    def post(self, username):
        logging.info(f"关注用户: {current_user.username} -> {username}")
        try:
            result = _follow_service().create_follow(
                operator=current_user, username=username
            )
            return success(data=result.data)
        except Exception as exc:
            logging.error("关注用户失败: %s", exc, exc_info=True)
            return error(500, f"关注用户失败: {exc}")

    def delete(self, username):
        logging.info(f"取消关注用户: {current_user.username} -> {username}")
        try:
            result = _follow_service().delete_follow(
                operator=current_user, username=username
            )
            return success(data=result.data)
        except Exception as exc:
            logging.error("取消关注用户失败: %s", exc, exc_info=True)
            return error(500, f"取消关注用户失败: {exc}")


def register_follow_api(bp, *, follow_url):
    user_follow = UserFollowApi.as_view("users_follow")
    bp.add_url_rule(follow_url, view_func=user_follow)

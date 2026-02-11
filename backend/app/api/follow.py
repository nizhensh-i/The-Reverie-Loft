import logging

from flask import current_app, request
from flask_jwt_extended import current_user, jwt_required

from ..decorators import DecoratedMethodView, permission_required
from ..infrastructure import db
from ..models import Follow, Permission, User
from ..utils.common import get_avatars_url
from ..utils.response import error, not_found, success
from ..utils.time_util import DateUtils
from . import api


# --------------------------- 关注 ---------------------------
# 在关注列表中，根据用户昵称或者账号搜索
def search_followed(user, search_query):
    logging.info(f"搜索关注用户: query={search_query}")
    followed_user_ids = user.followed.with_entities(Follow.followed_id).all()
    followed_user_ids = [item[0] for item in followed_user_ids]
    # 搜索用户名或账号
    followed_users = User.query.filter(
        User.id.in_(followed_user_ids),
        db.or_(
            User.username.ilike(f"%{search_query}%"),
            User.nickname.ilike(f"%{search_query}%"),
        ),
    ).all()
    follows = [
        {"username": item.username, "image": get_avatars_url(item.image)}
        for item in followed_users
        if item.username != user.username
    ]
    return follows


def search_fan(user, search_query):
    logging.info(f"搜索粉丝: query={search_query}")
    followed_user_ids = user.followers.with_entities(Follow.follower_id).all()
    followed_user_ids = [item[0] for item in followed_user_ids]
    # 搜索用户名或账号
    followed_users = User.query.filter(
        User.id.in_(followed_user_ids),
        db.or_(
            User.username.ilike(f"%{search_query}%"),
            User.nickname.ilike(f"%{search_query}%"),
        ),
    ).all()
    followers = [
        {"username": item.username, "image": get_avatars_url(item.image)}
        for item in followed_users
        if item.username != user.username
    ]
    return followers


@api.route("/users/<username>/followers")
def followers(username):
    """获取用户的粉丝列表"""
    logging.info(f"获取用户粉丝列表: username={username}")
    user = User.query.filter_by(username=username).first()
    if user is None:
        return not_found("用户名不存在")

    query = request.args.get("name", "")
    if query:
        followers = search_followed(user, query)
        return success(data=followers)

    page = request.args.get("page", 1, type=int)
    pagination = (
        user.followers.join(Follow.follower)
        .filter(User.username != username)
        .order_by(Follow.timestamp.desc())
        .paginate(
            page=page,
            per_page=current_app.config["FLASKY_FOLLOWERS_PER_PAGE"],
            error_out=False,
        )
    )

    # 批量查询反向关注状态
    follower_ids = [item.follower.id for item in pagination.items]
    following_back = set(
        Follow.query.filter_by(follower_id=user.id)
        .filter(Follow.followed_id.in_(follower_ids))
        .with_entities(Follow.followed_id)
        .all()
    )

    follows = [
        {
            "id": item.follower.id,
            "nickname": item.follower.nickname,
            "username": item.follower.username,
            "image": get_avatars_url(item.follower.image),
            "timestamp": DateUtils.datetime_to_str(item.timestamp),
            "is_following": item.follower.id in following_back,
        }
        for item in pagination.items
    ]
    return success(data=follows, total=pagination.total)


@api.route("/users/<username>/following")
def followed_by(username):
    """获取用户关注的人列表"""
    logging.info(f"获取用户关注列表: username={username}")
    user = User.query.filter_by(username=username).first()
    if user is None:
        return not_found("用户名不存在")

    # 在关注列表中，根据用户昵称或者账号搜索
    query = request.args.get("name", "")
    if query:
        follows = search_followed(user, query)
        return success(data=follows)

    page = request.args.get("page", 1, type=int)
    pagination = (
        user.followed.join(Follow.followed)
        .filter(User.username != username)
        .order_by(Follow.timestamp.desc())
        .paginate(
            page=page,
            per_page=current_app.config["FLASKY_FOLLOWERS_PER_PAGE"],
            error_out=False,
        )
    )

    # 批量查询反向关注状态
    followed_ids = [item.followed.id for item in pagination.items]
    following_back = set(
        Follow.query.filter_by(followed_id=user.id)
        .filter(Follow.follower_id.in_(followed_ids))
        .with_entities(Follow.follower_id)
        .all()
    )

    follows = [
        {
            "id": item.followed.id,
            "nickname": item.followed.nickname,
            "username": item.followed.username,
            "image": get_avatars_url(item.followed.image),
            "timestamp": DateUtils.datetime_to_str(item.timestamp),
            "is_following_back": item.followed.id in following_back,
        }
        for item in pagination.items
    ]
    return success(data=follows, total=pagination.total)


class UserFollowApi(DecoratedMethodView):
    """关注 & 粉丝"""

    decorators = []

    method_decorators = {
        "share": [jwt_required(), permission_required(Permission.FOLLOW)],
    }

    # def follow_or_unfollow(self, username, action="follow"):
    #     logging.info(f"关注用户: {current_user.username} -> {username}")
    #     user = User.query.filter_by(username=username).first()
    #     if user is None:
    #         return not_found("用户名不存在")
    #     if current_user.is_following(user):
    #         return error(400, "你已经关注了该用户")

    #     try:
    #         current_user.follow(user)
    #         db.session.commit()
    #         return success(data=user.to_json())
    #     except Exception as e:
    #         logging.error(f"关注用户失败: {str(e)}", exc_info=True)
    #         db.session.rollback()
    #         return error(500, f"关注用户失败: {str(e)}")

    def post(self, username):
        """关注用户"""
        logging.info(f"关注用户: {current_user.username} -> {username}")
        user = User.query.filter_by(username=username).first()
        if user is None:
            return not_found("用户名不存在")
        if current_user.is_following(user):
            return error(400, "你已经关注了该用户")

        try:
            current_user.follow(user)
            db.session.commit()
            return success(data=user.to_json())
        except Exception as e:
            logging.error(f"关注用户失败: {str(e)}", exc_info=True)
            db.session.rollback()
            return error(500, f"关注用户失败: {str(e)}")

    def delete(self, username):
        """取消关注用户"""
        logging.info(f"取消关注用户: {current_user.username} -> {username}")
        user = User.query.filter_by(username=username).first()
        if user is None:
            return not_found("用户名不存在")
        if not current_user.is_following(user):
            return error(400, "你未关注该用户")

        try:
            current_user.unfollow(user)
            db.session.commit()
            return success(data=user.to_json())
        except Exception as e:
            logging.error(f"取消关注用户失败: {str(e)}", exc_info=True)
            db.session.rollback()
            return error(500, f"取消关注用户失败: {str(e)}")


def register_follow_api(bp, *, follow_url):
    user_follow = UserFollowApi.as_view("users_follow")
    bp.add_url_rule(follow_url, view_func=user_follow)

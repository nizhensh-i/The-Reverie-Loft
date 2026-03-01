import logging

from flask import current_app

from ..domain.common.exceptions import NotFoundError
from ..infrastructure.database.sqlalchemy import db
from ..models import Follow, User
from ..utils.common import get_avatars_url
from ..utils.time_util import DateUtils
from .common.dto import ItemResult, ListResult, PageResult
from .common.unit_of_work import SqlAlchemyUnitOfWork


class FollowService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.uow = SqlAlchemyUnitOfWork(self.session)

    def get_user_by_username(self, username: str):
        user = User.query.filter_by(username=username).first()
        if user is None:
            raise NotFoundError("用户名不存在")
        return user

    def list_matched_following(self, *, user, search_query: str):
        logging.info("搜索关注用户: query=%s", search_query)
        followed_user_ids = user.followed.with_entities(Follow.followed_id).all()
        followed_user_ids = [item[0] for item in followed_user_ids]
        followed_users = User.query.filter(
            User.id.in_(followed_user_ids),
            db.or_(
                User.username.ilike(f"%{search_query}%"),
                User.nickname.ilike(f"%{search_query}%"),
            ),
        ).all()
        return ListResult(
            data=[
                {"username": item.username, "image": get_avatars_url(item.image)}
                for item in followed_users
                if item.username != user.username
            ]
        )

    def list_matched_followers(self, *, user, search_query: str):
        logging.info("搜索粉丝: query=%s", search_query)
        follower_ids = user.followers.with_entities(Follow.follower_id).all()
        follower_ids = [item[0] for item in follower_ids]
        followers = User.query.filter(
            User.id.in_(follower_ids),
            db.or_(
                User.username.ilike(f"%{search_query}%"),
                User.nickname.ilike(f"%{search_query}%"),
            ),
        ).all()
        return ListResult(
            data=[
                {"username": item.username, "image": get_avatars_url(item.image)}
                for item in followers
                if item.username != user.username
            ]
        )

    def list_followers(self, *, username: str, page: int):
        user = self.get_user_by_username(username)
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

        follower_ids = [item.follower.id for item in pagination.items]
        following_back = set(
            Follow.query.filter_by(follower_id=user.id)
            .filter(Follow.followed_id.in_(follower_ids))
            .with_entities(Follow.followed_id)
            .all()
        )

        data = [
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
        return PageResult(data=data, total=pagination.total)

    def list_following(self, *, username: str, page: int):
        user = self.get_user_by_username(username)
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

        followed_ids = [item.followed.id for item in pagination.items]
        following_back = set(
            Follow.query.filter_by(followed_id=user.id)
            .filter(Follow.follower_id.in_(followed_ids))
            .with_entities(Follow.follower_id)
            .all()
        )

        data = [
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
        return PageResult(data=data, total=pagination.total)

    def create_following(self, *, operator, username: str):
        user = self.get_user_by_username(username)
        try:
            operator.follow(user)
            self.uow.commit()
            return ItemResult(data=user.to_json())
        except Exception:
            self.uow.rollback()
            logging.exception("关注用户失败")
            raise

    def delete_following(self, *, operator, username: str):
        user = self.get_user_by_username(username)
        try:
            operator.unfollow(user)
            self.uow.commit()
            return ItemResult(data=user.to_json())
        except Exception:
            self.uow.rollback()
            logging.exception("取消关注用户失败")
            raise

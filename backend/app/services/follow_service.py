import logging

from ..application.dto import ItemResult, ListResult, PageResult
from ..domain.common.exceptions import NotFoundError
from ..domain.common.unit_of_work import UnitOfWork
from ..domain.follow.policies import (
    build_follow_search_item,
    build_follower_page_item,
    build_following_page_item,
    ensure_can_create_following,
    ensure_can_delete_following,
)
from ..domain.ports.assemblers import ResponseAssemblerPort
from ..domain.ports.asset_url import AssetUrlPort
from ..domain.ports.settings import PaginationSettingsPort
from ..utils.time_util import DateUtils


class FollowService:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        assembler: ResponseAssemblerPort,
        asset_url: AssetUrlPort,
        settings: PaginationSettingsPort,
    ):
        self.uow = uow
        self.assembler = assembler
        self.asset_url = asset_url
        self.settings = settings

    def get_user_by_username(self, username: str):
        user = self.uow.users.get_by_username(username)
        if user is None:
            raise NotFoundError("用户名不存在")
        return user

    def list_matched_following(self, *, username: str, search_query: str):
        user = self.get_user_by_username(username)
        logging.info("搜索关注用户: query=%s", search_query)
        followed_users = self.uow.follows.list_matched_following_users(
            user_id=user.id, search_query=search_query
        )
        return ListResult(
            data=[
                build_follow_search_item(
                    user=item,
                    avatar_url=self.asset_url.build(item.image),
                )
                for item in followed_users
                if item.username != user.username
            ]
        )

    def list_matched_followers(self, *, username: str, search_query: str):
        user = self.get_user_by_username(username)
        logging.info("搜索粉丝: query=%s", search_query)
        followers = self.uow.follows.list_matched_follower_users(
            user_id=user.id, search_query=search_query
        )
        return ListResult(
            data=[
                build_follow_search_item(
                    user=item,
                    avatar_url=self.asset_url.build(item.image),
                )
                for item in followers
                if item.username != user.username
            ]
        )

    def list_followers(self, *, username: str, page: int):
        user = self.get_user_by_username(username)
        page_entities = self.uow.follows.list_followers(
            user_id=user.id,
            page=page,
            per_page=self.settings.followers_per_page(),
        )

        follower_ids = [item.follower.id for item in page_entities.items]
        following_back = self.uow.follows.list_followed_ids(
            follower_id=user.id, candidate_ids=follower_ids
        )

        data = [
            {
                **build_follower_page_item(
                    relation=item,
                    avatar_url=self.asset_url.build(item.follower.image),
                    is_following=item.follower.id in following_back,
                ),
                "timestamp": DateUtils.datetime_to_str(item.timestamp),
            }
            for item in page_entities.items
        ]
        return PageResult(data=data, total=page_entities.total)

    def list_following(self, *, username: str, page: int):
        user = self.get_user_by_username(username)
        page_entities = self.uow.follows.list_following(
            user_id=user.id,
            page=page,
            per_page=self.settings.followers_per_page(),
        )

        followed_ids = [item.followed.id for item in page_entities.items]
        following_back = self.uow.follows.list_follower_ids(
            followed_id=user.id, candidate_ids=followed_ids
        )

        data = [
            {
                **build_following_page_item(
                    relation=item,
                    avatar_url=self.asset_url.build(item.followed.image),
                    is_following_back=item.followed.id in following_back,
                ),
                "timestamp": DateUtils.datetime_to_str(item.timestamp),
            }
            for item in page_entities.items
        ]
        return PageResult(data=data, total=page_entities.total)

    def create_follow(self, *, operator, username: str):
        target_user = self.get_user_by_username(username)
        is_following = self.uow.follows.exists_follow_relation(
            follower_id=operator.id, followed_id=target_user.id
        )
        ensure_can_create_following(
            operator_id=operator.id,
            target_user_id=target_user.id,
            already_following=is_following,
        )
        try:
            relation = self.uow.follows.create_follow_relation(
                follower_id=operator.id, followed_id=target_user.id
            )
            self.uow.follows.add(relation)
            self.uow.commit()
            user_extra_data = self.uow.users.build_user_extra_data(
                user_id=target_user.id,
                viewer_id=operator.id,
            )
            return ItemResult(
                data=self.assembler.map_user(target_user, extra_data=user_extra_data)
            )
        except Exception:
            self.uow.rollback()
            logging.exception("关注用户失败")
            raise

    def create_following(self, *, operator, username: str):
        return self.create_follow(operator=operator, username=username)

    def delete_follow(self, *, operator, username: str):
        target_user = self.get_user_by_username(username)
        is_following = self.uow.follows.exists_follow_relation(
            follower_id=operator.id, followed_id=target_user.id
        )
        ensure_can_delete_following(
            operator_id=operator.id,
            target_user_id=target_user.id,
            already_following=is_following,
        )
        try:
            self.uow.follows.delete_follow_relation(
                follower_id=operator.id, followed_id=target_user.id
            )
            self.uow.commit()
            user_extra_data = self.uow.users.build_user_extra_data(
                user_id=target_user.id,
                viewer_id=operator.id,
            )
            return ItemResult(
                data=self.assembler.map_user(target_user, extra_data=user_extra_data)
            )
        except Exception:
            self.uow.rollback()
            logging.exception("取消关注用户失败")
            raise

    def delete_following(self, *, operator, username: str):
        return self.delete_follow(operator=operator, username=username)

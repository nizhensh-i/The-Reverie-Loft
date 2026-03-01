import logging

from ..domain.comment.policies import (
    build_comment_notification_targets,
    can_delete_comment,
)
from ..domain.common.exceptions import ForbiddenError, NotFoundError, ValidationError
from ..infrastructure.database.sqlalchemy import db
from ..models import Comment, Post
from ..utils.common import get_avatars_url
from ..utils.text_filter import DFAFilter
from ..utils.time_util import DateUtils
from .common.dto import ActionResult, ItemResult, PageResult
from .common.unit_of_work import SqlAlchemyUnitOfWork


class CommentService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.uow = SqlAlchemyUnitOfWork(self.session)

    def get_replies_by_parent(self, *, root_comment_id: int, page: int, per_page: int):
        query = Comment.query.filter_by(root_comment_id=root_comment_id).order_by(
            Comment.timestamp.desc()
        )
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        replies = [reply.to_json() for reply in pagination.items]
        return PageResult(data=replies, total=query.count())

    def list_post_comments(
        self, *, post_id: int, page: int, per_page: int, reply_per_page: int
    ):
        post = Post.query.get(post_id)
        if not post:
            raise NotFoundError("文章不存在")

        root_comments_pagination = (
            post.comments.filter(Comment.root_comment_id.is_(None))
            .order_by(Comment.timestamp.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        comments = []
        for root_comment in root_comments_pagination.items:
            comment_data = root_comment.to_json()
            replies_result = self.get_replies_by_parent(
                root_comment_id=root_comment.id, page=1, per_page=reply_per_page
            )
            comment_data.update(
                {"reply": {"list": replies_result.data, "total": replies_result.total}}
            )
            comments.append(comment_data)

        return PageResult(data=comments, total=root_comments_pagination.total)

    def create_comment(
        self,
        *,
        post_id: int,
        author,
        body: str,
        direct_parent_id: int | None,
        at_list: list[int] | None,
    ):
        post = Post.query.get(post_id)
        if not post:
            raise NotFoundError("文章不存在")

        if not (body or "").strip():
            raise ValidationError("评论内容不能为空")

        direct_parent = None
        root_comment = None

        if direct_parent_id:
            direct_parent = self.session.get(Comment, direct_parent_id)
            if not direct_parent:
                raise NotFoundError("回复的评论不存在")
            root_comment = (
                direct_parent.root_comment
                if direct_parent.root_comment_id
                else direct_parent
            )

        try:
            comment = Comment(
                body=DFAFilter().filter(body, "*"),
                post=post,
                author=author,
                direct_parent=direct_parent,
                root_comment=root_comment,
            )
            self.session.add(comment)
            self.uow.commit()

            targets = build_comment_notification_targets(
                actor_id=author.id,
                post_author_id=post.author_id,
                direct_parent_author_id=(
                    direct_parent.author_id if direct_parent is not None else None
                ),
                at_list=at_list,
            )
            self._dispatch_comment_notification(
                post_id=post.id,
                comment_id=comment.id,
                trigger_user_id=author.id,
                notifications_data=targets,
            )

            return ItemResult(
                data={
                    "id": comment.id,
                    "parentId": comment.root_comment_id,
                    "uid": author.id,
                    "content": comment.body,
                    "createTime": DateUtils.datetime_to_str(comment.timestamp),
                    "user": {
                        "username": author.nickname
                        if author.nickname
                        else author.username,
                        "avatar": get_avatars_url(author.image),
                    },
                    "reply": "",
                }
            )
        except Exception:
            self.uow.rollback()
            raise

    def list_all_comments(self, *, page: int, per_page: int):
        query = Comment.query
        pagination = query.order_by(Comment.timestamp.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )
        comments = [
            {
                "content": item.body,
                "timestamp": DateUtils.datetime_to_str(item.timestamp),
                "author": item.author.username,
                "user_id": item.author.id,
                "image": get_avatars_url(item.author.image),
                "id": item.id,
                "disabled": item.disabled,
            }
            for item in pagination.items
        ]
        return PageResult(data=comments, total=query.count())

    def toggle_comment_status(self, *, comment_id: int, action: str):
        comment = Comment.query.get(comment_id)
        if not comment:
            raise NotFoundError("评论不存在")

        if action == "enable":
            comment.disabled = False
        elif action == "disable":
            comment.disabled = True
        else:
            raise ValidationError(f"传递参数错误, status{action}")

        self.uow.commit()
        return ActionResult(message="操作成功")

    def delete_comment(self, *, comment_id: int, operator):
        comment = Comment.query.get(comment_id)
        if not comment:
            raise NotFoundError("评论不存在")

        post = Post.query.get(comment.post_id)
        if not post:
            raise NotFoundError("文章不存在")

        if not can_delete_comment(operator=operator, comment=comment, post=post):
            raise ForbiddenError("没有权限删除此评论")

        try:
            self.session.delete(comment)
            self.uow.commit()
            logging.info("评论删除成功: id=%s", comment_id)
            return ActionResult(message="删除成功")
        except Exception:
            self.uow.rollback()
            raise

    @staticmethod
    def _dispatch_comment_notification(
        *,
        post_id: int,
        comment_id: int,
        trigger_user_id: int,
        notifications_data,
    ):
        from ..infrastructure.my_celery import create_comment_notifications

        create_comment_notifications.delay(
            post_id,
            comment_id,
            trigger_user_id,
            notifications_data,
        )

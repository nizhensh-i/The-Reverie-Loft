import logging

from ..application.dto import ActionResult, ItemResult, PageResult
from ..domain.comment.policies import (
    apply_comment_status,
    build_comment_notification_targets,
    can_delete_comment,
    resolve_root_comment,
    sanitize_comment_body,
    validate_comment_body,
)
from ..domain.common.exceptions import ForbiddenError, NotFoundError
from ..domain.common.unit_of_work import UnitOfWork
from ..domain.ports.assemblers import ResponseAssemblerPort
from ..domain.ports.notifications import NotificationDispatcherPort


class CommentService:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        assembler: ResponseAssemblerPort,
        notifier: NotificationDispatcherPort,
    ):
        self.uow = uow
        self.assembler = assembler
        self.notifier = notifier

    def list_comment_replies(self, *, root_comment_id: int, page: int, per_page: int):
        page_entities = self.uow.comments.list_replies(
            root_comment_id=root_comment_id, page=page, per_page=per_page
        )
        replies = [self.assembler.map_comment(reply) for reply in page_entities.items]
        return PageResult(data=replies, total=page_entities.total)

    def list_post_comments(
        self, *, post_id: int, page: int, per_page: int, reply_per_page: int
    ):
        post = self.uow.comments.get_post(post_id)
        if not post:
            raise NotFoundError("文章不存在")

        root_comments = self.uow.comments.list_post_root_comments(
            post_id=post_id, page=page, per_page=per_page
        )

        comments = []
        for root_comment in root_comments.items:
            comment_data = self.assembler.map_comment(root_comment)
            replies_result = self.list_comment_replies(
                root_comment_id=root_comment.id, page=1, per_page=reply_per_page
            )
            comment_data.update(
                {"reply": {"list": replies_result.data, "total": replies_result.total}}
            )
            comments.append(comment_data)

        return PageResult(data=comments, total=root_comments.total)

    def create_comment(
        self,
        *,
        post_id: int,
        author,
        body: str,
        direct_parent_id: int | None,
        at_list: list[int] | None,
    ):
        post = self.uow.comments.get_post(post_id)
        if not post:
            raise NotFoundError("文章不存在")

        validate_comment_body(body)

        direct_parent = None
        root_comment = None

        if direct_parent_id:
            direct_parent = self.uow.comments.get_comment(direct_parent_id)
            if not direct_parent:
                raise NotFoundError("回复的评论不存在")
            root_comment = resolve_root_comment(direct_parent)

        try:
            comment = self.uow.comments.create_comment(
                body=sanitize_comment_body(body),
                post=post,
                author=author,
                direct_parent=direct_parent,
                root_comment=root_comment,
            )
            self.uow.comments.add(comment)
            self.uow.commit()

            targets = build_comment_notification_targets(
                actor_id=author.id,
                post_author_id=post.author_id,
                direct_parent_author_id=(
                    direct_parent.author_id if direct_parent else None
                ),
                at_list=at_list,
            )
            mapped_targets = [
                (
                    receiver_id,
                    self.uow.comments.resolve_notification_type(
                        notification_type_code=notification_type.value
                    ),
                )
                for receiver_id, notification_type in targets
            ]
            self._dispatch_comment_notification(
                post_id=post.id,
                comment_id=comment.id,
                trigger_user_id=author.id,
                notifications_data=mapped_targets,
            )
            return ItemResult(data=self.assembler.map_created_comment(comment))
        except Exception:
            self.uow.rollback()
            raise

    def list_all_comments(self, *, page: int, per_page: int):
        page_entities = self.uow.comments.list_all_comments(
            page=page, per_page=per_page
        )
        comments = [
            self.assembler.map_admin_comment(item) for item in page_entities.items
        ]
        return PageResult(data=comments, total=page_entities.total)

    def update_comment_status(self, *, comment_id: int, action: str):
        comment = self.uow.comments.get_comment(comment_id)
        if not comment:
            raise NotFoundError("评论不存在")

        apply_comment_status(comment, action=action)

        self.uow.commit()
        return ActionResult(message="操作成功")

    def delete_comment(self, *, comment_id: int, operator):
        comment = self.uow.comments.get_comment(comment_id)
        if not comment:
            raise NotFoundError("评论不存在")

        post = self.uow.comments.get_post(comment.post_id)
        if not post:
            raise NotFoundError("文章不存在")

        if not can_delete_comment(operator=operator, comment=comment, post=post):
            raise ForbiddenError("没有权限删除此评论")

        try:
            self.uow.comments.delete(comment)
            self.uow.commit()
            logging.info("评论删除成功: id=%s", comment_id)
            return ActionResult(message="删除成功")
        except Exception:
            self.uow.rollback()
            raise

    def _dispatch_comment_notification(
        self,
        *,
        post_id: int,
        comment_id: int,
        trigger_user_id: int,
        notifications_data,
    ):
        self.notifier.dispatch_comment(
            post_id=post_id,
            comment_id=comment_id,
            trigger_user_id=trigger_user_id,
            notifications_data=notifications_data,
        )

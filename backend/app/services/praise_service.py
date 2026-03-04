import logging

from ..application.dto import ItemResult, ListResult
from ..domain.common.exceptions import NotFoundError
from ..domain.common.unit_of_work import UnitOfWork
from ..domain.ports.notifications import NotificationDispatcherPort
from ..domain.praise.policies import (
    ensure_praise_not_exists,
    resolve_like_notification_receiver,
)


class PraiseService:
    def __init__(self, *, uow: UnitOfWork, notifier: NotificationDispatcherPort):
        self.uow = uow
        self.notifier = notifier

    def list_praised_comment_ids_for_post(self, *, user_id: int, post_id: int):
        comment_ids = self.uow.praises.list_praised_comment_ids_for_post(
            user_id=user_id, post_id=post_id
        )
        return ListResult(data=comment_ids)

    def get_post_praise_stats(self, *, post_id: int):
        post = self.uow.praises.get_post(post_id)
        if not post:
            raise NotFoundError("文章不存在")
        return ItemResult(data={"praise_total": post.praise.count()})

    def create_post_praise(self, *, post_id: int, user):
        post = self.uow.praises.get_post(post_id)
        if not post:
            raise NotFoundError("文章不存在")

        existed = self.uow.praises.exists_post_praise(user_id=user.id, post_id=post_id)
        ensure_praise_not_exists(existed)

        try:
            praise = self.uow.praises.create_post_praise(post=post, author=user)
            self.uow.praises.add(praise)
            self.uow.commit()

            receiver_id = resolve_like_notification_receiver(
                actor_id=user.id, target_author_id=post.author_id
            )
            self.notifier.dispatch_like(
                post_id=post.id,
                comment_id=None,
                liker_id=user.id,
                receiver_id=receiver_id,
            )

            return ItemResult(
                data={"praise_total": post.praise.count(), "has_praised": True}
            )
        except Exception:
            self.uow.rollback()
            logging.exception("文章点赞失败")
            raise

    def get_comment_praise_stats(self, *, comment_id: int):
        comment = self.uow.praises.get_comment(comment_id)
        if not comment:
            raise NotFoundError("评论不存在")
        return ItemResult(data={"praise_total": comment.praise.count()})

    def create_comment_praise(self, *, comment_id: int, user):
        comment = self.uow.praises.get_comment(comment_id)
        if not comment:
            raise NotFoundError("评论不存在")

        existed = self.uow.praises.exists_comment_praise(
            user_id=user.id, comment_id=comment_id
        )
        ensure_praise_not_exists(existed)

        try:
            praise = self.uow.praises.create_comment_praise(
                comment=comment, author=user
            )
            self.uow.praises.add(praise)
            self.uow.commit()

            receiver_id = resolve_like_notification_receiver(
                actor_id=user.id, target_author_id=comment.author_id
            )
            self.notifier.dispatch_like(
                post_id=comment.post_id,
                comment_id=comment.id,
                liker_id=user.id,
                receiver_id=receiver_id,
            )

            return ItemResult(data={"praise_total": comment.praise.count()})
        except Exception:
            self.uow.rollback()
            logging.exception("评论点赞失败")
            raise

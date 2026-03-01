import logging

from ..domain.common.exceptions import NotFoundError, ValidationError
from ..infrastructure.database.sqlalchemy import db
from ..models import Comment, Post, Praise
from .common.dto import ItemResult, ListResult
from .common.unit_of_work import SqlAlchemyUnitOfWork


class PraiseService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.uow = SqlAlchemyUnitOfWork(self.session)

    def list_praised_comment_ids_for_post(self, *, user_id: int, post_id: int):
        comment_ids = (
            self.session.query(Praise.comment_id)
            .join(Comment)
            .filter(
                Praise.author_id == user_id,
                Comment.post_id == post_id,
                Praise.comment_id.isnot(None),
            )
            .distinct()
            .all()
        )
        return ListResult(data=[item[0] for item in comment_ids])

    def get_post_praise_stats(self, *, post_id: int):
        post = Post.query.get(post_id)
        if not post:
            raise NotFoundError("文章不存在")
        return ItemResult(data={"praise_total": post.praise.count()})

    def create_post_praise(self, *, post_id: int, user):
        post = Post.query.get(post_id)
        if not post:
            raise NotFoundError("文章不存在")

        existed = Praise.query.filter_by(author_id=user.id, post_id=post_id).first()
        if existed:
            raise ValidationError("您已经点赞过了~")

        try:
            praise = Praise(post=post, author=user)
            self.session.add(praise)
            self.uow.commit()

            if user.id != post.author_id:
                from ..infrastructure.my_celery import create_like_notifications

                create_like_notifications.delay(post.id, None, user.id, post.author_id)

            return ItemResult(
                data={"praise_total": post.praise.count(), "has_praised": True}
            )
        except Exception:
            self.uow.rollback()
            logging.exception("文章点赞失败")
            raise

    def get_comment_praise_stats(self, *, comment_id: int):
        comment = Comment.query.get(comment_id)
        if not comment:
            raise NotFoundError("评论不存在")
        return ItemResult(data={"praise_total": comment.praise.count()})

    def create_comment_praise(self, *, comment_id: int, user):
        comment = Comment.query.get(comment_id)
        if not comment:
            raise NotFoundError("评论不存在")

        existed = Praise.query.filter_by(
            author_id=user.id, comment_id=comment_id
        ).first()
        if existed:
            raise ValidationError("您已经点赞过了~")

        try:
            praise = Praise(comment=comment, author=user)
            self.session.add(praise)
            self.uow.commit()

            if user.id != comment.author_id:
                from ..infrastructure.my_celery import create_like_notifications

                create_like_notifications.delay(
                    comment.post_id, comment.id, user.id, comment.author_id
                )

            return ItemResult(data={"praise_total": comment.praise.count()})
        except Exception:
            self.uow.rollback()
            logging.exception("评论点赞失败")
            raise

# 日志
import logging

from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..api.posts import PostGroupApi
from ..decorators import DecoratedMethodView
from ..infrastructure.cache import cache_invalidator
from ..infrastructure.database.sqlalchemy import db
from ..models import Comment, Post, Praise
from ..utils.response import error, success
from . import api


# --------------------------- 点赞功能 ---------------------------
@api.route("/posts/<post_id>/comments/praised")
def has_praised_comment_id(post_id):
    """查找某文章下当前用户已点赞的评论id"""
    is_like = request.args.get("liked", "") == "true"
    if not is_like:
        return error(400, message=f"参数错误, liked:{request.args.get('liked', '')}")
    logging.info(f"查询用户已点赞评论: post_id={post_id}")
    comment_ids = (
        db.session.query(Praise.comment_id)
        .join(Comment)
        .filter(
            Praise.author_id == current_user.id,
            Comment.post_id == post_id,
            Praise.comment_id.isnot(None),
        )
        .distinct()
        .all()
    )
    return success(data=[item[0] for item in comment_ids])


class PraisePostApi(DecoratedMethodView):
    method_decorators = {
        "post": [
            jwt_required(),
            cache_invalidator(target_func=PostGroupApi.query_post),
        ],  # 自动清除缓存
        "share": [jwt_required()],
    }

    def get(self, post_id):
        # 获取文章点赞总数
        logging.info(f"获取文章点赞总数: id={post_id}")
        post = Post.query.get_or_404(post_id)
        return success(data={"praise_total": post.praise.count()})

    def post(self, post_id):
        """文章点赞"""
        logging.info(f"{current_user.username}文章点赞: id={post_id}")
        post = Post.query.get_or_404(post_id)
        # 防止用户重复点赞
        p = Praise.query.filter_by(author_id=current_user.id, post_id=post_id).first()
        if p:
            return error(400, "您已经点赞过了~")

        try:
            praise = Praise(post=post, author=current_user)
            db.session.add(praise)

            # 异步创建点赞通知
            if current_user.id != post.author_id:
                from ..infrastructure.my_celery import create_like_notifications

                create_like_notifications.delay(
                    post.id, None, current_user.id, post.author_id
                )

            db.session.commit()
            # 使用relationship的len()替代count()查询
            return success(
                data={"praise_total": post.praise.count(), "has_praised": True}
            )
        except Exception as e:
            logging.error(f"文章点赞失败: {str(e)}", exc_info=True)
            db.session.rollback()
            return error(500, f"操作失败，已回滚: {str(e)}")

    def delete(self, post_id):
        # 取消文章点赞
        return error(500, "取消点赞失败")


class PraiseCommentApi(DecoratedMethodView):
    method_decorators = {
        "get": [],
        "post": [jwt_required()],
        "delete": [jwt_required()],
    }

    def get(self, comment_id):
        """获取评论点赞总数"""
        logging.info(f"获取评论点赞总数: id={comment_id}")
        comment = Comment.query.get_or_404(comment_id)
        return success(data={"praise_total": comment.praise.count()})

    def post(self, comment_id):
        """评论点赞"""
        logging.info(f"{current_user.username}评论点赞: id={comment_id}")
        comment = Comment.query.get_or_404(comment_id)
        # 防止用户重复点赞
        p = Praise.query.filter_by(
            author_id=current_user.id, comment_id=comment_id
        ).first()
        if p:
            return error(400, "您已经点赞过了~")

        try:
            praise = Praise(comment=comment, author=current_user)
            db.session.add(praise)

            # 异步创建点赞通知
            if current_user.id != comment.author_id:
                create_like_notifications.delay(
                    comment.post_id, comment.id, current_user.id, comment.author_id
                )

            db.session.commit()

            # 使用relationship的len()替代count()查询
            return success(data={"praise_total": comment.praise.count()})
        except Exception as e:
            logging.error(f"评论点赞失败: {str(e)}", exc_info=True)
            db.session.rollback()
            return error(500, f"点赞操作失败，已回滚: {str(e)}")

    def delete(self, comment_id):
        # 取消评论点赞
        return error(500, "取消点赞失败")


def register_praise_api(bp, *, post_praise_url, comment_praise_url):
    post_praise = PraisePostApi.as_view("likes_post")
    comment_praise = PraiseCommentApi.as_view("likes_comment")
    bp.add_url_rule(post_praise_url, view_func=post_praise)
    bp.add_url_rule(comment_praise_url, view_func=comment_praise)

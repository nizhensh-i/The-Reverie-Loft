import logging

from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..api.posts import PostGroupApi
from ..decorators import DecoratedMethodView
from ..domain.common.exceptions import NotFoundError, ValidationError
from ..infrastructure.cache import cache_invalidator
from ..services.praise_service import PraiseService
from ..utils.response import error, success
from . import api

praise_service = PraiseService()


# --------------------------- 点赞功能 ---------------------------
@api.route("/posts/<post_id>/comments/praised")
@jwt_required()
def has_praised_comment_id(post_id):
    """查找某文章下当前用户已点赞的评论id"""
    is_like = request.args.get("liked", "") == "true"
    if not is_like:
        return error(400, message=f"参数错误, liked:{request.args.get('liked', '')}")
    logging.info(f"查询用户已点赞评论: post_id={post_id}")
    result = praise_service.list_praised_comment_ids_for_post(
        user_id=current_user.id, post_id=post_id
    )
    return success(data=result.data)


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
        result = praise_service.get_post_praise_stats(post_id=post_id)
        return success(data=result.data)

    def post(self, post_id):
        """文章点赞"""
        logging.info(f"{current_user.username}文章点赞: id={post_id}")
        try:
            result = praise_service.create_post_praise(
                post_id=post_id, user=current_user
            )
            return success(data=result.data)
        except (ValidationError, NotFoundError) as exc:
            return error(exc.code, exc.message)
        except Exception as exc:
            logging.error("文章点赞失败: %s", exc, exc_info=True)
            return error(500, f"操作失败，已回滚: {exc}")

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
        result = praise_service.get_comment_praise_stats(comment_id=comment_id)
        return success(data=result.data)

    def post(self, comment_id):
        """评论点赞"""
        logging.info(f"{current_user.username}评论点赞: id={comment_id}")
        try:
            result = praise_service.create_comment_praise(
                comment_id=comment_id, user=current_user
            )
            return success(data=result.data)
        except (ValidationError, NotFoundError) as exc:
            return error(exc.code, exc.message)
        except Exception as exc:
            logging.error("评论点赞失败: %s", exc, exc_info=True)
            return error(500, f"点赞操作失败，已回滚: {exc}")

    def delete(self, comment_id):
        # 取消评论点赞
        return error(500, "取消点赞失败")


def register_praise_api(bp, *, post_praise_url, comment_praise_url):
    post_praise = PraisePostApi.as_view("likes_post")
    comment_praise = PraiseCommentApi.as_view("likes_comment")
    bp.add_url_rule(post_praise_url, view_func=post_praise)
    bp.add_url_rule(comment_praise_url, view_func=comment_praise)

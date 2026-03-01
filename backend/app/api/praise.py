import logging

from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..application.cache import PostListCache
from ..composition import get_container
from ..decorators import DecoratedMethodView
from ..utils.response import error, success
from . import api


def _praise_service():
    return get_container().praise_service()


@api.route("/posts/<post_id>/comments/praised")
@jwt_required()
def has_praised_comment_id(post_id):
    is_like = request.args.get("liked", "") == "true"
    if not is_like:
        return error(400, message=f"参数错误, liked:{request.args.get('liked', '')}")
    logging.info(f"查询用户已点赞评论: post_id={post_id}")
    result = _praise_service().list_praised_comment_ids_for_post(
        user_id=current_user.id, post_id=post_id
    )
    return success(data=result.data)


class PraisePostApi(DecoratedMethodView):
    method_decorators = {
        "post": [jwt_required()],
        "share": [jwt_required()],
    }

    def get(self, post_id):
        logging.info(f"获取文章点赞总数: id={post_id}")
        result = _praise_service().get_post_praise_stats(post_id=post_id)
        return success(data=result.data)

    def post(self, post_id):
        logging.info(f"{current_user.username}文章点赞: id={post_id}")
        result = _praise_service().create_post_praise(
            post_id=post_id, user=current_user
        )
        PostListCache.invalidate_all()
        return success(data=result.data)

    def delete(self, post_id):
        return error(500, "取消点赞失败")


class PraiseCommentApi(DecoratedMethodView):
    method_decorators = {
        "get": [],
        "post": [jwt_required()],
        "delete": [jwt_required()],
    }

    def get(self, comment_id):
        logging.info(f"获取评论点赞总数: id={comment_id}")
        result = _praise_service().get_comment_praise_stats(comment_id=comment_id)
        return success(data=result.data)

    def post(self, comment_id):
        logging.info(f"{current_user.username}评论点赞: id={comment_id}")
        result = _praise_service().create_comment_praise(
            comment_id=comment_id, user=current_user
        )
        PostListCache.invalidate_all()
        return success(data=result.data)

    def delete(self, comment_id):
        return error(500, "取消点赞失败")


def register_praise_api(bp, *, post_praise_url, comment_praise_url):
    post_praise = PraisePostApi.as_view("likes_post")
    comment_praise = PraiseCommentApi.as_view("likes_comment")
    bp.add_url_rule(post_praise_url, view_func=post_praise)
    bp.add_url_rule(comment_praise_url, view_func=comment_praise)

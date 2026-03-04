import logging

from dependency_injector.wiring import Provide, inject
from flask import current_app, request
from flask_jwt_extended import current_user, jwt_required

from ..application.cache import PostListCache
from ..container import AppContainer
from ..decorators import DecoratedMethodView, permission_required
from ..domain.common.constants import PermissionCode
from ..infrastructure.my_limiter import limiter
from ..services.comment_service import CommentService
from ..utils.response import error, success
from . import api


@inject
def _comment_service(
    comment_service: CommentService = Provide[AppContainer.comment_service],
) -> CommentService:
    return comment_service


@inject
def _post_cache(
    post_cache: PostListCache = Provide[AppContainer.post_list_cache],
) -> PostListCache:
    return post_cache


@api.route("/comments")
@jwt_required()
@permission_required(PermissionCode.MODERATE)
def moderate():
    logging.info("管理评论")
    page = request.args.get("page", 1, type=int)
    result = _comment_service().list_all_comments(
        page=page, per_page=current_app.config["FLASKY_COMMENTS_PER_PAGE"]
    )
    return success(data=result.data, total=result.total)


@api.route("/comments/<int:comment_id>/replies")
def get_comment_replies(comment_id):
    logging.info("获取评论回复")
    root_comment_id = comment_id
    page = request.args.get("page", 1, type=int)
    result = _comment_service().list_comment_replies(
        root_comment_id=root_comment_id,
        page=page,
        per_page=current_app.config["FLASKY_COMMENTS_REPLY_PER_PAGE"],
    )
    return success(data=result.data, total=result.total, current_page=page)


class CommentApi(DecoratedMethodView):
    method_decorators = {
        "get": [],
        "post": [
            jwt_required(),
            limiter.limit(
                "1/second;3/minute", exempt_when=lambda: current_user.role_id == 3
            ),
        ],
    }

    def get(self, post_id):
        logging.info(f"获取文章评论: post_id={post_id}")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get(
            "size", current_app.config["FLASKY_COMMENTS_PER_PAGE"], type=int
        )
        result = _comment_service().list_post_comments(
            post_id=post_id,
            page=page,
            per_page=per_page,
            reply_per_page=current_app.config["FLASKY_COMMENTS_REPLY_PER_PAGE"],
        )
        return success(data=result.data, total=result.total, current_page=page)

    def post(self, post_id):
        logging.info(f"{current_user.username}发布评论: post_id={post_id}")
        data = request.get_json() or {}
        result = _comment_service().create_comment(
            post_id=post_id,
            author=current_user,
            body=data.get("body", ""),
            direct_parent_id=data.get("directParentId"),
            at_list=data.get("at"),
        )
        _post_cache().invalidate_all()
        return success(data=result.data)


class CommentManageApi(DecoratedMethodView):
    method_decorators = {
        "patch": [jwt_required(), permission_required(PermissionCode.MODERATE)],
        "delete": [jwt_required()],
    }

    @staticmethod
    def all_comments(page):
        return _comment_service().list_all_comments(
            page=page,
            per_page=current_app.config["FLASKY_COMMENTS_PER_PAGE"],
        )

    def patch(self, comment_id):
        status = request.json.get("action")
        logging.info(
            f"{current_user.username}{'开启' if status == 'enable' else '禁用'}评论: id={comment_id}"
        )
        if status not in ("enable", "disable"):
            return error(400, f"传递参数错误, status{status}")
        action_result = _comment_service().update_comment_status(
            comment_id=comment_id, action=status
        )
        list_result = CommentManageApi.all_comments(1)
        return success(
            message=action_result.message,
            data=list_result.data,
            total=list_result.total,
        )

    def delete(self, comment_id):
        logging.info(f"{current_user.username}删除评论: id={comment_id}")
        result = _comment_service().delete_comment(
            comment_id=comment_id, operator=current_user
        )
        _post_cache().invalidate_all()
        return success(message=result.message)


def register_comment_api(bp, *, comment_url, comment_manage_url):
    comment = CommentApi.as_view("comments")
    comment_manage = CommentManageApi.as_view("comments_manage")
    bp.add_url_rule(comment_url, view_func=comment)
    bp.add_url_rule(comment_manage_url, view_func=comment_manage)

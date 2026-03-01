import logging

from flask import current_app, request
from flask_jwt_extended import current_user, jwt_required
from werkzeug.exceptions import TooManyRequests

from ..api.posts import PostGroupApi
from ..decorators import DecoratedMethodView, permission_required
from ..domain.common.exceptions import ForbiddenError, NotFoundError, ValidationError
from ..infrastructure.cache import cache_invalidator
from ..infrastructure.my_limiter import limiter
from ..models import Permission
from ..services.comment_service import CommentService
from ..utils.response import error, success
from . import api

comment_service = CommentService()


# --------------------------- 评论 ---------------------------
@api.route("/comments")
@jwt_required()
@permission_required(Permission.MODERATE)
def moderate():
    """管理评论"""
    logging.info("管理评论")
    page = request.args.get("page", 1, type=int)
    result = comment_service.list_all_comments(
        page=page, per_page=current_app.config["FLASKY_COMMENTS_PER_PAGE"]
    )
    return success(data=result.data, total=result.total)


@api.route("/comments/<int:comment_id>/replies")
def get_comment_replies(comment_id):
    logging.info("获取评论回复")
    root_comment_id = comment_id
    page = request.args.get("page", 1, type=int)
    result = comment_service.get_replies_by_parent(
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
            cache_invalidator(target_func=PostGroupApi.query_post),
            limiter.limit(
                "1/second;3/minute", exempt_when=lambda: current_user.role_id == 3
            ),
        ],
    }

    @staticmethod
    def get_replies_by_parent(root_comment_id, page):
        return comment_service.get_replies_by_parent(
            root_comment_id=root_comment_id,
            page=page,
            per_page=current_app.config["FLASKY_COMMENTS_REPLY_PER_PAGE"],
        )

    def get(self, post_id):
        logging.info(f"获取文章评论: post_id={post_id}")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get(
            "size", current_app.config["FLASKY_COMMENTS_PER_PAGE"], type=int
        )
        result = comment_service.list_post_comments(
            post_id=post_id,
            page=page,
            per_page=per_page,
            reply_per_page=current_app.config["FLASKY_COMMENTS_REPLY_PER_PAGE"],
        )
        return success(data=result.data, total=result.total, current_page=page)

    def post(self, post_id):
        """发布评论（适配direct_parent关系）"""
        logging.info(f"{current_user.username}发布评论: post_id={post_id}")
        data = request.get_json() or {}
        try:
            result = comment_service.create_comment(
                post_id=post_id,
                author=current_user,
                body=data.get("body", ""),
                direct_parent_id=data.get("directParentId"),
                at_list=data.get("at"),
            )
            return success(data=result.data)
        except TooManyRequests:
            raise
        except (ValidationError, NotFoundError) as exc:
            return error(exc.code, exc.message)
        except Exception as exc:
            logging.error("发布评论失败: %s", exc, exc_info=True)
            return error(500, f"发布评论失败: {exc}")


class CommentManageApi(DecoratedMethodView):
    """评论管理"""

    method_decorators = {
        "patch": [jwt_required(), permission_required(Permission.MODERATE)],
        "delete": [jwt_required()],
    }

    @staticmethod
    def all_comments(page):
        return comment_service.list_all_comments(
            page=page,
            per_page=current_app.config["FLASKY_COMMENTS_PER_PAGE"],
        )

    def patch(self, comment_id):
        """禁用/恢复评论"""
        status = request.json.get("action")
        logging.info(
            f"{current_user.username}{'开启' if status == 'enable' else '禁用'}评论: id={comment_id}"
        )
        if status not in ("enable", "disable"):
            return error(400, f"传递参数错误, status{status}")
        try:
            action_result = comment_service.toggle_comment_status(
                comment_id=comment_id, action=status
            )
            list_result = CommentManageApi.all_comments(1)
            return success(
                message=action_result.message,
                data=list_result.data,
                total=list_result.total,
            )
        except Exception as exc:
            logging.error("%s操作失败: %s", status, exc, exc_info=True)
            return error(500, f"{status}操作失败: {exc}")

    def delete(self, comment_id):
        """删除评论"""
        logging.info(f"{current_user.username}删除评论: id={comment_id}")
        try:
            result = comment_service.delete_comment(
                comment_id=comment_id, operator=current_user
            )
            return success(message=result.message)
        except (ForbiddenError, NotFoundError) as exc:
            return error(exc.code, exc.message)
        except Exception as exc:
            logging.error("删除评论失败: %s", exc, exc_info=True)
            return error(500, f"删除失败: {exc}")


def register_comment_api(bp, *, comment_url, comment_manage_url):
    comment = CommentApi.as_view("comments")
    comment_manage = CommentManageApi.as_view("comments_manage")
    bp.add_url_rule(comment_url, view_func=comment)
    bp.add_url_rule(comment_manage_url, view_func=comment_manage)

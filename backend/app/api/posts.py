import logging

from flask import current_app, request
from flask_jwt_extended import current_user, jwt_required

from ..decorators import DecoratedMethodView, log_operate
from ..infrastructure.cache import cache, cache_invalidator
from ..infrastructure.my_limiter import limiter
from ..models import Permission
from ..services.post_service import PostService
from ..utils.response import forbidden, success

post_service = PostService()


class PostGroupApi(DecoratedMethodView):
    method_decorators = {
        "get": [log_operate],
        "post": [jwt_required()],
    }

    @staticmethod
    @cache.memoize(timeout=60)
    def query_post(page, per_page, tab_name=None):
        viewer = current_user if tab_name == "showFollowed" else None
        return post_service.list_posts(
            page=page, per_page=per_page, viewer=viewer, tab_name=tab_name
        )

    @staticmethod
    def submit_to_db(post_type, content, images=None):
        return post_service.create_post(
            author=current_user, content=content, post_type=post_type, images=images
        )

    @staticmethod
    @limiter.limit("2/day", exempt_when=lambda: current_user.role_id == 3)
    def publish_image_post(content, images):
        """发布图文文章（带限流）"""
        return PostGroupApi.submit_to_db("image", content, images)

    @staticmethod
    def posts_publish(data: dict):
        content = data.get("content", "")
        images = data.get("images", [])
        post_type = data.get("type", "text")
        if post_type == "image":
            return PostGroupApi.publish_image_post(content, images)
        return PostGroupApi.submit_to_db(post_type, content, images)

    def get(self):
        """获取所有文章"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get(
            "per_page", current_app.config["FLASKY_POSTS_PER_PAGE"], type=int
        )
        result = PostGroupApi.query_post(page, per_page, request.args.get("tabName"))
        return success(data=result.data, total=result.total)

    def post(self):
        """发布文章"""
        if not current_user.can(Permission.WRITE):
            return forbidden("没有权限发布文章")
        create_result = PostGroupApi.posts_publish(request.json or {})
        cache.delete_memoized(PostGroupApi.query_post)
        result = PostGroupApi.query_post(1, current_app.config["FLASKY_POSTS_PER_PAGE"])
        return success(
            message=create_result.message,
            data=result.data,
            total=result.total,
        )


class PostItemApi(DecoratedMethodView):
    method_decorators = {
        "get": [],
        "delete": [
            jwt_required(),
            cache_invalidator(target_func=PostGroupApi.query_post),
        ],
        "patch": [jwt_required()],
    }

    def get(self, id):
        """获取单篇文章"""
        logging.info(f"获取文章: id={id}")
        result = post_service.get_post_detail(id)
        return success(data=result.data)

    def delete(self, id):
        result = post_service.soft_delete_post(post_id=id)
        return success(message=result.message)

    def patch(self, id):
        logging.info(f"编辑文章: id={id}")
        result = post_service.edit_post(
            post_id=id, operator=current_user, payload=request.get_json() or {}
        )
        return success(data=result.data)


def register_post_api(bp, *, post_item_url, post_group_url):
    item = PostItemApi.as_view("post_item")
    group = PostGroupApi.as_view("post_group")
    bp.add_url_rule(post_item_url, view_func=item)
    bp.add_url_rule(post_group_url, view_func=group)

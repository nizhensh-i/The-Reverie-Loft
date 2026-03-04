import logging

from dependency_injector.wiring import Provide, inject
from flask import current_app, request
from flask_jwt_extended import current_user, jwt_required

from ..application.cache import PostListCache
from ..container import AppContainer
from ..decorators import DecoratedMethodView, log_operate
from ..infrastructure.my_limiter import limiter
from ..services.post_service import PostService
from ..utils.response import forbidden, success


@inject
def _post_service(
    post_service: PostService = Provide[AppContainer.post_service],
) -> PostService:
    return post_service


@inject
def _post_cache(
    post_cache: PostListCache = Provide[AppContainer.post_list_cache],
) -> PostListCache:
    return post_cache


def _query_post(page: int, per_page: int, tab_name: str | None = None):
    viewer = current_user
    viewer_id = current_user.id if current_user else None
    cached = _post_cache().get(
        page=page,
        per_page=per_page,
        tab_name=tab_name,
        viewer_id=viewer_id,
    )
    if cached:
        return cached

    result = _post_service().list_posts(
        page=page,
        per_page=per_page,
        viewer=viewer,
        tab_name=tab_name,
    )
    _post_cache().set(
        page=page,
        per_page=per_page,
        tab_name=tab_name,
        viewer_id=viewer_id,
        payload=result,
    )
    return result


class PostGroupApi(DecoratedMethodView):
    method_decorators = {
        "get": [log_operate],
        "post": [jwt_required()],
    }

    @staticmethod
    def submit_to_db(post_type, content, images=None):
        return _post_service().create_post(
            author=current_user, content=content, post_type=post_type, images=images
        )

    @staticmethod
    @limiter.limit("2/day", exempt_when=lambda: current_user.role_id == 3)
    def publish_image_post(content, images):
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
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get(
            "per_page", current_app.config["FLASKY_POSTS_PER_PAGE"], type=int
        )
        result = _query_post(page, per_page, request.args.get("tabName"))
        return success(data=result.data, total=result.total)

    def post(self):
        if not _post_service().can_publish(user=current_user):
            return forbidden("没有权限发布文章")
        create_result = PostGroupApi.posts_publish(request.json or {})
        _post_cache().invalidate_all()
        result = _query_post(1, current_app.config["FLASKY_POSTS_PER_PAGE"])
        return success(
            message=create_result.message,
            data=result.data,
            total=result.total,
        )


class PostItemApi(DecoratedMethodView):
    method_decorators = {
        "get": [],
        "delete": [jwt_required()],
        "patch": [jwt_required()],
    }

    def get(self, id):
        logging.info(f"获取文章: id={id}")
        result = _post_service().get_post(id, viewer=current_user)
        return success(data=result.data)

    def delete(self, id):
        result = _post_service().delete_post(post_id=id)
        _post_cache().invalidate_all()
        return success(message=result.message)

    def patch(self, id):
        logging.info(f"编辑文章: id={id}")
        result = _post_service().edit_post(
            post_id=id, operator=current_user, payload=request.get_json() or {}
        )
        _post_cache().invalidate_all()
        return success(data=result.data)


def register_post_api(bp, *, post_item_url, post_group_url):
    item = PostItemApi.as_view("post_item")
    group = PostGroupApi.as_view("post_group")
    bp.add_url_rule(post_item_url, view_func=item)
    bp.add_url_rule(post_group_url, view_func=group)

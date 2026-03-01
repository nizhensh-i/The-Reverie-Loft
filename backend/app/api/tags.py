import logging

from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..composition import get_container
from ..decorators import DecoratedMethodView, admin_required
from ..utils.response import error, success


def _tag_service():
    return get_container().tag_service()


def _user_profile_service():
    return get_container().user_profile_service()


class TagUserApi(DecoratedMethodView):
    method_decorators = {
        "post": [jwt_required()],
    }

    def post(self, user_id):
        logging.info(f"更新用户标签: user_id={user_id}")
        if not _tag_service().can_update_user_tags(
            operator=current_user,
            target_user_id=user_id,
        ):
            return error(400, "非当前用户，修改标签失败")

        d = request.get_json() or {}
        tag_add = set(d.get("tagAdd", []))
        tag_remove = set(d.get("tagRemove", []))
        target_user = _user_profile_service().get_user_by_id(user_id)
        result = _tag_service().update_user_tags(
            user=target_user,
            tag_add=tag_add,
            tag_remove=tag_remove,
        )
        return success(message=result.message)


class TagApi(DecoratedMethodView):
    method_decorators = {
        "share": [jwt_required()],
        "get": [],
        "post": [admin_required],
    }

    def get(self):
        logging.info("获取所有标签")
        result = _tag_service().list_tags()
        return success(data=result.data)

    def post(self):
        logging.info("更新公共标签库")
        d = request.json or {}
        tag_add = set(d.get("tagAdd", []))
        tag_remove = set(d.get("tagRemove", []))
        result = _tag_service().update_public_tags(
            tag_add=tag_add, tag_remove=tag_remove
        )
        return success(message=result.message)


def register_tag_api(bp, *, tag_user_url, tag_url):
    tag_user = TagUserApi.as_view("tags_user")
    tag = TagApi.as_view("tags")
    bp.add_url_rule(tag_user_url, view_func=tag_user)
    bp.add_url_rule(tag_url, view_func=tag)

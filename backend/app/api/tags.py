import logging

from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..decorators import DecoratedMethodView, admin_required
from ..services.tag_service import TagService
from ..utils.response import error, success

tag_service = TagService()


# --------------------------- 标签管理 ---------------------------
class TagUserApi(DecoratedMethodView):
    method_decorators = {
        "post": [jwt_required()],
    }

    def post(self, user_id):
        """更新当前用户标签"""
        logging.info(f"更新用户标签: user_id={user_id}")
        if not current_user or current_user.id != user_id:
            return error(400, "非当前用户，修改标签失败")
        d = request.get_json()
        tag_add = set(d.get("tagAdd", []))
        tag_remove = set(d.get("tagRemove", []))
        result = tag_service.update_user_tags(
            user=current_user, tag_add=tag_add, tag_remove=tag_remove
        )
        return success(message=result.message)


class TagApi(DecoratedMethodView):
    method_decorators = {
        "share": [jwt_required()],
        "get": [],
        "post": [admin_required],
    }

    def get(self):
        """获取所有标签"""
        logging.info("获取所有标签")
        result = tag_service.list_tags()
        return success(data=result.data)

    def post(self):
        """应该加上 管理员权限
        更新公共标签库
        """
        logging.info("更新公共标签库")
        d = request.json
        tag_add = set(d.get("tagAdd", []))
        tag_remove = set(d.get("tagRemove", []))
        result = tag_service.update_public_tags(tag_add=tag_add, tag_remove=tag_remove)
        return success(message=result.message)


def register_tag_api(bp, *, tag_user_url, tag_url):
    tag_user = TagUserApi.as_view("tags_user")
    tag = TagApi.as_view("tags")
    bp.add_url_rule(tag_user_url, view_func=tag_user)
    bp.add_url_rule(tag_url, view_func=tag)

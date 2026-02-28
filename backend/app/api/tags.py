# 日志
import logging

from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..decorators import DecoratedMethodView, admin_required
from ..infrastructure.database.sqlalchemy import db
from ..models import Tag
from ..utils.response import error, success


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
        # 添加新的标签
        for tag_name in tag_add:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            current_user.tags.append(tag)

        # 删除被移除的标签
        for tag_name in tag_remove:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                current_user.tags.remove(tag)
        db.session.commit()
        return success(message="用户标签更新成功")


class TagApi(DecoratedMethodView):
    method_decorators = {
        "share": [jwt_required()],
        "get": [],
        "post": [admin_required],
    }

    def get(self):
        """获取所有标签"""
        logging.info("获取所有标签")
        tags = Tag.query.all()
        return success(data=[tag.name for tag in tags])

    def post(self):
        """应该加上 管理员权限
        更新公共标签库
        """
        logging.info("更新公共标签库")
        d = request.json
        tag_add = set(d.get("tagAdd", []))
        tag_remove = set(d.get("tagRemove", []))

        # 添加新的标签
        t = [Tag(name=tag) for tag in tag_add if tag]
        if t:
            db.session.add_all(t)

        # 删除Tag表
        if tag_remove:
            tags_to_delete = Tag.query.filter(Tag.name.in_(tag_remove)).all()
            # 逐个删除，触发before_delete事件
            for tag in tags_to_delete:
                db.session.delete(tag)

        db.session.commit()
        return success(message="公共标签库更新成功")


def register_tag_api(bp, *, tag_user_url, tag_url):
    tag_user = TagUserApi.as_view("tags_user")
    tag = TagApi.as_view("tags")
    bp.add_url_rule(tag_user_url, view_func=tag_user)
    bp.add_url_rule(tag_url, view_func=tag)

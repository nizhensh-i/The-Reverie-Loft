# 日志
import logging

from flask import current_app, request
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.orm import joinedload

from ..decorators import admin_required
from ..infrastructure.database.sqlalchemy import db
from ..models import Post, Role, User
from ..utils.response import error, not_found, success
from . import api


def get_user_data(username):
    """获取用户数据的公共逻辑"""
    logging.info(f"获取用户信息: username={username}")
    user = User.query.filter_by(username=username).first()
    if not user:
        return not_found("用户不存在")
    # 如果登录的用户时管理员，则会携带 电子邮件地址
    # if current_user and current_user.is_administrator():
    #     return user.to_json()
    # j = user.to_json()
    # j.pop("email", None)
    # j.pop("confirmed", None)
    return user.to_json()


@api.route("/users/<username>")
@jwt_required(optional=True)
def get_user_by_username(username):
    """根据用户名获取用户数据"""
    data = get_user_data(username)
    return success(data=data)


@api.route("/users/<string:username>/posts")
def get_post_by_user(username):
    """根据用户名获取文章的资料页面路由"""
    logging.info(f"获取用户文章: username={username}")
    user = User.query.filter_by(username=username).first()
    if not user:
        return not_found("用户不存在")

    page = request.args.get("page", 1, type=int)
    pagination = (
        user.posts.filter_by(deleted=False)
        .options(
            joinedload(Post.author).load_only(
                User.id, User.username, User.nickname, User.image
            )
        )
        .order_by(Post.timestamp.desc())
        .paginate(
            page=page,
            per_page=current_app.config["FLASKY_POSTS_PER_PAGE"],
            error_out=False,
        )
    )
    posts = pagination.items

    posts_json = Post.batch_query_with_data(posts, is_list=True)

    return success(data={"posts": posts_json}, total=pagination.total)


@api.route("/users/generate_posts")
@admin_required
@jwt_required()
def generate_user_posts():
    """批量生成用户和文章"""
    logging.info("批量生成用户和文章")
    try:
        from ..fake import Fake

        Role.insert_roles()
        Fake.users()
        Fake.posts()
        return success(message="用户和文章生成成功")
    except Exception as e:
        logging.error(f"生成用户和文章失败: {str(e)}", exc_info=True)
        return error(500, f"生成用户和文章失败: {str(e)}")


@api.route("/users/permissions/<int:perm>")
@jwt_required(optional=True)
def can(perm):
    """检查用户权限"""
    logging.info(f"检查用户权限: perm={perm}")
    if current_user:
        return success(data=current_user.can(perm))
    return success(data=False)


@api.route("/edit-profile/<int:id>", methods=["POST"])
@jwt_required()
@admin_required
def edit_profile_admin(id):
    """管理员编辑用户资料"""
    logging.info(f"管理员编辑用户资料: user_id={id}")
    try:
        user = User.query.get_or_404(id)
        user_info = request.get_json()
        user.email = user_info.get("email")
        user.username = user_info.get("username")
        user.confirmed = user_info.get("confirmed")
        user.role = Role.query.get(int(user_info.get("roleId")))

        user.nickname = user_info.get("nickname")
        user.location = user_info.get("location")
        user.about_me = user_info.get("about_me")

        db.session.commit()
        return success(message="用户资料更新成功")
    except Exception as e:
        logging.error(f"管理员编辑用户资料失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"编辑用户资料失败: {str(e)}")

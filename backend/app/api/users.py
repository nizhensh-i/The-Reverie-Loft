import logging

from dependency_injector.wiring import Provide, inject
from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..container import AppContainer
from ..decorators import admin_required
from ..services.seed_service import SeedService
from ..services.user_service import UserService
from ..utils.response import error, success
from . import api


@inject
def _user_service(
    user_service: UserService = Provide[AppContainer.user_service],
) -> UserService:
    return user_service


@inject
def _seed_service(
    seed_service: SeedService = Provide[AppContainer.seed_service],
) -> SeedService:
    return seed_service


@api.route("/users/<username>")
@jwt_required(optional=True)
def get_user_by_username(username):
    logging.info(f"获取用户信息: username={username}")
    result = _user_service().get_user(
        username,
        viewer=(current_user if current_user else None),
    )
    return success(data=result.data)


@api.route("/users/<string:username>/posts")
def get_post_by_user(username):
    logging.info(f"获取用户文章: username={username}")
    page = request.args.get("page", 1, type=int)
    result = _user_service().list_user_posts(username=username, page=page)
    return success(data=result.data, total=result.total)


@api.route("/users/generate_posts")
@admin_required
@jwt_required()
def generate_user_posts():
    logging.info("批量生成用户和文章")
    try:
        result = _seed_service().generate_users_and_posts()
        return success(message=result["message"])
    except Exception as e:
        logging.error(f"生成用户和文章失败: {str(e)}", exc_info=True)
        return error(500, f"生成用户和文章失败: {str(e)}")


@api.route("/users/permissions/<int:perm>")
@jwt_required(optional=True)
def can(perm):
    logging.info(f"检查用户权限: perm={perm}")
    if current_user:
        return success(data=current_user.can(perm))
    return success(data=False)


@api.route("/edit-profile/<int:id>", methods=["POST"])
@jwt_required()
@admin_required
def edit_profile_admin(id):
    logging.info(f"管理员编辑用户资料: user_id={id}")
    result = _user_service().update_user_profile_by_admin(
        user_id=id, payload=request.get_json() or {}
    )
    return success(message=result.message)

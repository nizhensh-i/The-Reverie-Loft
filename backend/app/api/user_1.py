import logging

from dependency_injector.wiring import Provide, inject
from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..container import AppContainer
from ..decorators import DecoratedMethodView
from ..services.user_profile_service import UserProfileService
from ..utils.response import error, success


@inject
def _user_profile_service(
    user_profile_service: UserProfileService = Provide[
        AppContainer.user_profile_service
    ],
) -> UserProfileService:
    return user_profile_service


class UsersByIdApi(DecoratedMethodView):
    method_decorators = {
        "get": [jwt_required(optional=True)],
        "patch": [jwt_required()],
    }

    def get(self, id):
        logging.info(f"获取用户信息: id={id}")
        result = _user_profile_service().get_user(
            user_id=id,
            viewer=(current_user if current_user else None),
        )
        return success(data=result.data)

    def patch(self, id):
        logging.info(f"编辑用户资料: user_id={id}")
        if not current_user or current_user.id != id:
            return error(400, message="操作不合法，非当前用户")
        result = _user_profile_service().update_user_profile(
            user=current_user, payload=request.json
        )
        return success(data="", message=result.message)


class UsersByUsernameApi(DecoratedMethodView):
    method_decorators = {
        "get": [jwt_required(optional=True)],
    }

    def get(self, username):
        logging.info(f"按 username 获取用户信息: username={username}")
        result = _user_profile_service().get_user_by_name(
            username=username,
            viewer=(current_user if current_user else None),
        )
        return success(data=result.data)


class UserImageApi(DecoratedMethodView):
    method_decorators = {
        "get": [],
        "post": [jwt_required()],
    }

    def get(self, id):
        result = _user_profile_service().get_user_image(user_id=id)
        return success(data=result.data)

    def post(self, id):
        logging.info(f"存储用户图像地址: user_id={id}")
        image = (request.get_json() or {}).get("image")
        result = _user_profile_service().update_user_image(
            operator=current_user,
            user_id=id,
            image=image,
        )
        if not result.ok:
            return error(400, result.message)
        return success(data=result.data)


def register_user_api(bp, *, user_by_id_url, user_by_username_url, user_image_url):
    users = UsersByIdApi.as_view("users_by_id")
    users_by_username = UsersByUsernameApi.as_view("users_by_username")
    user_image = UserImageApi.as_view("users_image")
    bp.add_url_rule(user_by_id_url, view_func=users)
    bp.add_url_rule(user_by_username_url, view_func=users_by_username)
    bp.add_url_rule(user_image_url, view_func=user_image)

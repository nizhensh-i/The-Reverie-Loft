import logging

from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..decorators import DecoratedMethodView
from ..services.user_profile_service import UserProfileService
from ..utils.response import error, success

user_profile_service = UserProfileService()


# --------------------------- 编辑资料 ---------------------------
class UsersByIdApi(DecoratedMethodView):
    method_decorators = {
        "get": [],
        "patch": [jwt_required()],
    }

    def get(self, id):
        logging.info(f"获取用户信息: id={id}")
        user = user_profile_service.get_user_by_id(id)
        return success(data=user.to_json())

    def patch(self, id):
        """编辑用户资料"""
        logging.info(f"编辑用户资料: user_id={id}")
        if not current_user or current_user.id != id:
            return error(400, message="操作不合法，非当前用户")
        result = user_profile_service.update_user_profile(
            user=current_user, payload=request.json
        )
        return success(data="", message=result.message)


class UsersByUsernameApi(DecoratedMethodView):
    def get(self, username):
        logging.info(f"按 username 获取用户信息: username={username}")
        user = user_profile_service.get_user_by_username(username)
        return success(data=user.to_json())


class UserImageApi(DecoratedMethodView):
    method_decorators = {
        "get": [],
        "post": [jwt_required()],
    }

    def get(self, id):
        result = user_profile_service.get_user_image(user_id=id)
        return success(data=result.data)

    def post(self, id):
        """存储用户图像地址"""
        logging.info(f"存储用户图像地址: user_id={id}")
        if current_user and (current_user.is_administrator() or current_user.id == id):
            image = (request.get_json() or {}).get("image")
            result = user_profile_service.update_user_image(user_id=id, image=image)
            return success(data=result.data)
        return error(400, "非当前用户，修改失败")


def register_user_api(bp, *, user_by_id_url, user_by_username_url, user_image_url):
    users = UsersByIdApi.as_view("users_by_id")
    users_by_username = UsersByUsernameApi.as_view("users_by_username")
    user_image = UserImageApi.as_view("users_image")
    bp.add_url_rule(user_by_id_url, view_func=users)
    bp.add_url_rule(user_by_username_url, view_func=users_by_username)
    bp.add_url_rule(user_image_url, view_func=user_image)

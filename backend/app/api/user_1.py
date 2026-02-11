import logging

from flask import request
from flask_jwt_extended import current_user, jwt_required

from ..decorators import DecoratedMethodView
from ..infrastructure import db
from ..models import User
from ..utils.common import get_avatars_url
from ..utils.response import error, success
from .upload import get_random_user_avatars


# --------------------------- 编辑资料 ---------------------------
class UsersByIdApi(DecoratedMethodView):
    method_decorators = {
        "get": [],
        "patch": [jwt_required()],
    }

    # def admin(self, user):
    #     user_info = request.get_json()
    #     user.email = user_info.get("email", '')
    #     user.username = user_info.get("username", '')
    #     user.confirmed = user_info.get("confirmed", '')
    #     if user_info.get("role", ''):
    #         user.role = Role.query.get(int(user_info.get("role")))
    #     return

    def get(self, id):
        logging.info(f"获取用户信息: id={id}")
        user = User.query.get_or_404(id)
        return success(data=user.to_json())

    def patch(self, id):
        """编辑用户资料"""
        logging.info(f"编辑用户资料: user_id={id}")
        if not current_user or current_user.id != id:
            return error(400, message="操作不合法，非当前用户")
        for key, value in request.json.items():
            if hasattr(current_user, key):
                setattr(current_user, key, value)
        db.session.commit()
        return success(data="", message="用户资料更新成功")


class UsersByUsernameApi(DecoratedMethodView):
    def get(self, username):
        logging.info(f"按 username 获取用户信息: username={username}")
        user = User.query.filter_by(username=username).first_or_404()
        return success(data=user.to_json())


class UserImageApi(DecoratedMethodView):
    method_decorators = {
        "get": [],
        "post": [jwt_required()],
    }

    def get(self, id):
        user = User.query.get_or_404(id)
        return success(data={"image": get_avatars_url(user.image)})

    def post(self, id):
        """存储用户图像地址"""
        logging.info(f"存储用户图像地址: user_id={id}")
        if current_user and (current_user.is_administrator() or current_user.id == id):
            try:
                image = (
                    request.get_json().get("image")
                    if request.get_json().get("image")
                    else get_random_user_avatars()
                )
                user = User.query.get_or_404(id)
                user.image = image
                db.session.commit()
                return success(data={"image": get_avatars_url(image)})
            except Exception as e:
                logging.error(f"存储用户图像地址失败: {str(e)}", exc_info=True)
                db.session.rollback()
                return error(500, f"存储用户图像地址失败: {str(e)}")
        else:
            return error(400, "非当前用户，修改失败")


# class UserAdminApi(MethodView):
#     decorators = [admin_required]
#
#     def patch(self, user_id):
#         """管理员编辑用户资料"""
#         logging.info(f"管理员编辑用户资料: user_id={user_id}")
#         try:
#             user = User.query.get_or_404(user_id)
#             user_info = request.get_json()
#             user.email = user_info.get("email")
#             user.username = user_info.get("username")
#             user.confirmed = user_info.get("confirmed")
#             user.role = Role.query.get(int(user_info.get("role")))
#
#             user.nickname = user_info.get("nickname")
#             user.location = user_info.get("location")
#             user.about_me = user_info.get("about_me")
#
#             db.session.commit()
#             return success(message="用户资料更新成功")
#         except Exception as e:
#             logging.error(f"管理员编辑用户资料失败: {str(e)}", exc_info=True)
#             db.session.rollback()
#             return error(500, f"编辑用户资料失败: {str(e)}")


def register_user_api(bp, *, user_by_id_url, user_by_username_url, user_image_url):
    users = UsersByIdApi.as_view("users_by_id")
    users_by_username = UsersByUsernameApi.as_view("users_by_username")
    user_image = UserImageApi.as_view("users_image")
    # admin = UserAdminApi.as_view(f'{name}_admin')
    bp.add_url_rule(user_by_id_url, view_func=users)
    bp.add_url_rule(user_by_username_url, view_func=users_by_username)
    bp.add_url_rule(user_image_url, view_func=user_image)

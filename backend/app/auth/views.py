from flask import current_app, request
from flask_jwt_extended import current_user, jwt_required

from ..decorators import admin_required
from ..infrastructure.auth import AuthCodeTokenService
from ..infrastructure.database.redis import redis
from ..schemas import (
    BindEmailRequest,
    ChangeEmailRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    RegisterRequest,
)
from ..services.auth_service import AuthService
from ..utils.response import error, success
from ..utils.time_util import DateUtils
from ..utils.validation import validate_json
from . import auth

code_token_service = AuthCodeTokenService(redis)
auth_service = AuthService(code_token_service=code_token_service)


@auth.before_app_request
@jwt_required(optional=True, verify_type=False)
def before_request():
    if current_user:
        current_user.ping()


@auth.route("/login", methods=["post"])
def login():
    j = request.get_json()
    result = auth_service.create_login_session(
        username=j.get("uiAccountName"),
        password=j.get("uiPassword"),
    )
    if result is not None:
        return success(
            data=result.data["user"].to_json(),
            access_token=result.data["access_token"],
            refresh_token=result.data["refresh_token"],
        )
    return error(code=400, message="账号或密码错误")


@auth.route("/register", methods=["POST"])
@validate_json(RegisterRequest)
def register(validated_data):
    result = auth_service.create_user_account(
        username=validated_data.username,
        password=validated_data.password,
        email=validated_data.email if validated_data.email else None,
    )
    if not result.ok:
        return error(message=result.message)
    return success()


@auth.route("/applyCode", methods=["POST"])
@jwt_required(optional=True)
@DateUtils.record_time
def apply_code():
    email = request.get_json().get("email")
    result = auth_service.create_email_code(email=email, current_user=current_user)
    if not result.ok:
        return error(code=400, message=result.message)
    return success()


@auth.route("/confirm", methods=["POST"])
@jwt_required()
@validate_json(BindEmailRequest)
def confirm(validated_data):
    """绑定邮箱"""
    email = validated_data.email
    code = validated_data.code

    result = auth_service.update_email_confirmation(
        user=current_user,
        email=email,
        code=code,
        admin_email=current_app.config["FLASKY_ADMIN"],
    )
    if not result.ok:
        return error(message=result.message)
    return success(
        data={"isConfirmed": current_user.confirmed, "roleId": current_user.role_id}
    )


@auth.route("/changeEmail", methods=["POST"])
@jwt_required(fresh=True)
@validate_json(ChangeEmailRequest)
def change_email(validated_data):
    """更换邮箱"""
    email = validated_data.new_email
    code = validated_data.code
    password = validated_data.password

    result = auth_service.update_user_email(
        user=current_user,
        new_email=email,
        code=code,
        password=password,
    )
    if not result.ok:
        return error(message=result.message)
    return success()


@auth.route("/changePassword", methods=["POST"])
@jwt_required(fresh=True)
@validate_json(ChangePasswordRequest)
def change_password(validated_data):
    result = auth_service.update_user_password(
        user=current_user,
        old_password=validated_data.old_password,
        new_password=validated_data.new_password,
    )
    if not result.ok:
        return error(message=result.message)
    return success()


@auth.route("/resetPassword", methods=["POST"])
@validate_json(ForgotPasswordRequest)
def reset_password(validated_data):
    email = validated_data.email
    code = validated_data.code
    password = validated_data.new_password

    result = auth_service.update_password_by_email(
        email=email, code=code, new_password=password
    )
    if not result.ok:
        return error(message=result.message)
    return success()


@auth.route("/helpChangePassword", methods=["POST"])
@admin_required
@jwt_required()
def change_password_admin():
    username = request.get_json().get("username")
    new_password = request.get_json().get("newPassword")
    result = auth_service.update_password_by_admin(
        username=username, new_password=new_password
    )
    if result.ok:
        return success()
    return error(message=result.message)


@auth.route("/setPassword", methods=["POST"])
@jwt_required()
def set_password():
    """
    设置密码（用于has_password=false的用户）

    请求参数:
        new_password: 新密码

    返回:
        success: 设置成功
    """
    data = request.get_json()
    new_password = data.get("new_password")
    result = auth_service.update_password_for_social_user(
        user=current_user, new_password=new_password
    )
    if not result.ok:
        return error(code=400, message=result.message)
    return success(message="密码设置成功")

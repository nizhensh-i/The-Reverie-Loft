from flask import current_app, request
from flask_jwt_extended import current_user, jwt_required

from ..composition import get_container
from ..decorators import admin_required
from ..schemas import (
    BindEmailRequest,
    ChangeEmailRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    RegisterRequest,
)
from ..utils.response import error, success
from ..utils.time_util import DateUtils
from ..utils.validation import validate_json
from . import auth


@auth.before_app_request
@jwt_required(optional=True, verify_type=False)
def before_request():
    if current_user:
        get_container().auth_service().touch_user_last_seen(user_id=current_user.id)


@auth.route("/login", methods=["post"])
def login():
    j = request.get_json() or {}
    result = (
        get_container()
        .auth_service()
        .create_login_session(
            username=j.get("uiAccountName"),
            password=j.get("uiPassword"),
        )
    )
    if result is not None:
        return success(
            data=result.data["user"],
            access_token=result.data["access_token"],
            refresh_token=result.data["refresh_token"],
        )
    return error(code=400, message="账号或密码错误")


@auth.route("/register", methods=["POST"])
@validate_json(RegisterRequest)
def register(validated_data):
    result = (
        get_container()
        .auth_service()
        .create_user_account(
            username=validated_data.username,
            password=validated_data.password,
            email=validated_data.email if validated_data.email else None,
        )
    )
    if not result.ok:
        return error(message=result.message)
    return success()


@auth.route("/applyCode", methods=["POST"])
@jwt_required(optional=True)
@DateUtils.record_time
def apply_code():
    email = (request.get_json() or {}).get("email")
    result = (
        get_container()
        .auth_service()
        .create_email_code(email=email, current_user=current_user)
    )
    if not result.ok:
        return error(code=400, message=result.message)
    return success()


@auth.route("/confirm", methods=["POST"])
@jwt_required()
@validate_json(BindEmailRequest)
def confirm(validated_data):
    result = (
        get_container()
        .auth_service()
        .update_email_confirmation(
            user=current_user,
            email=validated_data.email,
            code=validated_data.code,
            admin_email=current_app.config["FLASKY_ADMIN"],
        )
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
    result = (
        get_container()
        .auth_service()
        .update_user_email(
            user=current_user,
            new_email=validated_data.new_email,
            code=validated_data.code,
            password=validated_data.password,
        )
    )
    if not result.ok:
        return error(message=result.message)
    return success()


@auth.route("/changePassword", methods=["POST"])
@jwt_required(fresh=True)
@validate_json(ChangePasswordRequest)
def change_password(validated_data):
    result = (
        get_container()
        .auth_service()
        .update_user_password(
            user=current_user,
            old_password=validated_data.old_password,
            new_password=validated_data.new_password,
        )
    )
    if not result.ok:
        return error(message=result.message)
    return success()


@auth.route("/resetPassword", methods=["POST"])
@validate_json(ForgotPasswordRequest)
def reset_password(validated_data):
    result = (
        get_container()
        .auth_service()
        .update_password_by_email(
            email=validated_data.email,
            code=validated_data.code,
            new_password=validated_data.new_password,
        )
    )
    if not result.ok:
        return error(message=result.message)
    return success()


@auth.route("/helpChangePassword", methods=["POST"])
@admin_required
@jwt_required()
def change_password_admin():
    payload = request.get_json() or {}
    result = (
        get_container()
        .auth_service()
        .update_password_by_admin(
            username=payload.get("username"),
            new_password=payload.get("newPassword"),
        )
    )
    if result.ok:
        return success()
    return error(message=result.message)


@auth.route("/setPassword", methods=["POST"])
@jwt_required()
def set_password():
    data = request.get_json() or {}
    result = (
        get_container()
        .auth_service()
        .update_password_for_social_user(
            user=current_user,
            new_password=data.get("new_password"),
        )
    )
    if not result.ok:
        return error(code=400, message=result.message)
    return success(message="密码设置成功")

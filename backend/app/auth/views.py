import logging
import os

from flask import current_app, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    jwt_required,
)
from sqlalchemy.orm.attributes import flag_modified

from ..decorators import admin_required
from ..infrastructure.auth import AuthCodeTokenService
from ..infrastructure.database.redis import redis
from ..infrastructure.database.sqlalchemy import db
from ..infrastructure.my_celery import send_email
from ..infrastructure.storage import get_random_user_avatars
from ..models import Role, User
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

code_token_service = AuthCodeTokenService(redis)


@auth.before_app_request
@jwt_required(optional=True, verify_type=False)
def before_request():
    if current_user:
        current_user.ping()
        # if (not current_user.confirmed and request.endpoint
        #         and request.blueprint != 'auth' and request.endpoint != 'static'):
        #     return '用户邮件未认证'


@auth.route("/login", methods=["post"])
def login():
    j = request.get_json()
    user = User.query.filter_by(username=j.get("uiAccountName")).one_or_none()
    if user and user.verify_password(j.get("uiPassword")):
        # 创建新鲜令牌
        fresh_access_token = "Bearer " + create_access_token(identity=user, fresh=True)
        refresh_token = "Bearer " + create_refresh_token(identity=user)
        user.ping()
        return success(
            data=user.to_json(),
            access_token=fresh_access_token,
            refresh_token=refresh_token,
        )
    return error(code=400, message="账号或密码错误")


@auth.route("/register", methods=["POST"])
@validate_json(RegisterRequest)
def register(validated_data):
    # 检查用户名是否已存在
    u = User.query.filter_by(username=validated_data.username).first()
    if u:
        return error(message="该用户名已被注册，请换一个")

    # 检查邮箱是否已存在
    if validated_data.email:
        existing_email = User.query.filter_by(email=validated_data.email).first()
        if existing_email:
            return error(message="该邮箱已被注册，请换一个")

    email = validated_data.email if validated_data.email else None
    random_image = (
        "" if os.getenv("FLASK_CONFIG") == "testing" else get_random_user_avatars()
    )
    logging.info(f"随机图像为：{random_image}")
    user = User(
        email=email,
        username=validated_data.username,
        password=validated_data.password,
        image=random_image,
    )
    db.session.add(user)
    db.session.commit()
    return success()


@auth.route("/applyCode", methods=["POST"])
@jwt_required(optional=True)
@DateUtils.record_time
def apply_code():
    email = request.get_json().get("email")
    code = code_token_service.generate_email_code(email)
    if current_user:
        username = (
            current_user.nickname if current_user.nickname else current_user.username
        )
    else:
        user = User.query.filter_by(email=email).first()
        if not user:
            return error(code=400, message="您输入的邮箱未绑定过账号")
        username = user.nickname if user.nickname else user.username
    # celery发送邮件
    send_email.delay(
        email,
        "Confirm Your Account",
        "code_email.html",
        username=username,
        code=code,
        year=DateUtils.get_year(),
    )
    return success()


@auth.route("/confirm", methods=["POST"])
@jwt_required()
@validate_json(BindEmailRequest)
def confirm(validated_data):
    """绑定邮箱"""
    email = validated_data.email
    code = validated_data.code

    if current_user.email and email != current_user.email:
        return error(message="输入的邮件与用户的邮件不一致")
    if not code_token_service.compare_email_code(email, code):
        return error(message="绑定失败")

    current_user.confirmed = True
    if current_user.email == current_app.config["FLASKY_ADMIN"]:
        current_user.role = Role.query.filter_by(name="Administrator").first()
        logging.info(f"设置用户 {current_user.username} 为管理员")
    db.session.add(current_user)
    code_token_service.clear_email_code(email)
    db.session.commit()
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

    if User.query.filter_by(email=email).first():
        return error(message="填写的邮箱已经存在")
    if current_user.email == email:
        return error(message="请更换新的邮箱地址")

    # 密码
    if not current_user.verify_password(password):
        return error(message="密码错误")
    if not code_token_service.compare_email_code(email, code):
        return error(message="验证码错误")

    current_user.email = email
    current_user.social_account["email"] = email
    flag_modified(current_user, "social_account")
    db.session.add(current_user)
    code_token_service.clear_email_code(email)
    db.session.commit()
    return success()


@auth.route("/changePassword", methods=["POST"])
@jwt_required(fresh=True)
@validate_json(ChangePasswordRequest)
def change_password(validated_data):
    # 如果提供了旧密码，则验证旧密码
    if validated_data.old_password is not None:
        if not current_user.verify_password(validated_data.old_password):
            return error(message="原密码错误")

    # 设置新密码
    current_user.password = validated_data.new_password
    # 用户具备密码登陆能力
    current_user.has_password = True
    db.session.commit()
    return success()


@auth.route("/resetPassword", methods=["POST"])
@validate_json(ForgotPasswordRequest)
def reset_password(validated_data):
    email = validated_data.email
    code = validated_data.code
    password = validated_data.new_password

    # 验证码
    if not code_token_service.compare_email_code(email, code):
        return error(message="验证码错误")

    user = User.query.filter_by(email=email).first()
    if not user:
        return error(message="此邮箱尚未绑定")
    user.password = password
    user.has_password = True
    code_token_service.clear_email_code(email)
    db.session.commit()
    return success()


@auth.route("/helpChangePassword", methods=["POST"])
@admin_required
@jwt_required()
def change_password_admin():
    username = request.get_json().get("username")
    new_password = request.get_json().get("newPassword")
    user = User.query.filter_by(username=username).first()
    if user:
        user.password = new_password
        db.session.commit()
        return success()
    return error(message="用户不存在")


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
    try:
        data = request.get_json()
        new_password = data.get("new_password")

        if not new_password:
            return error(code=400, message="新密码不能为空")

        if len(new_password) < 3:
            return error(code=400, message="密码长度不能少于3个字符")

        # 设置密码
        current_user.password = new_password
        # 更新has_password标记
        current_user.has_password = True
        db.session.commit()

        return success(message="密码设置成功")
    except Exception as e:
        logging.exception("设置密码失败: %s", e)
        db.session.rollback()
        return error(code=500, message="设置密码失败")

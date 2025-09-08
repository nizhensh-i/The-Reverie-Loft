import logging
import random

from flask import request
from flask_jwt_extended import create_access_token, current_user, jwt_required

from .. import db
from ..api.upload import dir_file_name
from ..decorators import admin_required
from ..models import User
from ..mycelery.tasks import send_email
from ..schemas import (BindEmailRequest, ChangeEmailRequest,
                       ChangePasswordRequest, ForgotPasswordRequest,
                       RegisterRequest)
from ..utils.response import error, success
from ..utils.time_util import DateUtils
from ..utils.validation import validate_json
from . import auth


@auth.before_app_request
@jwt_required(optional=True)
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
        token = create_access_token(identity=user, expires_delta=False)
        user.ping()
        return success(data=user.to_json(), token="Bearer " + token)
    return error(code=400, message="账号或密码错误")


def get_random_user_avatars():
    try:
        avatars, total = dir_file_name("userAvatars/", 1, 10, False)
        return avatars[random.randint(0, total - 1)]
    except Exception as e:
        logging.warning(f'注册时从七牛云随机指定图像失败，原因：{e}')
        return ''


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
    random_image = get_random_user_avatars()
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
    code = User.generate_code(email)
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
    email = validated_data.email
    code = validated_data.code

    if current_user.email and email != current_user.email:
        return error(message="输入的邮件与用户的邮件不一致")
    if current_user.confirm(email, code):
        db.session.commit()
        return success(
            data={"isConfirmed": current_user.confirmed, "roleId": current_user.role_id}
        )
    return error(message="绑定失败")


@auth.route("/changeEmail", methods=["POST"])
@jwt_required()
@validate_json(ChangeEmailRequest)
def change_email(validated_data):
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
    # 验证码
    if current_user.change_email(email, code):
        db.session.commit()
        return success()
    return error(message="验证码错误")


@auth.route("/changePassword", methods=["POST"])
@jwt_required()
@validate_json(ChangePasswordRequest)
def change_password(validated_data):
    if current_user.verify_password(validated_data.old_password):
        current_user.password = validated_data.new_password
        db.session.add(current_user)
        db.session.commit()
        return success()
    return error(message="原密码错误")


@auth.route("/resetPassword", methods=["POST"])
@validate_json(ForgotPasswordRequest)
def reset_password(validated_data):
    email = validated_data.email
    code = validated_data.code
    password = validated_data.new_password

    # 验证码
    if User.compare_code(email, code):
        user = User.query.filter_by(email=email).first()
        if not user:
            return error(message="此邮箱尚未绑定")
        user.password = password
        db.session.add(user)
        db.session.commit()
        return success()
    return error(message="验证码错误")


@auth.route("/helpChangePassword", methods=["POST"])
@admin_required
@jwt_required()
def change_password_admin():
    username = request.get_json().get("username")
    new_password = request.get_json().get("newPassword")
    user = User.query.filter_by(username=username).first()
    if user:
        user.password = new_password
        db.session.add(user)
        db.session.commit()
        return success()
    return error(message="用户不存在")

import os

from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy.orm.attributes import flag_modified

from ..infrastructure.auth import AuthCodeTokenService
from ..infrastructure.database.sqlalchemy import db
from ..infrastructure.my_celery import send_email
from ..infrastructure.storage import get_random_user_avatars
from ..models import Role, User
from ..utils.time_util import DateUtils
from .common.dto import ActionResult, ItemResult
from .common.unit_of_work import SqlAlchemyUnitOfWork


class AuthService:
    def __init__(self, code_token_service: AuthCodeTokenService, session=None):
        self.code_token_service = code_token_service
        self.session = session or db.session
        self.uow = SqlAlchemyUnitOfWork(self.session)

    def rollback(self):
        self.uow.rollback()

    def create_login_session(self, *, username: str, password: str):
        user = User.query.filter_by(username=username).one_or_none()
        if not user or not user.verify_password(password):
            return None

        fresh_access_token = "Bearer " + create_access_token(identity=user, fresh=True)
        refresh_token = "Bearer " + create_refresh_token(identity=user)
        user.ping()
        return ItemResult(
            data={
                "user": user,
                "access_token": fresh_access_token,
                "refresh_token": refresh_token,
            }
        )

    def create_user_account(self, *, username: str, password: str, email: str | None):
        existed_username = User.query.filter_by(username=username).first()
        if existed_username:
            return ActionResult(ok=False, message="该用户名已被注册，请换一个")

        if email:
            existed_email = User.query.filter_by(email=email).first()
            if existed_email:
                return ActionResult(ok=False, message="该邮箱已被注册，请换一个")

        random_image = (
            "" if os.getenv("FLASK_CONFIG") == "testing" else get_random_user_avatars()
        )
        user = User(
            email=email, username=username, password=password, image=random_image
        )
        self.session.add(user)
        self.uow.commit()
        return ActionResult()

    def create_email_code(self, *, email: str, current_user):
        code = self.code_token_service.generate_email_code(email)
        if current_user:
            username = (
                current_user.nickname
                if current_user.nickname
                else current_user.username
            )
        else:
            user = User.query.filter_by(email=email).first()
            if not user:
                return ActionResult(ok=False, message="您输入的邮箱未绑定过账号")
            username = user.nickname if user.nickname else user.username

        send_email.delay(
            email,
            "Confirm Your Account",
            "code_email.html",
            username=username,
            code=code,
            year=DateUtils.get_year(),
        )
        return ActionResult()

    def update_email_confirmation(
        self, *, user, email: str, code: str, admin_email: str
    ):
        if user.email and email != user.email:
            return ActionResult(ok=False, message="输入的邮件与用户的邮件不一致")
        if not self.code_token_service.compare_email_code(email, code):
            return ActionResult(ok=False, message="绑定失败")

        user.confirmed = True
        if user.email == admin_email:
            user.role = Role.query.filter_by(name="Administrator").first()

        self.session.add(user)
        self.code_token_service.clear_email_code(email)
        self.uow.commit()
        return ActionResult()

    def update_user_email(self, *, user, new_email: str, code: str, password: str):
        if User.query.filter_by(email=new_email).first():
            return ActionResult(ok=False, message="填写的邮箱已经存在")
        if user.email == new_email:
            return ActionResult(ok=False, message="请更换新的邮箱地址")
        if not user.verify_password(password):
            return ActionResult(ok=False, message="密码错误")
        if not self.code_token_service.compare_email_code(new_email, code):
            return ActionResult(ok=False, message="验证码错误")

        user.email = new_email
        user.social_account["email"] = new_email
        flag_modified(user, "social_account")
        self.session.add(user)
        self.code_token_service.clear_email_code(new_email)
        self.uow.commit()
        return ActionResult()

    def update_user_password(
        self, *, user, old_password: str | None, new_password: str
    ):
        if old_password is not None and not user.verify_password(old_password):
            return ActionResult(ok=False, message="原密码错误")
        user.password = new_password
        user.has_password = True
        self.uow.commit()
        return ActionResult()

    def update_password_by_email(self, *, email: str, code: str, new_password: str):
        if not self.code_token_service.compare_email_code(email, code):
            return ActionResult(ok=False, message="验证码错误")

        user = User.query.filter_by(email=email).first()
        if not user:
            return ActionResult(ok=False, message="此邮箱尚未绑定")

        user.password = new_password
        user.has_password = True
        self.code_token_service.clear_email_code(email)
        self.uow.commit()
        return ActionResult()

    def update_password_by_admin(self, *, username: str, new_password: str):
        user = User.query.filter_by(username=username).first()
        if not user:
            return ActionResult(ok=False, message="用户不存在")
        user.password = new_password
        self.uow.commit()
        return ActionResult()

    def update_password_for_social_user(self, *, user, new_password: str):
        if not new_password:
            return ActionResult(ok=False, message="新密码不能为空")
        if len(new_password) < 3:
            return ActionResult(ok=False, message="密码长度不能少于3个字符")
        user.password = new_password
        user.has_password = True
        self.uow.commit()
        return ActionResult()

import os

from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy.orm.attributes import flag_modified

from ..application.dto import ActionResult, ItemResult
from ..domain.auth.policies import (
    resolve_email_code_username,
    should_grant_admin_role,
    validate_confirm_email_request,
    validate_new_email_change,
    validate_social_password,
)
from ..domain.common.exceptions import ValidationError
from ..domain.common.unit_of_work import UnitOfWork
from ..domain.ports.assemblers import ResponseAssemblerPort
from ..domain.ports.auth import EmailCodePort, MailSenderPort
from ..domain.ports.storage import AvatarProviderPort
from ..utils.time_util import DateUtils


class AuthService:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        code_token_service: EmailCodePort,
        assembler: ResponseAssemblerPort,
        mail_sender: MailSenderPort,
        avatar_provider: AvatarProviderPort,
    ):
        self.code_token_service = code_token_service
        self.assembler = assembler
        self.mail_sender = mail_sender
        self.avatar_provider = avatar_provider
        self.uow = uow

    def rollback(self):
        self.uow.rollback()

    def create_login_session(self, *, username: str, password: str):
        user = self.uow.auth.get_user_by_username(username)
        if not user or not user.verify_password(password):
            return None

        fresh_access_token = "Bearer " + create_access_token(identity=user, fresh=True)
        refresh_token = "Bearer " + create_refresh_token(identity=user)
        self.uow.users.touch_last_seen(user_id=user.id)
        user_extra_data = self.uow.users.build_user_extra_data(
            user_id=user.id, viewer_id=None
        )
        self.uow.commit()
        return ItemResult(
            data={
                "user": self.assembler.map_user(user, extra_data=user_extra_data),
                "access_token": fresh_access_token,
                "refresh_token": refresh_token,
            }
        )

    def create_user_account(self, *, username: str, password: str, email: str | None):
        existed_username = self.uow.auth.get_user_by_username(username)
        if existed_username:
            return ActionResult(ok=False, message="该用户名已被注册，请换一个")

        if email:
            existed_email = self.uow.auth.get_user_by_email(email)
            if existed_email:
                return ActionResult(ok=False, message="该邮箱已被注册，请换一个")

        random_image = (
            ""
            if os.getenv("FLASK_CONFIG") == "testing"
            else self.avatar_provider.get_random_avatar()
        )
        user = self.uow.auth.create_user(
            email=email,
            username=username,
            password=password,
            image=random_image,
        )
        self.uow.auth.add_user(user)
        self.uow.flush()
        self.uow.follows.add(
            self.uow.follows.create_follow_relation(
                follower_id=user.id,
                followed_id=user.id,
            )
        )
        self.uow.commit()
        return ActionResult()

    def touch_user_last_seen(self, *, user_id: int) -> None:
        self.uow.users.touch_last_seen(user_id=user_id)
        self.uow.commit()

    def create_email_code(self, *, email: str, current_user):
        code = self.code_token_service.generate_email_code(email)
        if current_user:
            username = resolve_email_code_username(current_user=current_user)
        else:
            user = self.uow.auth.get_user_by_email(email)
            if not user:
                return ActionResult(ok=False, message="您输入的邮箱未绑定过账号")
            username = resolve_email_code_username(target_user=user)

        self.mail_sender.send_template_email(
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
        try:
            validate_confirm_email_request(user_email=user.email, input_email=email)
        except ValidationError as exc:
            return ActionResult(ok=False, message=exc.message)

        if not self.code_token_service.compare_email_code(email, code):
            return ActionResult(ok=False, message="绑定失败")

        user.confirmed = True
        if should_grant_admin_role(user_email=user.email, admin_email=admin_email):
            user.role = self.uow.auth.get_role_by_name("Administrator")

        self.uow.auth.add_user(user)
        self.code_token_service.clear_email_code(email)
        self.uow.commit()
        return ActionResult()

    def update_user_email(self, *, user, new_email: str, code: str, password: str):
        if self.uow.auth.get_user_by_email(new_email):
            return ActionResult(ok=False, message="填写的邮箱已经存在")
        try:
            validate_new_email_change(current_email=user.email, new_email=new_email)
        except ValidationError as exc:
            return ActionResult(ok=False, message=exc.message)
        if not user.verify_password(password):
            return ActionResult(ok=False, message="密码错误")
        if not self.code_token_service.compare_email_code(new_email, code):
            return ActionResult(ok=False, message="验证码错误")

        user.email = new_email
        user.social_account["email"] = new_email
        flag_modified(user, "social_account")
        self.uow.auth.add_user(user)
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

        user = self.uow.auth.get_user_by_email(email)
        if not user:
            return ActionResult(ok=False, message="此邮箱尚未绑定")

        user.password = new_password
        user.has_password = True
        self.code_token_service.clear_email_code(email)
        self.uow.commit()
        return ActionResult()

    def update_password_by_admin(self, *, username: str, new_password: str):
        user = self.uow.auth.get_user_by_username(username)
        if not user:
            return ActionResult(ok=False, message="用户不存在")
        user.password = new_password
        self.uow.commit()
        return ActionResult()

    def update_password_for_social_user(self, *, user, new_password: str):
        try:
            validate_social_password(new_password)
        except ValidationError as exc:
            return ActionResult(ok=False, message=exc.message)
        user.password = new_password
        user.has_password = True
        self.uow.commit()
        return ActionResult()

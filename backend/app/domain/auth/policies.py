from ..common.exceptions import ValidationError


def resolve_email_code_username(*, current_user=None, target_user=None):
    user = current_user or target_user
    if user is None:
        return None
    return user.nickname if user.nickname else user.username


def validate_confirm_email_request(*, user_email: str | None, input_email: str):
    if user_email and input_email != user_email:
        raise ValidationError("输入的邮件与用户的邮件不一致")


def should_grant_admin_role(*, user_email: str | None, admin_email: str):
    return bool(user_email and user_email == admin_email)


def validate_new_email_change(*, current_email: str | None, new_email: str):
    if current_email == new_email:
        raise ValidationError("请更换新的邮箱地址")


def validate_social_password(new_password: str | None):
    if not new_password:
        raise ValidationError("新密码不能为空")
    if len(new_password) < 3:
        raise ValidationError("密码长度不能少于3个字符")

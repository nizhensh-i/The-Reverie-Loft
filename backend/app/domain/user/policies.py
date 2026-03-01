from dataclasses import dataclass

from ..common.exceptions import ValidationError

PROTECTED_PROFILE_FIELDS = {
    "id",
    "username",
    "email",
    "password",
    "role",
    "role_id",
    "confirmed",
    "has_password",
}

EDITABLE_PROFILE_FIELDS = {
    "nickname",
    "location",
    "about_me",
    "birthday",
    "gender",
    "website",
    "company",
    "occupation",
    "school",
}


@dataclass(frozen=True)
class AdminUserUpdatePayload:
    email: str | None
    username: str | None
    confirmed: bool | None
    role_id: int
    nickname: str | None
    location: str | None
    about_me: str | None


def get_editable_profile_fields():
    return EDITABLE_PROFILE_FIELDS


def should_update_profile_field(field_name: str):
    return (
        field_name in EDITABLE_PROFILE_FIELDS
        and field_name not in PROTECTED_PROFILE_FIELDS
    )


def extract_admin_update_payload(payload: dict) -> AdminUserUpdatePayload:
    if payload is None:
        raise ValidationError("参数错误")

    role_id = payload.get("roleId")
    try:
        parsed_role_id = int(role_id)
    except (TypeError, ValueError) as exc:
        raise ValidationError("角色参数错误") from exc

    return AdminUserUpdatePayload(
        email=payload.get("email"),
        username=payload.get("username"),
        confirmed=payload.get("confirmed"),
        role_id=parsed_role_id,
        nickname=payload.get("nickname"),
        location=payload.get("location"),
        about_me=payload.get("about_me"),
    )

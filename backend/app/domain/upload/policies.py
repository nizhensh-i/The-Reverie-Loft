from ..common.constants import InterestImageTypeCode
from ..common.exceptions import ValidationError

PUBLIC_IMAGE_PREFIXES = (
    "userBackground/mobile/",
    "userBackground/pc/",
    "userBackground/static",
    "userAvatars/",
)


def normalize_storage_path(path: str | None) -> str:
    return (path or "").strip().lstrip("/")


def normalize_storage_keys(keys) -> list[str]:
    if keys is None:
        return []
    if isinstance(keys, str):
        normalized = normalize_storage_path(keys)
        return [normalized] if normalized else []
    if isinstance(keys, list):
        cleaned = []
        for key in keys:
            if not isinstance(key, str):
                continue
            normalized = normalize_storage_path(key)
            if normalized:
                cleaned.append(normalized)
        return cleaned
    return []


def _user_private_prefix(user_id: int) -> str:
    return f"user_image/user_{user_id}/"


def can_access_storage_prefix(
    *, user_id: int, is_admin: bool, prefix: str, allow_dev_prefix: bool = False
) -> bool:
    normalized_prefix = normalize_storage_path(prefix)
    if is_admin:
        return True
    if not normalized_prefix:
        return False
    if allow_dev_prefix and normalized_prefix.startswith("dev/"):
        return True
    if normalized_prefix.startswith(_user_private_prefix(user_id)):
        return True
    return normalized_prefix.startswith(PUBLIC_IMAGE_PREFIXES)


def can_manage_storage_keys(
    *, user_id: int, is_admin: bool, keys, allow_dev_prefix: bool = False
) -> bool:
    normalized_keys = normalize_storage_keys(keys)
    if not normalized_keys:
        return False
    if is_admin:
        return True

    user_prefix = _user_private_prefix(user_id)
    for key in normalized_keys:
        if allow_dev_prefix and key.startswith("dev/"):
            continue
        if not key.startswith(user_prefix):
            return False
    return True


def build_upload_token_policy(*, now_ts: int):
    return {
        "fsizeLimit": 10 * 1024 * 1024,
        "deadline": now_ts + 3600,
    }


def resolve_interest_image_type(interest_type: str | None):
    if interest_type == "movie":
        return InterestImageTypeCode.MOVIE
    if interest_type == "book":
        return InterestImageTypeCode.BOOK
    raise ValidationError("兴趣图片类型不支持")

from ..common.exceptions import ValidationError


def ensure_praise_not_exists(existed_praise):
    if existed_praise:
        raise ValidationError("您已经点赞过了~")


def resolve_like_notification_receiver(*, actor_id: int, target_author_id: int):
    if actor_id == target_author_id:
        return None
    return target_author_id

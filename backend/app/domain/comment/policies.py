from ..common.constants import NotificationTypeCode, PermissionCode
from ..common.exceptions import ValidationError
from ..text.keyword_filter import DFAFilter


def build_comment_notification_targets(
    *,
    actor_id: int,
    post_author_id: int,
    direct_parent_author_id: int | None,
    at_list: list[int] | None,
):
    """Return notification targets as list[(receiver_id, NotificationType)]."""
    targets = []

    if direct_parent_author_id is None:
        if actor_id != post_author_id:
            targets.append((post_author_id, NotificationTypeCode.COMMENT))
    else:
        if actor_id != direct_parent_author_id:
            targets.append((direct_parent_author_id, NotificationTypeCode.REPLY))

    if at_list:
        targets.extend(
            (receiver_id, NotificationTypeCode.AT) for receiver_id in at_list
        )

    return targets


def can_delete_comment(*, operator, comment, post):
    is_comment_author = operator.id == comment.author_id
    is_post_author = operator.id == post.author_id
    is_admin = operator.can(PermissionCode.ADMIN)
    return is_comment_author or is_post_author or is_admin


def validate_comment_body(body: str):
    if not (body or "").strip():
        raise ValidationError("评论内容不能为空")


def sanitize_comment_body(body: str):
    return DFAFilter().filter(body or "", "*")


def resolve_root_comment(direct_parent):
    if direct_parent is None:
        return None
    return (
        direct_parent.root_comment if direct_parent.root_comment_id else direct_parent
    )


def apply_comment_status(comment, *, action: str):
    if action == "enable":
        comment.disabled = False
        return
    if action == "disable":
        comment.disabled = True
        return
    raise ValidationError(f"传递参数错误, status{action}")

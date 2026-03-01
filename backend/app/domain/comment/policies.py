from ...models import NotificationType, Permission


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
            targets.append((post_author_id, NotificationType.COMMENT))
    else:
        if actor_id != direct_parent_author_id:
            targets.append((direct_parent_author_id, NotificationType.REPLY))

    if at_list:
        targets.extend((receiver_id, NotificationType.AT) for receiver_id in at_list)

    return targets


def can_delete_comment(*, operator, comment, post):
    is_comment_author = operator.id == comment.author_id
    is_post_author = operator.id == post.author_id
    is_admin = operator.can(Permission.ADMIN)
    return is_comment_author or is_post_author or is_admin

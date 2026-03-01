from ..common.exceptions import ValidationError


def ensure_can_create_following(
    *, operator_id: int, target_user_id: int, already_following: bool
):
    if operator_id == target_user_id:
        raise ValidationError("不能关注自己")
    if already_following:
        raise ValidationError("你已经关注了该用户")


def ensure_can_delete_following(
    *, operator_id: int, target_user_id: int, already_following: bool
):
    if operator_id == target_user_id:
        raise ValidationError("不能取消关注自己")
    if not already_following:
        raise ValidationError("你未关注该用户")


def build_follow_search_item(*, user, avatar_url: str):
    return {
        "username": user.username,
        "image": avatar_url,
    }


def build_follower_page_item(*, relation, avatar_url: str, is_following: bool):
    return {
        "id": relation.follower.id,
        "nickname": relation.follower.nickname,
        "username": relation.follower.username,
        "image": avatar_url,
        "timestamp": relation.timestamp,
        "is_following": is_following,
    }


def build_following_page_item(*, relation, avatar_url: str, is_following_back: bool):
    return {
        "id": relation.followed.id,
        "nickname": relation.followed.nickname,
        "username": relation.followed.username,
        "image": avatar_url,
        "timestamp": relation.timestamp,
        "is_following_back": is_following_back,
    }

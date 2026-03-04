from __future__ import annotations

from ..utils.common import get_avatars_url
from ..utils.time_util import DateUtils
from .read_models import replace_markdown_image_refs


def map_image(image):
    return {
        "id": image.id,
        "url": get_avatars_url(image.url),
        "describe": image.describe,
        "type": image.type.value,
        "related_id": image.related_id,
        "disabled": image.disabled,
        "timestamp": image.timestamp,
    }


def map_notification(notification):
    return {
        "id": notification.id,
        "type": notification.type.value,
        "image": get_avatars_url(notification.trigger_user.image),
        "time": notification.created_at
        if isinstance(notification.created_at, str)
        else DateUtils.datetime_to_str(notification.created_at),
        "triggerNickName": notification.trigger_user.nickname,
        "triggerUsername": notification.trigger_user.username,
        "triggerId": notification.trigger_user_id,
        "content": "",
        "postId": notification.post_id,
        "commentId": notification.comment_id,
        "isRead": notification.is_read,
    }


def map_message(message):
    return {
        "content": message.content,
        "uid": message.sender_id,
        "user": {
            "username": message.sender.nickname
            if message.sender.nickname
            else message.sender.username,
            "avatar": get_avatars_url(message.sender.image),
        },
        "createTime": message.timestamp
        if isinstance(message.timestamp, str)
        else DateUtils.datetime_to_str(message.timestamp),
        "sender_id": message.sender_id,
        "is_read": message.is_read,
    }


def map_log(log):
    country = log.country if log.country else ""
    city = log.city if log.city else ""
    return {
        "id": log.id,
        "username": log.username,
        "ip": log.ip,
        "addr": country + city,
        "browser": log.browser,
        "os": log.os,
        "device": log.device,
        "operate": log.operate,
        "operateTime": log.operate_time
        if isinstance(log.operate_time, str)
        else DateUtils.datetime_to_str(log.operate_time),
    }


def map_comment(comment):
    return {
        "id": comment.id,
        "parentId": comment.root_comment_id,
        "directParentId": comment.direct_parent_id,
        "uid": comment.author.id,
        "content": comment.body if not comment.disabled else "<p><i>此评论已被版主禁用</i></p>",
        "likes": comment.praise.count(),
        "createTime": DateUtils.datetime_to_str(comment.timestamp),
        "user": {
            "username": comment.author.nickname
            if comment.author.nickname
            else comment.author.username,
            "avatar": get_avatars_url(comment.author.image),
            "homeLink": f"/user/{comment.author.username}",
        },
    }


def map_created_comment(comment):
    author = comment.author
    return {
        "id": comment.id,
        "parentId": comment.root_comment_id,
        "uid": author.id,
        "content": comment.body,
        "createTime": DateUtils.datetime_to_str(comment.timestamp),
        "user": {
            "username": author.nickname if author.nickname else author.username,
            "avatar": get_avatars_url(author.image),
        },
        "reply": "",
    }


def map_admin_comment(comment):
    return {
        "content": comment.body,
        "timestamp": DateUtils.datetime_to_str(comment.timestamp),
        "author": comment.author.username,
        "user_id": comment.author.id,
        "image": get_avatars_url(comment.author.image),
        "id": comment.id,
        "disabled": comment.disabled,
    }


def map_online_user(user):
    return {
        "username": user.username,
        "nickName": user.nickname,
    }


def map_post(post, extra_data, *, is_list=False):
    if not extra_data:
        raise ValueError("map_post() 需要额外的参数")

    author_data = extra_data.get("author_data", {})
    images = extra_data.get("images", [])
    comment_count = extra_data.get("comment_count", 0)
    praise_num = extra_data.get("praise_num", 0)
    has_praised = extra_data.get("has_praised", False)

    urls = [img["url"] for img in images]
    pos = [img["describe"] for img in images]

    data = {
        "id": post.id,
        "post_images": urls if post.derived_type == "image" else [],
        "pos": pos,
        "post_type": post.derived_type,
        "timestamp": post.timestamp
        if isinstance(post.timestamp, str)
        else DateUtils.datetime_to_str(post.timestamp),
        "author": author_data.get("username", ""),
        "nick_name": author_data.get("nickname", ""),
        "user_id": author_data.get("id", 0),
        "music": author_data.get("music", None),
        "comment_count": comment_count,
        "image": author_data.get("image", ""),
        "praise_num": praise_num,
        "has_praised": has_praised,
    }

    if is_list:
        data["summary"] = post.summary
    else:
        content = post.content
        if post.has_image and post.derived_type == "markdown":
            content = replace_markdown_image_refs(content, pos, urls)
        data["content"] = content

    return data


def batch_map_posts(posts, *, extra_data_map, is_list=False):
    if not posts:
        return []

    return [map_post(post, extra_data_map[post.id], is_list=is_list) for post in posts]


def map_user(user, *, extra_data):
    if extra_data is None:
        raise ValueError("map_user() 需要 extra_data")

    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "location": user.location,
        "about_me": user.about_me,
        "sex": user.sex,
        "bg_image": user.bg_image,
        "pc_bg_image": user.pc_bg_image,
        "member_since": user.member_since
        if isinstance(user.member_since, str)
        else DateUtils.datetime_to_str(user.member_since),
        "last_seen": user.last_seen
        if isinstance(user.last_seen, str)
        else DateUtils.datetime_to_str(user.last_seen),
        "image": get_avatars_url(user.image),
        "admin": user.is_administrator(),
        "email": user.email,
        "roleId": user.role.id if user.role else None,
        "confirmed": user.confirmed,
        "post_count": extra_data.get("post_count", 0),
        "followers_count": extra_data.get("followers_count", 0),
        "followed_count": extra_data.get("followed_count", 0),
        "praised_count": extra_data.get("praised_count", 0),
        "is_followed_by_current_user": extra_data.get(
            "is_followed_by_current_user", False
        ),
        "is_following_current_user": extra_data.get("is_following_current_user", False),
        "interest": extra_data.get("interest", {"movies": [], "books": []}),
        "social_account": user.social_account,
        "music": user.music,
        "tags": extra_data.get("tags", []),
        "bound_providers": extra_data.get("bound_providers", []),
        "has_password": user.has_password,
    }


class ApiResponseAssembler:
    map_user = staticmethod(map_user)
    batch_map_posts = staticmethod(batch_map_posts)
    map_comment = staticmethod(map_comment)
    map_created_comment = staticmethod(map_created_comment)
    map_admin_comment = staticmethod(map_admin_comment)
    map_notification = staticmethod(map_notification)
    map_message = staticmethod(map_message)
    map_log = staticmethod(map_log)
    map_online_user = staticmethod(map_online_user)
    map_image = staticmethod(map_image)

import logging

from celery import shared_task

from ...presenters.event_serializers import serialize_notification_events
from ..database.sqlalchemy import db
from ..socketio import get_socketio_client


def _create_and_emit_notifications(notifications):
    """创建通知并推送给用户"""
    if not notifications:
        return

    db.session.add_all(notifications)
    db.session.flush()

    # 批量推送通知
    socketio = get_socketio_client()
    notification_data = serialize_notification_events(notifications)
    for i, notification in enumerate(notifications):
        socketio.emit(
            "new_notification",
            notification_data[i],
            to=str(notification.receiver_id),
        )

    db.session.commit()


@shared_task(ignore_result=True)
def create_new_post_notifications(post_id, author_id, follower_ids):
    """创建新文章通知并推送给粉丝

    Args:
        post_id: 文章ID
        author_id: 作者ID
        follower_ids: 粉丝ID列表
    """
    from ...infrastructure.persistence.models import Notification, NotificationType

    try:
        notifications = [
            Notification(
                receiver_id=follower_id,
                trigger_user_id=author_id,
                post_id=post_id,
                type=NotificationType.NewPost,
            )
            for follower_id in follower_ids
        ]

        _create_and_emit_notifications(notifications)
        logging.info(f"新文章通知任务完成: post_id={post_id}, 粉丝数={len(follower_ids)}")

    except Exception as e:
        db.session.rollback()
        logging.error(f"新文章通知任务失败: {str(e)}", exc_info=True)


@shared_task(ignore_result=True)
def create_comment_notifications(post_id, comment_id, author_id, notifications_data):
    """创建评论通知

    Args:
        post_id: 文章ID
        comment_id: 评论ID
        author_id: 评论作者ID
        notifications_data: 通知数据列表，格式为 [(receiver_id, notification_type), ...]
    """
    from ...infrastructure.persistence.models import Notification

    try:
        notifications = [
            Notification(
                receiver_id=receiver_id,
                trigger_user_id=author_id,
                post_id=post_id,
                comment_id=comment_id,
                type=notification_type,
            )
            for receiver_id, notification_type in notifications_data
        ]

        _create_and_emit_notifications(notifications)
        logging.info(
            f"评论通知任务完成: post_id={post_id}, comment_id={comment_id}, 通知数={len(notifications_data)}"
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"评论通知任务失败: {str(e)}", exc_info=True)


@shared_task(ignore_result=True)
def create_like_notifications(post_id, comment_id, liker_id, receiver_id):
    """创建点赞通知

    Args:
        post_id: 文章ID (评论点赞时传入评论所在文章ID)
        comment_id: 评论ID (文章点赞时传入None)
        liker_id: 点赞者ID
        receiver_id: 接收者ID (文章作者或评论作者)
    """
    from ...infrastructure.persistence.models import Notification, NotificationType

    try:
        if receiver_id is None:
            return

        notification = Notification(
            receiver_id=receiver_id,
            trigger_user_id=liker_id,
            post_id=post_id,
            comment_id=comment_id,
            type=NotificationType.LIKE,
        )

        _create_and_emit_notifications([notification])
        logging.info(f"点赞通知任务完成: post_id={post_id}, comment_id={comment_id}")

    except Exception as e:
        db.session.rollback()
        logging.error(f"点赞通知任务失败: {str(e)}", exc_info=True)


@shared_task(ignore_result=True)
def create_chat_notifications(receiver_id, sender_id, message_id):
    """创建私信通知"""
    from ...infrastructure.persistence.models import Notification, NotificationType

    try:
        notification = Notification(
            receiver_id=receiver_id,
            trigger_user_id=sender_id,
            type=NotificationType.CHAT,
        )

        _create_and_emit_notifications([notification])
        logging.info(f"私信通知任务完成: receiver_id={receiver_id}, sender_id={sender_id}")

    except Exception as e:
        db.session.rollback()
        logging.error(f"私信通知任务失败: {str(e)}", exc_info=True)

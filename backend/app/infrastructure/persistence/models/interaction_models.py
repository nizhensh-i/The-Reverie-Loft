from enum import Enum

from ....infrastructure.database.sqlalchemy import db
from ....utils.time_util import DateUtils


class NotificationType(Enum):
    AT = "@"
    COMMENT = "评论"
    REPLY = "回复"
    LIKE = "点赞"
    CHAT = "私信"
    NewPost = "新文章"


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(NotificationType))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=DateUtils.now_time)

    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    trigger_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(
        db.Integer, db.ForeignKey("posts.id", ondelete="SET NULL"), nullable=True
    )
    comment_id = db.Column(
        db.Integer, db.ForeignKey("comments.id", ondelete="SET NULL"), nullable=True
    )


class Log(db.Model):
    __tablename__ = "log"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    ip = db.Column(db.String(100))
    country = db.Column(db.String(50))
    city = db.Column(db.String(50))
    browser = db.Column(db.String(50))
    browser_version = db.Column(db.String(50))
    os = db.Column(db.String(50))
    os_version = db.Column(db.String(50))
    device = db.Column(db.String(50))
    operate = db.Column(db.String(64))
    operate_time = db.Column(db.DateTime, index=True, default=DateUtils.now_time)


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=DateUtils.now_time)
    is_read = db.Column(db.Boolean, default=False)

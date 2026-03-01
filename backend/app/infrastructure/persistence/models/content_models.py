from enum import Enum

from ....infrastructure.database.sqlalchemy import db
from ....utils.time_util import DateUtils


class PostType(Enum):
    TEXT = "text"
    MARKDOWN = "markdown"


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.String(500))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    content = db.Column(db.Text)
    has_image = db.Column(db.Boolean, default=False)
    type = db.Column(db.Enum(PostType))
    timestamp = db.Column(db.DateTime, index=True, default=DateUtils.now_time)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    comments = db.relationship(
        "Comment", backref="post", lazy="dynamic", passive_deletes=True
    )
    praise = db.relationship(
        "Praise", backref="post", lazy="dynamic", passive_deletes=True
    )
    notifications = db.relationship("Notification", backref="post", lazy="dynamic")
    deleted = db.Column(db.Boolean, default=False)

    @property
    def derived_type(self):
        if self.type == PostType.TEXT and not self.has_image:
            return "text"
        if self.type == PostType.TEXT and self.has_image:
            return "image"
        return "markdown"


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=DateUtils.now_time)
    disabled = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"))

    root_comment_id = db.Column(
        db.Integer, db.ForeignKey("comments.id", ondelete="CASCADE")
    )
    root_comment = db.relationship(
        "Comment", remote_side=[id], foreign_keys=[root_comment_id]
    )

    direct_parent_id = db.Column(
        db.Integer, db.ForeignKey("comments.id", ondelete="CASCADE")
    )
    direct_parent = db.relationship(
        "Comment",
        remote_side=[id],
        foreign_keys=[direct_parent_id],
        back_populates="direct_children",
    )
    direct_children = db.relationship(
        "Comment",
        back_populates="direct_parent",
        foreign_keys=[direct_parent_id],
        cascade="all, delete-orphan",
    )

    notifications = db.relationship("Notification", backref="comments", lazy="dynamic")
    praise = db.relationship(
        "Praise", backref="comment", lazy="dynamic", passive_deletes=True
    )


class Praise(db.Model):
    __tablename__ = "praise"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"))
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id", ondelete="CASCADE"))


class ImageType(Enum):
    MOVIE = "电影"
    BOOK = "书籍"
    POST = "文章"
    COMMENT = "评论"


class Image(db.Model):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    describe = db.Column(db.String(64))
    type = db.Column(db.Enum(ImageType))
    related_id = db.Column(db.Integer, nullable=False)
    disabled = db.Column(db.Boolean, default=False)
    isDeleted = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=DateUtils.now_time)

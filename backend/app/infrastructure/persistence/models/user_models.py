from sqlalchemy import event
from werkzeug.security import check_password_hash, generate_password_hash

from ....domain.common.constants import PermissionCode
from ....infrastructure.database.sqlalchemy import db
from ....utils.time_util import DateUtils

Permission = PermissionCode


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref="role", lazy="dynamic")

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles(session=None):
        db.create_all()
        resolved_session = session or db.session
        roles = {
            "User": [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            "Moderator": [
                Permission.FOLLOW,
                Permission.COMMENT,
                Permission.WRITE,
                Permission.MODERATE,
            ],
            "Administrator": [
                Permission.FOLLOW,
                Permission.COMMENT,
                Permission.WRITE,
                Permission.MODERATE,
                Permission.ADMIN,
            ],
        }
        default_role = "User"
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
            role.reset_permissions()
            for perm in roles[role_name]:
                role.add_permission(perm)
            role.default = role.name == default_role
            resolved_session.add(role)

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return "<Role %r>" % self.name


class Follow(db.Model):
    __tablename__ = "follows"
    follower_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=DateUtils.now_time)


user_tag = db.Table(
    "user_tag",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id")),
)


class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True, nullable=False)


@event.listens_for(Tag, "before_delete")
def delete_tag_cleanup(mapper, connection, target):
    connection.execute(user_tag.delete().where(user_tag.c.tag_id == target.id))


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    has_password = db.Column(db.Boolean, default=True)
    confirmed = db.Column(db.Boolean, default=False)
    nickname = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    sex = db.Column(db.String(10), nullable=True)
    bg_image = db.Column(db.String(255), nullable=True)
    pc_bg_image = db.Column(db.String(255), nullable=True)
    member_since = db.Column(db.DateTime(), default=DateUtils.now_time)
    last_seen = db.Column(db.DateTime(), default=DateUtils.now_time)
    image = db.Column(db.String(255))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    social_account = db.Column(
        db.JSON,
        default=lambda: {
            "github": None,
            "qq": None,
            "wechat": None,
            "bilibili": None,
            "twitter": None,
            "tiktok": None,
            "rednote": None,
            "email": None,
        },
    )
    music = db.Column(
        db.JSON,
        default=lambda: {
            "name": None,
            "artist": None,
            "url": None,
            "pic": None,
            "lrc": None,
        },
    )

    tags = db.relationship(
        "Tag",
        secondary="user_tag",
        backref=db.backref("users", lazy="dynamic"),
        lazy="dynamic",
    )

    posts = db.relationship("Post", backref="author", lazy="dynamic")
    praises = db.relationship("Praise", backref="author", lazy="dynamic")

    followed = db.relationship(
        "Follow",
        foreign_keys=[Follow.follower_id],
        backref=db.backref("follower", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    followers = db.relationship(
        "Follow",
        foreign_keys=[Follow.followed_id],
        backref=db.backref("followed", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    comments = db.relationship("Comment", backref="author", lazy="dynamic")

    received_notification = db.relationship(
        "Notification",
        foreign_keys="Notification.receiver_id",
        backref="receiver",
        lazy="dynamic",
    )
    triggered_notification = db.relationship(
        "Notification",
        foreign_keys="Notification.trigger_user_id",
        backref="trigger_user",
        lazy="dynamic",
    )

    sent_messages = db.relationship(
        "Message",
        foreign_keys="Message.sender_id",
        backref=db.backref("sender", lazy="joined"),
        lazy="dynamic",
    )
    received_messages = db.relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        backref=db.backref("receiver", lazy="joined"),
        lazy="dynamic",
    )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            relation = Follow(follower=self, followed=user)
            db.session.add(relation)

    def unfollow(self, user):
        relation = self.followed.filter_by(followed_id=user.id).first()
        if relation:
            db.session.delete(relation)

    def is_following(self, user):
        if user and not user.id:
            return False
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user and not user.id:
            return False
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def __repr__(self):
        return "<User %r>" % self.username


class AnonymousUser:
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

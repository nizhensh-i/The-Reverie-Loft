import random
import re
import logging
from datetime import timedelta
from enum import Enum


from flask import current_app
from flask_jwt_extended import create_access_token, current_user
from sqlalchemy import and_, event, func
from sqlalchemy.orm.attributes import flag_modified
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, jwt, redis
from .exceptions import ValidationError
from .utils.common import get_avatars_url
from .utils.time_util import DateUtils


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


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
    def insert_roles():
        db.create_all()
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
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = role.name == default_role
            db.session.add(role)
        db.session.commit()

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
    # 同时设置follower_id，followed_id为主键，保证同一对用户只能存在一条关系
    # 关注者id
    follower_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    # 被关注者id
    followed_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=DateUtils.now_time)


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
    # 通知类型
    type = db.Column(db.Enum(NotificationType))
    # 是否已读
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=DateUtils.now_time)

    # 接收者（文章作者）
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # 触发者（评论/点赞用户）
    trigger_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # 关联文章id
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    # 评论id
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"))

    def to_json(self):
        data = {
            "id": self.id,
            "type": self.type.value,
            "image": get_avatars_url(self.trigger_user.image),
            "time": self.created_at
            if isinstance(self.created_at, str)
            else DateUtils.datetime_to_str(self.created_at),
            "triggerNickName": self.trigger_user.nickname,
            "triggerUsername": self.trigger_user.username,
            "triggerId": self.trigger_user_id,
            "content": "",
            "postId": self.post_id,
            "commentId": self.comment_id,
            "isRead": self.is_read,
        }
        return data


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    confirmed = db.Column(db.Boolean, default=False)
    # 用户资料
    nickname = db.Column(db.String(64))
    location = db.Column(db.String(64))
    # 签名
    about_me = db.Column(db.Text())
    # 存储男或女，允许为空
    sex = db.Column(db.String(10), nullable=True)
    # 个人资料背景图片
    bg_image = db.Column(db.String(255), nullable=True)
    member_since = db.Column(db.DateTime(), default=DateUtils.now_time)
    last_seen = db.Column(db.DateTime(), default=DateUtils.now_time)
    # 用户图像
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
    # https://github.com/metowolf/MetingJS字段格式
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
    # secondary参数必须设置为关联表
    tags = db.relationship(
        "Tag",
        secondary="user_tag",
        backref=db.backref("users", lazy="dynamic"),
        lazy="dynamic",
    )

    posts = db.relationship("Post", backref="author", lazy="dynamic")

    praises = db.relationship("Praise", backref="author", lazy="dynamic")

    # 关注者
    followed = db.relationship(
        "Follow",
        foreign_keys=[Follow.follower_id],
        backref=db.backref("follower", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    # 被关注者
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
        foreign_keys=[Notification.receiver_id],
        backref="receiver",
        lazy="dynamic",
    )

    triggered_notification = db.relationship(
        "Notification",
        foreign_keys=[Notification.trigger_user_id],
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

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(
            Follow.follower_id == self.id, Post.deleted.is_(False)
        )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.role:
            if self.email == current_app.config["FLASKY_ADMIN"] and self.confirmed:
                self.role = Role.query.filter_by(name="Administrator").first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        self.follow(self)

    def ping(self):
        self.last_seen = DateUtils.now_time()
        db.session.add(self)
        db.session.commit()

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

    def generate_confirmation_token(self, expiration=3600):
        additional_claims = {"confirm": self.id}
        confirm_token = create_access_token(
            identity=current_user,
            additional_claims=additional_claims,
            expires_delta=timedelta(seconds=expiration),
        )
        return confirm_token

    @staticmethod
    def generate_code(email, expiration=60 * 3):
        code = random.randint(100000, 999999)
        redis.setex(email, expiration, code)
        return code

    @staticmethod
    def compare_code(email, code):
        try:
            result = User.get_value(email)
            print("result", result)
        except Exception as e:
            print("redis 取值失败", e)
            return False
        if not result:
            print("无对应键")
            return False
        if code != result:
            print("验证码不匹配")
            return False
        return True

    def confirm(self, email, code):
        if User.compare_code(email, code):
            self.confirmed = True
            # 角色设置管理员
            if self.email == current_app.config["FLASKY_ADMIN"]:
                self.role = Role.query.filter_by(name="Administrator").first()
                logging.info(f"设置用户 {self.username} 为管理员")
            db.session.add(self)
            redis.delete(email)
            return True
        else:
            return False

    def change_email(self, new_email, code):
        if User.compare_code(new_email, code):
            self.email = new_email
            self.social_account["email"] = new_email
            # 标记 social_account 已修改
            flag_modified(self, "social_account")
            db.session.add(self)
            return True
        else:
            return False

    @staticmethod
    def get_value(key):
        # 获取键值
        value = redis.get(key)
        # if value:
        #     return value.decode()
        return value

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        if user and not user.id:
            return False
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user and not user.id:
            return False
        return self.followers.filter_by(follower_id=user.id).first() is not None

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
        db.session.commit()

    def send_msg(self, user, content):
        m = Message(sender=self, receiver=user, content=content)
        db.session.add(m)

    def to_json(self):
        post_praises = Praise.query.join(Post).filter(Post.author_id == self.id).count()
        comment_praises = (
            Praise.query.join(Comment).filter(Comment.author_id == self.id).count()
        )
        total_praises = post_praises + comment_praises
        interest_images = (
            Image.query.filter(
                and_(
                    Image.type.in_([ImageType.MOVIE, ImageType.BOOK]),
                    Image.related_id == self.id,
                )
            )
            .order_by(Image.id.asc())
            .all()
        )
        interest = {"movies": [], "books": []}
        if interest_images:
            for image in interest_images:
                if image.type == ImageType.MOVIE:
                    interest["movies"].append(image.to_json())
                elif image.type == ImageType.BOOK:
                    interest["books"].append(image.to_json())
        json_user = {
            # 后端接口
            # 'url': url_for('api.get_user', id=self.id),
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname,
            "location": self.location,
            "about_me": self.about_me,
            "sex": self.sex,
            "bg_image": self.bg_image,
            "member_since": self.member_since
            if isinstance(self.member_since, str)
            else DateUtils.datetime_to_str(self.member_since),
            "last_seen": self.last_seen
            if isinstance(self.last_seen, str)
            else DateUtils.datetime_to_str(self.last_seen),
            "image": get_avatars_url(self.image),
            "admin": self.is_administrator(),
            "email": self.email,
            "roleId": self.role.id,
            "confirmed": self.confirmed,
            # 'posts_url': url_for('api.get_user_posts', id=self.id),
            # 'followed_posts_url': url_for('api.get_user_followed_posts',
            #                               id=self.id),
            "post_count": self.posts.count(),
            # 粉丝
            "followers_count": self.followers.count() - 1,
            # 关注
            "followed_count": self.followed.count() - 1,
            # 获赞数量(文章+评论获赞)
            "praised_count": total_praises,
            # 是否被当前用户关注
            "is_followed_by_current_user": self.is_followed_by(current_user)
            if current_user
            else False,
            # 是否关注了当前用户
            "is_following_current_user": self.is_following(current_user)
            if current_user
            else False,
            "interest": interest,
            "social_account": self.social_account,
            "music": self.music,
            "tags": [tag.name for tag in self.tags],
        }
        return json_user

    def __repr__(self):
        return "<User %r>" % self.username


class AnonymousUser:
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


@jwt.user_identity_loader
def user_identify_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


class PostType(Enum):
    TEXT = "纯文字"
    IMAGE = "图文"


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)

    # title = db.Column(db.String(200))
    summary = db.Column(db.String(500))

    # 存储纯文本/Markdown 内容，用于纯文字和图文文章
    body = db.Column(db.Text)
    # 存储富文本编辑器生成的 HTML 内容
    body_html = db.Column(db.Text)

    # 类型：纯文字或者图文
    type = db.Column(db.Enum(PostType))

    # 封面图片
    # cover = db.Column(db.String(255))
    # # 浏览量
    # view_count = db.Column(db.Integer, default=0)
    # # 点赞数
    # like_count = db.Column(db.Integer, default=0)
    # # 评论数
    # comment_count = db.Column(db.Integer, default=0)

    # 发布时间
    timestamp = db.Column(db.DateTime, index=True, default=DateUtils.now_time)
    # 更新时间
    # updated_at = db.Column(db.DateTime)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    comments = db.relationship("Comment", backref="post", lazy="dynamic")
    praise = db.relationship("Praise", backref="post", lazy="dynamic")
    notifications = db.relationship("Notification", backref="post", lazy="dynamic")
    deleted = db.Column(db.Boolean, default=False)

    def to_json(self, extra_data, is_list=False):
        """
        纯序列化函数，不包含任何数据库查询
        必须传入 extra_data 参数包含所有需要的外部数据：
        {
            'author_data': {'username': str, 'nickname': str, 'image': str, 'id': int},
            'images': [{'url': str, 'describe': str}],
            'comment_count': int,
            'praise_num': int,
            'has_praised': bool
        }

        is_list: 是否为列表API调用，如果为True，则使用summary字段替代body和body_html
        """
        if not extra_data:
            raise ValueError("to_json() 需要额外的参数")

        author_data = extra_data.get("author_data", {})
        images = extra_data.get("images", [])
        comment_count = extra_data.get("comment_count", 0)
        praise_num = extra_data.get("praise_num", 0)
        has_praised = extra_data.get("has_praised", False)

        # 从预填充数据构建图片URL和位置
        urls = [img["url"] for img in images]
        pos = [img["describe"] for img in images]

        j = {
            "id": self.id,
            "post_images": urls if not self.body_html else [],
            "pos": pos,
            "post_type": self.type.value,
            "timestamp": self.timestamp
            if isinstance(self.timestamp, str)
            else DateUtils.datetime_to_str(self.timestamp),
            "author": author_data.get("username", ""),
            "nick_name": author_data.get("nickname", ""),
            "user_id": author_data.get("id", 0),
            "music": author_data.get("music", None),
            "comment_count": comment_count,
            "image": author_data.get("image", ""),
            "praise_num": praise_num,
            "has_praised": has_praised,
        }
        # 文章列表只返回摘要
        if is_list:
            j.update({"summary": self.summary})
        # 文章详情返回完整内容
        else:
            body = self.body
            body_html = self.body_html
            if self.type == PostType.IMAGE and self.body_html:
                body = Post.replace_body(self.body, pos, urls)
                body_html = Post.replace_body_html(self.body_html, pos, urls)
            j.update(
                {
                    "body": body,
                    "body_html": body_html,
                }
            )
        return j

    @staticmethod
    def _query_post_images(post_ids):
        """
        批量查询文章图片数据
        返回按文章ID分组的图片数据字典
        """
        images_query = (
            db.session.query(Image.related_id, Image.url, Image.describe, Image.id)
            .filter(Image.type == ImageType.POST, Image.related_id.in_(post_ids))
            .order_by(Image.related_id.asc(), Image.id.asc())
            .all()
        )

        images_dict = {}
        for image in images_query:
            if image.related_id not in images_dict:
                images_dict[image.related_id] = []
            images_dict[image.related_id].append(
                {
                    "url": get_avatars_url(image.url),
                    "describe": image.describe,
                    "id": image.id,
                }
            )

        return images_dict

    @staticmethod
    def _query_comment_counts(post_ids):
        """
        批量查询文章评论数量
        返回文章ID到评论数的映射字典
        """
        comments_count_query = (
            db.session.query(
                Comment.post_id, func.count(Comment.id).label("comment_count")
            )
            .filter(Comment.post_id.in_(post_ids))
            .group_by(Comment.post_id)
            .all()
        )

        return {post_id: count for post_id, count in comments_count_query}

    @staticmethod
    def _query_praise_counts(post_ids):
        """
        批量查询文章点赞数量
        返回文章ID到点赞数的映射字典
        """
        praise_count_query = (
            db.session.query(
                Praise.post_id, func.count(Praise.id).label("praise_count")
            )
            .filter(Praise.post_id.in_(post_ids))
            .group_by(Praise.post_id)
            .all()
        )

        return {post_id: count for post_id, count in praise_count_query}

    @staticmethod
    def _query_user_praised(post_ids):
        """
        批量查询用户对文章的点赞状态
        返回文章ID到是否点赞的映射字典
        """
        current_user_id = current_user.id if current_user else None
        if not current_user_id:
            return {}

        user_praised_query = (
            db.session.query(Praise.post_id)
            .filter(Praise.post_id.in_(post_ids), Praise.author_id == current_user_id)
            .all()
        )

        return {post_id: True for post_id, in user_praised_query}

    @staticmethod
    def _build_extra_data(
        posts, images_dict, comment_counts, praise_counts, user_praised
    ):
        """
        为每篇文章构建预填充的extra_data
        返回文章ID到extra_data的映射字典
        """
        extra_data_map = {}
        for post in posts:
            extra_data_map[post.id] = {
                "author_data": {
                    "username": post.author.username,
                    "nickname": post.author.nickname,
                    "image": get_avatars_url(post.author.image),
                    "id": post.author.id,
                    "music": post.author.music,
                },
                "images": images_dict.get(post.id, []),
                "comment_count": comment_counts.get(post.id, 0),
                "praise_num": praise_counts.get(post.id, 0),
                "has_praised": user_praised.get(post.id, False),
            }

        return extra_data_map

    @staticmethod
    def batch_query_with_data(posts, is_list=False):
        """
        为一组文章批量查询并预填充所有相关数据
        返回预填充了数据后的文章列表

        is_list: 是否为列表API调用，如果为True，使用summary字段减少网络传输
        """

        if not posts:
            return []

        post_ids = [post.id for post in posts]

        # 1. 批量查询图片数据
        images_dict = Post._query_post_images(post_ids)

        # 2. 批量查询评论数量
        comment_counts = Post._query_comment_counts(post_ids)

        # 3. 批量查询点赞数量
        praise_counts = Post._query_praise_counts(post_ids)

        # 4. 批量查询用户点赞状态
        user_praised = Post._query_user_praised(post_ids)

        # 5. 构建extra_data映射
        extra_data_map = Post._build_extra_data(
            posts, images_dict, comment_counts, praise_counts, user_praised
        )

        # 6. 批量转换为JSON
        return [
            post.to_json(extra_data=extra_data_map[post.id], is_list=is_list)
            for post in posts
        ]

    @staticmethod
    def from_json(json_post):
        body = json_post.get("body")
        if body is None or body == "":
            raise ValidationError("post does not have a body")
        return Post(body=body)

    @staticmethod
    def replace_body_html(html, pos, image_urls):
        pos2url = {str(_pos): _url for _pos, _url in zip(pos, image_urls)}

        def replacer(match):
            src = match.group(1)
            alt = match.group(2)
            url = pos2url.get(src)
            if url:
                return f'<img src="{url}" alt="{alt}">'
            else:
                # 不替换
                return match.group(0)

        # 匹配 <img src="数字" alt="xxx">，支持前后有其他内容
        pattern = re.compile(r'<img\s+src="(\d+)"\s+alt="([^"]*)">')
        return pattern.sub(replacer, html)

    @staticmethod
    def replace_body(content, pos, image_urls):
        pos2url = {str(_pos): _url for _pos, _url in zip(pos, image_urls)}

        def replacer(match):
            alt = match.group(1)
            pos = match.group(2)
            url = pos2url.get(pos)
            if url:
                return f"![{alt}]({url})"
            else:
                return match.group(0)

        # 匹配 ![xxx](数字)
        pattern = re.compile(r"!\[([^\]]*)\]\((\d+)\)")
        return pattern.sub(replacer, content)


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=DateUtils.now_time)
    disabled = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))

    # 根评论id
    root_comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"))
    # 根评论
    root_comment = db.relationship(
        "Comment", remote_side=[id], foreign_keys=[root_comment_id]
    )

    # 直接父评论id
    direct_parent_id = db.Column(db.Integer, db.ForeignKey("comments.id"))
    # 直接父评论 remote_side指向"一"的那方
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

    # 通知
    notifications = db.relationship("Notification", backref="comments", lazy="dynamic")
    # 评论点赞
    praise = db.relationship("Praise", backref="comment", lazy="dynamic")

    def to_json(self):
        j = {
            "id": self.id,
            "parentId": self.root_comment_id,
            "directParentId": self.direct_parent_id,
            "uid": self.author.id,
            "content": self.body if not self.disabled else "<p><i>此评论已被版主禁用</i></p>",
            "likes": self.praise.count(),
            "createTime": DateUtils.datetime_to_str(self.timestamp),
            "user": {
                "username": self.author.nickname
                if self.author.nickname
                else self.author.username,
                "avatar": get_avatars_url(self.author.image),
                # 'address': self.author.location,
                "homeLink": f"/user/{self.author.username}",
            },
        }
        return j

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get("body")
        if body is None or body == "":
            raise ValidationError("comment does not have a body")
        return Comment(body=body)


class Praise(db.Model):
    __tablename__ = "praise"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"))

    @staticmethod
    def has_praised(post_id):
        if not current_user:
            return False
        r = Praise.query.filter_by(post_id=post_id, author_id=current_user.id).first()
        return True if r else False


class Log(db.Model):
    __tablename__ = "log"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    ip = db.Column(db.String(100))
    country = db.Column(db.String(50))
    city = db.Column(db.String(50))
    # 浏览器
    browser = db.Column(db.String(50))
    browser_version = db.Column(db.String(50))
    # 操作系统
    os = db.Column(db.String(50))
    os_version = db.Column(db.String(50))
    # 设备
    device = db.Column(db.String(50))
    # 操作行为
    operate = db.Column(db.String(64))
    operate_time = db.Column(db.DateTime, index=True, default=DateUtils.now_time)

    def to_json(self):
        country = self.country if self.country else ""
        city = self.city if self.city else ""
        json_log = {
            "id": self.id,
            "username": self.username,
            "ip": self.ip,
            "addr": country + city,
            "browser": self.browser,
            "os": self.os,
            "device": self.device,
            "operate": self.operate,
            "operateTime": self.operate_time
            if isinstance(self.operate_time, str)
            else DateUtils.datetime_to_str(self.operate_time),
        }
        return json_log


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=DateUtils.now_time)
    is_read = db.Column(db.Boolean, default=False)

    def to_json(self):
        # j = {
        #     'id': self.id,
        #     'sender_id': self.sender_id,
        #     'content': self.content,
        #     'timestamp': DateUtils.datetime_to_str(self.timestamp),
        #     'is_read': self.is_read
        # }
        j = {
            "content": self.content,
            "uid": self.sender_id,
            "user": {
                "username": self.sender.nickname
                if self.sender.nickname
                else self.sender.username,
                "avatar": get_avatars_url(self.sender.image),
            },
            "createTime": self.timestamp
            if isinstance(self.timestamp, str)
            else DateUtils.datetime_to_str(self.timestamp),
            "sender_id": self.sender_id,
            "is_read": self.is_read,
        }
        return j


class ImageType(Enum):
    MOVIE = "电影"
    BOOK = "书籍"
    POST = "文章"
    COMMENT = "评论"


class Image(db.Model):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    # 当type等于movie，book, post(markdown)时，需填写
    describe = db.Column(db.String(64))
    # 图片类型。比如 movie, book, post, comment, markdown
    type = db.Column(db.Enum(ImageType))
    # 关联的id。比如用户，文章，评论id
    related_id = db.Column(db.Integer, nullable=False)
    # 是否禁用（0：未禁用，1：已禁用）
    disabled = db.Column(db.Boolean, default=False)
    # 是否删除（0：未删除，1：已删除）
    isDeleted = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=DateUtils.now_time)

    def to_json(self):
        j = {
            "id": self.id,
            "url": get_avatars_url(self.url),
            "describe": self.describe,
            "type": self.type.value,
            "related_id": self.related_id,
            "disabled": self.disabled,
            "timestamp": self.timestamp,
        }
        return j


# 用户tagb标签。 与用户是 多对多关系
class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True, nullable=False)

    def to_json(self):
        return {"id": self.id, "name": self.name}


# 为Tag模型添加删除前的事件监听。注意，批量删除不会触发，需要改为逐个删除
@event.listens_for(Tag, "before_delete")
def delete_tag_cleanup(mapper, connection, target):
    """删除Tag前，清理中间表中所有关联记录"""
    # 删除中间表中该tag_id对应的所有记录
    connection.execute(user_tag.delete().where(user_tag.c.tag_id == target.id))


user_tag = db.Table(
    "user_tag",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id")),
)

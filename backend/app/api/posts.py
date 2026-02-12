import logging

from flask import current_app, request
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.orm import joinedload

from .. import cache, db, limiter
from ..decorators import DecoratedMethodView
from ..models import Follow, Image, ImageType, Permission, Post, PostType, User
from ..mycelery.notification_task import create_new_post_notifications
from ..utils.cache_helper import cache_invalidator
from ..utils.markdown_truncate import MarkdownTruncator
from ..utils.response import error, success


class PostItemApi(DecoratedMethodView):
    method_decorators = {
        "get": [],
        "delete": [jwt_required(), cache_invalidator],
        "patch": [jwt_required()],
    }

    @staticmethod
    def soft_delete(post):
        logging.info(f"逻辑删除文章: id={post.id}")
        post.deleted = True
        db.session.commit()

    def get(self, id):
        """获取单篇文章"""
        logging.info(f"获取文章: id={id}")
        # 预加载post.author
        post = (
            Post.query.options(
                joinedload(Post.author).load_only(
                    User.id, User.username, User.nickname, User.image
                )
            )
            .filter_by(id=id, deleted=False)
            .first_or_404()
        )

        posts_json = Post.batch_query_with_data([post], is_list=False)

        return success(data=posts_json[0])

    def delete(self, id):
        p = Post.query.filter_by(id=id, deleted=False).first()
        if not p:
            logging.warning(f"用户 {current_user.username} 尝试删除不存在的文章 {id}")
            return error(404, "文章不存在")
        PostItemApi.soft_delete(p)
        return success(message="文章删除成功")

    def patch(self, id):
        logging.info(f"编辑文章: id={id}")
        # 预加载post.author
        post = Post.query.options(
            joinedload(Post.author).load_only(
                User.id, User.username, User.nickname, User.image
            )
        ).get_or_404(id)
        if current_user.username != post.author.username and not current_user.can(
            Permission.ADMIN
        ):
            logging.warning(f"用户 {current_user.username} 尝试编辑不属于自己的文章 {id}")
            return error(403, "没有权限编辑此文章")

        # 对表单编辑业务逻辑
        j = request.get_json()
        post.content = j.get("content", post.content)
        # 更新summary字段
        if "content" in j:
            post.summary = MarkdownTruncator.get_smart_preview(post.content)
        # 编辑markdown文章时新增图片
        images = j.get("images")
        if images:
            images = [
                Image(
                    url=image.get("url", ""),
                    type=ImageType.POST,
                    describe=image.get("pos", ""),
                    related_id=post.id,
                )
                for image in images
            ]
            db.session.add_all(images)
        db.session.commit()

        posts_json = Post.batch_query_with_data([post], is_list=False)

        return success(data=posts_json[0])


class PostGroupApi(DecoratedMethodView):
    method_decorators = {
        # "get": [log_operate],
        # "get": [sql_profile],
        "post": [jwt_required()],
    }

    @staticmethod
    @cache.memoize(timeout=60)
    def query_post(page, per_page, tab_name=None):
        if tab_name and tab_name == "showFollowed":
            base_query = current_user.followed_posts
        else:
            base_query = Post.query.filter_by(deleted=False)

        # 主查询：预加载作者信息
        # joinedload() 的行为是自动创建 join
        query = base_query.options(
            joinedload(Post.author).load_only(
                User.id, User.username, User.nickname, User.image
            )
        ).order_by(Post.timestamp.desc())

        # 分页查询
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        posts = paginate.items

        if not posts:
            return [], paginate.total

        result = Post.batch_query_with_data(posts, is_list=True)

        return result, paginate.total

    @staticmethod
    def new_post_notification(post_id):
        """异步创建新文章通知并推送给粉丝"""
        # 批量查询当前用户的所有粉丝（排除自己）
        followers = (
            Follow.query.filter_by(followed_id=current_user.id)
            .filter(Follow.follower_id != current_user.id)
            .all()
        )

        follower_ids = [follow.follower_id for follow in followers]
        create_new_post_notifications.delay(post_id, current_user.id, follower_ids)

    @staticmethod
    def submit_to_db(post_type, content, images=None):
        try:
            post = Post(
                content=content,
                summary=MarkdownTruncator.get_smart_preview(content),
                type=post_type,
                has_image=bool(images),  # 如果有图片则设置has_image为True
                author=current_user,
            )
            db.session.add(post)
            db.session.flush()
            # images：  [ '', '' ] or [ {'url':'', 'pos':''},{} ]
            # markdown
            if images and isinstance(images[0], dict):
                images = [
                    Image(
                        url=image.get("url", ""),
                        type=ImageType.POST,
                        describe=image.get("pos", ""),
                        related_id=post.id,
                    )
                    for image in images
                ]
                db.session.add_all(images)
            # 图文
            elif images and isinstance(images[0], str):
                images = [
                    Image(url=image, type=ImageType.POST, related_id=post.id)
                    for image in images
                ]
                db.session.add_all(images)
            db.session.commit()
            PostGroupApi.new_post_notification(post.id)
            logging.info(f"创建新文章: user_id={current_user.id}, post_id={post.id}")
        except Exception as e:
            logging.error(f"创建文章失败: {str(e)}", exc_info=True)
            db.session.rollback()
            raise f"创建文章失败: {str(e)}"

    @staticmethod
    @limiter.limit("2/day", exempt_when=lambda: current_user.role_id == 3)
    def publish_image_post(content, images):
        """发布图文文章（带限流）"""
        PostGroupApi.submit_to_db(PostType.TEXT, content, images)

    @staticmethod
    def posts_publish(data: dict):
        content = data.get("content", "")
        # 验证内容长度至少3个字符
        if len(content.strip()) < 3:
            return error(400, "内容长度至少需要3个字符")

        images = data.get("images", [])
        # 可选text, image, markdown
        post_type = data.get("type", "text")
        match post_type:
            case "text":
                PostGroupApi.submit_to_db(PostType.TEXT, content, images)
            case "image":
                PostGroupApi.publish_image_post(content, images)
            case "markdown":
                PostGroupApi.submit_to_db(PostType.MARKDOWN, content, images)

    def get(self):
        """获取所有文章"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get(
            "per_page", current_app.config["FLASKY_POSTS_PER_PAGE"], type=int
        )
        posts, total = PostGroupApi.query_post(
            page, per_page, request.args.get("tabName")
        )
        return success(data=posts, total=total)

    def post(self):
        """发布文章"""
        if current_user.can(Permission.WRITE):
            PostGroupApi.posts_publish(request.json)
            # 清除缓存
            cache.delete_memoized(PostGroupApi.query_post)
            posts, total = PostGroupApi.query_post(
                1, current_app.config["FLASKY_POSTS_PER_PAGE"]
            )
            return success(data=posts, total=total)


def register_post_api(bp, *, post_item_url, post_group_url):
    item = PostItemApi.as_view("post_item")
    group = PostGroupApi.as_view("post_group")
    bp.add_url_rule(post_item_url, view_func=item)
    bp.add_url_rule(post_group_url, view_func=group)

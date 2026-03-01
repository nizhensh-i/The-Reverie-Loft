import logging

from sqlalchemy.orm import joinedload

from ..domain.common.exceptions import NotFoundError, ValidationError
from ..domain.post.policies import ensure_can_edit_post
from ..infrastructure.database.sqlalchemy import db
from ..models import Follow, Image, ImageType, Post, PostType, User
from ..utils.markdown_truncate import MarkdownTruncator
from .common.dto import ActionResult, ItemResult, PageResult
from .common.unit_of_work import SqlAlchemyUnitOfWork


class PostService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.uow = SqlAlchemyUnitOfWork(self.session)

    def list_posts(
        self, *, page: int, per_page: int, viewer=None, tab_name: str | None = None
    ):
        if tab_name == "showFollowed" and viewer is not None:
            base_query = viewer.followed_posts
        else:
            base_query = Post.query.filter_by(deleted=False)

        query = base_query.options(
            joinedload(Post.author).load_only(
                User.id, User.username, User.nickname, User.image
            )
        ).order_by(Post.timestamp.desc())

        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        posts = paginate.items
        if not posts:
            return PageResult(data=[], total=paginate.total)

        return PageResult(
            data=Post.batch_query_with_data(posts, is_list=True),
            total=paginate.total,
        )

    def get_post_detail(self, post_id: int):
        post = (
            Post.query.options(
                joinedload(Post.author).load_only(
                    User.id, User.username, User.nickname, User.image
                )
            )
            .filter_by(id=post_id, deleted=False)
            .first()
        )
        if not post:
            raise NotFoundError("文章不存在")

        return ItemResult(data=Post.batch_query_with_data([post], is_list=False)[0])

    def create_post(
        self, *, author, content: str, post_type: str = "text", images=None
    ):
        images = images or []
        if len((content or "").strip()) < 3:
            raise ValidationError("内容长度至少需要3个字符")

        try:
            mapped_type = self._map_post_type(post_type)
            post = Post(
                content=content,
                summary=MarkdownTruncator.get_smart_preview(content),
                type=mapped_type,
                has_image=bool(images),
                author=author,
            )
            self.session.add(post)
            self.session.flush()

            self._append_images(post_id=post.id, images=images)
            self.uow.commit()

            self._dispatch_new_post_notification(post_id=post.id, author_id=author.id)
            logging.info("创建新文章: user_id=%s, post_id=%s", author.id, post.id)
            return ActionResult(message="发布文章成功", data={"post_id": post.id})
        except Exception:
            self.uow.rollback()
            raise

    def soft_delete_post(self, *, post_id: int):
        post = Post.query.filter_by(id=post_id, deleted=False).first()
        if not post:
            raise NotFoundError("文章不存在")

        logging.info("逻辑删除文章: id=%s", post.id)
        post.deleted = True
        self.uow.commit()
        return ActionResult(message="文章删除成功")

    def edit_post(self, *, post_id: int, operator, payload: dict):
        post = Post.query.options(
            joinedload(Post.author).load_only(
                User.id, User.username, User.nickname, User.image
            )
        ).get(post_id)
        if not post:
            raise NotFoundError("文章不存在")

        ensure_can_edit_post(operator, post)

        content = payload.get("content")
        if content is not None:
            post.content = content
            post.summary = MarkdownTruncator.get_smart_preview(post.content)

        images = payload.get("images")
        if images:
            self._append_images(post_id=post.id, images=images)

        self.uow.commit()
        return ItemResult(data=Post.batch_query_with_data([post], is_list=False)[0])

    def _append_images(self, *, post_id: int, images):
        if not images:
            return

        if isinstance(images[0], dict):
            image_entities = [
                Image(
                    url=image.get("url", ""),
                    type=ImageType.POST,
                    describe=image.get("pos", ""),
                    related_id=post_id,
                )
                for image in images
            ]
            self.session.add_all(image_entities)
            return

        if isinstance(images[0], str):
            image_entities = [
                Image(url=image, type=ImageType.POST, related_id=post_id)
                for image in images
            ]
            self.session.add_all(image_entities)

    @staticmethod
    def _map_post_type(post_type: str):
        if post_type == "markdown":
            return PostType.MARKDOWN
        # 兼容原逻辑: text/image 都存为 TEXT
        return PostType.TEXT

    @staticmethod
    def _dispatch_new_post_notification(*, post_id: int, author_id: int):
        followers = (
            Follow.query.filter_by(followed_id=author_id)
            .filter(Follow.follower_id != author_id)
            .all()
        )
        follower_ids = [follow.follower_id for follow in followers]
        from ..infrastructure.my_celery import create_new_post_notifications

        create_new_post_notifications.delay(post_id, author_id, follower_ids)

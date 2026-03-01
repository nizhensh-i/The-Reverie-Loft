from sqlalchemy import func
from sqlalchemy.orm import joinedload

from ....domain.common.repositories import PageEntities
from ....domain.post.repositories import PostRepository
from ....infrastructure.persistence.models import (
    Comment,
    Follow,
    Image,
    ImageType,
    Post,
    PostType,
    Praise,
    User,
)
from ....utils.common import get_avatars_url


class SqlAlchemyPostRepository(PostRepository):
    def __init__(self, session):
        self.session = session

    @staticmethod
    def create_post(
        *,
        author,
        content: str,
        summary: str,
        post_type_value: str,
        has_image: bool,
    ):
        return Post(
            content=content,
            summary=summary,
            type=PostType(post_type_value),
            has_image=has_image,
            author=author,
        )

    def list_posts(
        self, *, page: int, per_page: int, viewer=None, tab_name: str | None = None
    ) -> PageEntities:
        if tab_name == "showFollowed" and viewer is not None:
            base_query = Post.query.join(
                Follow, Follow.followed_id == Post.author_id
            ).filter(
                Follow.follower_id == viewer.id,
                Post.deleted.is_(False),
            )
        else:
            base_query = Post.query.filter_by(deleted=False)

        query = base_query.options(
            joinedload(Post.author).load_only(
                User.id, User.username, User.nickname, User.image
            )
        ).order_by(Post.timestamp.desc())
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        return PageEntities(items=paginate.items, total=paginate.total)

    def get_post_detail(self, post_id: int):
        return (
            Post.query.options(
                joinedload(Post.author).load_only(
                    User.id, User.username, User.nickname, User.image
                )
            )
            .filter_by(id=post_id, deleted=False)
            .first()
        )

    def get_post_for_update(self, post_id: int):
        return Post.query.options(
            joinedload(Post.author).load_only(
                User.id, User.username, User.nickname, User.image
            )
        ).get(post_id)

    def get_active_post(self, post_id: int):
        return Post.query.filter_by(id=post_id, deleted=False).first()

    def add(self, post) -> None:
        self.session.add(post)

    def add_images(self, image_entities) -> None:
        if image_entities:
            self.session.add_all(image_entities)

    @staticmethod
    def create_post_images(image_payloads):
        if not image_payloads:
            return []
        return [
            Image(
                url=item["url"],
                type=ImageType.POST,
                describe=item.get("describe", ""),
                related_id=item["related_id"],
            )
            for item in image_payloads
        ]

    @staticmethod
    def set_post_type(post, *, post_type_value: str) -> None:
        post.type = PostType(post_type_value)

    @staticmethod
    def list_follower_ids(*, author_id: int) -> list[int]:
        followers = (
            Follow.query.filter_by(followed_id=author_id)
            .filter(Follow.follower_id != author_id)
            .all()
        )
        return [follow.follower_id for follow in followers]

    @staticmethod
    def list_posts_without_summary():
        return Post.query.filter((Post.summary.is_(None)) | (Post.summary == "")).all()

    @staticmethod
    def list_posts_without_content():
        return Post.query.filter((Post.content.is_(None)) | (Post.content == "")).all()

    @staticmethod
    def list_post_ids_with_images():
        rows = (
            Image.query.with_entities(Image.related_id)
            .filter(Image.type == ImageType.POST)
            .distinct()
            .all()
        )
        return [item[0] for item in rows]

    @staticmethod
    def bulk_mark_posts_has_image(post_ids: list[int]) -> None:
        if not post_ids:
            return
        Post.query.filter(Post.id.in_(post_ids)).update(
            {Post.has_image: True}, synchronize_session=False
        )

    @staticmethod
    def count_posts() -> int:
        return Post.query.count()

    @staticmethod
    def count_posts_has_image() -> int:
        return Post.query.filter(Post.has_image.is_(True)).count()

    @staticmethod
    def count_posts_with_content() -> int:
        return Post.query.filter(
            (Post.content.isnot(None)) & (Post.content != "")
        ).count()

    @staticmethod
    def get_by_id(post_id: int):
        return Post.query.filter_by(id=post_id).first()

    @staticmethod
    def build_post_extra_data_map(
        posts, *, viewer_id: int | None = None
    ) -> dict[int, dict]:
        if not posts:
            return {}

        post_ids = [post.id for post in posts]

        images_query = (
            Image.query.with_entities(
                Image.related_id, Image.url, Image.describe, Image.id
            )
            .filter(Image.type == ImageType.POST, Image.related_id.in_(post_ids))
            .order_by(Image.related_id.asc(), Image.id.asc())
            .all()
        )
        images_dict: dict[int, list[dict]] = {}
        for image in images_query:
            images_dict.setdefault(image.related_id, []).append(
                {
                    "url": get_avatars_url(image.url),
                    "describe": image.describe,
                    "id": image.id,
                }
            )

        comments_count_query = (
            Comment.query.with_entities(
                Comment.post_id, func.count(Comment.id).label("comment_count")
            )
            .filter(Comment.post_id.in_(post_ids))
            .group_by(Comment.post_id)
            .all()
        )
        comment_counts = {post_id: count for post_id, count in comments_count_query}

        praise_count_query = (
            Praise.query.with_entities(
                Praise.post_id, func.count(Praise.id).label("praise_count")
            )
            .filter(Praise.post_id.in_(post_ids))
            .group_by(Praise.post_id)
            .all()
        )
        praise_counts = {post_id: count for post_id, count in praise_count_query}

        user_praised = {}
        if viewer_id:
            user_praised_query = (
                Praise.query.with_entities(Praise.post_id)
                .filter(Praise.post_id.in_(post_ids), Praise.author_id == viewer_id)
                .all()
            )
            user_praised = {post_id: True for post_id, in user_praised_query}

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

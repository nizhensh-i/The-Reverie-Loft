from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload

from ....domain.common.repositories import PageEntities
from ....domain.user.repositories import UserRepository
from ....infrastructure.persistence.models import (
    Comment,
    Follow,
    Image,
    ImageType,
    Post,
    Praise,
    Role,
    Tag,
    ThirdPartyAccount,
    User,
    user_tag,
)
from ....utils.common import get_avatars_url
from ....utils.time_util import DateUtils


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session):
        self.session = session

    @staticmethod
    def get_by_id(user_id: int):
        return User.query.get(user_id)

    @staticmethod
    def get_by_username(username: str):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_role_by_id(role_id: int):
        return Role.query.get(role_id)

    @staticmethod
    def list_user_posts(*, user_id: int, page: int, per_page: int) -> PageEntities:
        pagination = (
            Post.query.filter_by(author_id=user_id, deleted=False)
            .options(
                joinedload(Post.author).load_only(
                    User.id, User.username, User.nickname, User.image
                )
            )
            .order_by(Post.timestamp.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        return PageEntities(items=pagination.items, total=pagination.total)

    @staticmethod
    def list_by_ids(user_ids: list[int]):
        if not user_ids:
            return []
        return User.query.filter(User.id.in_(user_ids)).all()

    def add(self, entity) -> None:
        self.session.add(entity)

    def init_roles(self) -> None:
        Role.insert_roles(session=self.session)

    @staticmethod
    def touch_last_seen(*, user_id: int) -> None:
        User.query.filter_by(id=user_id).update(
            {User.last_seen: DateUtils.now_time()},
            synchronize_session=False,
        )

    @staticmethod
    def build_user_extra_data(*, user_id: int, viewer_id: int | None = None) -> dict:
        post_praises = Praise.query.join(Post).filter(Post.author_id == user_id).count()
        comment_praises = (
            Praise.query.join(Comment).filter(Comment.author_id == user_id).count()
        )

        interest_images = (
            Image.query.filter(
                and_(
                    Image.type.in_([ImageType.MOVIE, ImageType.BOOK]),
                    Image.related_id == user_id,
                )
            )
            .order_by(Image.id.asc())
            .all()
        )
        interest = {"movies": [], "books": []}
        for image in interest_images:
            payload = {
                "id": image.id,
                "url": get_avatars_url(image.url),
                "describe": image.describe,
                "type": image.type.value,
                "related_id": image.related_id,
                "disabled": image.disabled,
                "timestamp": image.timestamp,
            }
            if image.type == ImageType.MOVIE:
                interest["movies"].append(payload)
            elif image.type == ImageType.BOOK:
                interest["books"].append(payload)

        bound_providers = [
            provider
            for provider, in ThirdPartyAccount.query.with_entities(
                ThirdPartyAccount.provider
            )
            .filter_by(user_id=user_id)
            .all()
        ]

        is_followed_by_current_user = False
        is_following_current_user = False
        if viewer_id:
            is_followed_by_current_user = (
                Follow.query.filter_by(
                    follower_id=viewer_id, followed_id=user_id
                ).first()
                is not None
            )
            is_following_current_user = (
                Follow.query.filter_by(
                    follower_id=user_id, followed_id=viewer_id
                ).first()
                is not None
            )

        followers_count = (
            Follow.query.with_entities(func.count(Follow.follower_id))
            .filter(Follow.followed_id == user_id, Follow.follower_id != user_id)
            .scalar()
            or 0
        )
        followed_count = (
            Follow.query.with_entities(func.count(Follow.followed_id))
            .filter(Follow.follower_id == user_id, Follow.followed_id != user_id)
            .scalar()
            or 0
        )

        post_count = (
            Post.query.with_entities(func.count(Post.id))
            .filter(Post.author_id == user_id)
            .scalar()
            or 0
        )

        tags = [
            name
            for name, in Tag.query.with_entities(Tag.name)
            .join(user_tag, user_tag.c.tag_id == Tag.id)
            .filter(user_tag.c.user_id == user_id)
            .all()
        ]

        return {
            "praised_count": post_praises + comment_praises,
            "interest": interest,
            "bound_providers": bound_providers,
            "post_count": post_count,
            "followers_count": followers_count,
            "followed_count": followed_count,
            "is_followed_by_current_user": is_followed_by_current_user,
            "is_following_current_user": is_following_current_user,
            "tags": tags,
        }

from ....domain.common.repositories import PageEntities
from ....domain.follow.repositories import FollowRepository
from ....infrastructure.database.sqlalchemy import db
from ....infrastructure.persistence.models import Follow, User


class SqlAlchemyFollowRepository(FollowRepository):
    def __init__(self, session):
        self.session = session

    @staticmethod
    def list_matched_following_users(*, user_id: int, search_query: str):
        followed_user_ids = Follow.query.filter_by(follower_id=user_id).with_entities(
            Follow.followed_id
        )
        return User.query.filter(
            User.id.in_(followed_user_ids),
            db.or_(
                User.username.ilike(f"%{search_query}%"),
                User.nickname.ilike(f"%{search_query}%"),
            ),
        ).all()

    @staticmethod
    def list_matched_follower_users(*, user_id: int, search_query: str):
        follower_ids = Follow.query.filter_by(followed_id=user_id).with_entities(
            Follow.follower_id
        )
        return User.query.filter(
            User.id.in_(follower_ids),
            db.or_(
                User.username.ilike(f"%{search_query}%"),
                User.nickname.ilike(f"%{search_query}%"),
            ),
        ).all()

    @staticmethod
    def list_followers(*, user_id: int, page: int, per_page: int) -> PageEntities:
        pagination = (
            Follow.query.join(Follow.follower)
            .filter(Follow.followed_id == user_id, Follow.follower_id != user_id)
            .order_by(Follow.timestamp.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        return PageEntities(items=pagination.items, total=pagination.total)

    @staticmethod
    def list_following(*, user_id: int, page: int, per_page: int) -> PageEntities:
        pagination = (
            Follow.query.join(Follow.followed)
            .filter(Follow.follower_id == user_id, Follow.followed_id != user_id)
            .order_by(Follow.timestamp.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        return PageEntities(items=pagination.items, total=pagination.total)

    @staticmethod
    def list_followed_ids(*, follower_id: int, candidate_ids: list[int]) -> set[int]:
        rows = (
            Follow.query.filter_by(follower_id=follower_id)
            .filter(Follow.followed_id.in_(candidate_ids))
            .with_entities(Follow.followed_id)
            .all()
        )
        return {item[0] for item in rows}

    @staticmethod
    def list_follower_ids(*, followed_id: int, candidate_ids: list[int]) -> set[int]:
        rows = (
            Follow.query.filter_by(followed_id=followed_id)
            .filter(Follow.follower_id.in_(candidate_ids))
            .with_entities(Follow.follower_id)
            .all()
        )
        return {item[0] for item in rows}

    @staticmethod
    def exists_follow_relation(*, follower_id: int, followed_id: int) -> bool:
        return (
            Follow.query.filter_by(
                follower_id=follower_id, followed_id=followed_id
            ).first()
            is not None
        )

    @staticmethod
    def create_follow_relation(*, follower_id: int, followed_id: int):
        return Follow(follower_id=follower_id, followed_id=followed_id)

    def add(self, entity) -> None:
        self.session.add(entity)

    def delete_follow_relation(self, *, follower_id: int, followed_id: int) -> None:
        relation = Follow.query.filter_by(
            follower_id=follower_id, followed_id=followed_id
        ).first()
        if relation:
            self.session.delete(relation)

    def ensure_self_follows(self) -> int:
        user_ids = [user_id for user_id, in User.query.with_entities(User.id).all()]
        if not user_ids:
            return 0

        existing_self_follow_ids = {
            follower_id
            for follower_id, in Follow.query.with_entities(Follow.follower_id)
            .filter(
                Follow.follower_id.in_(user_ids),
                Follow.follower_id == Follow.followed_id,
            )
            .all()
        }
        missing_ids = [
            user_id for user_id in user_ids if user_id not in existing_self_follow_ids
        ]
        if not missing_ids:
            return 0

        self.session.add_all(
            [
                Follow(follower_id=user_id, followed_id=user_id)
                for user_id in missing_ids
            ]
        )
        return len(missing_ids)

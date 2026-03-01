from ....domain.praise.repositories import PraiseRepository
from ....infrastructure.persistence.models import Comment, Post, Praise


class SqlAlchemyPraiseRepository(PraiseRepository):
    def __init__(self, session):
        self.session = session

    def list_praised_comment_ids_for_post(self, *, user_id: int, post_id: int):
        rows = (
            self.session.query(Praise.comment_id)
            .join(Comment)
            .filter(
                Praise.author_id == user_id,
                Comment.post_id == post_id,
                Praise.comment_id.isnot(None),
            )
            .distinct()
            .all()
        )
        return [item[0] for item in rows]

    @staticmethod
    def get_post(post_id: int):
        return Post.query.get(post_id)

    @staticmethod
    def get_comment(comment_id: int):
        return Comment.query.get(comment_id)

    @staticmethod
    def exists_post_praise(*, user_id: int, post_id: int) -> bool:
        return (
            Praise.query.filter_by(author_id=user_id, post_id=post_id).first()
            is not None
        )

    @staticmethod
    def exists_comment_praise(*, user_id: int, comment_id: int) -> bool:
        return (
            Praise.query.filter_by(author_id=user_id, comment_id=comment_id).first()
            is not None
        )

    def add(self, praise) -> None:
        self.session.add(praise)

    @staticmethod
    def create_post_praise(*, post, author):
        return Praise(post=post, author=author)

    @staticmethod
    def create_comment_praise(*, comment, author):
        return Praise(comment=comment, author=author)

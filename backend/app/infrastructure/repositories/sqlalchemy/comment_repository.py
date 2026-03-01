from ....domain.comment.repositories import CommentRepository
from ....domain.common.repositories import PageEntities
from ....infrastructure.persistence.models import Comment, NotificationType, Post


class SqlAlchemyCommentRepository(CommentRepository):
    def __init__(self, session):
        self.session = session

    @staticmethod
    def get_post(post_id: int):
        return Post.query.get(post_id)

    def get_comment(self, comment_id: int):
        return self.session.get(Comment, comment_id)

    @staticmethod
    def list_replies(*, root_comment_id: int, page: int, per_page: int) -> PageEntities:
        query = Comment.query.filter_by(root_comment_id=root_comment_id).order_by(
            Comment.timestamp.desc()
        )
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return PageEntities(items=pagination.items, total=query.count())

    @staticmethod
    def list_post_root_comments(
        *, post_id: int, page: int, per_page: int
    ) -> PageEntities:
        query = (
            Comment.query.filter_by(post_id=post_id)
            .filter(Comment.root_comment_id.is_(None))
            .order_by(Comment.timestamp.desc())
        )
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return PageEntities(items=pagination.items, total=pagination.total)

    @staticmethod
    def list_all_comments(*, page: int, per_page: int) -> PageEntities:
        query = Comment.query
        pagination = query.order_by(Comment.timestamp.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )
        return PageEntities(items=pagination.items, total=query.count())

    def add(self, comment) -> None:
        self.session.add(comment)

    @staticmethod
    def create_comment(
        *,
        post,
        author,
        body: str,
        direct_parent=None,
        root_comment=None,
    ):
        return Comment(
            body=body,
            post=post,
            author=author,
            direct_parent=direct_parent,
            root_comment=root_comment,
        )

    def delete(self, comment) -> None:
        self.session.delete(comment)

    @staticmethod
    def resolve_notification_type(*, notification_type_code: str):
        notification_type_map = {
            "at": NotificationType.AT,
            "comment": NotificationType.COMMENT,
            "reply": NotificationType.REPLY,
        }
        return notification_type_map[notification_type_code]

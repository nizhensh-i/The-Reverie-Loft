from ....domain.common.unit_of_work import UnitOfWork
from .auth_repository import SqlAlchemyAuthRepository
from .comment_repository import SqlAlchemyCommentRepository
from .follow_repository import SqlAlchemyFollowRepository
from .log_repository import SqlAlchemyLogRepository
from .message_repository import SqlAlchemyMessageRepository
from .notification_repository import SqlAlchemyNotificationRepository
from .oauth_repository import SqlAlchemyOAuthRepository
from .post_repository import SqlAlchemyPostRepository
from .praise_repository import SqlAlchemyPraiseRepository
from .tag_repository import SqlAlchemyTagRepository
from .upload_repository import SqlAlchemyUploadRepository
from .user_repository import SqlAlchemyUserRepository


class SqlAlchemyRepositoryUnitOfWork(UnitOfWork):
    def __init__(self, session):
        self.session = session
        self.posts = SqlAlchemyPostRepository(session)
        self.comments = SqlAlchemyCommentRepository(session)
        self.users = SqlAlchemyUserRepository(session)
        self.follows = SqlAlchemyFollowRepository(session)
        self.tags = SqlAlchemyTagRepository(session)
        self.auth = SqlAlchemyAuthRepository(session)
        self.oauth = SqlAlchemyOAuthRepository(session)
        self.uploads = SqlAlchemyUploadRepository(session)
        self.notifications = SqlAlchemyNotificationRepository(session)
        self.messages = SqlAlchemyMessageRepository(session)
        self.logs = SqlAlchemyLogRepository(session)
        self.praises = SqlAlchemyPraiseRepository(session)

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def flush(self) -> None:
        self.session.flush()

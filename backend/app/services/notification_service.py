from sqlalchemy.orm import joinedload

from ..domain.common.exceptions import ValidationError
from ..infrastructure.database.sqlalchemy import db
from ..models import Notification, User
from .common.dto import ActionResult, ListResult
from .common.unit_of_work import SqlAlchemyUnitOfWork


class NotificationService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.uow = SqlAlchemyUnitOfWork(self.session)

    def list_user_notifications(self, *, user_id: int):
        notifications = (
            Notification.query.options(
                joinedload(Notification.trigger_user).load_only(
                    User.id, User.username, User.nickname, User.image
                )
            )
            .filter_by(receiver_id=user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )
        return ListResult(data=[item.to_json() for item in notifications])

    def update_notifications_read(self, *, user_id: int, ids):
        if ids is None:
            raise ValidationError("参数错误: ids 不能为空")
        Notification.query.filter(
            Notification.id.in_(ids), Notification.receiver_id == user_id
        ).update({"is_read": True}, synchronize_session=False)
        self.uow.commit()
        return ActionResult(message="通知已标记为已读")

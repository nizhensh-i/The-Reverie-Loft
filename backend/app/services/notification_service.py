from ..application.dto import ActionResult, ListResult
from ..domain.common.unit_of_work import UnitOfWork
from ..domain.notification.policies import normalize_notification_ids
from ..domain.ports.assemblers import ResponseAssemblerPort


class NotificationService:
    def __init__(self, *, uow: UnitOfWork, assembler: ResponseAssemblerPort):
        self.uow = uow
        self.assembler = assembler

    def list_user_notifications(self, *, user_id: int):
        notifications = self.uow.notifications.list_by_receiver(user_id=user_id)
        return ListResult(
            data=[self.assembler.map_notification(item) for item in notifications]
        )

    def update_notifications_read(self, *, user_id: int, ids):
        normalized_ids = normalize_notification_ids(ids)
        if not normalized_ids:
            return ActionResult(message="通知已标记为已读")
        self.uow.notifications.mark_read(user_id=user_id, ids=normalized_ids)
        self.uow.commit()
        return ActionResult(message="通知已标记为已读")

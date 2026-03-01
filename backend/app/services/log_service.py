from ..application.dto import ActionResult, PageResult
from ..domain.common.unit_of_work import UnitOfWork
from ..domain.log.policies import normalize_log_delete_ids
from ..domain.ports.assemblers import ResponseAssemblerPort
from ..domain.ports.presence import PresencePort


class LogService:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        assembler: ResponseAssemblerPort,
        presence_port: PresencePort,
    ):
        self.uow = uow
        self.assembler = assembler
        self.presence_port = presence_port

    def rollback(self):
        self.uow.rollback()

    def list_online_users(self):
        user_ids = self.presence_port.list_online_user_ids()
        online_users = self.uow.users.list_by_ids(user_ids)
        users = [self.assembler.map_online_user(user) for user in online_users]
        return PageResult(data=users, total=len(user_ids))

    def list_logs(self, *, page: int, per_page: int):
        page_entities = self.uow.logs.list_logs(page=page, per_page=per_page)
        return PageResult(
            data=[self.assembler.map_log(log) for log in page_entities.items],
            total=page_entities.total,
        )

    def delete_logs(self, *, ids):
        normalized_ids = normalize_log_delete_ids(ids)
        if not normalized_ids:
            return ActionResult(message="没有提供要删除的日志ID", data={"deleted_count": 0})
        deleted_count = self.uow.logs.delete_by_ids(normalized_ids)
        self.uow.commit()
        return ActionResult(
            message=f"成功删除 {deleted_count} 条日志记录",
            data={"deleted_count": deleted_count},
        )

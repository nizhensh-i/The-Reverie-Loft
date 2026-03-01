from ..infrastructure.database.redis import redis
from ..infrastructure.database.sqlalchemy import db
from ..infrastructure.socketio.services import init_ws_services
from ..models import Log, User
from .common.dto import ActionResult, PageResult
from .common.unit_of_work import SqlAlchemyUnitOfWork


class LogService:
    def __init__(self, session=None):
        self.session = session or db.session
        self.uow = SqlAlchemyUnitOfWork(self.session)

    def rollback(self):
        self.uow.rollback()

    def list_online_users(self):
        _, presence, _, _ = init_ws_services(redis)
        user_ids = presence.list_online_users()
        online_users = User.query.filter(User.id.in_(user_ids)).all()
        users = [{"username": u.username, "nickName": u.nickname} for u in online_users]
        return PageResult(data=users, total=len(user_ids))

    def list_logs(self, *, page: int, per_page: int):
        query = Log.query
        paginate = query.order_by(Log.operate_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        logs = paginate.items
        return PageResult(data=[log.to_json() for log in logs], total=query.count())

    def delete_logs(self, *, ids):
        if not ids:
            return ActionResult(message="没有提供要删除的日志ID", data={"deleted_count": 0})
        deleted_count = Log.query.filter(Log.id.in_(ids)).delete()
        self.uow.commit()
        return ActionResult(
            message=f"成功删除 {deleted_count} 条日志记录",
            data={"deleted_count": deleted_count},
        )

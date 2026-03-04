from ....domain.common.repositories import PageEntities
from ....domain.log.repositories import LogRepository
from ....infrastructure.persistence.models import Log


class SqlAlchemyLogRepository(LogRepository):
    def __init__(self, session):
        self.session = session

    @staticmethod
    def list_logs(*, page: int, per_page: int) -> PageEntities:
        query = Log.query
        pagination = query.order_by(Log.operate_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return PageEntities(items=pagination.items, total=query.count())

    @staticmethod
    def delete_by_ids(ids: list[int]) -> int:
        return Log.query.filter(Log.id.in_(ids)).delete()

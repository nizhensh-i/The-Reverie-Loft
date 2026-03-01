class SqlAlchemyUnitOfWork:
    """Small transaction wrapper to centralize commit/rollback semantics."""

    def __init__(self, session):
        self.session = session

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

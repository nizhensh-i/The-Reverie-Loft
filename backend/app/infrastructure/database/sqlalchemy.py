from flask_sqlalchemy import SQLAlchemy

from ..capabilities import set_capability
from ..exceptions import ConfigurationError

db = SQLAlchemy()


class SqlalchemyAdapter:
    def __init__(self, app):
        if app.config["SQLALCHEMY_DATABASE_URI"]:
            db.init_app(app)
            set_capability("database", enabled=True, degraded=False, reason="")
        elif not app.config["TESTING"]:
            set_capability(
                "database",
                enabled=False,
                degraded=True,
                reason="SQLALCHEMY_DATABASE_URI 未配置",
            )
            raise ConfigurationError(
                "SQLALCHEMY_DATABASE_URI 未配置", component="database"
            )


def setup_sqlalchemy(app, throw_exception_if_not_set=True):
    try:
        SqlalchemyAdapter(app)
    except Exception as e:
        set_capability("database", enabled=False, degraded=True, reason=str(e))
        if throw_exception_if_not_set:
            raise e

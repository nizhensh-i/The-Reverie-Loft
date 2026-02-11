from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class SqlalchemyAdapter:
    def __init__(self, app):
        if app.config["SQLALCHEMY_DATABASE_URI"]:
            db.init_app(app)
        elif not app.config["TESTING"]:
            raise "未设置数据库url"


def setup_sqlalchemy(app, throw_exception_if_not_set=True):
    try:
        SqlalchemyAdapter(app)
    except Exception as e:
        if throw_exception_if_not_set:
            raise e

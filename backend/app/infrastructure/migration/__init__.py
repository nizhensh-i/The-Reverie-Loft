import click
from flask_migrate import Migrate, stamp, upgrade
from sqlalchemy import inspect

migrate = Migrate()


def setup_migration(app, db):
    migrate.init_app(app, db)

    @app.shell_context_processor
    def make_shell_context():
        from app.infrastructure.persistence.models import (
            Comment,
            Follow,
            Image,
            ImageType,
            Log,
            Permission,
            Post,
            PostType,
            Praise,
            Role,
            User,
        )

        return dict(
            db=db,
            User=User,
            Follow=Follow,
            Role=Role,
            Permission=Permission,
            Post=Post,
            Comment=Comment,
            Praise=Praise,
            Log=Log,
            Image=Image,
            PostType=PostType,
            ImageType=ImageType,
        )

    @app.cli.command()
    def deploy():
        """运行部署任务"""
        try:
            upgrade()
        except Exception:
            # 兼容历史迁移链缺少“初始建表”脚本的场景：
            # 只要核心业务表尚未建立，就按当前模型建表并将版本标记到 head。
            inspector = inspect(db.engine)
            existing_tables = set(inspector.get_table_names())
            core_tables = {"users", "roles", "posts"}
            if core_tables.issubset(existing_tables):
                raise

            from app.infrastructure.persistence import models as _models  # noqa: F401

            db.create_all()
            stamp(revision="head")

        from app.infrastructure.repositories.sqlalchemy.unit_of_work import (
            SqlAlchemyRepositoryUnitOfWork,
        )

        uow = SqlAlchemyRepositoryUnitOfWork(db.session)
        uow.users.init_roles()
        uow.follows.ensure_self_follows()
        uow.commit()

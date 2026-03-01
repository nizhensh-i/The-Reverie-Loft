import click
from flask_migrate import Migrate, upgrade

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
        upgrade()
        from app.infrastructure.repositories.sqlalchemy.unit_of_work import (
            SqlAlchemyRepositoryUnitOfWork,
        )

        uow = SqlAlchemyRepositoryUnitOfWork(db.session)
        uow.users.init_roles()
        uow.follows.ensure_self_follows()
        uow.commit()

    @app.cli.command("add")
    @click.argument("some")
    def add(some):
        print(some)

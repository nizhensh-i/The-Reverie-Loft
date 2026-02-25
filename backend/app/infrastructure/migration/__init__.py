import click
from flask_migrate import Migrate, upgrade

migrate = Migrate()


def setup_migration(app, db):
    migrate.init_app(app, db)

    @app.shell_context_processor
    def make_shell_context():
        from app.models import (
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
        from app.models import Role, User

        Role.insert_roles()
        User.add_self_follows()

    @app.cli.command("add")
    @click.argument("some")
    def add(some):
        print(some)

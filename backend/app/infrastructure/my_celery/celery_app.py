from datetime import timedelta

from celery import Celery, Task


def celery_init_app(app) -> Celery:
    """
    mac：
        cd blog_backend
        celery -A app.make_celery worker -B --loglevel INFO --logfile=logs/celery.log

    windows:
        cd blog_backend
        celery -A app.make_celery worker -B --loglevel INFO --logfile=logs/celery.log -P eventlet
    """

    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(
        app.name, task_cls=FlaskTask, BROKER_CONNECTION_RETRY_ON_STARTUP=True
    )
    celery_app.config_from_object(app.config["CELERY"])

    # 配置周期性任务
    celery_app.conf.beat_schedule = {
        "del_post_task": {
            "task": "app.mycelery.tasks.hard_delete_post",
            "schedule": timedelta(days=30),
            # 测试用，1分钟执行一次
            # "schedule": timedelta(minutes=1.0),
        },
    }

    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def setup_celery(app):
    celery_init_app(app)

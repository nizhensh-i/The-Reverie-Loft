from datetime import timedelta

from celery import Celery, Task

from ..capabilities import capability_enabled, get_capability, set_capability


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
    celery_config = dict(app.config["CELERY"])
    if not capability_enabled("redis", default=True):
        # Redis 不可用时降级为进程内执行，避免 .delay() 直接失败。
        celery_config.update(
            {
                "broker_url": "memory://",
                "result_backend": "cache+memory://",
                "task_always_eager": True,
                "task_eager_propagates": True,
            }
        )
        reason = (get_capability("redis") or {}).get("reason", "redis unavailable")
        set_capability(
            "celery",
            enabled=True,
            degraded=True,
            reason=f"fallback to eager mode: {reason}",
        )
    else:
        set_capability("celery", enabled=True, degraded=False, reason="")
        celery_app.conf.update(celery_config)

    # 配置周期性任务
    celery_app.conf.beat_schedule = {
        "del_post_task": {
            "task": "app.infrastructure.my_celery.tasks.hard_delete_post",
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

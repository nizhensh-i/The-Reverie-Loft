import logging
import time
from functools import wraps

from flask import request
from flask.views import MethodView
from flask_jwt_extended import current_user
from flask_sqlalchemy import record_queries
from user_agents import parse

from .domain.common.constants import PermissionCode
from .utils.response import forbidden


class DecoratedMethodView(MethodView):
    method_decorators = {
        # '方法名': [装饰器列表]
        # 'get': [admin_required],
        # 'post': [user_required],
        # 共有的
        # 'share': [],
    }

    def dispatch_request(self, *args, **kwargs):
        meth = getattr(self, request.method.lower(), None)
        if meth is None and request.method == "HEAD":
            meth = getattr(self, "get", None)
        assert meth is not None, f"Unimplemented method {request.method}"
        share = self.method_decorators.get("share", [])
        # 逐个装饰当前方法
        for dec in share + self.method_decorators.get(request.method.lower(), []):
            meth = dec(meth)
        return meth(*args, **kwargs)


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                return forbidden()
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    return permission_required(PermissionCode.ADMIN)(f)


def log_operate(f):
    def decorate(*args, **kwargs):
        if request.args.get("page", 1, type=int) != 1:
            return f(*args, **kwargs)

        if "X-Forwarded-For" in request.headers:
            client_ip = request.headers.get("X-Forwarded-For")
        else:
            client_ip = request.remote_addr

        user_agent = request.headers.get("user-agent")
        if user_agent:
            u = parse(user_agent)
            ua = {
                "browser": u.browser.family,
                "browser_version": u.browser.version_string,
                "os": u.os.family,
                "os_version": u.os.version_string,
                "device": u.device.family,
            }
        else:
            ua = {
                "browser": "",
                "browser_version": "",
                "os": "",
                "os_version": "",
                "device": "",
            }
        is_register = True if current_user else False
        ua.update(
            {
                "username": current_user.username if is_register else "游客",
                "operate": "访问首页",
            }
        )

        # 延迟导入以避免循环依赖
        from .infrastructure.my_celery import log_visitor

        # 记录用户
        log_visitor.delay(is_register, client_ip, ua)
        return f(*args, **kwargs)

    return decorate


def sql_profile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 记录开始时间
        start_time = time.time()

        # 执行函数
        result = func(*args, **kwargs)

        # 拿到 SQL 执行记录
        queries = record_queries.get_recorded_queries()

        total_sql = len(queries)
        total_sql_time = sum(q.duration for q in queries)  # 秒

        # 函数名称
        func_name = func.__name__

        logging.info("\n===== SQL STATISTICS =====")
        logging.info(f"Function     : {func_name}")
        logging.info(f"Total SQL    : {total_sql}")
        logging.info(f"SQL Time     : {total_sql_time:.2f} sec")
        logging.info(f"Total Time   : {time.time() - start_time:.2f} sec\n")

        for idx, q in enumerate(queries, start=1):
            logging.info(
                f"\n[{idx}] ({q.duration:.6f}s) \n{q.statement} \nParams: {q.parameters} \n{'-' * 60}"
            )
        logging.info("==========================\n")

        return result

    return wrapper

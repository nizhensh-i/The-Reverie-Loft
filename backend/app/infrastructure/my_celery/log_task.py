import logging
import os

import requests
from celery import shared_task

from ...utils.time_util import DateUtils
from ..database.sqlalchemy import db


@shared_task(ignore_result=False)
def log_visitor(is_register, client_ip, user_agent):
    # 构建查询条件
    log_filter = {"username": user_agent.get("username")}
    if not is_register:
        log_filter = {"ip": client_ip}
    from ...infrastructure.persistence.models import Log

    # 获取最近访问记录
    last_visit = (
        Log.query.filter_by(**log_filter).order_by(Log.operate_time.desc()).first()
    )

    # 判断访问间隔
    now = DateUtils.now_time()
    should_log = not last_visit or DateUtils.datetime_diff(
        now, DateUtils.datetime_to_str(last_visit.operate_time), 5
    )

    # 记录日志
    if should_log:
        # 用户身份信息
        client_info = get_client_info(client_ip)
        client_info.update(user_agent)

        db.session.add(Log(**client_info))
        db.session.commit()
        logging.info("访客已记录日志")


def get_client_info(client_ip):
    # 获取用户地理位置
    if os.environ.get("FLASK_DEBUG", None):
        country = None
        city = None
    else:
        try:
            r = requests.get(f"https://ipapi.co/{client_ip}/json/")
            local_data = r.json()
            country = local_data.get("country_name")
            city = local_data.get("city")
        except Exception:
            country = None
            city = None

    user_info = {"ip": client_ip, "country": country, "city": city}
    return user_info

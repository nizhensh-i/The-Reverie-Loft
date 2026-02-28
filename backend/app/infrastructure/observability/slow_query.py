import logging

from flask import current_app
from flask_sqlalchemy import record_queries


def setup_slow_query_monitor(app):
    @app.after_request
    def after_request(response):
        for query in record_queries.get_recorded_queries():
            if query.duration >= current_app.config["FLASKY_SLOW_DB_QUERY_TIME"]:
                logging.warning(
                    "慢查询: %s\\n参数: %s\\n时长: %fs\\n",
                    query.statement,
                    query.parameters,
                    query.duration,
                )
        return response

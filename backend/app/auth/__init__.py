from flask import Blueprint

auth = Blueprint("auth", __name__)

from . import third_party_login  # noqa: E402,F401 保证路由注册
from . import jwt, views


def setup_auth_bp(app):
    app.register_blueprint(auth, url_prefix="/auth")


__all__ = ["setup_auth_bp"]

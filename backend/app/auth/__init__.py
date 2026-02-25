from flask import Blueprint

auth = Blueprint("auth", __name__)

from . import jwt, third_party_login, views  # noqa: E402,F401 保证路由注册


def setup_auth_bp(app):
    app.register_blueprint(auth, url_prefix="/auth")


__all__ = ["setup_auth_bp"]

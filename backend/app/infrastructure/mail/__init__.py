import os

from flask_mail import Mail

mail = Mail()


class MailAdapter:
    def __init__(self, app):
        if os.getenv("MAIL_USERNAME") and os.getenv("MAIL_PASSWORD"):
            mail.init_app(app)
        elif not app.config["TESTING"]:
            raise "未设置Email代理凭证"


def setup_mail(app, throw_exception_if_not_set=True):
    try:
        MailAdapter(app)
    except Exception as e:
        if throw_exception_if_not_set:
            raise e

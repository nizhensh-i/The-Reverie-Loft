import logging

from flask_mail import Mail

from ..capabilities import set_capability
from ..config import InfraConfig

mail = Mail()


class MailAdapter:
    def __init__(self, app):
        if InfraConfig.has_mail_credentials():
            mail.init_app(app)
            set_capability("mail", enabled=True, degraded=False, reason="")
        else:
            reason = "missing env config: MAIL_USERNAME/MAIL_PASSWORD"
            set_capability("mail", enabled=False, degraded=True, reason=reason)
            logging.warning("邮件服务降级: %s", reason)


def setup_mail(app, throw_exception_if_not_set=True):
    try:
        MailAdapter(app)
    except Exception as e:
        set_capability("mail", enabled=False, degraded=True, reason=str(e))
        if throw_exception_if_not_set:
            raise e

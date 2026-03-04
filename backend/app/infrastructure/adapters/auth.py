from ...domain.ports.auth import EmailCodePort, MailSenderPort
from ..auth import AuthCodeTokenService
from ..my_celery import send_email


class RedisEmailCodeAdapter(EmailCodePort):
    def __init__(self, redis_client):
        self._service = AuthCodeTokenService(redis_client)

    def generate_email_code(self, email: str, expiration: int = 60 * 3):
        return self._service.generate_email_code(email=email, expiration=expiration)

    def compare_email_code(self, email: str, code: str | int) -> bool:
        return self._service.compare_email_code(email=email, code=code)

    def clear_email_code(self, email: str) -> None:
        self._service.clear_email_code(email=email)


class CeleryMailSender(MailSenderPort):
    def send_template_email(
        self, to: str, subject: str, template: str, **kwargs
    ) -> None:
        send_email.delay(to, subject, template, **kwargs)

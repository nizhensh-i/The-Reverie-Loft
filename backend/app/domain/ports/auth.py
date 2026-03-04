from __future__ import annotations

from typing import Optional, Protocol


class EmailCodePort(Protocol):
    def generate_email_code(
        self, email: str, expiration: int = 60 * 3
    ) -> Optional[int]:
        ...

    def compare_email_code(self, email: str, code: str | int) -> bool:
        ...

    def clear_email_code(self, email: str) -> None:
        ...


class MailSenderPort(Protocol):
    def send_template_email(
        self, to: str, subject: str, template: str, **kwargs
    ) -> None:
        ...
